from django.db import models
from users.managers import CustomUserManager
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Represents customers and platform users.
    """
    username = None
    email = models.EmailField(unique=True)
    address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    USERNAME_FIELD = 'email'  # Use email instead of username
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Author(models.Model):
    """
    Represents book authors.
    """
    name = models.CharField(max_length=200)
    biography = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Member(models.Model):
    """
    Represents library members with membership details.
    """
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    membership_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)


    def __str__(self):
        return f"{self.name} - {self.email}"


