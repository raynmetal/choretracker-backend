import jwt

from datetime import datetime, timedelta 

from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin

from tracker.managers import CustomUserManager

# Create your models here.
class User(AbstractUser, PermissionsMixin):
    username = None
    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField('email address', unique=True, db_index=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    def __str__(self):
        return self.email
    
    @property 
    def token(self):
        return self._generate_jwt_token() 
    
    def _generate_jwt_token(self):
        dt = datetime.now() + timedelta(days=60)
        token = jwt.encode({
            'id': self.pk,
            'exp': int(dt.timestamp())
        }, settings.SECRET_KEY, algorithm='HS256')

        return token.decode('utf-8')
