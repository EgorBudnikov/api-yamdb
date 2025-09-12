from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import AbstractUser
from django.db import models

from reviews.constants import (
    LENGTH_EMAIL,
    LENGTH_ROLE,
    LENGTH_USERNAME,
    MAX_NAME_LENGTH,
    TEXT_MAX_LENGHT,
)
from reviews.validators import (
    check_name_username_validators,
    check_score,
    check_year_availability,
    username_validator
)


class AuthorTextDateModel(models.Model):
    """Абстрактная модель для пользовательского контента."""

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    text = models.TextField('Текст')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ('-pub_date',)


class NameSlugModel(models.Model):
    """Абстрактная модель для категорий и жанров."""

    name = models.CharField(
        max_length=TEXT_MAX_LENGHT,
        verbose_name='Название',
        help_text='Введите название'
    )
    slug = models.SlugField(unique=True,
                            verbose_name='Слаг',
                            help_text='Введите слаг')

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name[:MAX_NAME_LENGTH]


class Category(NameSlugModel):
    """Модель категорий."""

    class Meta(NameSlugModel.Meta):
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(NameSlugModel):
    """Модель жанров."""

    class Meta(NameSlugModel.Meta):
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    """Модель произведений."""

    name = models.CharField(max_length=TEXT_MAX_LENGHT,
                            verbose_name='Произведение',
                            help_text='Введите название произведения')
    year = models.SmallIntegerField(
        validators=(check_year_availability,),
        help_text='Дата выхода произведения', verbose_name='Дата выхода')
    category = models.ForeignKey(
        Category, null=True, on_delete=models.SET_NULL, related_name='titles',
        verbose_name='Категория',
        help_text='Выберете категорию'
    )
    description = models.TextField(null=True, verbose_name='Описание',
                                   help_text='Введите описание')
    genre = models.ManyToManyField(Genre, related_name='titles',
                                   verbose_name='Жанр',
                                   help_text='Введите жанр')

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('year',)

    def __str__(self):
        return self.name[:MAX_NAME_LENGTH]

    @admin.display(description='Жанры')
    def get_genre_list(self):
        """Возвращает строку с жанрами, разделёнными запятыми."""
        return ', '.join([genre.name for genre in self.genre.all()])


class TitleGenre(models.Model):
    """Дополнительная модель: Произведение - Жанр."""

    title = models.ForeignKey(Title, on_delete=models.CASCADE,
                              related_name='title_genres')
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE,
                              related_name='titles_genre')

    def __str__(self):
        return f'{self.title.name} - {self.genre.name}'


class User(AbstractUser):
    """Кастомная модель User."""

    user = 'user'
    moderator = 'moderator'
    admin = 'admin'

    CHOICES = (
        (user, 'Пользователь'),
        (moderator, 'Модератор'),
        (admin, 'Админ'),
    )

    username = models.CharField(
        max_length=LENGTH_USERNAME, unique=True,
        validators=[username_validator, check_name_username_validators],
        error_messages={
            'unique': 'Такой username уже есть.'
        }, verbose_name='Имя пользователя')
    email = models.EmailField(
        max_length=LENGTH_EMAIL, unique=True,
        error_messages={
            'unique': 'Такой email уже есть.'
        }, verbose_name='E-mail')
    bio = models.TextField(blank=True, verbose_name='Биография')
    role = models.CharField(max_length=LENGTH_ROLE, choices=CHOICES,
                            default=user, verbose_name='Роль пользователя')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == self.admin or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == self.moderator


class Review(AuthorTextDateModel):
    """Модель для отзывов."""

    title = models.ForeignKey(
        Title, on_delete=models.CASCADE,
        verbose_name='Отзыв'
    )
    score = models.PositiveSmallIntegerField(
        verbose_name='Оценка',
        validators=(check_score,),
    )

    class Meta(AuthorTextDateModel.Meta):
        default_related_name = 'reviews'
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_review'
            )
        ]

    def __str__(self):
        return f'Отзыв автора {self.author} на {self.title}'


class Comment(AuthorTextDateModel):
    """Модель для комментариев к отзывам."""

    review = models.ForeignKey(
        Review, on_delete=models.CASCADE,
        verbose_name='Отзыв'
    )

    class Meta(AuthorTextDateModel.Meta):
        default_related_name = 'comments'
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f'Комментарий автора {self.author}'
