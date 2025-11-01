# apps/subscribe/services/signed_urls.py
import hmac
import base64
import hashlib
import time
from datetime import datetime, timedelta
from urllib.parse import urlencode, quote
from django.conf import settings
from azure.storage.blob import generate_blob_sas, BlobSasPermissions


def _now_epoch() -> int:
    return int(time.time())


def generate_azure_sas_url(blob_name: str, *, expires_in: int | None = None) -> tuple[str, int]:
    """
    Генерирует SAS (Shared Access Signature) URL для Azure Blob Storage.
    
    Args:
        blob_name: имя blob'а в контейнере (например, 'movies/videos/transformers.mp4')
        expires_in: время жизни ссылки в секундах (по умолчанию из настроек)
    
    Returns:
        tuple: (signed_url, expiration_timestamp)
    """
    if not blob_name:
        raise ValueError("Blob name cannot be empty")
    
    ttl = expires_in or settings.STREAM_URL_EXP_SECONDS
    expiry_time = datetime.utcnow() + timedelta(seconds=ttl)
    
    try:
        # Генерируем SAS токен с правами только на чтение
        sas_token = generate_blob_sas(
            account_name=settings.AZURE_ACCOUNT_NAME,
            account_key=settings.AZURE_ACCOUNT_KEY,
            container_name=settings.AZURE_MEDIA_CONTAINER,
            blob_name=blob_name,
            permission=BlobSasPermissions(read=True),
            expiry=expiry_time,
            # Опционально: ограничение по IP
            # ip=user_ip if hasattr(settings, 'ENABLE_IP_RESTRICTION') and settings.ENABLE_IP_RESTRICTION else None
        )
        
        # Формируем полный URL
        base_url = settings.AZURE_BLOB_BASE_URL.rstrip('/')
        container = settings.AZURE_MEDIA_CONTAINER
        # Кодируем blob_name для корректной работы с путями
        encoded_blob = quote(blob_name)
        
        signed_url = f"{base_url}/{container}/{encoded_blob}?{sas_token}"
        
        return signed_url, int(expiry_time.timestamp())
    
    except Exception as e:
        # Логируем ошибку
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error generating Azure SAS URL for blob {blob_name}: {e}")
        raise


def generate_signed_url_for_movie(movie, *, expires_in: int | None = None) -> tuple[str, int]:
    """
    Универсальная функция для генерации подписанных URL для видео.
    Автоматически выбирает бэкенд на основе настроек.
    
    Args:
        movie: объект Movie с полем video (FileField)
        expires_in: время жизни ссылки в секундах
    
    Returns:
        tuple: (signed_url, expiration_timestamp)
    """
    if not movie.video:
        raise ValueError("Movie has no video file attached")
    
    # Получаем имя файла в хранилище
    # Для Azure Storage это будет путь внутри контейнера
    storage_key = movie.video.name
    
    if not storage_key:
        raise ValueError("Movie video file has no storage key")
    
    backend = (getattr(settings, 'STREAM_BACKEND', 'AZURE')).upper()
    
    if backend == 'AZURE':
        return generate_azure_sas_url(storage_key, expires_in=expires_in)
    elif backend == 'S3':
        # Если в будущем захочешь добавить S3
        return generate_s3_presigned_url(storage_key, expires_in=expires_in)
    else:
        raise ValueError(f"Unsupported storage backend: {backend}")


def generate_s3_presigned_url(key: str, *, expires_in: int | None = None) -> tuple[str, int]:
    """
    Генерация presigned URL для S3 (на будущее).
    """
    import boto3
    from botocore.exceptions import ClientError
    
    ttl = expires_in or settings.STREAM_URL_EXP_SECONDS
    
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )
        
        url = s3_client.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                'Key': key,
            },
            ExpiresIn=ttl,
        )
        
        expiration = _now_epoch() + ttl
        return url, expiration
    
    except ClientError as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error generating S3 presigned URL for key {key}: {e}")
        raise