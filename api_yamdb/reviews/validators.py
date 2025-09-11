from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone

from reviews.constants import (
    FORBIDDEN_USERNAME,
    MAX_SCORE,
    MIN_SCORE,
    USERNAME_PATTERN
)

username_validator = RegexValidator(
    regex=USERNAME_PATTERN,
    message='username может содержать только буквы, цифры и @.+-_'
)


def check_name_username_validators(arg):
    '''Нельзя использовать в username.'''
    if arg.lower() in FORBIDDEN_USERNAME:
        raise ValidationError(
            f'Нельзя использовать в username {FORBIDDEN_USERNAME}')


def check_year_availability(year):
    """Проверка даты произведения."""
    current_year = timezone.now().year
    if year and year >= current_year:
        raise ValidationError(
            'Год выпуска произведения не должен быть больше текущего.'
        )


def check_score(score: int) -> None:
    """Функция проверки корректности оценки."""
    if not MIN_SCORE <= score <= MAX_SCORE:
        raise ValidationError(
            'Оценка должна быть в диапазоне от одного до десяти.'
        )
