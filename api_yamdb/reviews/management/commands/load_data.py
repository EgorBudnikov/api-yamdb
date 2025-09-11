from django.core.management.base import BaseCommand

from reviews.models import (
    Category, Comment, Genre, TitleGenre, Review, Title, User
)


category_field_mapping = {
    'name': 'name',
    'slug': 'slug'
}

genre_field_mapping = {
    'name': 'name',
    'slug': 'slug'
}

title_field_mapping = {
    'name': 'name',
    'year': 'year',
    'category': 'category_id'
}

title_genre_field_mapping = {
    'title_id': 'title_id',
    'genre_id': 'genre_id'
}

user_field_mapping = {
    'id': 'id',
    'username': 'username',
    'email': 'email',
    'role': 'role',
    'bio': 'bio',
    'first_name': 'first_name',
    'last_name': 'last_name'
}

review_field_mapping = {
    'title_id': 'title_id',
    'text': 'text',
    'author': 'author_id',
    'score': 'score',
    'pub_date': 'pub_date'
}

comment_field_mapping = {
    'review_id': 'review_id',
    'text': 'text',
    'author': 'author_id',
    'pub_date': 'pub_date'
}

model_field_mappings = {
    Category: category_field_mapping,
    Genre: genre_field_mapping,
    Title: title_field_mapping,
    TitleGenre: title_genre_field_mapping,
    Review: review_field_mapping,
    Comment: comment_field_mapping
}


class Command(BaseCommand):
    help = "Загрузка данных из нескольких CSV файлов в базу данных для моделей"

    def handle(self, *args, **options):
        from csv import reader

        # Список путей к вашим CSV файлам и соответствующие модели
        csv_files_and_models = [
            {
                'file_path': 'static/data/category.csv',
                'model': Category,
                'fields': ['name', 'slug']
            },
            {
                'file_path': 'static/data/genre.csv',
                'model': Genre,
                'fields': ['name', 'slug']
            },
            {
                'file_path': 'static/data/titles.csv',
                'model': Title,
                'fields': ['name', 'description', 'year', 'category_id']
            },
            {
                'file_path': 'static/data/genre_title.csv',
                'model': TitleGenre,
                'fields': ['title_id', 'genre_id']
            },
            {
                'file_path': 'static/data/users.csv',
                'model': User,
                'fields': ['id', 'username', 'email', 'role',
                           'bio', 'first_name', 'last_name']
            },
            {
                'file_path': 'static/data/review.csv',
                'model': Review,
                'fields': ['title_id', 'text', 'author_id',
                           'score', 'pub_date']
            },
            {
                'file_path': 'static/data/comments.csv',
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
                        field_mapping = user_field_mapping
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
