from django.core.management.base import BaseCommand
from apps.movies.models import Movie
from apps.movies.tasks import compute_movie_duration, bulk_recompute_durations
import time


class Command(BaseCommand):
    help = 'Compute durations for movies without duration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Recompute duration for ALL movies (even with existing duration)',
        )
        parser.add_argument(
            '--movie-id',
            type=int,
            help='Compute duration for specific movie ID',
        )
        parser.add_argument(
            '--sync',
            action='store_true',
            help='Execute synchronously instead of using Celery',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=100,
            help='Maximum number of movies to process (default: 100)',
        )

    def handle(self, *args, **options):
        if options['movie_id']:
            # Обработка конкретного фильма
            movie_id = options['movie_id']
            
            if options['sync']:
                from apps.movies.tasks import compute_movie_duration
                result = compute_movie_duration(movie_id)
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Result: {result}")
                )
            else:
                compute_movie_duration.delay(movie_id)# type: ignore
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Queued movie {movie_id}")
                )
            
            return
        
        # Обработка нескольких фильмов
        if options['all']:
            queryset = Movie.objects.filter(video__isnull=False)
            self.stdout.write("Processing ALL movies with video files...")
        else:
            queryset = Movie.objects.filter(
                video__isnull=False,
                duration__isnull=True
            )
            self.stdout.write("Processing movies without duration...")
        
        limit = options['limit']
        movie_ids = list(queryset.values_list('id', flat=True)[:limit])
        
        if not movie_ids:
            self.stdout.write(
                self.style.WARNING("No movies found to process.")
            )
            return
        
        self.stdout.write(f"Found {len(movie_ids)} movies to process.")
        
        if options['sync']:
            # Синхронное выполнение
            for i, movie_id in enumerate(movie_ids, 1):
                self.stdout.write(f"[{i}/{len(movie_ids)}] Processing movie {movie_id}...")
                
                try:
                    result = compute_movie_duration(movie_id) # type: ignore
                    
                    if result.get('success'):
                        duration = result.get('duration')
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"  ✓ Duration: {duration}s"
                            )
                        )
                    elif result.get('skipped'):
                        self.stdout.write(
                            self.style.WARNING("  ⏭ Skipped (already has duration)")
                        )
                    else:
                        self.stdout.write(
                            self.style.ERROR(f"  ✗ Error: {result.get('error')}")
                        )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"  ✗ Exception: {e}")
                    )
                
                # Небольшая задержка между запросами
                if i < len(movie_ids):
                    time.sleep(0.5)
        else:
            # Асинхронное выполнение через Celery
            bulk_recompute_durations.delay(movie_ids)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ Queued {len(movie_ids)} movies for background processing."
                )
            )
        
        self.stdout.write(
            self.style.SUCCESS("\n✅ Done!")
        )