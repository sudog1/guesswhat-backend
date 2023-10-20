from django.urls import path
from . import views

urlpatterns = [
    # 퀴즈 조회/생성
    path("", views.QuizView.as_view(), name="quizzes"),
    # 퀴즈 상세/삭제
    path("<int:quiz_id>/", views.QuizView.as_view(), name="quiz_detail"),
    # 힌트
    path("<int:quiz_id>/hint/", views.HintView.as_view(), name="hint"),
    # 좋아요
    path("<int:quiz_id>/likes/", views.LikesView.as_view(), name="likes"),
    # 댓글 조회/등록
    path("<int:quiz_id>/comments/", views.CommentsView.as_view(), name="comments"),

]