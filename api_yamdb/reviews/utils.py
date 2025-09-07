from django.core.exceptions import ValidationError
from django.utils import timezone


def check_year_availability(year):
    current_year = timezone.now().year
    if year and year >= current_year:
        raise ValidationError(
            'Год выпуска произведения не должен быть больше текущего.'
        )


def check_score(score: int) -> None:
    if not 1 <= score <= 10:
        raise ValidationError(
            'Оценка должна быть в диапазоне от одного до десяти.'
        )
