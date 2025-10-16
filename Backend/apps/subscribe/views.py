from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

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


class MovieWatchView(generics.RetrieveAPIView):
    """Проверка возможности просмотра фильма по подписке"""
    serializer_class = WatchMovieSerializer
    permission_classes = [permissions.IsAuthenticated]


        