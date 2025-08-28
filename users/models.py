from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.utils import timezone


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    is_seller = models.BooleanField(default=False)
    # Use only one field for email verification
    email_verified = models.BooleanField(default=False)

    def get_uidb64(self):
        return urlsafe_base64_encode(force_bytes(self.pk))

    def verify_email(self):
        """Mark user's email as verified and activate account"""
        self.email_verified = True
        self.is_active = True  # Activate account when email is verified
        self.save()

    def __str__(self):
        return self.username