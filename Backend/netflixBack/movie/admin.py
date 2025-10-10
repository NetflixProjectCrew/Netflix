from django.contrib import admin
from .models import Movie, Genre, Author


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'year', 'likes')  
    list_filter = ('year', 'genres', 'authors') 
    search_fields = ('title', 'description')     
    filter_horizontal = ('genres', 'authors')    


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

