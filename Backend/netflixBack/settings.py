import os
from pathlib import Path
from decouple import config


BASE_DIR = Path(__file__).resolve().parent.parent

# Наш секретный ключ джанго
SECRET_KEY = config("SECRET_KEY")


DEBUG = config("DEBUG", default=False, cast=bool)

# Разрешенные хосты для подключения к серверу нашего Django-приложения 
ALLOWED_HOSTS = ['localhost', '127.0.0.1',]

# Стандартные приложения Django, которые идут по умолчанию
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

# Сторонние приложения, которые мы добавляем для расширения функционала (рест фреймворк, фильтры и т.д.)
THIRD_PARTY_APPS = [
    "rest_framework",
    "corsheaders",
    "django_filters",
    "rest_framework_simplejwt",
]

# Наши локальные приложения, которые мы создаем для реализации бизнес-логики нашего проекта
LOCAL_APPS = [
    "apps.accounts",
    "apps.movies",
]

# Объединяем все приложения в один список, чтобы Django знал обо всех установленных приложениях
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


# Настройки нашего Миддлвера
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Корневой юрл файл нашего проекта
ROOT_URLCONF = "netflixBack.urls"


# Настройки шаблонов
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]



WSGI_APPLICATION = "netflixBack.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
# Базовые настройки базы данных (по умолчанию SQLite в джанго)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


#AUTH_USER_MODEL = "accounts.User"  # Указываем кастомную модель пользователя

# Валидация паролей
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Настройки интернационализации
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# Статические файлы (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / 'staticfiles'


# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Настройки Django REST Framework
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",  # По умолчанию все запросы разрешены
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",  # Ограничение по количеству запросов для анонимных пользователей
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",  # Максимум 100 запросов в час для анонимных пользователей
    },
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",  # Ответы будут в формате JSON
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",  # Принимаем данные в формате JSON
    ],
}

if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True  # Разрешаем все источники при DEBUG режиме
else:
    CORS_ALLOWED_ORIGINS = [
        config("FRONTEND_URL"),  # Разрешаем только фронтенд домен, указанный в .env файле
    ]

#JWT configuration
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60), # Время жизни access токена
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),    # Время жизни refresh токена
    'ROTATE_REFRESH_TOKENS': True,                  # Обновляем refresh токен при каждом запросе
    'BLACKLIST_AFTER_ROTATION': True,               # Добавляем старые refresh токены в черный список
    'UPDATE_LAST_LOGIN': True,                      # Обновляем поле last_login при каждом запросе
    'ALGORITHM': 'HS256',                           # Алгоритм шифрования
    'SIGNING_KEY': SECRET_KEY,                      # Ключ для шифрования
    'AUTH_HEADER_TYPES': ('Bearer',),               # Тип заголовка авторизации
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',       # Имя заголовка авторизации
    'USER_ID_FIELD': 'id',                          # Поле пользователя, которое будет использоваться
    'USER_ID_CLAIM': 'user_id',                     # Клейм, в котором будет храниться ID пользователя
}


SECURE_BROWSER_XSS_FILTER = True # Включаем защиту от XSS атак (не даём вписывать скрипты в поля форм и т.д.)
X_FRAME_OPTIONS = "DENY" # Запрещаем отображение сайта в iframe (защита от кликджекинга)
SECURE_CONTENT_TYPE_NOSNIFF = True # Защита от MIME-атаки (не даём отправлять .exe файлы вместо изображений и т.д.)


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "DEBUG", # Уровень логов
            "class": "logging.FileHandler", # Логируем в файл
            "filename": BASE_DIR / "debug.log", # Путь к файлу логов
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file"], # Используемый хендлер
            "level": "DEBUG", # Уровень логов
            "propagate": True, # Распространяем логи родительским логгерам
        },
    },
}