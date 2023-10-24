from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import F
from rest_framework import status, permissions
from django.contrib.auth import get_user_model, authenticate
from accounts.models import History
from .models import Quiz
from . import constant
from quizzes.serializers import QuizListSerializer,QuizDetailSerializer, QuizCreateSerializer,CommentListSerializer,CommentCreateSerializer, AnswerReadSerializer
from quizzes.serializers import AnswerCreateSerializer

# Create your views here.
class QuizView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    def get(self,request,quiz_id=None):
        if quiz_id:
            # 상세보기
            quiz = get_object_or_404(Quiz, pk=quiz_id)
            serializer = QuizDetailSerializer(quiz)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # 전체보기
            quizzes = Quiz.objects.all()
            serializer = QuizListSerializer(quizzes, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self,request):
        serializer = QuizCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
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
    def post(self,request,quiz_id):
        quiz = get_object_or_404(Quiz, pk=quiz_id)
        hint = quiz.hint
        user = request.user
        user.update(point=F("point")-constant.HINT_DEDUCTED_POINT)
        History.objects.create(user=user, action="hint", point=user.point)
        return Response({"hint": hint}, status=status.HTTP_200_OK)


class LikesView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, quiz_id):
        user = request.user
        quiz = get_object_or_404(Quiz, pk=quiz_id)
        author = quiz.author
        if user in quiz.likes.all():
            return Response({"detail": "이미 좋아요를 눌렀습니다."}, status=status.HTTP_200_OK)
        else:
            quiz.likes.add(user)
            author.update(point=F("point")+constant.LIKED_ACQUIRED_POINT)
            # History 모델 objects 모델 매니저 쿼리셋을 생성
            History.objects.create(user=author, action="likes", point=author.point)
            return Response({"detail": "좋아요."}, status=status.HTTP_200_OK)


class CommentsView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    def get(self,request,quiz_id):
        quiz=get_object_or_404(Quiz,pk=quiz_id)
        # 일반 댓글 가져옴
        comments=quiz.comments.select_related("author").only("author__nickname", "content", "updated_at")
        comments_serializer=CommentListSerializer(comments,many=True)
        if quiz.solved == True:
            answer = quiz.answer
            answer_serializer=AnswerReadSerializer(answer)
            return Response({"answer": answer_serializer.data, "comments": comments_serializer.data,},status=status.HTTP_200_OK)
        
        return Response({"comments": comments_serializer.data},status=status.HTTP_200_OK)
    
    def post(self,request,quiz_id):
        quiz=get_object_or_404(Quiz,pk=quiz_id)
        if quiz.solved != True:
            if request.data["content"]==quiz.correct_answer:
                serializer=AnswerCreateSerializer(data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    user.update(point=F("point")+constant.ANSWERED_POINT)
                    user=request.user
                    History.objects.create(user=user, action="quiz", point=user.point)
                    quiz.solved = True
                    quiz.save()
                    return Response({"data": serializer.data, "is_answer": True},status=status.HTTP_200_OK)
                else:
                    return Response({"detail": "유효하지 않은 댓글"},status=status.HTTP_400_BAD_REQUEST)
        serializer=CommentCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data, "is_answer": False},status=status.HTTP_200_OK)
