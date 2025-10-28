from datetime import timedelta
from django.utils import timezone
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.db.models import F

class Genre(models.Model):
    """Модель жанра фильма"""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        db_table = "genres"
        verbose_name = "Genre"
        verbose_name_plural = "Genres"
        ordering = ["name"]

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Actor(models.Model):
    """Модель актера"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/actors/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "actors"
        verbose_name = "Actor"
        verbose_name_plural = "Actors"
        ordering = ["name"]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    
    def __str__(self):
        return self.name


class Author(models.Model):
    """Модель автора фильма"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/authors/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "authors"
        verbose_name = "Author"
        verbose_name_plural = "Authors"
        ordering = ["name"]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    
    def __str__(self):
        return self.name


class MovieCharacter(models.Model):
    name = models.CharField(max_length=100, unique=True)  
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    # можно добавить "franchise" и т.п.

    class Meta:
        db_table = "movie_characters"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Casting(models.Model):
    """Связь: в каком фильме какой актёр играет какого персонажа"""
    movie = models.ForeignKey('Movie', related_name='cast', on_delete=models.CASCADE)
    character = models.ForeignKey('MovieCharacter', related_name='appearances', on_delete=models.PROTECT)
    actor = models.ForeignKey('Actor', related_name='castings', on_delete=models.PROTECT)

    credit_order = models.PositiveIntegerField(default=0)
    is_voice = models.BooleanField(default=False)
    is_cameo = models.BooleanField(default=False)
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = "casting"
        unique_together = ('movie', 'character', 'actor')
        ordering = ['movie', 'credit_order']

    

class Movie(models.Model):
    """Модель фильма"""

    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    
    description = models.TextField()
    year = models.IntegerField()
    poster = models.ImageField(upload_to='movies/posters/', blank=True, null=True)
    video = models.FileField(upload_to='movies/videos', blank=True, null=True)
    duration = models.DurationField(null=True, blank=True)

    views = models.PositiveIntegerField(default=0)
    genres = models.ManyToManyField(
        Genre, 
        related_name='movies', 
        blank=True,
        )
    
    author = models.ForeignKey(
        Author, 
        related_name='movies', 
        blank=True,
        on_delete=models.CASCADE, 
        null=True
        )
    
    characters = models.ManyToManyField(
        MovieCharacter,
        through='Casting',
        related_name='movies',
        blank=True,
    )
    actors = models.ManyToManyField(
        Actor,
        through='Casting',
        related_name='movies',
        blank=True,
    )


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    last_meta_update = models.DateTimeField(null=True, blank=True)
    meta_dirty = models.BooleanField(default=False)

    class Meta:
        db_table = "movies"
        verbose_name = "Movie"
        verbose_name_plural = "Movies"
        ordering = ["author", "title"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def needs_meta_refresh(self, ttl_minutes: int = 60) -> bool:
        if self.meta_dirty or not self.last_meta_update:
            return True
        return timezone.now() - self.last_meta_update > timedelta(minutes=ttl_minutes)

    def get_absolute_url(self):
        return reverse("movie-watch", kwargs={"slug": self.slug})
    
    @property
    def views_count(self):
        return self.views
    

    def increment_views(self):
        """Метод для увеличения количества просмотров фильма"""
        Movie.objects.filter(pk=self.pk).update(views=F('views') + 1)
