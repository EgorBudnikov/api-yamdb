from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

CHOICES = (
    ('user', 'Пользователь'),
    ('moderator', 'Модератор'),
    ('admin', 'Админ'),
)

username_validator = RegexValidator(
    regex=r'^[\w.@+-]+\Z',
    message='username может содержать только буквы, цифры и @.+-_'
)


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

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == 'moderator'


class ConfirmationCode(models.Model):
    """Модель для регистрации пользователя."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
