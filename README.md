# api_yamdb
api_yamdb

Реализовано с помощью Django REST Framework.

Технологии

Python 3.12
Django 5.1
Django REST Framework
SQLite (по умолчанию)

Для локального запуска бота необходимо:

Создать и активировать виртуальное окружение
python -m venv venv
source venv\Scripts\activate

Установить зависимости 'requirements.txt'
pip install -r requirements.txt

Запустить сервер:
python manage.py runserver

Эндпоинты

Регистрация нового пользователя

/api/v1/auth/signup/ (POST): Регистрация нового пользователя.
/api/v1/auth/token/ (POST): Получение токена по коду подтверждения.
/api/v1/users/ (GET, POST): Список пользователей и создание нового (только для администратора).
/api/v1/users/{username}/ (GET, PATCH, DELETE): Получение, изменение или удаление пользователя (только для администратора).
/api/v1/users/me/ (GET, PATCH): Получение или изменение данных текущего пользователя.

Категории и жанры

/api/v1/categories/ (GET, POST): Список категорий, создание новой (POST только для администратора).
/api/v1/categories/{slug}/ (DELETE): Удаление категории (только для администратора).
/api/v1/genres/ (GET, POST): Список жанров, создание нового (POST только для администратора).
/api/v1/genres/{slug}/ (DELETE): Удаление жанра (только для администратора).

Произведения

/api/v1/titles/ (GET, POST): Список произведений, добавление нового (POST — только для администратора).
/api/v1/titles/{title_id}/ (GET, PATCH, DELETE): Подробная информация, изменение или удаление произведения (PATCH/DELETE — только для администратора).

Отзывы

/api/v1/titles/{title_id}/reviews/ (GET, POST): Список отзывов для произведения, добавление нового (POST — только для аутентифицированных).
/api/v1/titles/{title_id}/reviews/{review_id}/ (GET, PATCH, DELETE): Получение, изменение или удаление отзыва (PATCH/DELETE — только автор, модератор или администратор).

Комментарии

/api/v1/titles/{title_id}/reviews/{review_id}/comments/ (GET, POST): Список комментариев к отзыву, добавление нового (POST — только для аутентифицированных).
/api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/ (GET, PATCH, DELETE): Получение, изменение или удаление комментария (PATCH/DELETE — только автор, модератор или адмигистратор).