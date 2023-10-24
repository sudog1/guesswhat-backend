from rest_framework import serializers
from accounts.models import User
from django.contrib.auth import get_user_model

class UserCreateSerialzier(serializers.ModelSerializer):
    
    class Meta:
        model=get_user_model()
        fields =( "username",
            "email",
            "password",
            "nickname",)
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = super().create(validated_data)
        password = user.password
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user
    
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "point", "nickname"]


#로그인
# class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
#     @classmethod
#     def get_token(cls, user):
#         token = super().get_token(user)
#         token['nickname'] = user.nickname
#         return token