from rest_framework import generics, permissions, filters, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import transaction
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend

from .models import Movie, Genre, Author, Actor, MovieCharacter, Casting
from apps.accounts.models import Watched, Favorite
from .serializers import (
    MovieSerializer,
    MovieDetailSerializer,
    MovieCreateUpdateSerializer,
    GenreSerializer,
    AuthorSerializer,
    ActorSerializer,
    MovieCharacterSerializer,
    CastingSerializer,
    CastingCreateSerializer,
)
from .permissions import IsAdminOrReadOnly

from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser  # или IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Movie
from .tasks import compute_movie_duration

# ===== Genres =====

class GenreListCreateView(generics.ListCreateAPIView):
    serializer_class = GenreSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'movies_count']
    ordering = ['name']

    def get_queryset(self):
        return Genre.objects.annotate(movies_count=Count('movies')).all()


class GenreDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]
    lookup_field = 'slug'


# ===== Authors =====

class AuthorListCreateView(generics.ListCreateAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'bio']
    ordering_fields = ['name']
    ordering = ['name']


class AuthorDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]
    lookup_field = 'slug'


# ===== Actors =====

class ActorListCreateView(generics.ListCreateAPIView):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'bio']
    ordering_fields = ['name']
    ordering = ['name']


class ActorDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]
    lookup_field = 'slug'


# ===== Characters =====

class CharacterListCreateView(generics.ListCreateAPIView):
    queryset = MovieCharacter.objects.all()
    serializer_class = MovieCharacterSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'slug']
    ordering_fields = ['name']
    ordering = ['name']


class CharacterDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MovieCharacter.objects.all()
    serializer_class = MovieCharacterSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]
    lookup_field = 'slug'


# ===== Movies =====

class MovieListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['year', 'genres', 'author', 'author__slug', 'genres__slug']
    search_fields = ['title', 'description', 'author__name', 'genres__name']
    ordering_fields = ['title', 'year', 'views']
    ordering = ['-year']

    def get_queryset(self):
        return (
            Movie.objects
            .select_related('author')
            .prefetch_related('genres', 'cast__actor', 'cast__character')
            .annotate()  # при желании можно аннотировать likes
            .distinct()
            .all()
        )

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MovieCreateUpdateSerializer
        return MovieSerializer


class MovieDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = (
        Movie.objects
        .select_related('author')
        .prefetch_related('genres', 'cast__actor', 'cast__character')
        .all()
    )
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return MovieCreateUpdateSerializer
        return MovieDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


# ===== Movie Actions =====

FINISH_THRESHOLD = 90  # %
MIN_WATCH_SECONDS_TO_COUNT_VIEW = 60

class MovieActionsViewSet(viewsets.GenericViewSet):
    queryset = Movie.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'slug'

    @staticmethod
    def _to_nonneg_int(val, default=0):
        try:
            return max(int(val), 0)
        except (TypeError, ValueError):
            return default

    @action(detail=True, methods=['post'])
    def like(self, request, slug=None):
        movie = self.get_object()
        Favorite.objects.get_or_create(user=request.user, movie=movie)
        return Response({'status': 'liked'})

    @action(detail=True, methods=['post'])
    def unlike(self, request, slug=None):
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

        position = self._to_nonneg_int(request.data.get('position_sec', 0))
        duration = self._to_nonneg_int(request.data.get('duration_sec', 0))

        percent = 0 if duration == 0 else min(100, round(position * 100 / duration))
        finished = percent >= FINISH_THRESHOLD

        with transaction.atomic():
            obj, _ = Watched.objects.select_for_update().get_or_create(
                user=request.user, movie=movie
            )

            obj.last_position_sec = max(obj.last_position_sec, position)
            obj.duration_sec = max(obj.duration_sec, duration)
            obj.progress_percent = max(obj.progress_percent, percent)

            if not obj.finished and finished:
                obj.finished = True
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


class MovieRefreshMetaView(APIView):
    permission_classes = [IsAdminUser]  # можно IsAuthenticated, если нужно шире

    def post(self, request, slug):
        movie = get_object_or_404(Movie, slug=slug)
        compute_movie_duration.delay(movie.id) #type: ignore
        return Response({"status": "scheduled"}, status=status.HTTP_202_ACCEPTED)

# ===== Casting endpoints =====

class CastingViewSet(viewsets.ModelViewSet):
    """
    Состав фильма. Поддерживает:
    - GET /movies/<slug>/cast/           -> список каста фильма
    - POST /movies/<slug>/cast/          -> добавить запись (actor, character, ...), body = CastingCreateSerializer
    - DELETE /movies/<slug>/cast/<pk>/   -> удалить запись каста
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]

    def get_queryset(self):
        movie_slug = self.kwargs.get('slug')
        return (
            Casting.objects
            .filter(movie__slug=movie_slug)
            .select_related('movie', 'actor', 'character')
            .order_by('credit_order', 'id')
        )

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return CastingCreateSerializer
        return CastingSerializer

    def perform_create(self, serializer):
        movie_slug = self.kwargs.get('slug')
        movie = generics.get_object_or_404(Movie, slug=movie_slug)
        serializer.save(movie=movie)


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