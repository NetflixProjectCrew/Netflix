from django.shortcuts import render
from django.contrib.auth import login
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes


from .models import User
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer
)


class RegisterView(generics.CreateAPIView):
    """Регистрация нового пользователя."""
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny,]
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        # Достаем сериализатор и валидируем данные
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Создаем нового пользователя
        user = serializer.save()

        # Генерируем токены для нового пользователя
        refresh = RefreshToken.for_user(user)


        return Response({
            "user": UserProfileSerializer(user).data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "message": "User registered successfully."
        }, status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    """Аутентификация(вход) пользователя."""

    permission_classes = [permissions.AllowAny,]
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        login(request, user)
        refresh = RefreshToken.for_user(user)

        return Response({
            "user": UserProfileSerializer(user).data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "message": "User logined successfully."
        }, status=status.HTTP_200_OK)
       


class ProfileView(generics.RetrieveUpdateAPIView):
    """Просмотр и обновление профиля пользователя."""
    permission_classes = [permissions.IsAuthenticated,]
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserProfileSerializer


class ChangePasswordView(generics.UpdateAPIView):
    """Изменение пароля пользователя."""
    permission_classes = [permissions.IsAuthenticated,]
    serializer_class = ChangePasswordSerializer

    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "Password updated successfully."}, 
            status=status.HTTP_200_OK
            )



@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    refresh_token = request.data.get('refresh')
    if not refresh_token:
        return Response({"error": "Refresh token is required."},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"message": "User logged out successfully."},
                        status=status.HTTP_200_OK)
    except Exception:
        return Response({"error": "Invalid token or token already blacklisted."},
                        status=status.HTTP_400_BAD_REQUEST)
