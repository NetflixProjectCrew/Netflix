from celery import shared_task
from django.utils import timezone
from .models import Subscription, SubscriptionHistory

@shared_task
def check_expired_subscriptions():
    """
    Задача для проверки и обновления статусов подписок.
    """
    now = timezone.now()

    expired_subscriptions = Subscription.objects.filter(
        end_date__lt=now,
        status='active'
    )

    expired_count = 0
    
    for sub in expired_subscriptions:
        sub.delete()

        # Логируем изменение статуса
        SubscriptionHistory.objects.create(
            subscription=sub,
            action='expired',
            description=f"Subscription expired for plan {sub.plan.name}",
        )
        expired_count += 1
    
    return {
        "expired_count": expired_count,
        "checked_at": now.isoformat()
    }


@shared_task
def send_subcription_expiry_reminders():
    """
    Задача для отправки напоминаний о скором истечении подписки.
    """
    from datetime import timedelta
    from django.core.mail import send_mail
    from django.conf import settings

    # Находим подписки, которые истекают через 3 дня
    reminder_date = timezone.now() + timedelta(days=3)
    expiring_subscriptions = Subscription.objects.filter(
        end_date__date=reminder_date.date(),
        status='active',
        auto_renew=False
    )
    

    reminder_count = 0

    for sub in expiring_subscriptions:
        user = sub.user
        try:
            send_mail(
                subject='Your subscription is expiring soon',
                message=f'Dear {sub.user.get_full_name() or sub.user.username},\n\n'
                f'Your {sub.plan.name} subscription will expire on {sub.end_date.strftime("%B %d, %Y")}.\n\n'
                f'To continue enjoying our content, please renew your subscription.\n\n'
                f'Best regards,\nNetflix Crew Team',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[sub.user.email],
                fail_silently=True
            )
            reminder_count += 1
       
        except Exception as e:
            # Логируем ошибку отправки письма, но продолжаем
            print(f"Failed to send reminder to {user.email}: {e}")
   
    return {
        "reminder_count": reminder_count,
        "checked_at": timezone.now().isoformat()
    }

