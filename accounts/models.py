from django.db import models
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)
from django.contrib.auth.validators import UnicodeUsernameValidator


class UserManager(BaseUserManager):
    def create_user(self, password, **fields):
        user = self.model(**fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, **fields):
        fields.setdefault("is_admin", True)
        fields.setdefault("is_superuser", True)
        user = self.create_user(**fields)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        "username",
        max_length=30,
        unique=True,
        validators=[username_validator],
    )
    email = models.EmailField(
        "email",
        max_length=50,
        unique=True,
    )
    nickname = models.CharField(
        "nickname",
        max_length=30,
        unique=True,
    )
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    point = models.PositiveIntegerField(default=100)

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "nickname"]

    def __str__(self):
        return self.nickname

    @property
    def is_staff(self):
        return self.is_admin


class History(models.Model):
    ACTION_CHOICE = (
        ("likes", "likes"),
        ("quiz", "quiz"),
        ("hint", "hint"),
        ("create", "create"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="history")
    action = models.CharField(max_length=10, choices=ACTION_CHOICE, default="likes")
    created_at = models.DateTimeField(auto_now_add=True)
    point = models.PositiveIntegerField()
