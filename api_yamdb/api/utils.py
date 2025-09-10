from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator


def send_mail_code(user, email):
    code = default_token_generator.make_token(user)

    send_mail(
        'Код подтверждения YAMBL',
        f'Ваш новый код подтверждения {code}',
        None,
        [email],
        fail_silently=False,
    )
