from django.core.mail import send_mail
from django.utils import timezone

from .models import Attempt


class MailingNotAllowedError(Exception):
    """Рассылка сейчас не может быть запущена (не наступило время или нет получателей)."""

    pass


def send_mailing(mailing):
    """Отправка рассылок получателям с валидатором времени и списка получателей"""

    # Валидатор времени
    now = timezone.now()
    if not (mailing.start_time <= now <= mailing.end_time):
        raise MailingNotAllowedError(
            f"Рассылка №{mailing.pk} сейчас недоступна. "
            f"Время отправки: {mailing.start_time:%d.%m.%Y %H:%M} - {mailing.end_time:%d.%m.%Y %H:%M}"
        )

    # Валидатор списка получателей
    recipients = mailing.recipients.all()
    if not recipients:
        raise MailingNotAllowedError(f"У рассылки №{mailing.pk} нет получателей.")

    # Отправка писем
    message = mailing.message

    for recipient in recipients:
        mailing.refresh_from_db()
        if mailing.is_disabled:
            raise MailingNotAllowedError("Рассылка отменена.")

        try:
            send_mail(
                subject=message.message_title,
                message=message.message_text,
                from_email=None,
                recipient_list=[recipient.email],
                fail_silently=False,
            )

        except Exception as exc:
            Attempt.objects.create(
                mailing=mailing, status=Attempt.STATUS_FAILED, server_response=str(exc)
            )
        else:
            Attempt.objects.create(
                mailing=mailing, status=Attempt.STATUS_SUCCESS, server_response="OK"
            )
