from django.db.models.signals import post_save, pre_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import Subscription, SubscriptionHistory


@receiver(pre_save, sender=Subscription)
def subscription_post_save(sender, instance, created, **kwargs):
    """
    Обработчик сохранения подписки.
    """
    if created:
        # Новая подписка создается
        SubscriptionHistory.objects.create(
            subscription=instance,
            action = "created",
            description = f"Subscription created with plan {instance.plan.name}",
        )
    else:
        if hasattr(instance, '_previous_status'):
            if instance._previous_status != instance.status:
                # Статус подписки изменился
                SubscriptionHistory.objects.create(
                    subscription=instance,
                    action = instance.status,
                    description = f"Subscription status changed from {instance._previous_status} to {instance.status}",
                )

# @receiver(pre_delete, sender=Subscription)
# def subscription_pre_delete(sender, instance, **kwargs):
#     """
#     Обработчик удаления подписки.
#     """
#     SubscriptionHistory.objects.create(
#         subscription=instance,
#         action = "deleted",
#         description = f"Subscription deleted with plan {instance.plan.name}",
#     )

