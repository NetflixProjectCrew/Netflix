from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class SubscriptionPlan(models.Model):
    """Модель плана подписки"""
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.IntegerField(default=30)  # Продолжительность в днях
    stripe_price_id = models.CharField(max_length=255, unique=True)  # ID цены в Stripe
    features = models.JSONField(default=dict, help_text="Особенности плана в формате JSON")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        db_table = "subscription_plans"
        verbose_name = "Subscription Plan"
        verbose_name_plural = "Subscription Plans"
        ordering = ["price"]

    def __str__(self):
        return f"{self.name} - ${self.price} for {self.duration_days} days"


class Subscription(models.Model):
    """Модель подписки пользователя"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('canceled', 'Canceled'),
        ('expired', 'Expired'),
        ('pending', 'Pending'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='subscriptions'
        )
    
    plan = models.ForeignKey(
        SubscriptionPlan, 
        on_delete=models.CASCADE, 
        related_name='subscriptions'
        )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    
    stripe_subscription_id = models.CharField(max_length=255, unique=True,  null=True, blank=True, default=None )  # ID подписки в Stripe
    auto_renew = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "subscriptions"
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['end_date', 'status']),
        ]

    def __str__(self):
        return f"Subscription of {self.user.email} to {self.plan.name}"

    def save(self, *args, **kwargs):
        
        if not self.end_date:
            self.end_date = self.start_date + timedelta(days=self.plan.duration_days)
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        """Проверяет, активна ли подписка."""
        return self.status == 'active' and self.end_date > timezone.now()
    
    @property
    def days_remaining(self):
        """Возвращает количество дней до окончания подписки."""
        if not self.is_active:
            return 0
        
        delta = self.end_date - timezone.now()

        return max(delta.days, 0)
    
    def extend_subscription(self, additional_days):
        """Продлевает подписку на указанное количество дней."""
        if self.is_active:
            self.end_date += timedelta(days=additional_days)
        else:
            self.start_date = timezone.now()
            self.end_date = self.start_date + timedelta(days=additional_days)
            self.status = 'active'
        self.save()
        return self.end_date
    
    def cancel(self):
        """Отменяет подписку."""
        self.status = 'canceled'
        self.auto_renew = False
        self.save()
    
    def expire(self):
        """Истекает подписку."""
        self.status = 'expired'
        self.auto_renew = False
        self.save()
    
    def activate(self):
        """Активирует подписку."""
        self.status = 'active'
        self.auto_renew = True
        self.start_date = timezone.now()
        self.end_date = self.start_date + timedelta(days=self.plan.duration_days)
        self.save()


class SubscriptionHistory(models.Model):
    """История изменений подписки пользователя"""
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('canceled', 'Canceled'),
        ('expired', 'Expired'),
        ('renewed', 'Renewed'),
        ('payment_failed', 'Payment Failed'),
    ]

    subscription = models.ForeignKey(
        Subscription, 
        on_delete=models.CASCADE, 
        related_name='history'
        )
    
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, help_text="Дополнительные данные о событии в формате JSON", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "subscription_history"
        verbose_name = "Subscription History"
        verbose_name_plural = "Subscription Histories"
        ordering = ["-created_at"]

    def __str__(self):
        return f"User: {self.subscription.user.username} - Action: {self.action}"
