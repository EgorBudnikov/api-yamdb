from django.core.exceptions import ValidationError
from django.utils import timezone

from reviews.constants import MAX_SCORE, MIN_SCORE

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
