# Определяет модели для приложения "accounts"
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Пользовательская модель пользователя, расширяющая AbstractUser."""

    username = models.CharField(
        max_length=50,
        unique=True,
        error_messages={
            'unique': "A user with that username already exists.",
        },
    )
    email = models.EmailField(
        unique=True,
        error_messages={
            'unique': "A user with that email already exists.",
        },
    )
    # Базовые поля
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Поля, связанные с бизнес логикой
    # watched_movies
    # favorite_movies
    # subscription_status
    # subscription_expiry
    # subscription_type
    # 



    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['username']

    def __str__(self):
        return self.username

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    

