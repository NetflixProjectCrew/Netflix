# Определяет модели для приложения "accounts"
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

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
    favorite_movies = models.ManyToManyField(
        'movies.Movie',
        through='accounts.Favorite',
        related_name='fans',   # movie.fans -> queryset пользователей
        blank=True,
    )
    watched_movies = models.ManyToManyField(
        'movies.Movie',
        through='accounts.Watched',
        related_name='watchers',  # movie.watchers -> queryset пользователей
        blank=True,
    )
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
    

class Favorite(models.Model):
    """Лайк/избранное."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey('movies.Movie', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_favorites'
        unique_together = ('user', 'movie')  # один лайк на фильм
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} ♥ {self.movie}'


class Watched(models.Model):
    """Факт просмотра (можно расширять прогрессом)."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    movie = models.ForeignKey('movies.Movie', on_delete=models.CASCADE)
    
    
    last_position_sec = models.PositiveIntegerField(default=0)  # для резюме-просмотра
    duration_sec = models.PositiveIntegerField(default=0)  # длительность фильма
    progress_percent = models.PositiveSmallIntegerField(default=0)  # 0–100
    finished = models.BooleanField(default=True)    


    created_at = models.DateTimeField(auto_now_add=True)
    watched_at = models.DateTimeField(auto_now=True)  # когда в последний раз смотрел


    class Meta:
        db_table = 'user_watched'
        unique_together = ('user', 'movie')  # один активный запись на фильм
        ordering = ['-watched_at']

    def __str__(self):
        return f'{self.user} watched {self.movie} ({self.progress_percent}%)'