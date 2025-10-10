from django.db import models

class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
    

class Author(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Movie(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    year = models.IntegerField()
    poster = models.ImageField(upload_to='posters/', blank=True, null=True)
    video = models.FileField(upload_to='movies/', blank=True, null=True)

    likes = models.PositiveIntegerField(default=0)
    genres = models.ManyToManyField(Genre, related_name='movies', blank=True)
    authors = models.ManyToManyField(Author, related_name='movies', blank=True)

    def __str__(self):
        return self.title
