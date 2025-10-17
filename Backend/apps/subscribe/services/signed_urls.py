import hmac, base64, hashlib, time
from urllib.parse import urlencode
from django.conf import settings

def _now_epoch() -> int:
    return int(time.time())

def _sign_message(message: str, secret: str) -> str:
    sig = hmac.new(secret.encode("utf-8"), message.encode("utf-8"), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(sig).decode("ascii").rstrip("=")

def generate_local_signed_proxy_url(path: str, *, expires_in: int | None = None) -> tuple[str, int]:
    """
    Возвращает ссылку на наш прокси-эндпоинт /api/stream с подписью (dev/standalone).
    path — относительный путь до видеофайла в хранилище (например, movie.video.name).
    """
    ttl = expires_in or settings.STREAM_URL_EXP_SECONDS
    exp = _now_epoch() + ttl
    payload = f"{path}:{exp}"
    token = _sign_message(payload, settings.SIGNED_STREAM_SECRET)
    query = urlencode({"path": path, "exp": exp, "token": token})
    return f"{settings.STREAM_BASE_URL}?{query}", exp

def generate_s3_presigned_url(key: str, *, expires_in: int | None = None) -> tuple[str, int]:
    """
    Генерация presigned URL для S3. key — ключ в бакете (например, movie.video.name).
    """
    import boto3
    ttl = expires_in or settings.STREAM_URL_EXP_SECONDS
    s3 = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME,
    )
    url = s3.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": settings.AWS_S3_BUCKET_NAME, "Key": key},
        ExpiresIn=ttl,
    )
    return url, _now_epoch() + ttl

def generate_signed_url_for_movie(movie, *, expires_in: int | None = None) -> tuple[str, int]:
    """
    Универсальная фабрика ссылок: выбирает бэкенд из настроек.
    Ожидается, что у movie есть FileField/ImageField, например movie.video (movie.video.name — ключ/путь).
    """
    storage_key = getattr(movie.video, "name", None)
    if not storage_key:
        raise ValueError("Movie has no video file/key (movie.video.name is empty).")

    backend = (settings.STREAM_BACKEND or "LOCAL").upper()
    if backend == "S3":
        return generate_s3_presigned_url(storage_key, expires_in=expires_in)
    # По умолчанию — наш локальный прокси с HMAC-подписями
    return generate_local_signed_proxy_url(storage_key, expires_in=expires_in)
