from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import F
from rest_framework import status, permissions
from django.contrib.auth import get_user_model, authenticate
from accounts.models import History
from config.settings import DEEPL_API_KEY, KARLO_API_KEY
from .models import Quiz
from . import constant
from quizzes.serializers import (
    QuizListSerializer,
    QuizDetailSerializer,
    QuizCreateSerializer,
    CommentListSerializer,
    CommentCreateSerializer,
    AnswerReadSerializer,
)
from quizzes.serializers import AnswerCreateSerializer
import deepl
import base64
from django.core.files.base import ContentFile
from datetime import datetime
from django.db.models import Count


# Create your views here.
class QuizView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, quiz_id=None):
        if quiz_id:
            # 상세보기
            user = request.user
            quiz = get_object_or_404(
                Quiz.objects.annotate(
                    likes_count=Count("likes", distinct=True),
                    comments_count=Count("comments", distinct=True),
                ),
                pk=quiz_id,
            )
            serializer = QuizDetailSerializer(quiz)
            data = serializer.data
            if user.is_authenticated and quiz in user.likes.all():
                data["is_liked"] = True
            else:
                data["is_liked"] = False
            return Response(data, status=status.HTTP_200_OK)
        else:
            # 전체보기
            quizzes = (
                Quiz.objects.select_related("author")
                .only("author__nickname", "created_at", "solved")
                .annotate(
                    likes_count=Count("likes", distinct=True),
                    comments_count=Count("comments", distinct=True),
                )
                .order_by("-created_at")
            )

            serializer = QuizListSerializer(quizzes, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data
        encoded_image = data.get("image")
        decoded_image = base64.b64decode(encoded_image)
        current_time = int(datetime.now().timestamp())
        image_file = ContentFile(decoded_image, name=f"{current_time}.webp")
        data["image"] = image_file
        serializer = QuizCreateSerializer(data=data)
        if serializer.is_valid():
            user = request.user
            serializer.save(author=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, quiz_id):
        quiz = get_object_or_404(Quiz, pk=quiz_id)
        user = request.user
        if quiz.author != user:
            return Response({"detail": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        quiz.delete()
        return Response({"detail": "삭제되었습니다"}, status=status.HTTP_200_OK)


class HintView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, quiz_id):
        quiz = get_object_or_404(Quiz, pk=quiz_id)
        hint = quiz.hint
        user = request.user
        user.point = F("point") + constant.HINT_DEDUCTED_POINT
        user.save()
        user.refresh_from_db()
        History.objects.create(user=user, action="hint", point=user.point)
        return Response({"hint": hint}, status=status.HTTP_200_OK)


class LikesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, quiz_id):
        user = request.user
        quiz = get_object_or_404(Quiz, pk=quiz_id)
        author = quiz.author
        if user in quiz.likes.all():
            return Response(
                {"detail": "이미 좋아요를 눌렀습니다."}, status=status.HTTP_400_BAD_REQUEST
            )
        else:
            quiz.likes.add(user)
            author.point = F("point") + constant.LIKED_ACQUIRED_POINT
            author.save()
            author.refresh_from_db()
            History.objects.create(user=author, action="likes", point=author.point)
            return Response(
                {"likes_count": quiz.likes.count()}, status=status.HTTP_200_OK
            )


class CommentsView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, quiz_id):
        quiz = get_object_or_404(Quiz, pk=quiz_id)
        # 일반 댓글 가져옴
        comments = quiz.comments.select_related("author").only(
            "author__nickname", "content", "created_at"
        )
        comments_serializer = CommentListSerializer(comments, many=True)
        if quiz.solved == True:
            answer = quiz.answer
            answer_serializer = AnswerReadSerializer(answer)
            return Response(
                {
                    "answer": answer_serializer.data,
                    "comments": comments_serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"comments": comments_serializer.data}, status=status.HTTP_200_OK
        )

    def post(self, request, quiz_id):
        quiz = get_object_or_404(Quiz, pk=quiz_id)
        user = request.user
        if user==quiz.author:
            return Response({"detail": "권한이 없습니다"}, status=status.HTTP_403_FORBIDDEN)
        
        if quiz.solved != True:
            if request.data.get("content") == quiz.correct_answer:
                serializer = AnswerCreateSerializer(data=request.data)
                if serializer.is_valid():
                    serializer.save(author=user, quiz=quiz)
                    user.point = F("point") + constant.ANSWERED_POINT
                    user.save()
                    user.refresh_from_db()
                    History.objects.create(user=user, action="quiz", point=user.point)
                    quiz.solved = True
                    quiz.save()
                    return Response(
                        {"data": serializer.data, "is_answer": True},
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(
                        {"detail": "유효하지 않은 댓글"}, status=status.HTTP_400_BAD_REQUEST
                    )
        serializer = CommentCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=user, quiz=quiz)
            return Response(
                {"data": serializer.data, "is_answer": False}, status=status.HTTP_200_OK
            )
        return Response({"detail": "유효하지 않은 댓글"}, status=status.HTTP_400_BAD_REQUEST)


class ImageView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        prompt = request.data.get("prompt")
        print(prompt)
        if user.point < 1:
            return Response({"detail": "포인트가 부족합니다."}, status=status.HTTP_403_FORBIDDEN)
        user.point = F("point") - constant.API_REQUEST_POINT
        user.save()
        user.refresh_from_db()
        History.objects.create(user=user, action="quiz", point=user.point)
        translator = deepl.Translator(DEEPL_API_KEY)
        result = translator.translate_text(prompt, target_lang="EN-US")
        return Response(
            {"prompt": result.text, "API_KEY": KARLO_API_KEY}, status=status.HTTP_200_OK
        )
