import re
from random import randint

from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework_simplejwt.tokens import AccessToken

from api.utils import send_mail_code
from reviews.constants import (LENGTH_CODE, LENGTH_EMAIL, LENGTH_USERNAME,
                               FORBIDDEN_USERNAME,
                               USERNAME_PATTERN)
from reviews.models import Category, Comment, Genre, Review, Title, User
from reviews.validators import check_year_availability


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
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')

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
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )

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


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов."""

    author = SlugRelatedField(read_only=True, slug_field='username')

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, data):
        request = self.context.get('request')
        if request.method == 'POST':
            reviews = Review.objects.filter(
                author=request.user,
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
        fields = ('id', 'text', 'author', 'pub_date')


class RegisterSerializer(serializers.Serializer):
    '''Сериализатор для регистрации пользователей'''

    username = serializers.CharField(
        max_length=LENGTH_USERNAME,
        error_messages={
            'required': 'Поле username обязательно.',
            'max_length':
            f'Длина username не больше {LENGTH_USERNAME} символов.'
        }
    )

    email = serializers.EmailField(
        max_length=LENGTH_EMAIL,
        error_messages={
            'required': 'Поле email обязательно.',
            'max_length': f'Длина email не больше {LENGTH_EMAIL} символов.',
            'invalid': 'Введите корректный email.'
        }
    )

    def validate_username(self, value):
        """Валидация username."""
        if value in FORBIDDEN_USERNAME:
            raise serializers.ValidationError(
                f'Нельзя использовать username {value}.'
            )

        if not re.match(USERNAME_PATTERN, value):
            raise serializers.ValidationError(
                'Должен состоять из латинских букв, цифр и символов @.+-_'
            )

        return value

    def validate(self, data):
        """Дополнительная валидация."""
        username = data['username']
        email = data['email']

        existing_by_username = User.objects.filter(username=username).first()
        existing_by_email = User.objects.filter(email=email).first()

        if existing_by_username and existing_by_username.email != email:
            raise serializers.ValidationError({
                'username': ['Такой username уже существует.']
            })

        if existing_by_email and existing_by_email.username != username:
            raise serializers.ValidationError({
                'email': ['Такой email уже существует.']
            })

        return data

    def create(self, validated_data):
        """Создает или получает пользователя."""
        username = validated_data['username']
        email = validated_data['email']

        existing_user = User.objects.filter(
            username=username,
            email=email
        ).first()

        if existing_user:
            user = existing_user
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=str(randint(10, 999999)),

            )

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

        self.user = get_object_or_404(User, username=username)

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
