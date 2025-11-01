from celery import shared_task
from django.utils.timezone import now as dateNow
from datetime import timedelta
from .models import Movie
from .utils.video_meta import (
    probe_duration_seconds,
    probe_video_metadata,
    get_video_url_for_processing,
    extract_duration_from_filename
)
import logging

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60  # повторить через 60 секунд
)
def compute_movie_duration(self, movie_id: int):
    """
    Вычисляет длительность видео с использованием ffprobe.
    Поддерживает Azure Storage и локальные файлы.
    """
    try:
        movie = Movie.objects.get(pk=movie_id)
    except Movie.DoesNotExist:
        logger.error(f"Movie {movie_id} not found")
        return {'error': 'Movie not found'}
    
    if not movie.video:
        logger.warning(f"Movie {movie_id} has no video file")
        return {'error': 'No video file'}
    
    # Проверяем, нужно ли обновлять длительность
    if movie.duration and not movie.meta_dirty:
        logger.info(f"Movie {movie_id} already has duration, skipping")
        return {'skipped': True, 'duration': movie.duration}
    
    # Получаем URL для обработки
    video_url = get_video_url_for_processing(movie.video)
    
    if not video_url:
        logger.error(f"Unable to get video URL for movie {movie_id}")
        return {'error': 'Unable to get video URL'}
    
    logger.info(f"Processing video for movie {movie_id}: {video_url[:100]}...")
    
    # Пытаемся извлечь полные метаданные
    metadata = probe_video_metadata(video_url, timeout=120)
    
    if metadata and metadata.get('duration'):
        # Успешно получили метаданные
        movie.duration = metadata['duration_timedelta']
        movie.last_meta_update = dateNow()
        movie.meta_dirty = False
        movie.save(update_fields=['duration', 'last_meta_update', 'meta_dirty'])
        
        logger.info(
            f"Movie {movie_id} duration updated: {metadata['duration']}s "
            f"({metadata.get('width')}x{metadata.get('height')}, "
            f"{metadata.get('codec')}, {metadata.get('fps')} fps)"
        )
        
        return {
            'success': True,
            'movie_id': movie_id,
            'duration': metadata['duration'],
            'metadata': metadata
        }
    
    # Fallback 1: простое извлечение длительности
    duration_sec = probe_duration_seconds(video_url, timeout=120)
    
    if duration_sec:
        movie.duration = timedelta(seconds=duration_sec)
        movie.last_meta_update = dateNow()
        movie.meta_dirty = False
        movie.save(update_fields=['duration', 'last_meta_update', 'meta_dirty'])
        
        logger.info(f"Movie {movie_id} duration updated (fallback): {duration_sec}s")
        
        return {
            'success': True,
            'movie_id': movie_id,
            'duration': duration_sec,
            'method': 'fallback'
        }
    
    # Fallback 2: извлечение из имени файла
    filename = movie.video.name
    duration_from_filename = extract_duration_from_filename(filename)
    
    if duration_from_filename:
        movie.duration = timedelta(seconds=duration_from_filename)
        movie.last_meta_update = dateNow()
        movie.meta_dirty = False
        movie.save(update_fields=['duration', 'last_meta_update', 'meta_dirty'])
        
        logger.warning(
            f"Movie {movie_id} duration extracted from filename: "
            f"{duration_from_filename}s (may be inaccurate)"
        )
        
        return {
            'success': True,
            'movie_id': movie_id,
            'duration': duration_from_filename,
            'method': 'filename',
            'warning': 'Duration extracted from filename, may be inaccurate'
        }
    
    # Если все методы не сработали - повторяем задачу
    logger.error(f"Failed to extract duration for movie {movie_id}")
    
    # Повторяем задачу (максимум 3 раза)
    try:
        raise self.retry(countdown=60 * (self.request.retries + 1))
    except Exception as retry_exc:
        logger.error(f"Max retries exceeded for movie {movie_id}")
        return {
            'error': 'Failed to extract duration after all retries',
            'movie_id': movie_id
        }


@shared_task(name="movies.refresh_stale_movies")
def refresh_stale_movies(ttl_minutes: int = 60, limit: int = 50):
    """
    Находит фильмы без длительности или с устаревшими метаданными
    и ставит их в очередь на обработку.
    """
    qs = Movie.objects.filter(video__isnull=False)
    ids = []
    now = dateNow()
    
    # Приоритет 1: фильмы без длительности
    for movie in qs.filter(duration__isnull=True).only('id')[:limit]:
        ids.append(movie.id)# type: ignore
    
    # Приоритет 2: фильмы с meta_dirty
    if len(ids) < limit:
        remaining = limit - len(ids)
        for movie in qs.filter(meta_dirty=True).only('id')[:remaining]:
            if movie.id not in ids:# type: ignore
                ids.append(movie.id)# type: ignore
    
    # Приоритет 3: устаревшие метаданные
    if len(ids) < limit:
        remaining = limit - len(ids)
        cutoff = now - timedelta(minutes=ttl_minutes)
        for movie in qs.filter(last_meta_update__lt=cutoff).only('id')[:remaining]:
            if movie.id not in ids:# type: ignore
                ids.append(movie.id)# type: ignore
    
    # Запускаем задачи
    for movie_id in ids:
        compute_movie_duration.delay(movie_id)# type: ignore
    
    logger.info(f"Queued {len(ids)} movies for duration refresh")
    
    return {
        'queued': len(ids),
        'checked_at': now.isoformat()
    }


@shared_task
def bulk_recompute_durations(movie_ids: list[int]):
    """
    Массовый перерасчет длительности для списка фильмов.
    Полезно для admin actions или management commands.
    """
    if movie_ids is None:
        # Все фильмы без длительности
        movie_ids = list(
            Movie.objects.filter(
                video__isnull=False,
                duration__isnull=True
            ).values_list('id', flat=True)[:500]  # безопасный лимит
        )
    
    for movie_id in movie_ids:
        compute_movie_duration.delay(movie_id)# type: ignore
    
    return {
        'queued': len(movie_ids),
        'movie_ids': movie_ids
    }