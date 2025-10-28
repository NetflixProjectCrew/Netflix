from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Movie
from .tasks import compute_movie_duration

@receiver(post_save, sender=Movie)
def schedule_duration_compute(sender, instance: Movie, created, **kwargs):
    if created or (instance.video and instance.duration is None):
        compute_movie_duration.delay(instance.pk)