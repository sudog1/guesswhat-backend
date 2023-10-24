from rest_framework import serializers
from .models import Quiz,Comment, Answer

class QuizListSerializer(serializers.ModelSerializer):
    likes_count = serializers.IntegerField()
    comments_count = serializers.IntegerField()
    author = serializers.SerializerMethodField()

    def get_author(self, obj):
        return {
            "id": obj.author.pk,
            "nickname": obj.author.nickname,
        }
    class Meta:
        model=Quiz
        fields=("author", "solved", "likes_count", "comments_count", "image")

class QuizDetailSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    answer_len = serializers.SerializerMethodField()
    def get_author(self, obj):
        return {
            "id": obj.author.pk,
            "nickname": obj.author.nickname,
        }
    def get_answer_len(self, obj):
        return len(obj.correct_answer)
    class Meta:
        model=Quiz
        fields=("image", "author", "answer_len")

class QuizCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model=Quiz
        fields="__all__"


class AnswerReadSerializer(serializers.ModelSerializer):
    author=serializers.SerializerMethodField()
    def get_author(self,obj):
        return {"nickname":obj.author.nickname,"id":obj.author.id}
    class Meta:
        model=Answer
        fields=("author","content","updated_at")

class CommentListSerializer(serializers.ModelSerializer):
    author=serializers.SerializerMethodField()
    # quiz=serializers.SerializerMethodField()
    def get_author(self,obj):
        return {"nickname":obj.author.nickname,"id":obj.author.id}
    # def get_quiz(self,obj):
    #     return {""}
    class Meta:
        model=Comment
        fields=("author","content","updated_at")

class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model=Comment
        fields="__all__"

class AnswerCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model=Answer
        fields="__all__"