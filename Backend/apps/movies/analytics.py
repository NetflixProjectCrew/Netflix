from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone
from datetime import timedelta
from .models import Movie
from apps.accounts.models import Watched


class MovieAnalytics:
    """Аналитика по фильмам"""
    
    @staticmethod
    def get_popular_movies(days=30, limit=10):
        """Самые популярные фильмы за период"""
        cutoff_date = timezone.now() - timedelta(days=days)
        
        return (
            Movie.objects
            .annotate(
                recent_views=Count(
                    'watchers',
                    filter=Q(watched__watched_at__gte=cutoff_date)
                ),
                completion_rate=Avg(
                    'watched__progress_percent',
                    filter=Q(watched__watched_at__gte=cutoff_date)
                )
            )
            .filter(recent_views__gt=0)
            .order_by('-recent_views')[:limit]
        )
    
    @staticmethod
    def get_user_recommendations(user, limit=10):
        """Рекомендации на основе истории просмотров"""
        # Получаем жанры просмотренных фильмов
        watched_genres = (
            user.watched_movies.all()
            .values_list('genres__id', flat=True)
            .distinct()
        )
        
        # Ищем похожие фильмы
        return (
            Movie.objects
            .filter(genres__id__in=watched_genres)
            .exclude(id__in=user.watched_movies.values_list('id', flat=True))
            .annotate(views_count=Count('watchers'))
            .order_by('-views_count', '-created_at')
            .distinct()[:limit]
        )