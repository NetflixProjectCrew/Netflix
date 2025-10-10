from rest_framework import generics, permissions, filters, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend

from .models import Movie, Genre, Author
from .serializers import (
    MovieSerializer,
    MovieDetailSerializer,
    MovieCreateUpdateSerializer,
    GenreSerializer, 
    AuthorSerializer
)
from .permissions import IsAdminOrReadOnly


class GenreListCreateView(generics.ListCreateAPIView):
    """ API endpoint для жанров фильмов """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'movies_count']
    ordering = ['name']


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
        queryset = Movie.objects.select_related('author').prefetch_related('genres').all()
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
        """Переопределяем метод retrieve чтобы увеличить счетчик просмотров"""
        instance = self.get_object()
        
        if request.method == 'GET':
            instance.increment_views()

        # instance.save(update_fields=['views'])
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)