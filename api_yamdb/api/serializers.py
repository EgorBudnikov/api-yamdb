import re
from random import randint

from django.db import IntegrityError
from django.contrib.auth.tokens import default_token_generator
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework_simplejwt.tokens import AccessToken

from api.utils import send_mail_code
from reviews.constants import (LENGTH_CODE, LENGTH_EMAIL, LENGTH_USERNAME,
                               FORBIDDEN_USERNAME, EMAIL_PATTERN,
                               USERNAME_PATTERN)
from reviews.models import Category, Comment, Genre, Review, Title, User
from reviews.utils import check_year_availability


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Категория."""

    class Meta:
        model = Category
        exclude = ('id',)


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Жанр."""

    class Meta:
        model = Genre
        exclude = ('id',)


class TitleCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления произведения."""

    genre = serializers.SlugRelatedField(
        many=True, slug_field='slug', queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = '__all__'

    def validate_year(self, attrs):
        check_year_availability(attrs)
        return attrs


class TitleDisplaySerializer(serializers.ModelSerializer):
    """Сериализатор для вывода произведения."""

    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Title
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['genre'] = GenreSerializer(
            instance.genre.all(), many=True
        ).data
        representation['category'] = CategorySerializer(instance.category).data
        return representation


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор регистрации пользователей."""

    class Meta:
        model = User
        fields = ('username', 'email', 'role',
                  'first_name', 'last_name', 'bio')
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True},
        }


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов."""

    author = SlugRelatedField(read_only=True, slug_field='username')
    title = SlugRelatedField(read_only=True, slug_field='name')

    class Meta:
        model = Review
        fields = ('id', 'title', 'author', 'text', 'score', 'pub_date')
        read_only_fields = ('author', 'title', 'pub_date')

    def validate(self, data):
        if not self.instance:
            reviews = Review.objects.filter(
                author=self.context.get('request').user,
                title=self.context.get('title_id')
            )
            if reviews.exists():
                raise serializers.ValidationError(
                    'Вы уже оставляли отзыв на это произведение.'
                )
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев к отзывам."""

    author = SlugRelatedField(read_only=True, slug_field='username')

    class Meta:
        model = Comment
        fields = ('id', 'review', 'author', 'text', 'pub_date')
        read_only_fields = ('author', 'review', 'pub_date')


class RegisterSerializer(serializers.ModelSerializer):
    '''Сериализатор для регистрации пользователей'''

    class Meta:
        model = User
        fields = ('username', 'email')
        extra_kwargs = {
            'username': {'validators': []},
            'email': {'validators': []}
        }

    def validate(self, data):
        """Валидация данных регистрации."""
        username = data.get('username')
        email = data.get('email')

        errors = {}

        # Проверка наличия полей
        if not email:
            errors['email'] = ['Поле отсутствует.']

        if not username:
            errors['username'] = ['Поле отсутствует.']

        # Проверка длин
        if email and len(email) > LENGTH_EMAIL:
            errors['email'] = [
                f'Длина email не больше {LENGTH_EMAIL} символов.']

        if username and len(username) > LENGTH_USERNAME:
            errors['username'] = [
                f'Длина username не больше {LENGTH_USERNAME} символов.']

        # Проверка запрещенных username
        if username and username.lower() in FORBIDDEN_USERNAME:
            errors['username'] = [
                f'Нельзя использовать username {username}.']

        # Проверка форматов
        if username and not re.match(USERNAME_PATTERN, username):
            errors['username'] = [
                'Должен состоять из латинских букв, цифр и символов @.+-_']

        if email and not re.match(EMAIL_PATTERN, email):
            errors['email'] = ['Введите корректный email.']

        if errors:
            raise serializers.ValidationError(errors)

        return data

    def create(self, validated_data):
        """Создает или получает пользователя и отправляет код подтверждения."""
        username = validated_data['username']
        email = validated_data['email']

        try:
            user, created = User.objects.get_or_create(
                username=username,
                email=email,
                defaults={
                    'password': str(randint(10, 999999))
                }
            )
        except IntegrityError:
            raise serializers.ValidationError({
                'error': 'Конфликт данных пользователя'
            })

        send_mail_code(user, email)

        return user


class TokenSerializer(serializers.Serializer):
    """Серилизатор получения токена."""

    username = serializers.CharField(max_length=LENGTH_USERNAME)
    confirmation_code = serializers.CharField(max_length=LENGTH_CODE)

    def validate(self, data):
        """Валидация username и confirmation_code."""
        username = data.get('username')
        confirmation_code = data.get('confirmation_code')

        if not username or not confirmation_code:
            raise serializers.ValidationError(
                'Для токена используйте username и confirmation_code.'
            )

        try:
            self.user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.user_not_found = True
            raise serializers.ValidationError({
                'username': ['Пользователь с таким username не существует.']
            })

        if not self.user.is_admin:
            if not default_token_generator.check_token(
                self.user, confirmation_code
            ):
                raise serializers.ValidationError({
                    'confirmation_code': ['Неверный код подтверждения.']
                })

        return data

    def create(self, validated_data):
        """Создание токена."""
        return AccessToken.for_user(self.user)
