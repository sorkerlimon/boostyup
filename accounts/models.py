import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
import random

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    is_email_verified = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

class Profile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=255, blank=True)
    nick_name = models.CharField(max_length=255, blank=True)
    gender = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    language = models.CharField(max_length=50, blank=True)
    timezone = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class OTP(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField()
    code = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    @classmethod
    def generate_otp(cls, email):
        code = str(random.randint(100000, 999999))
        from django.utils import timezone
        from datetime import timedelta
        expires_at = timezone.now() + timedelta(minutes=10)
        
        otp = cls.objects.create(
            email=email,
            code=code,
            expires_at=expires_at
        )
        
        from django.conf import settings
        send_mail(
            'BOOSTYUPME - Verification Code',
            f'Your verification code is: {code}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        
        return otp
