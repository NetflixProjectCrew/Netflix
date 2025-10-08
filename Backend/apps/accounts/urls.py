from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView 
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),  # Регистрация и аутентификация пользователей
    path('login/', views.LoginView.as_view(), name='login'),  # Регистрация и аутентификация пользователей
    path('logout/', views.logout_view, name='logout'),  # Выход пользователя
    path('profile/', views.ProfileView.as_view(), name='profile'),  # Просмотр и обновление профиля пользователя
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),  # Изменение пароля пользователя
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Обновление JWT токена
]

