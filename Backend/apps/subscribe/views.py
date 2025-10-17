from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView

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



class MovieWatchView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, slug: str):
        movie = get_object_or_404(Movie, slug=slug)
        ok, reason, meta = can_user_watch(request.user, movie)
        if not ok:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        url, expires_at = generate_signed_url_for_movie(movie)
        return Response({"url": url, "expires_at": expires_at, "meta": meta}, status=200)


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





