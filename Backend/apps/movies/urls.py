from django.urls import path
from . import views

app_name = 'movies'

movie_like  = views.MovieActionsViewSet.as_view({'post': 'like'})
movie_unlike = views.MovieActionsViewSet.as_view({'post': 'unlike'})
movie_progress = views.MovieActionsViewSet.as_view({'post': 'progress'})

urlpatterns = [
    # Genres
    path('genres/', views.GenreListCreateView.as_view(), name='genre-list-create'),
    path('genres/<slug:slug>/', views.GenreDetailView.as_view(), name='genre-detail'),

    # Authors
    path('authors/', views.AuthorListCreateView.as_view(), name='author-list-create'),
    path('authors/<slug:slug>/', views.AuthorDetailView.as_view(), name='author-detail'),
    
    # Actors
    path('actors/', views.ActorListCreateView.as_view(), name='actor-list-create'),
    path('actors/<slug:slug>/', views.ActorDetailView.as_view(), name='actor-detail'),


    # Movies CRUD 
    path('movies/', views.MovieListCreateView.as_view(),  name='movie-list'),
    path('movies/<slug:slug>/', views.MovieDetailView.as_view(), name='movie-detail'),

    # Movie actions 
    path('movies/<slug:slug>/like/', movie_like, name='movie-like'),
    path('movies/<slug:slug>/unlike/', movie_unlike, name='movie-unlike'),
    path('movies/<slug:slug>/progress/', movie_progress, name='movie-progress'),

    # «Мои просмотренные»
    path('me/watched/', views.MyWatchedMoviesView.as_view(),  name='my-watched-movies'),
]

