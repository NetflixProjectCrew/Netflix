from rest_framework import serializers
from django.utils.text import slugify
from .models import Movie, Genre, Author


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для модели жанра фильма"""
    movies_count = serializers.SerializerMethodField()

    class Meta:
        model = Genre
        fields = ['id', 'name', 'slug', 'films_count']
        read_only_fields = ['slug', 'films_count']

    def get_movies_count(self, obj):
        return obj.movies.count()
    
    def create(self, validated_data):
        validated_data['slug'] = slugify(validated_data['name'])
        return super().create(validated_data)
    

class AuthorSerializer(serializers.ModelSerializer):
    """Сериализатор для модели автора фильма"""
    movies_count = serializers.SerializerMethodField()

    class Meta:
        model = Author
        fields = [
            'id', 'name', 'slug', 'bio', 'created_at', 
            'updated_at', 'movies_count'
            ]
        read_only_fields = ['slug', 'created_at', 'updated_at', 'movies_count']

    def get_movies_count(self, obj):
        return obj.movies.count()
    
    def create(self, validated_data):
        validated_data['slug'] = slugify(validated_data['name'])
        return super().create(validated_data)


class MovieSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()
    genres = serializers.StringRelatedField(many=True)
    likes = serializers.ReadOnlyField()
    views = serializers.ReadOnlyField()

    class Meta:
        model = Movie
        fields = [
            'id', 'title', 'slug', 'description', 
            'year', 'poster', 'video', 'likes', 
            'views', 'author', 'genres'
            ]
        read_only_fields = ['slug', 'author','likes', 'views']
    
    def to_representation(self, instance):
        data = super().to_representation(instance)

        if len(data['description']) > 50:
            data['description'] = data['description'][:50] + '...'
        return data


class MovieDetailSerializer(serializers.ModelSerializer):
    author_info = serializers.SerializerMethodField()
    genres_info = serializers.SerializerMethodField()

    likes = serializers.ReadOnlyField()
    views = serializers.ReadOnlyField()

    class Meta:
        model = Movie
        fields = [
            'id', 'title', 'slug', 'description', 
            'year', 'poster', 'video', 'likes', 
            'views', 'author', 'genres'
            ]
        read_only_fields = ['slug', 'author','likes', 'views']
    
    def get_author_info(self, obj):
        author = obj.author
        return {
            'id': author.id,
            'name': author.name,
            'slug': author.slug,
            'bio': author.bio,
            'avatar': author.avatar.url if author.avatar else None,
            'movies_count': author.movies.count()
        }
    
    def get_genres_info(self, obj):
        if obj.genres:
            return [
                {
                    'id': genre.id,
                    'name': genre.name,
                    'slug': genre.slug,
                    'movies_count': genre.movies.count()
                } for genre in obj.genres.all()
            ]
        return []


class MovieCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления фильма"""
   
    class Meta:
        model = Movie
        fields = [
            'title', 'description', 
            'year', 'poster', 'video', 
            'author', 'genres'
            ]
    
    def create(self, validated_data):
        validated_data['slug'] = slugify(validated_data['title'])
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        if 'title' in validated_data:
            validated_data['slug'] = slugify(validated_data['title'])
        return super().update(instance, validated_data)
