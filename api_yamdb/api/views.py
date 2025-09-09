import re
from random import randint

from django.contrib.auth import get_user_model
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (
    exceptions, filters, mixins, pagination, viewsets
)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from api.constants import (
    BAD_REQUEST, NOT_FOUND, LEN_EMAIL, LEN_USERNAME, METHOD_NOT_ALLOWED
)
from api.filters import TitleFilter
from api.permissions import (
    AdminPerm, IsAdminOrReadOnly, IsAuthorModeratorAdminOrReadOnly
)
from api.serializers import (
    CategorySerializer, CommentSerializer, GenreSerializer,
    ReviewSerializer, TitleCreateUpdateSerializer, TitleDisplaySerializer,
    UserSerializer
)
from api.utils import send_mail_code
from reviews.models import (
    Category, Comment, ConfirmationCode, Genre, Review, Title, User
)

User = get_user_model()


class BaseCreateListDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Базовый вьюсет с общими настройками."""
    pagination_class = pagination.LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    permission_classes = (IsAdminOrReadOnly,)
    search_fields = ('name',)
    lookup_field = 'slug'

    pass


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Произведение."""

    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')).order_by('rating')
    pagination_class = pagination.LimitOffsetPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = TitleFilter
    permission_classes = (IsAdminOrReadOnly,)
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return TitleCreateUpdateSerializer
        return TitleDisplaySerializer


class GenreViewSet(BaseCreateListDestroyViewSet):
    """Вьюсет для модели Жанр."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoryViewSet(BaseCreateListDestroyViewSet):
    """Вьюсет для модели Категория."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    Обрабатывает регистрацию нового пользователя.

    Принимает POST-запрос с данными email и username.
    Проводит валидацию данных, проверяет существующих пользователей
    и либо создает нового пользователя, либо возвращает ошибки.
    """
    email = request.data.get('email')
    username = request.data.get('username')

    # Валидация базовых проверок
    errors = _validate_basic_checks(request, email, username)
    if errors:
        return Response(errors, status=BAD_REQUEST)

    # Валидация форматов
    format_errors = _validate_formats(email, username)
    if format_errors:
        return Response(format_errors, status=BAD_REQUEST)

    # Проверка существующих пользователей
    return _handle_user_registration(email, username)


def _validate_basic_checks(request, email, username):
    """
    Проверяет базовые условия валидации данных регистрации.

    Проверяет наличие обязательных полей, их длину и специальные случаи.
    """
    errors = {}

    if len(request.data) != 2:
        errors['errors'] = ['Должно быть только два поля username и email.']

    if not email:
        errors['email'] = ['Поле отсутствует.']

    if not username:
        errors['username'] = ['Поле отсутствует.']

    if email and len(email) > LEN_EMAIL:
        errors['email'] = ['Длина email не больше 254 символов.']

    if username and len(username) > LEN_USERNAME:
        errors['username'] = ['Длина username не больше 150 символов.']

    if username == 'me':
        errors['username'] = ['Нельзя использовать в username "me".']

    return errors


def _validate_formats(email, username):
    """
    Проверяет форматы email и username на соответствие паттернам.
    """
    errors = {}

    if username:
        username_pattern = r'^[\w.@+-]+\Z'
        if not re.match(username_pattern, username):
            errors['username'] = [
                'Должен состоять из латинских букв, цифр и символов "w.@+-".'
            ]

    if email:
        email_pattern = r'^[a-zA-Z\d_.+-]+@[a-zA-Z\d]+\.[a-zA-Z\d.]+$'
        if not re.match(email_pattern, email):
            errors['email'] = ['Введите корректный email.']

    return errors


def _handle_user_registration(email, username):
    """
    Обрабатывает логику регистрации пользователя на основе проверок.

    Проверяет существующих пользователей, обрабатывает конфликты
    и создает нового пользователя при успешной проверке.
    """
    try:
        user_by_email = User.objects.get(email=email)
    except User.DoesNotExist:
        user_by_email = None

    try:
        user_by_username = User.objects.get(username=username)
    except User.DoesNotExist:
        user_by_username = None

    # Оба пользователя существуют и это разные люди
    if (
        user_by_email
        and user_by_username
        and user_by_email != user_by_username
    ):
        return Response({
            'email': ['Такой email уже существует.'],
            'username': ['Такой username уже существует.']
        }, status=BAD_REQUEST)

    # Email уже существует
    if user_by_email and (
        not user_by_username or user_by_email != user_by_username
    ):
        return Response({
            'email': ['Такой email уже существует.']
        }, status=BAD_REQUEST)

    # Username уже существует
    if user_by_username and (
        not user_by_email or user_by_username != user_by_email
    ):
        return Response({
            'username': ['Такой username уже существует.']
        }, status=BAD_REQUEST)

    # Пользователь уже существует (повторный запрос)
    if user_by_email and user_by_username:
        return send_mail_code(user_by_email, email)

    # Новый пользователь
    user = User.objects.create_user(
        username=username,
        email=email,
        password=str(randint(10, 999999)),
        is_active=False,
    )

    return send_mail_code(user, email)


@api_view(['POST'])
@permission_classes([AllowAny])
def token_obtain(request):
    """Функция для получения токена."""
    username = request.data.get('username')
    confirmation_code = request.data.get('confirmation_code')

    if len(request.data) != 2 or not username or not confirmation_code:
        return Response(
            {
                'error': 'Для токена используйте username и confirmation_code.'
            },
            status=BAD_REQUEST
        )

    try:
        user = User.objects.get(username=username)

        if user.is_superuser:
            return Response({'token': str(AccessToken.for_user(user))})

        code = ConfirmationCode.objects.get(user=user, code=confirmation_code)
    except User.DoesNotExist:
        return Response(
            {'error': ['Пользователь с таким username не найден.']},
            status=NOT_FOUND
        )
    except ConfirmationCode.DoesNotExist:
        return Response(
            {'error': ['Неверный код подтверждения.']},
            status=BAD_REQUEST
        )

    user.is_active = True
    user.save()
    code.is_used = True
    code.save()

    token = AccessToken.for_user(user)

    return Response({'token': str(token)})


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def change_profile(request):
    """Функция обработки метода PATCH для изменения профиля."""
    user = request.user

    if request.method == 'PATCH':
        data = request.data.copy()

        if not user.is_admin:
            data['role'] = user.role

        serializer = UserSerializer(user, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    elif request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)


class UsersViewSet(viewsets.ModelViewSet):
    """Вьюсет на работу с юзерами админу и суперюзеру."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AdminPerm]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'

    def update(self, request, *args, **kwargs):
        if request.method == 'PUT':
            return Response(
                {'detail': 'Метод PUT запрещет. Используйте PATCH.'},
                status=METHOD_NOT_ALLOWED)
        return super().update(request, *args, **kwargs)


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с отзывами: CRUD."""

    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorModeratorAdminOrReadOnly, )

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        return Review.objects.select_related('author').filter(title=title_id)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['title_id'] = self.kwargs.get('title_id')
        return context

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с комментариями: CRUD."""

    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    serializer_class = CommentSerializer
    pagination_class = pagination.LimitOffsetPagination
    permission_classes = (IsAuthorModeratorAdminOrReadOnly, )

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        return (
            Comment.objects
            .select_related('author')
            .filter(review=review_id)
        )

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, pk=review_id)
        serializer.save(author=self.request.user, review=review)
