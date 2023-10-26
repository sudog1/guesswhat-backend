from rest_framework import serializers
from .models import Quiz, Comment, Answer


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
        model = Quiz
        fields = (
            "id",
            "author",
            "solved",
            "image",
            "created_at",
            "likes_count",
            "comments_count",
        )


class QuizDetailSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    likes_count = serializers.IntegerField()
    comments_count = serializers.IntegerField()
    answer_len = serializers.SerializerMethodField()

    def get_author(self, obj):
        return {
            "id": obj.author.pk,
            "nickname": obj.author.nickname,
        }

    def get_answer_len(self, obj):
        return len(obj.correct_answer)

    class Meta:
        model = Quiz
        fields = (
            "image",
            "author",
            "answer_len",
            "likes_count",
            "comments_count",
        )


class QuizCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ("correct_answer", "hint", "image")


class AnswerReadSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    def get_author(self, obj):
        return {"nickname": obj.author.nickname, "id": obj.author.id}

    class Meta:
        model = Answer
        fields = ("author", "content", "created_at")


class CommentListSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    def get_author(self, obj):
        return {"nickname": obj.author.nickname, "id": obj.author.id}

    class Meta:
        model = Comment
        fields = ("author", "content", "created_at")


class CommentCreateSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    def get_author(self, obj):
        return {"nickname": obj.author.nickname, "id": obj.author.id}

    class Meta:
        model = Comment
        fields = ("content", "author")


class AnswerCreateSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    def get_author(self, obj):
        return {"nickname": obj.author.nickname, "id": obj.author.id}

    class Meta:
        model = Answer
        fields = ("content", "author")
