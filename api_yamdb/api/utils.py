from random import randint

from django.core.mail import send_mail

from rest_framework.response import Response
from reviews.models import ConfirmationCode


def send_mail_code(user, email):
    code = str(randint(100000, 999999))
    ConfirmationCode.objects.create(user=user, code=code)

    send_mail(
        'Код подтверждения',
        f'Ваш новый код подтверждения {code}',
        None,
        [email],
        fail_silently=False,
    )
    return Response({'email': email, 'username': user.username})
