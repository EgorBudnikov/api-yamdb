from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from reviews.utils import check_score, check_year_availability

CHOICES = (
    ('user', 'Пользователь'),
    ('moderator', 'Модератор'),
    ('admin', 'Админ'),
)

username_validator = RegexValidator(
    regex=r'^[\w.@+-]+\Z',
    message='username может содержать только буквы, цифры и @.+-_'
)


class Category(models.Model):
    """Модель категорий."""

    name = models.CharField(
        max_length=256,
        verbose_name='Категория',
        help_text='Введите категорию'
    )
    slug = models.SlugField(max_length=50, unique=True,
                            verbose_name='Слаг категории',
                            help_text='Введите слаг для категории')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории',

    def __str__(self):
        return self.name[:15]


class Genre(models.Model):
    """Модель жанров."""

    name = models.CharField(max_length=256, verbose_name='Жанр',
                            help_text='Введите жанр')
    slug = models.SlugField(max_length=50, unique=True,
                            verbose_name='Слаг жанра',
                            help_text='Введите слаг для жанра')

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name[:15]


class Title(models.Model):
    """Модель произведений."""

    name = models.CharField(max_length=256, verbose_name='Произведение',
                            help_text='Введите название произведения')
    year = models.PositiveSmallIntegerField(
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
        return self.name[:15]


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

    username = models.CharField(
        max_length=150, blank=True, null=False, unique=True,
        validators=[username_validator],
        error_messages={
            'unique': 'Такой username уже есть.'
        })
    email = models.EmailField(
        max_length=254, blank=True, null=False, unique=True,
        error_messages={
            'unique': 'Такой email уже есть.'
        })
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    bio = models.TextField(blank=True)
    role = models.CharField(max_length=10, choices=CHOICES, default='user')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == 'moderator'


class Review(models.Model):
    """Модель для отзывов."""

    title = models.ForeignKey(
        Title, on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор отзыва'
    )
    text = models.TextField('Текст отзыва')
    score = models.PositiveSmallIntegerField(
        verbose_name='Оценка',
        validators=(check_score,),
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ('-pub_date',)
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_review'
            )
        ]

    def __str__(self):
        return f'Отзыв автора {self.author} на {self.title}'


class Comment(models.Model):
    """Модель для комментариев к отзывам."""

    review = models.ForeignKey(
        Review, on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария'
    )
    text = models.TextField('Текст комментария')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-pub_date',)

    def __str__(self):
        return f'Комментарий автора {self.author}'
