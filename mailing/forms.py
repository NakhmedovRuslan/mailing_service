from django import forms

from .models import MailingModel, Message, Recipient


class MailingForm(forms.ModelForm):
    """Настройка формы "новая рассылка" """

    class Meta:
        model = MailingModel
        fields = ["start_time", "end_time", "message", "recipients"]
        widgets = {
            "start_time": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"},
                format="%Y-%m-%dT%H:%M",
            ),
            "end_time": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"},
                format="%Y-%m-%dT%H:%M",
            ),
            "message": forms.Select(attrs={"class": "form-select"}),
            "recipients": forms.SelectMultiple(
                attrs={"class": "form-select", "size": 8}
            ),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.fields["start_time"].input_formats = ["%Y-%m-%dT%H:%M"]
        self.fields["end_time"].input_formats = ["%Y-%m-%dT%H:%M"]

        if user:
            self.fields["message"].queryset = Message.objects.filter(owner=user)
            self.fields["recipients"].queryset = Recipient.objects.filter(owner=user)


class MessageForm(forms.ModelForm):
    """Настройка формы "новое сообщение" """

    class Meta:
        model = Message
        fields = ["message_title", "message_text"]
        widgets = {
            "message_title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Тема сообщения",
                }
            ),
            "message_text": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 6,
                    "placeholder": "Текст сообщения",
                }
            ),
        }
        labels = {
            "message_title": "Тема",
            "message_text": "Текст сообщения",
        }


class RecipientForm(forms.ModelForm):
    """Настройка формы "новый получатель" """

    class Meta:
        model = Recipient
        fields = ["email", "full_name", "comments"]
        widgets = {
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "user@example.com",
                }
            ),
            "full_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Иванов Иван Иванович",
                }
            ),
            "comments": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Необязательный комментарий",
                }
            ),
        }
        labels = {
            "email": "Email",
            "full_name": "Ф.И.О.",
            "comments": "Комментарий",
        }
