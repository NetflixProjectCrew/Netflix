#🎬 Netflix Clone API — Django REST Framework Backend

Современное серверное приложение для потокового видео-сервиса, аналогичного Netflix.
Поддерживает регистрацию, просмотр фильмов, систему подписок и платежи через Stripe.

Frontend (React/Vue) можно подключать отдельно — API готов для интеграции.

##🚀 Основные возможности
👤 Пользователи

###Регистрация и аутентификация (JWT)
→ djangorestframework-simplejwt

Профиль пользователя — аватар, имя, email, дата регистрации

Изменение пароля, выход (logout) с добавлением refresh-токена в blacklist

Избранное и история просмотров — лайки и прогресс фильма сохраняются

###🎞 Фильмы

CRUD API для фильмов, жанров и авторов

Счётчик лайков и просмотров
— просмотры считаются только при достижении 90% фильма

Оптимизация запросов (select_related, prefetch_related)

Фильтры и поиск по жанрам, авторам, названию и описанию

Пагинация, сортировка и статистика просмотров

###💳 Подписки и платежи

Система тарифных планов (модель SubscriptionPlan)

Stripe интеграция (создание клиентов, сессий оплаты, возвраты)

История подписок и событий (created, renewed, canceled, payment_failed)

Автоматическое продление и вычисление оставшихся дней

Доступ к просмотру фильмов только при активной подписке

###🛠 Администрирование

Модерация фильмов, жанров и авторов через Django Admin

Управление подписками и платежами пользователей

Отчёты и история транзакций

##🧰 Технологический стек
Backend

Python 3.13, Django 5.2

Django REST Framework

SimpleJWT — аутентификация

django-filter — фильтрация списков

PostgreSQL (или SQLite по умолчанию)

Stripe API — платежи

Pillow — работа с изображениями

CORS Headers — фронтенд интеграция

.env с секретами (Stripe ключи, JWT настройки и т.д.)

📁 Структура проекта
Backend/
├── apps/
│   ├── accounts/        # Пользователи, JWT, профили
│   ├── movies/          # Фильмы, жанры, авторы, лайки и просмотры
│   ├── subscribe/       # Подписки и планы
│   ├── payment/         # Платежи, Stripe-интеграция
│   └── __init__.py
├── netflixBack/              # Настройки Django
├── manage.py
└── requirements.txt

🧱 Основные модели данных
Модель	Описание
User	Расширенная модель пользователя (email — логин, аватар, подписка)
Movie	Фильмы с описанием, жанрами, автором, постером и видео
Genre	Категории фильмов
Author	Режиссёры/создатели, с биографией и фото
Favorite	Лайки фильмов
Watched	Прогресс просмотра, длительность, процент
SubscriptionPlan	Тарифный план подписки (цена, продолжительность, JSON-features)
Subscription	Активная подписка пользователя
SubscriptionHistory	История событий подписок
Payment / Refund	Транзакции, возвраты, статусы, Stripe поля
🔗 API Endpoints
Accounts
POST /accounts/register/         # Регистрация
POST /accounts/login/            # Вход (JWT)
POST /accounts/logout/           # Выход
GET  /accounts/profile/          # Получение профиля
PUT  /accounts/profile/          # Обновление профиля
PATCH /accounts/change-password/ # Изменение пароля
POST /accounts/token/refresh/    # Обновление токена

Movies
GET  /movies/movies/                 # Список фильмов
POST /movies/movies/                 # Добавление фильма (admin)
GET  /movies/movies/{slug}/          # Детали фильма
PUT  /movies/movies/{slug}/          # Обновление фильма
POST /movies/movies/{slug}/like/     # Лайк
POST /movies/movies/{slug}/unlike/   # Удалить лайк
POST /movies/movies/{slug}/progress/ # Отправка прогресса просмотра
GET  /movies/me/watched/             # Мои просмотренные фильмы

Genres / Authors
GET  /movies/genres/
POST /movies/genres/
GET  /movies/authors/
POST /movies/authors/

Subscribe
GET  /subscribe/plans/           # Список активных планов
GET  /subscribe/plans/{id}/      # Детали плана
GET  /subscribe/me/              # Текущая подписка пользователя
GET  /subscribe/me/history/      # История событий подписки

Payment
POST /payment/create-checkout/   # Создание Stripe Checkout-сессии
POST /payment/refund/            # Возврат платежа
POST /payment/webhook/           # Обработка Stripe Webhook

💳 Stripe интеграция

StripeService: создание клиентов, checkout-сессий, возвраты

PaymentService: управление платежами и их статусами

Вся бизнес-логика обернута в try/except с логированием ошибок

Метаданные платежей (user_id, subscription_id, payment_id) сохраняются для аналитики

🔒 Безопасность

JWT-аутентификация с Refresh/Access токенами

CSRF-защита для админки

CORS разрешения только для доверенных доменов

Валидация всех входных данных сериализаторами

IsAdminOrReadOnly для защиты CRUD эндпоинтов

🧪 Тестирование

Тесты через pytest или django.test

Вручную можно проверить через Postman или HTTPie

Токены автоматически подставляются при запросах

⚙️ Развертывание
Требования:

Python ≥ 3.10

PostgreSQL или SQLite

Stripe аккаунт

Быстрый запуск:
git clone <репозиторий>
cd Backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver

Переменные .env:
DEBUG=True
SECRET_KEY=your_secret
ALLOWED_HOSTS=127.0.0.1,localhost

# JWT
ACCESS_TOKEN_LIFETIME_MIN=30
REFRESH_TOKEN_LIFETIME_DAYS=7

# Stripe
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx

🧭 План развития

 Подключить Celery и Redis для фоновых задач

 Добавить REST API для Refund и PaymentHistory

 Swagger / ReDoc документация (drf-spectacular)

 Полный CI/CD workflow через Docker и GitHub Actions

 Поддержка промокодов и подарочных подписок

📝 Лицензия

MIT License — свободное использование и модификация.
