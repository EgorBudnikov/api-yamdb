import re
from random import randint

from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from api.utils import send_mail_code
from reviews.constants import LENGTH_EMAIL, LENGTH_USERNAME, FORBIDDEN_USERNAME
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
                f'Нельзя использовать в username {", ".join(FORBIDDEN_USERNAME)}.']

        # Проверка форматов
        if username:
            username_pattern = r'^[\w.@+-]+\Z'
            if not re.match(username_pattern, username):
                errors['username'] = [
                    'Должен состоять из латинских букв, цифр и символов "@.+-_".']

        if email:
            email_pattern = r'^[a-zA-Z\d_.+-]+@[a-zA-Z\d]+\.[a-zA-Z\d.]+$'
            if not re.match(email_pattern, email):
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
