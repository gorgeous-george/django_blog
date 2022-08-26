from celery import shared_task
from django.core.mail import send_mail


@shared_task
def send_email_task(subject, message_text, recipient_email):
    send_mail(
        subject,
        message_text,
        'test@abc.com',
        [recipient_email],
        fail_silently=False,
    )
