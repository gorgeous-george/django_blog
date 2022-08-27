from celery import shared_task
from django.core.mail import send_mail


@shared_task
def send_email_task(subject, message_text, from_email):
    send_mail(
        subject,
        message_text,
        from_email,
        ['helpdesk@my_blog.com'],
        fail_silently=False,
    )