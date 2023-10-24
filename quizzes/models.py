from django.db import models
from config.settings import AUTH_USER_MODEL

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
    image = models.CharField(max_length=255,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(
        AUTH_USER_MODEL,
        related_name="quizzes_likes",
    )


class Comment(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="comments",)
    author=models.ForeignKey(AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='comments')
    content=models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Answer(models.Model):
    quiz = models.OneToOneField(Quiz,on_delete=models.CASCADE)
    author = models.ForeignKey(AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='answers')
    content=models.CharField(max_length=128)                        
    created_at = models.DateTimeField(auto_now_add=True)