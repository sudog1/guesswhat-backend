from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)
from .views import UserView, RankingView

urlpatterns = [
    # 로그인
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    # 갱신
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # 로그아웃
    path("token/blacklist/", TokenBlacklistView.as_view(), name="token_blacklist"),
    # 회원가입/회원수정
    path("", UserView.as_view(), name="account"),
    # 프로필 정보조회
    path("<int:user_id>/", UserView.as_view(), name="account_profile"),
    # 명예의전당?
    path("ranking/", RankingView.as_view(), name="ranking"),
    # 나의랭킹
    path("<int:user_id>/ranking/", RankingView.as_view(), name="myranking"),
]
