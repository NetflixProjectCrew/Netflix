import logging
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.throttling import UserRateThrottle

from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction

from .models import SubscriptionPlan, Subscription, SubscriptionHistory
from .serializers import (
    SubscriptionPlanSerializer,
    SubscriptionSerializer,
    SubscriptionCreateSerializer,
    SubscriptionHistorySerializer,
    UserSubscriptionStatusSerializer,
    WatchMovieSerializer,
)

from apps.movies.models import Movie
from .services.access import can_user_watch
from .services.signed_urls import generate_signed_url_for_movie

logger = logging.getLogger(__name__)

class SubscriptionPlanListView(generics.ListAPIView):
    """Просмотр всех активных планов подписки"""
    queryset = SubscriptionPlan.objects.filter(is_active=True)
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.AllowAny]


class SubscriptionPlanDetailView(generics.RetrieveAPIView):
    """Просмотр деталей конкретного плана подписки"""
    queryset = SubscriptionPlan.objects.filter(is_active=True)
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.AllowAny]


class UserSubscriptionView(generics.RetrieveAPIView):
    """Просмотр текущей подписки пользователя"""
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Получаем текущую активную подписку пользователя | None"""
        try:
            return self.request.user.subscription # type: ignore
        except Subscription.DoesNotExist:
            return None
    
    def retrieve(self, request, *args, **kwargs):
        """ Возвращаем информацию о подписке"""

        subscription = self.get_object()
        if subscription:
            serializer = self.get_serializer(subscription)
            return Response(serializer.data)
        else:
            return Response({
                "detail": "У вас нет активной подписки."
                }, status=status.HTTP_404_NOT_FOUND)
        

class SubscriptionHistoryView(generics.ListAPIView):
    """Просмотр истории подписок пользователя"""
    serializer_class = SubscriptionHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Получаем историю подписок пользователя"""
        try:
            subscription = self.request.user.subscription # type: ignore
            return subscription.history.all().order_by('-created_at')
        except Subscription.DoesNotExist:
            return SubscriptionHistory.objects.none()


class StreamLinkThrottle(UserRateThrottle):
    """Ограничение запросов на получение ссылок для стриминга"""
    rate = '200/hour' 


class MovieWatchView(APIView):
    """
    Генерирует временную подписанную ссылку для просмотра фильма.
    Доступно только пользователям с активной подпиской.
    """
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [StreamLinkThrottle]

    def get(self, request, slug: str):
        """
        GET /api/v1/subscribe/movies/{slug}/stream-link/
        
        Response:
        {
            "url": "https://...blob.core.windows.net/media/movies/video.mp4?sas_token...",
            "expires_at": 1234567890,
            "expires_in": 900,
            "movie": {
                "id": 1,
                "title": "Movie Title",
                "slug": "movie-title"
            }
        }
        """
        # Получаем фильм
        movie = get_object_or_404(Movie, slug=slug)
        
        # Проверяем доступ пользователя
        can_watch, reason, meta = can_user_watch(request.user, movie)
        
        if not can_watch:
            error_messages = {
                'auth_required': 'Authentication required to watch movies.',
                'subscription_missing': 'Active subscription required. Please subscribe to watch this movie.',
                'subscription_inactive': 'Your subscription has expired. Please renew to continue watching.',
            }
            
            return Response({
                'error': error_messages.get(reason or 'access_denied', 'Access denied'),
                'reason': reason,
                'meta': meta
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Проверяем наличие видео файла
        if not movie.video:
            return Response({
                'error': 'Video file not available for this movie',
                'movie': {
                    'id': movie.id, # type: ignore
                    'title': movie.title,
                    'slug': movie.slug
                }
            }, status=status.HTTP_404_NOT_FOUND)
        
        try:
            # Генерируем подписанную ссылку
            signed_url, expires_at = generate_signed_url_for_movie(movie)
            
            # Логируем запрос  
            logger.info(
                f"Stream link generated for user {request.user.id} "
                f"({request.user.username}) for movie {movie.id} ({movie.title})" # type: ignore
            )
            
         
            return Response({
                'url': signed_url,
                'expires_at': expires_at,
                'expires_in': expires_at - int(timezone.now().timestamp()),
                'movie': {
                    'id': movie.id, # type: ignore
                    'title': movie.title,
                    'slug': movie.slug,
                },
                'meta': meta
            }, status=status.HTTP_200_OK)
        
        except ValueError as e:
            logger.error(f"ValueError generating stream link for movie {movie.id}: {e}") # type: ignore
            return Response({
                'error': 'Unable to generate stream link',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        except Exception as e:
            logger.exception(f"Unexpected error generating stream link for movie {movie.id}: {e}") # type: ignore
            return Response({
                'error': 'Internal server error',
                'detail': 'Please try again later'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def refresh_stream_link(request, slug: str):
    """
    Обновляет (перегенерирует) временную ссылку для продолжения просмотра.
    Полезно, если время жизни ссылки истекло во время просмотра.
    
    POST /api/v1/subscribe/movies/{slug}/refresh-stream-link/
    """
    movie = get_object_or_404(Movie, slug=slug)
    
    can_watch, reason, meta = can_user_watch(request.user, movie)
    
    if not can_watch:
        return Response({
            'error': 'Access denied',
            'reason': reason
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        signed_url, expires_at = generate_signed_url_for_movie(movie)
        
        logger.info(
            f"Stream link refreshed for user {request.user.id} "
            f"for movie {movie.id}" # type: ignore
        )
        
        return Response({
            'url': signed_url,
            'expires_at': expires_at,
            'expires_in': expires_at - int(timezone.now().timestamp()),
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.exception(f"Error refreshing stream link: {e}")
        return Response({
            'error': 'Unable to refresh stream link'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def subscription_status(request):
    serializer = UserSubscriptionStatusSerializer(request.user)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cancel_subscription(request):
    """Отмена подписки пользователя"""
    try:
        subscription = request.user.subscription

        if not subscription.is_active:
            return Response({
                'error': 'У вас нет активной подписки для отмены.'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            subscription.cancel()

            SubscriptionHistory.objects.create(
                subscription=subscription,
                action='canceled',
                description='Пользователь отменил подписку.',
            )
        return Response({
            'detail': 'Ваша подписка была успешно отменена и будет действовать до конца оплаченного периода.'
            }, status=status.HTTP_200_OK)
    
    except Subscription.DoesNotExist:
        return Response({
            'error': 'У вас нет подписки для отмены.'
            }, status=status.HTTP_400_BAD_REQUEST)





