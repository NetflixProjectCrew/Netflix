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
    avatar = models.ImageField(upload_to='actors/', blank=True, null=True)

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
    avatar = models.ImageField(upload_to='authors/', blank=True, null=True)

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


class Movie(models.Model):
    """Модель фильма"""

    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    
    description = models.TextField()
    year = models.IntegerField()
    poster = models.ImageField(upload_to='posters/', blank=True, null=True)
    video = models.FileField(upload_to='movies/', blank=True, null=True)

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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
    
    def get_absolute_url(self):
        return reverse("movie-watch", kwargs={"slug": self.slug})
    
    @property
    def views_count(self):
        return self.views
    

    def increment_views(self):
        """Метод для увеличения количества просмотров фильма"""
        Movie.objects.filter(pk=self.pk).update(views=F('views') + 1)
