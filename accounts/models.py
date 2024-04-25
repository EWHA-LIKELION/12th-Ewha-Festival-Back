from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    nickname=models.CharField(max_length=8)
    is_booth=models.BooleanField(default=False)
    is_tf=models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.nickname
