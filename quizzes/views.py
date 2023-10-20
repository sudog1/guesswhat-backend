from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model, authenticate

# Create your views here.
class QuizView(APIView):
    pass 

class HintView(APIView):
    pass

class LikesView(APIView):
    pass

class CommentsView(APIView):
    pass