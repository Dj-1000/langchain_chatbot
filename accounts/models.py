from django.db import models
from django.contrib.auth.models import AbstractBaseUser,AbstractUser,User
from django.contrib.auth import get_user_model
from django.contrib.auth.models import UserManager,BaseUserManager


class ChatUser(AbstractUser):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.CharField(max_length=100,unique=True)
    password = models.CharField(max_length=100)
    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS=['username']

    def __str__(self) -> str:
        return self.email










