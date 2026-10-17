from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(label="Никнейм", max_length=30, required=True)

    class Meta:
        model = CustomUser
        fields = ("email", "first_name", "last_name", "username", "avatar")

    def __init__(self, *args, **kwargs):
        """Форма для регистрации"""
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)

        self.fields["email"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "email@example.com",
            }
        )
        self.fields["email"].help_text = (
            "После регистрации на указанный email будет направлено письмо с подтверждением"
        )

        self.fields["first_name"].widget.attrs.update(
            {
                "class": "form-control",
            }
        )

        self.fields["last_name"].widget.attrs.update(
            {
                "class": "form-control",
            }
        )

        self.fields["username"].widget.attrs.update(
            {
                "class": "form-control",
            }
        )

        self.fields["avatar"].widget.attrs.update({"class": "form-control"})

        self.fields["password1"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Пароль",
            }
        )

        self.fields["password2"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Повторите пароль",
            }
        )
        self.fields["password2"].help_text = ""


class CustomAuthenticationForm(AuthenticationForm):
    """Форма для логина"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Email"
        self.fields["username"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "email@example.com",
                "autofocus": True,
            }
        )
        self.fields["password"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Пароль",
            }
        )
