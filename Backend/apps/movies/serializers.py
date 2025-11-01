from rest_framework import serializers
from django.utils.text import slugify
from .models import Movie, Genre, Author, Actor, MovieCharacter, Casting
from apps.accounts.models import Watched


# ===== Base =====

class GenreSerializer(serializers.ModelSerializer):
    movies_count = serializers.SerializerMethodField()

    class Meta:
        model = Genre
        fields = ['id', 'name', 'slug', 'movies_count']
        read_only_fields = ['slug', 'movies_count']

    def get_movies_count(self, obj):
        return obj.movies.count()

    def create(self, validated_data):
        validated_data['slug'] = slugify(validated_data['name'])
        return super().create(validated_data)


class AuthorSerializer(serializers.ModelSerializer):
    movies_count = serializers.SerializerMethodField()

    class Meta:
        model = Author
        fields = ['id', 'name', 'slug', 'bio', 'created_at', 'updated_at', 'movies_count']
        read_only_fields = ['slug', 'created_at', 'updated_at', 'movies_count']

    def get_movies_count(self, obj):
        return obj.movies.count()

    def create(self, validated_data):
        validated_data['slug'] = slugify(validated_data['name'])
        return super().create(validated_data)


class ActorSerializer(serializers.ModelSerializer):
    movies_count = serializers.SerializerMethodField()

    class Meta:
        model = Actor
        fields = ['id', 'name', 'slug', 'bio', 'avatar', 'created_at', 'updated_at', 'movies_count']
        read_only_fields = ['slug', 'created_at', 'updated_at', 'movies_count']

    def get_movies_count(self, obj):
        return obj.movies.count()

    def create(self, validated_data):
        validated_data['slug'] = slugify(validated_data['name'])
        return super().create(validated_data)


# ===== Characters & Cast =====

class MovieCharacterSerializer(serializers.ModelSerializer):
    appearances_count = serializers.SerializerMethodField()

    class Meta:
        model = MovieCharacter
        fields = ['id', 'name', 'slug', 'appearances_count']
        read_only_fields = ['slug', 'appearances_count']

    def get_appearances_count(self, obj):
        return obj.appearances.count()

    def create(self, validated_data):
        validated_data['slug'] = slugify(validated_data['name'])
        return super().create(validated_data)


class ActorShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = ['id', 'name', 'slug', 'avatar']


class CharacterShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovieCharacter
        fields = ['id', 'name', 'slug']


class CastingSerializer(serializers.ModelSerializer):
    """Read-serializer: выдаём состав с вложенными актёром и персонажем"""
    actor = ActorShortSerializer(read_only=True)
    character = CharacterShortSerializer(read_only=True)

    class Meta:
        model = Casting
        fields = ['id', 'actor', 'character', 'credit_order', 'is_voice', 'is_cameo', 'notes']


class CastingCreateSerializer(serializers.ModelSerializer):
    """
    Write-serializer: создаём/меняем записи каста по ID.
    Передаём: actor (id), character (id). movie берём из view.
    """
    class Meta:
        model = Casting
        fields = ['actor', 'character', 'credit_order', 'is_voice', 'is_cameo', 'notes']


# ===== Movies =====

class MovieSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()
    genres = serializers.StringRelatedField(many=True)
    likes = serializers.SerializerMethodField()
    views = serializers.ReadOnlyField()
    cast = CastingSerializer(many=True, read_only=True)  # <-- добавили состав
    
    class Meta:
        model = Movie
        fields = [
            'id', 'title', 'slug', 'description', 
            'year', 'poster', 'video', 'likes',
            'views', 'author', 'genres', 'cast'
        ]
        read_only_fields = ['slug', 'author', 'likes', 'views',]

 
    def get_likes(self, obj):
        request = self.context.get('request')
        count = getattr(obj, 'favorite_set', None).count() if hasattr(obj, 'favorite_set') else 0 # type: ignore
        is_liked = False
        if request and request.user.is_authenticated and hasattr(obj, 'favorite_set'):
            is_liked = obj.favorite_set.filter(user=request.user).exists()
        return {'count': count, 'is_liked': is_liked}

    def get_user_progress(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return None
        w = (
            Watched.objects.filter(user=user, movie=obj)
            .only('last_position_sec', 'duration_sec', 'progress_percent', 'finished')
            .first()
        )
        if not w:
            return None
        return {
            'position_sec': w.last_position_sec,
            'duration_sec': w.duration_sec,
            'progress_percent': w.progress_percent,
            'finished': w.finished,
        }


class MovieDetailSerializer(serializers.ModelSerializer):
    author_info = serializers.SerializerMethodField()
    genres_info = serializers.SerializerMethodField()
    likes = serializers.ReadOnlyField()
    views = serializers.ReadOnlyField()
    cast = CastingSerializer(many=True, read_only=True)  # <-- cast и здесь
    
    class Meta:
        model = Movie
        fields = [
            'id', 'title', 'slug', 'description',
            'year', 'poster', 'video', 'likes',
            'views', 'author', 'author_info', 'genres', 'genres_info',
            'cast',
        ]
        read_only_fields = ['slug', 'author', 'likes', 'views']

    def get_author_info(self, obj):
        author = obj.author
        if not author:
            return None
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
    """Создание/обновление фильма без каста (каст — отдельным эндпоинтом)"""
    class Meta:
        model = Movie
        fields = ['title', 'description', 'year', 'poster', 'video', 'author', 'genres']

    def create(self, validated_data):
        validated_data['slug'] = slugify(validated_data['title'])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'title' in validated_data:
            validated_data['slug'] = slugify(validated_data['title'])
        return super().update(instance, validated_data)
