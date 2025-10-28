from celery import shared_task
from django.utils.timezone import now as dateNow
from datetime import timedelta
from .models import Movie
from .utils.video_meta import probe_duration_seconds


@shared_task
def compute_movie_duration(movie_id: int):
    m = Movie.objects.get(pk=movie_id)
    if not m.video:
        return
    url = m.video.url
    dur = probe_duration_seconds(url)
    if dur:
        m.duration = timedelta(seconds=dur)
        m.save(update_fields=["duration"])


@shared_task(name="movies.refresh_stale_movies")
def refresh_stale_movies(ttl_minutes: int = 60, limit: int = 50):
    """
    Найти 'устаревшие' или 'грязные' фильмы и поставить их в очередь на обновление.
    Ограничение по batch, чтобы не забивать очередь.
    """
    qs = Movie.objects.all()
    ids = []
    now = dateNow()
    for m in qs.only("id", "last_meta_update", "meta_dirty")[:10000]:  # грубая отсечка
        if m.meta_dirty or not m.last_meta_update or (now - (m.last_meta_update or now)).total_seconds() > ttl_minutes * 60:
            ids.append(m.id) # type: ignore
            if len(ids) >= limit:
                break

    for mid in ids:
        compute_movie_duration.delay(mid)

    return {"queued": len(ids)}