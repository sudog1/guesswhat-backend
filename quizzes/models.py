from django.db import models
from config.settings import AUTH_USER_MODEL


def image_file_path(instance, filename):
    return f"images/{instance.author.nickname}/{filename}"


# Create your models here.


class Quiz(models.Model):
    author = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="quizzes",
        null=True,
    )
    correct_answer = models.CharField(max_length=50)
    hint = models.CharField(max_length=128, blank=True)
    solved = models.BooleanField(default=False)
    image = models.ImageField(upload_to=image_file_path)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(
        AUTH_USER_MODEL,
        related_name="likes",
    )


class Comment(models.Model):
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(
        AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments"
    )
    content = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)


class Answer(models.Model):
    quiz = models.OneToOneField(Quiz, on_delete=models.CASCADE)
    author = models.ForeignKey(
        AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="answers"
    )
    content = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
