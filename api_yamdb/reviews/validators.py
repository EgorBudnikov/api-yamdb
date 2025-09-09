from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

from reviews.constants import USERNAME_PATTERN, FORBIDDEN_USERNAME

username_validator = RegexValidator(
    regex=USERNAME_PATTERN,
    message='username может содержать только буквы, цифры и @.+-_'
)


def check_name_username_validators(arg):
    '''Нельзя использовать в username.'''
    if arg.lower() in FORBIDDEN_USERNAME:
        raise ValidationError(
            f'Нельзя использовать в username {FORBIDDEN_USERNAME}')
