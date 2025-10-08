from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации нового пользователя."""

    password = serializers.CharField(write_only=True, 
                                     required=True, 
                                     validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password', 'password_confirm', 'avatar')
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'avatar': {'required': False},
        }

    # Настраиваем валидацию паролей (совпадение)
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Пароли не совпадают!"})
        return attrs

    # Метод - создание нового пользователя
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user
    

class UserLoginSerializer(serializers.Serializer):
    """Сериализатор для аутентификации(входа) пользователя."""

    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)


    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                username=email, 
                password=password) # если все ок, то аутентифицируем пользователя
            
            if not user: # если пользователь не найден, то ошибка
                raise serializers.ValidationError("Неверный email или пароль - попробуйте снова.(user not found)")
            
            if not user.is_active: # если пользователь не активен, то ошибка
                raise serializers.ValidationError("Аккаунт пользователя деактивирован.")
            
        else:
            raise serializers.ValidationError("Необходимо указать 'email' и 'password'.")

        attrs['user'] = user
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения профиля пользователя."""
    full_name = serializers.ReadOnlyField()
    # Тут можно добавить другие связанные поля, например, список любимых фильмов и т.д.

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 
            'last_name', 'avatar','is_staff',
            'created_at', 'updated_at'
            )
        read_only_fields = ('id', 'email', 'is_staff', 'created_at', 'updated_at')


class UserUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления профиля пользователя."""

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'avatar')
        extra_kwargs = {
            'username': {'required': False},
            'first_name': {'required': False},
            'last_name': {'required': False},
            'avatar': {'required': False},
        }

    def validate_username(self, value):
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(username=value).exists():
            raise serializers.ValidationError("Пользователь с таким username уже существует.")
        return value
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items(): # проходимся по всем полям
            setattr(instance, attr, value) # обновляем поля
        instance.save() # сохраняем изменения
        return instance # возвращаем обновленный объект пользователя


class ChangePasswordSerializer(serializers.Serializer):
    """Сериализатор для изменения пароля пользователя."""

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True, 
        validators=[validate_password]
        )
    new_password_confirm = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Старый пароль неверен.")
        return value
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "Новые пароли не совпадают!"})
        return attrs
    
    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password']) # type: ignore
        user.save()
        return user
    