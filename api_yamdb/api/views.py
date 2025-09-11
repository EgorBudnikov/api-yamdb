from django.contrib.auth import get_user_model
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (
    filters, mixins, pagination, viewsets
)
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.constants import (
    BAD_REQUEST, NOT_FOUND
)
from api.filters import TitleFilter
from api.permissions import (
    AdminPerm, IsAdminOrReadOnly, IsAuthorModeratorAdminOrReadOnly
)
from api.serializers import (
    CategorySerializer, CommentSerializer, GenreSerializer,
    ReviewSerializer, TitleCreateUpdateSerializer, TitleDisplaySerializer,
    UserSerializer, RegisterSerializer, TokenSerializer
)
from reviews.models import (
    Category, Comment, Genre, Review, Title, User
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
    Всегда возвращает 200, если данные валидны.
    """
    serializer = RegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=BAD_REQUEST)

    user = serializer.save()

    return Response({
        'email': user.email,
        'username': user.username
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def token_obtain(request):
    """Функция для получения токена."""

    serializer = TokenSerializer(data=request.data)

    if not serializer.is_valid():
        errors = serializer.errors

        user_not_found = getattr(serializer, 'user_not_found', False)

        if user_not_found:
            status = NOT_FOUND
        else:
            status = BAD_REQUEST

        return Response(errors, status=status)

    token = serializer.save()

    return Response({'token': str(token)})


class UsersViewSet(viewsets.ModelViewSet):
    """Вьюсет на работу с юзерами админу и суперюзеру."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AdminPerm]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'
    http_method_names = ('get', 'post', 'patch', 'delete')

    @action(
        detail=False,
        methods=['get', 'patch'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Для обработки get/patch запроса к урлу api/v1/users/me."""
        user = request.user

        if request.method == 'PATCH':
            data = request.data
            serializer = UserSerializer(user, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(role=user.role)
        else:
            serializer = UserSerializer(user)
        return Response(serializer.data)


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
