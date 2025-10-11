from rest_framework import serializers
from django.utils import timezone
from .models import SubscriptionPlan, Subscription, SubscriptionHistory


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    """Сериализатор для модели плана подписки"""

    class Meta:
        model = SubscriptionPlan
        fields = [
            'id', 'name', 'price', 
            'duration_days', 'features',
            'is_active', 'created_at',
            ]
        read_only_fields = ['id', 'created_at']

    def to_representation(self, instance):
        """Переопределяем представление для гарантии корректного вывода"""
        data = super().to_representation(instance)

        # Убедимся, что features - это объект
        if not data.get('features'):
            data['features'] = {}
        
        return data


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для подписки"""
    plan_info = SubscriptionPlanSerializer(source='plan', read_only=True)
    user_info = serializers.SerializerMethodField()
    is_active = serializers.ReadOnlyField()
    days_remaining = serializers.ReadOnlyField()

    class Meta:
        model = Subscription
        fields = [
            'id', 'user', 'user_info', 'plan',  
            'plan_info', 'start_date', 'end_date', 
            'status', 'auto_renew', 'is_active', 
            'days_remaining', 'created_at', 'updated_at'
            ]
        read_only_fields = [
            'id', 'user', 'status', 'start_date', 'end_date', 
            'created_at', 'updated_at',
            ]

    def get_user_info(self, obj):
        """Возвращает основную информацию о пользователе."""

        return {
            "id": obj.user.id,
            "username": obj.user.username,
            "full_name": obj.user.full_name,
            "email": obj.user.email,
        }
    

class SubscriptionCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания подписки"""
    
    class Meta:
        model = Subscription
        fields = ['plan']
    
    def validate_plan(self, value):
        """Проверка, что план активен."""
        if not value.is_active:
            raise serializers.ValidationError("Выбранный план подписки неактивен.")
        return value
    
    def validate(self, attrs):
        """Общая валидация перед созданием подписки."""
        user = self.context['request'].user

        # Проверяем, есть ли у пользователя уже активная подписка
        if hasattr(user, 'subscription') and user.subscription.is_active:
            raise serializers.ValidationError({
                "non_field_errors":"У вас уже есть активная подписка."
                })

        return attrs

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        validated_data['status'] = 'pending'  # Начинаем с 'pending', пока не будет подтверждения оплаты
        validated_data['start_date'] = timezone.now()
        validated_data['end_date'] = timezone.now() 
        return super().create(validated_data)


class SubscriptionHistorySerializer(serializers.ModelSerializer):
    """Сериализатор для истории подписок"""
 
    class Meta:
        model = SubscriptionHistory
        fields = [
            'id', 'action', 'description', 'metadata', 'created_at'
            ]
        read_only_fields = ['id', 'action']


class UserSubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения информации о подписке пользователя в профиле."""
    has_subscription = serializers.BooleanField()
    is_active = serializers.BooleanField()
    subscription = SubscriptionSerializer()
    can_watch_movies = serializers.BooleanField()

    def to_representation(self, instance):
        """Формирует ответ с информацией о подписке пользователя."""
        user = instance
        has_subscription = hasattr(user, 'subscription')
        subscription = user.subscription if has_subscription else None
        is_active = subscription.is_active if subscription else False

        return {
            'has_subscription': has_subscription,
            'is_active': is_active,
            'subscription': SubscriptionSerializer(subscription).data if subscription else None,
            'can_watch_movies': is_active,
        }