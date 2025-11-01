from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import Movie
from .tasks import compute_movie_duration
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Movie)
def schedule_duration_compute(sender, instance: Movie, created, **kwargs):
    """
    Запускает задачу вычисления длительности при:
    1. Создании нового фильма с видео
    2. Обновлении видео файла
    3. Если duration=None и есть видео
    """
    should_compute = False
    
    if created:
        # Новый фильм с видео
        if instance.video:
            should_compute = True
            logger.info(f"New movie {instance.id} created with video, scheduling duration compute")# type: ignore
    else:
        # Обновление существующего фильма
        if instance.video and not instance.duration:
            should_compute = True
            logger.info(f"Movie {instance.id} has video but no duration, scheduling compute")# type: ignore
        
        # Проверяем, изменился ли видео файл
        try:
            old_instance = Movie.objects.only('video').get(pk=instance.pk)
            if old_instance.video != instance.video and instance.video:
                should_compute = True
                logger.info(f"Movie {instance.id} video file changed, scheduling duration compute")# type: ignore
        except Movie.DoesNotExist:
            pass
    
    if should_compute:
        # Запускаем задачу после commit'а транзакции
        transaction.on_commit(
            lambda: compute_movie_duration.apply_async(# type: ignore
                args=[instance.pk],
                countdown=5  # задержка 5 секунд для завершения загрузки в Azure
            )
        )