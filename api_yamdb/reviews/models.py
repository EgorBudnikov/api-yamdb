from django.db import models

from reviews.utils import check_year_availability


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
