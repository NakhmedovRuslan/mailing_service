from django.core.exceptions import ValidationError
from django.utils import timezone

from django.db import models


################ МОДЕЛЬ ПОЛУЧАТЕЛИ #################

class Recipient(models.Model):
    email = models.EmailField(unique=True, verbose_name="Email")
    full_name = models.CharField(max_length=150, verbose_name="Ф.И.О.")
    comments = models.TextField(blank=True, verbose_name="Комментарий")

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Получатель"
        verbose_name_plural = "Получатели"
        ordering = ('email',)


################ МОДЕЛЬ СООБЩЕНИЯ #################

class Message(models.Model):
    message_title = models.CharField(max_length=50, verbose_name="Тема письма")
    message_text = models.TextField(verbose_name="Тело письма")

    def __str__(self):
        return self.message_title  # удобно видеть тему, а не "Message object"

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"


################ МОДЕЛЬ РАССЫЛКИ #################

class MailingModel(models.Model):
    STATUS_CREATED = 'Создана'
    STATUS_STARTED = 'Запущена'
    STATUS_FINISHED = 'Завершена'

    STATUS_CHOICES = [
        (STATUS_CREATED, 'Создана'),
        (STATUS_STARTED, 'Запущена'),
        (STATUS_FINISHED, 'Завершена'),
    ]

    start_time = models.DateTimeField(
        verbose_name="Дата и время начала отправки", null=False, blank=False
    )
    end_time = models.DateTimeField(
        verbose_name="Дата и время окончания отправки", null=False, blank=False
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_CREATED,
        verbose_name="Статус рассылки",
    )
    message = models.ForeignKey(
        'Message',
        on_delete=models.CASCADE,
        related_name='mailings',
        verbose_name="Сообщение",
    )
    recipients = models.ManyToManyField(
        'Recipient',
        related_name='mailings',
        verbose_name="Получатели",
    )

    def update_status(self):
        """Динамическое обновление статуса рассылки"""
        time_now = timezone.now()
        if self.start_time > time_now:
            if self.status != self.STATUS_CREATED:
                self.status = self.STATUS_CREATED
                self.save()
        elif self.start_time <= time_now <= self.end_time:
            if self.status != self.STATUS_STARTED:
                self.status = self.STATUS_STARTED
                self.save()
        else:
            if self.status != self.STATUS_FINISHED:
                self.status = self.STATUS_FINISHED
                self.save()

    def clean(self):
        """Валидатор даты начала/окончания рассылки"""
        super().clean()
        time_now = timezone.now()

        if self.start_time and self.start_time < time_now:
            raise ValidationError({"start_time": "Дата начала рассылки не может быть в прошлом."})

        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError({"end_time": "Дата окончания рассылки должна быть позже даты начала."})

    def __str__(self):
        return f"Рассылка №{self.pk} ({self.status})"

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        ordering = ('-start_time',)


################ МОДЕЛЬ ПОПЫТКА ОТПРАВКИ #################

class Attempt(models.Model):
    STATUS_SUCCESS = 'Успешно'
    STATUS_FAILED = 'Не успешно'

    STATUS_CHOICES = [
        (STATUS_SUCCESS, 'Успешно'),
        (STATUS_FAILED, 'Не успешно'),
    ]

    attempted_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата и время попытки",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        verbose_name="Статус",
    )
    server_response = models.TextField(
        blank=True,
        verbose_name="Ответ почтового сервера",
    )
    mailing = models.ForeignKey(
        'MailingModel',
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name="Рассылка",
    )

    def __str__(self):
        return f"Попытка #{self.pk} — {self.status}"

    class Meta:
        verbose_name = "Попытка рассылки"
        verbose_name_plural = "Попытки рассылки"
        ordering = ('-attempted_at',)
