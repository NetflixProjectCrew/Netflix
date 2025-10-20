from rest_framework import generics, permissions, filters, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Q, Count
from django_filters.rest_framework import DjangoFilterBackend

from .models import Movie, Genre, Author, Actor
from apps.accounts.models import Watched, Favorite
from .serializers import (
    MovieSerializer,
    MovieDetailSerializer,
    MovieCreateUpdateSerializer,
    GenreSerializer, 
    AuthorSerializer,
    ActorSerializer
)
from .permissions import IsAdminOrReadOnly


class GenreListCreateView(generics.ListCreateAPIView):
    """ API endpoint для жанров фильмов """
    
    serializer_class = GenreSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'movies_count']
    ordering = ['name']

    def get_queryset(self):
        """Возвращает жанры с аннотацией количества фильмов"""
        queryset = Genre.objects.annotate(movies_count=Count('movies')).all()
        return queryset

class GenreDetailView(generics.RetrieveUpdateDestroyAPIView):
    """ API endpoint для конкретного жанра фильма """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]
    lookup_field = 'slug'


class AuthorListCreateView(generics.ListCreateAPIView):
    """ API endpoint для авторов фильмов """
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'bio']
    ordering_fields = ['name']
    ordering = ['name']


class AuthorDetailView(generics.RetrieveUpdateDestroyAPIView):
    """ API endpoint для конкретного автора фильма """
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]
    lookup_field = 'slug'


class ActorListCreateView(generics.ListCreateAPIView):
    """ API endpoint для актеров фильмов """
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'bio']
    ordering_fields = ['name']
    ordering = ['name']


class ActorDetailView(generics.RetrieveUpdateDestroyAPIView):
    """ API endpoint для конкретного актера фильма """
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]
    lookup_field = 'slug'


class MovieListCreateView(generics.ListCreateAPIView):
    """ API endpoint для фильмов """
    serializer_class = MovieSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend ,filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['year','genres' ,'author','author__slug', 'genres__slug']
    search_fields = ['title', 'description', 'author__name', 'genres__name']
    ordering_fields = ['title', 'year', 'likes', 'views']
    ordering = ['-year']

    def get_queryset(self):
        """Возвращает фильмы с оптимизацией запросов"""
        queryset = (
            Movie.objects
                        .select_related('author')
                        .prefetch_related('genres')
                        .annotate(likes=Count('fans'))
                        .distinct()
                        .all()
                )
        return queryset
    

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MovieCreateUpdateSerializer
        return MovieSerializer


class MovieDetailView(generics.RetrieveUpdateDestroyAPIView):
    """ API endpoint для конкретного фильма """
    queryset = Movie.objects.select_related('author').prefetch_related('genres').all()
    serializer_class = MovieDetailSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return MovieCreateUpdateSerializer
        return MovieDetailSerializer
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Старая логика инкремента просмотров
        # if request.method == 'GET':
        #     instance.increment_views()
        # instance.save(update_fields=['views'])
    
        serializer = self.get_serializer(instance)
        return Response(serializer.data)



FINISH_THRESHOLD = 90  # %
MIN_WATCH_SECONDS_TO_COUNT_VIEW = 60  

class MovieActionsViewSet(viewsets.GenericViewSet):
    queryset = Movie.objects.all()
    permission_classes = [permissions.IsAuthenticated,]
    lookup_field = 'slug'


    @staticmethod
    def _to_nonneg_int(val, default=0):
        """Преобразует значение в неотрицательное целое число, возвращает default при ошибке."""
        try:
            return max(int(val), 0)
        except (TypeError, ValueError):
            return default

    @action(detail=True, methods=['post'])
    def like(self, request, slug=None):
        """Поставить лайк фильму"""
        movie = self.get_object()
        Favorite.objects.get_or_create(user=request.user, movie=movie)
        return Response({'status': 'liked'})

    @action(detail=True, methods=['post'])
    def unlike(self, request, slug=None):
        """Убрать лайк"""
        movie = self.get_object()
        Favorite.objects.filter(user=request.user, movie=movie).delete()
        return Response({'status': 'unliked'})

    @action(detail=True, methods=['post'])
    def progress(self, request, slug=None):
        """
        Body:
        {
          "position_sec": 123,
          "duration_sec": 3600
        }
        """
        movie = self.get_object()

        # получение данных из запроса
        position = self._to_nonneg_int(request.data.get('position_sec', 0))
        
        duration = self._to_nonneg_int(request.data.get('duration_sec', 0))

        # пересчёт процентов
        percent = 0 if duration == 0 else min(100, round(position * 100 / duration))
        finished = percent >= FINISH_THRESHOLD

        with transaction.atomic():
            obj, _ = Watched.objects.select_for_update().get_or_create(
                user=request.user, movie=movie
            )

            # Не откатываем назад прогресс, если пришла меньшая позиция (например, перемотка назад)
            obj.last_position_sec = max(obj.last_position_sec, position)
            obj.duration_sec = max(obj.duration_sec, duration)
            obj.progress_percent = max(obj.progress_percent, percent)

            # Фиксируем «завершено» только один раз
            if not obj.finished and finished:
                obj.finished = True

                # Инкрементируем просмотры фильма только при первом достижении порога завершения
                if movie and obj.last_position_sec >= MIN_WATCH_SECONDS_TO_COUNT_VIEW:
                    movie.increment_views()

            obj.save(update_fields=[
                'last_position_sec', 
                'duration_sec', 
                'progress_percent',
                'finished', 
            ])

        return Response({
            'position_sec': obj.last_position_sec,
            'duration_sec': obj.duration_sec,
            'progress_percent': obj.progress_percent,
            'finished': obj.finished,
        })


class MyWatchedMoviesView(generics.ListAPIView):
    """ API endpoint для списка просмотренных фильмов пользователя """
    serializer_class = MovieSerializer
    permission_classes = [permissions.IsAuthenticated]
    
   
    def get_queryset(self):
        user = self.request.user

        movie_ids = (Watched.objects
                     .filter(user=user)                
                     .values_list('movie_id', flat=True))


        return (
            Movie.objects
            .filter(id__in = movie_ids)
            .select_related('author')
            .prefetch_related('genres')
            .all()
            )
