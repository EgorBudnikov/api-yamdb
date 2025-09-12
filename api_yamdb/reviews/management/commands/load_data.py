from csv import reader

from django.core.management.base import BaseCommand

from reviews.models import (
    Category, Comment, Genre, TitleGenre, Review, Title, User
)


BASE_PATH = 'static/data/'

CATEGORY_FIELD_MAPPING = {
    'name': 'name',
    'slug': 'slug'
}

GENRE_FIELD_MAPPING = {
    'name': 'name',
    'slug': 'slug'
}

TITLE_FIELD_MAPPING = {
    'name': 'name',
    'year': 'year',
    'category': 'category_id'
}

TITLE_GENRE_FIELD_MAPPING = {
    'title_id': 'title_id',
    'genre_id': 'genre_id'
}

USER_FIELD_MAPPING = {
    'id': 'id',
    'username': 'username',
    'email': 'email',
    'role': 'role',
    'bio': 'bio',
    'first_name': 'first_name',
    'last_name': 'last_name'
}

REVIEW_FIELD_MAPPING = {
    'title_id': 'title_id',
    'text': 'text',
    'author': 'author_id',
    'score': 'score',
    'pub_date': 'pub_date'
}

COMMENT__FIELD_MAPPING = {
    'review_id': 'review_id',
    'text': 'text',
    'author': 'author_id',
    'pub_date': 'pub_date'
}

model_field_mappings = {
    Category: CATEGORY_FIELD_MAPPING,
    Genre: GENRE_FIELD_MAPPING,
    Title: TITLE_FIELD_MAPPING,
    TitleGenre: TITLE_GENRE_FIELD_MAPPING,
    Review: REVIEW_FIELD_MAPPING,
    Comment: COMMENT__FIELD_MAPPING
}


class Command(BaseCommand):
    help = "Загрузка данных из нескольких CSV файлов в базу данных для моделей"

    def handle(self, *args, **options):

        # Список путей к вашим CSV файлам и соответствующие модели
        csv_files_and_models = [
            {
                'file_path': BASE_PATH + 'category.csv',
                'model': Category,
                'fields': ['name', 'slug']
            },
            {
                'file_path': BASE_PATH + 'genre.csv',
                'model': Genre,
                'fields': ['name', 'slug']
            },
            {
                'file_path': BASE_PATH + 'titles.csv',
                'model': Title,
                'fields': ['name', 'description', 'year', 'category_id']
            },
            {
                'file_path': BASE_PATH + 'genre_title.csv',
                'model': TitleGenre,
                'fields': ['title_id', 'genre_id']
            },
            {
                'file_path': BASE_PATH + 'users.csv',
                'model': User,
                'fields': ['id', 'username', 'email', 'role',
                           'bio', 'first_name', 'last_name']
            },
            {
                'file_path': BASE_PATH + 'review.csv',
                'model': Review,
                'fields': ['title_id', 'text', 'author_id',
                           'score', 'pub_date']
            },
            {
                'file_path': BASE_PATH + 'comments.csv',
                'model': Comment,
                'fields': ['text', 'pub_date', 'author', 'review']
            }
        ]

        for item in csv_files_and_models:
            file_path = item['file_path']
            model = item['model']

            with open(file_path, 'r', encoding='utf-8') as csvfile:
                csv_reader = reader(csvfile)
                next(csv_reader)

                for row in csv_reader:
                    # Сопоставляем данные из строки CSV с полями модели
                    if model == User:
                        field_mapping = USER_FIELD_MAPPING
                        model_data = {
                            field_mapping[model_field]: row[i] for i,
                            model_field in enumerate(field_mapping)
                        }
                    else:
                        field_mapping = model_field_mappings[model]
                        model_data = {
                            field_mapping[model_field]: row[i + 1] for i,
                            model_field in enumerate(field_mapping)
                        }

                    model_instance = model(**model_data)
                    model_instance.save()

            self.stdout.write(self.style.SUCCESS(f'Данные из файла {
                file_path} успешно загружены в модель {model.__name__}'))
