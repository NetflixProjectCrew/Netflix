import json
import subprocess
import logging
from typing import Optional, Tuple
from django.conf import settings
from datetime import timedelta

logger = logging.getLogger(__name__)


def probe_duration_seconds(input_url: str, *, timeout: int = 60) -> Optional[int]:
    """
    Возвращает длительность в секундах, либо None при ошибке.
    
    Args:
        input_url: URL или путь к видеофайлу
        timeout: таймаут выполнения команды в секундах
    
    Returns:
        int: длительность в секундах или None
    """
    try:
        cmd = [
            "ffprobe", 
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "json",
            input_url
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False  # не бросаем исключение при ненулевом коде возврата
        )
        
        if result.returncode != 0:
            logger.error(f"ffprobe failed with code {result.returncode}: {result.stderr}")
            return None
        
        payload = json.loads(result.stdout)
        duration = float(payload["format"]["duration"])
        return int(round(duration))
        
    except subprocess.TimeoutExpired:
        logger.error(f"ffprobe timeout ({timeout}s) for URL: {input_url}")
        return None
    except FileNotFoundError:
        logger.error("ffprobe not found. Install ffmpeg: apt-get install ffmpeg")
        return None
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        logger.error(f"Failed to parse ffprobe output: {e}")
        return None
    except Exception as e:
        logger.exception(f"Unexpected error in probe_duration_seconds: {e}")
        return None


def probe_video_metadata(input_url: str, *, timeout: int = 60) -> Optional[dict]:
    """
    Извлекает полные метаданные видео (длительность, разрешение, битрейт и т.д.)
    
    Returns:
        dict: {
            'duration': int,  # секунды
            'duration_timedelta': timedelta,
            'width': int,
            'height': int,
            'bitrate': int,
            'codec': str,
            'fps': float
        }
    """
    try:
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration,bit_rate:stream=codec_name,width,height,r_frame_rate",
            "-of", "json",
            input_url
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False
        )
        
        if result.returncode != 0:
            logger.error(f"ffprobe failed: {result.stderr}")
            return None
        
        data = json.loads(result.stdout)
        
        # Извлекаем данные
        format_data = data.get("format", {})
        stream_data = data.get("streams", [{}])[0]  # первый видео стрим
        
        duration_sec = int(round(float(format_data.get("duration", 0))))
        
        # Парсим frame rate (может быть в формате "30000/1001")
        fps_str = stream_data.get("r_frame_rate", "0/1")
        try:
            num, denom = map(int, fps_str.split('/'))
            fps = num / denom if denom else 0
        except:
            fps = 0
        
        metadata = {
            'duration': duration_sec,
            'duration_timedelta': timedelta(seconds=duration_sec),
            'width': stream_data.get('width'),
            'height': stream_data.get('height'),
            'bitrate': int(format_data.get('bit_rate', 0)),
            'codec': stream_data.get('codec_name'),
            'fps': round(fps, 2) if fps else None
        }
        
        return metadata
        
    except Exception as e:
        logger.exception(f"Error extracting video metadata: {e}")
        return None


def get_azure_blob_sas_url(blob_name: str, expires_in: int = 300) -> Optional[str]:
    """
    Генерирует временный SAS URL для Azure Blob (для работы ffprobe).
    
    Args:
        blob_name: имя blob'а в контейнере
        expires_in: время жизни SAS токена в секундах
    
    Returns:
        str: полный URL с SAS токеном или None
    """
    try:
        from azure.storage.blob import generate_blob_sas, BlobSasPermissions
        from datetime import datetime, timedelta
        
        sas_token = generate_blob_sas(
            account_name=settings.AZURE_ACCOUNT_NAME,
            account_key=settings.AZURE_ACCOUNT_KEY,
            container_name=settings.AZURE_MEDIA_CONTAINER,
            blob_name=blob_name,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(seconds=expires_in)
        )
        
        base_url = settings.AZURE_BLOB_BASE_URL.rstrip('/')
        container = settings.AZURE_MEDIA_CONTAINER
        
        return f"{base_url}/{container}/{blob_name}?{sas_token}"
        
    except Exception as e:
        logger.exception(f"Error generating Azure SAS URL: {e}")
        return None


def get_video_url_for_processing(file_field) -> Optional[str]:
    """
    Получает URL видео для обработки (локальный путь или Azure SAS URL).
    
    Args:
        file_field: Django FileField/ImageField объект
    
    Returns:
        str: URL или путь к файлу
    """
    if not file_field:
        return None
    
    storage_backend = settings.STORAGES['default']['BACKEND']
    
    # Azure Storage
    if 'azure' in storage_backend.lower():
        blob_name = file_field.name
        return get_azure_blob_sas_url(blob_name)
    
    # Локальное хранилище
    elif 'FileSystemStorage' in storage_backend:
        return file_field.path
    
    # S3 или другое
    else:
        try:
            return file_field.url
        except:
            logger.error("Unable to get video URL for processing")
            return None


def extract_duration_from_filename(filename: str) -> Optional[int]:
    """
    Пытается извлечь длительность из имени файла (fallback метод).
    Например: "movie_1h30m.mp4" -> 5400 секунд
    
    Returns:
        int: длительность в секундах или None
    """
    import re
    
    # Паттерны: 1h30m, 1h30m15s, 90m, 5400s
    patterns = [
        r'(\d+)h(\d+)m(?:(\d+)s)?',  # 1h30m или 1h30m15s
        r'(\d+)m(?:(\d+)s)?',         # 90m или 90m30s
        r'(\d+)s',                     # 5400s
    ]
    
    for pattern in patterns:
        match = re.search(pattern, filename.lower())
        if match:
            groups = match.groups()
            
            if len(groups) == 3 and groups[0]:  # XhYmZs
                hours = int(groups[0])
                minutes = int(groups[1])
                seconds = int(groups[2]) if groups[2] else 0
                return hours * 3600 + minutes * 60 + seconds
            
            elif len(groups) == 2 and pattern == r'(\d+)m(?:(\d+)s)?':  # XmYs
                minutes = int(groups[0])
                seconds = int(groups[1]) if groups[1] else 0
                return minutes * 60 + seconds
            
            elif len(groups) == 1:  # Xs
                return int(groups[0])
    
    return None