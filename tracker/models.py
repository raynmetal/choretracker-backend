from django.db import models
from django.contrib.auth.models import AbstractUser

from tracker.managers import CustomUserManager

# Create your models here.
class User(AbstractUser):
    username = None
    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField('email address', unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email
