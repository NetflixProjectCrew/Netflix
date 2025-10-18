from django.db import models
from django.conf import settings
from decimal import Decimal


class Payment(models.Model):
    """Модель платежа"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('canceled', 'Canceled'),
        ('refunded', 'Refunded'),
    ]   

    PAYMENT_METHOD_CHOICES = [
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
        ('manual', 'Manual'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments',
    )

    subscription = models.ForeignKey(
        'subscribe.Subscription',
        on_delete=models.CASCADE,
        related_name='payments',
        null=True,
        blank=True,
    )
    
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    currency = models.CharField(
        max_length=3,
        default='USD',
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
    )

    # Stripe - специфичные поля
    stripe_payment_intent_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    stripe_session_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    stripe_customer_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    # Метаданные о платеже
    description = models.TextField(
        null=True,
        blank=True,
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
    )

    # Временные метки
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )
    proccessed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        db_table = 'payments'
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['stripe_payment_intent_id']),
            models.Index(fields=['stripe_session_id']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f'Payment {self.id} -{self.user.username} - {self.amount} {self.currency} - {self.status}'#type: ignore
    
    @property
    def is_successful(self):
        """Проверяет, был ли платеж успешным"""
        return self.status == 'succeeded'
    
    @property
    def is_pending(self):
        """Проверяет, находится ли платеж в ожидании"""
        return self.status == 'pending'
    
    @property
    def can_be_refunded(self):
        """Проверяет, можно ли вернуть платеж"""
        return self.status == 'succeeded' and self.amount > Decimal('0.00')
    
    def mark_as_succeeded(self):
        """Отмечает платеж как успешный"""
        from django.utils import timezone
        self.status = 'succeeded'
        self.proccessed_at = timezone.now()
        self.save(update_fields=['status', 'proccessed_at'])
    
    def mark_as_failed(self, reason=None):
        """Отмечает платеж как неудачный"""
        from django.utils import timezone
        self.status = 'failed'
        self.proccessed_at = timezone.now()
        if reason:
            self.metadata['failure_reason'] = reason
        self.save(update_fields=['status', 'proccessed_at'])


class PaymentAttempt(models.Model):
    """Модель попытки платежа"""
    
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name='attempts',
    )
    stripe_charge_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    status = models.CharField(
        max_length=20,
        choices=Payment.STATUS_CHOICES,
        default='pending',
    )
    error_message = models.TextField(
        null=True,
        blank=True,
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
    ) 
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
 
    
    class Meta:
        db_table = 'payment_attempts'
        verbose_name = 'Payment Attempt'
        verbose_name_plural = 'Payment Attempts'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'PaymentAttempt {self.id} - Payment {self.payment.id} - {self.status}'#type: ignore
    

class Refund(models.Model):
    """Модель возврата платежа"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('canceled', 'Canceled'),
    ]

    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name='refunds',
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    reason = models.TextField(
        null=True,
        blank=True,
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
    )
    stripe_refund_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    processed_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_refunds',
    )

    class Meta:
        db_table = 'refunds'
        verbose_name = 'Refund'
        verbose_name_plural = 'Refunds'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Refund {self.id} - Payment {self.payment.id} - {self.amount}'#type: ignore
    
    @property
    def is_partial(self):
        """Проверяет, является ли возврат частичным"""
        return self.amount < self.payment.amount

    def process_refund(self):
        """Обрабатывает возврат платежа"""
        from django.utils import timezone
        self.status = 'succeeded'
        self.processed_at = timezone.now()
        self.save(update_fields=['status', 'processed_at'])
    

class WebhookEvent(models.Model):
    """Модель события вебхука платежной системы"""
    
    PROVIDER_CHOICES = [
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processed', 'Processed'),
        ('failed', 'Failed'),
        ('ignored', 'Ignored'),
    ]
    provider = models.CharField(
        max_length=20,
        choices=PROVIDER_CHOICES,
    )
    event_id = models.CharField(
        max_length=255,
        unique=True,
    )
    event_type = models.CharField(
        max_length=100,
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
    )

    data = models.JSONField()
    processed_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    error_message = models.TextField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        db_table = 'webhook_events'
        verbose_name = 'Webhook Event'
        verbose_name_plural = 'Webhook Events'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'WebhookEvent {self.provider} - {self.event_type} - Status: {self.status}'
    
    def mark_as_processed(self):
        """Отмечает событие как обработанное"""
        from django.utils import timezone
        self.processed = True
        self.processed_at = timezone.now()
        self.save(update_fields=['processed', 'processed_at'])
    
    def mark_as_failed(self, error_message):
        """Отмечает событие как неудачное"""
        from django.utils import timezone
        self.status = 'failed'
        self.error_message = error_message
        self.processed_at = timezone.now()
        self.save(update_fields=['status', 'error_message', 'processed_at'])