import secrets

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView
from django.views.generic.base import View
from dotenv import load_dotenv

from config import settings

from .models import CustomUser

load_dotenv(override=True)

from django.core.mail import send_mail
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import CreateView

from .forms import CustomAuthenticationForm, CustomUserCreationForm


class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "users/register.html"
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        user = form.save()
        user.is_active = False
        token = secrets.token_hex(16)
        user.token = token
        user.save()
        host = self.request.get_host()
        url = f"http://{host}/users/confirm_email/{token}/"
        send_mail(
            subject="[СЕРВИС РАССЫЛОК] Подтвердите ваш аккаунт!",
            message=f"""Спасибо за регистрацию в сервисе рассылок. Для продолжения работы в сервисе 
            подтвердите свой аккаунт перейдя по ссылке {url}""",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )
        return super().form_valid(form)


def email_verification(request, token):
    user = get_object_or_404(CustomUser, token=token)
    user.is_active = True
    user.save()
    return redirect(reverse("users:login"))


class CustomLoginView(LoginView):
    template_name = "users/login.html"
    authentication_form = CustomAuthenticationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy("mailing:index")


class UserListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = CustomUser
    template_name = "users/user_list.html"
    context_object_name = "users"
    permission_required = "users.can_view_users"
    raise_exception = True


class UserBlockView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "users.can_block_users"
    raise_exception = True

    def post(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        if user == request.user or user.is_superuser:
            messages.error(request, "Нельзя заблокировать этого пользователя.")
            return redirect("users:user_list")
        user.is_active = not user.is_active
        user.save()
        return redirect("users:user_list")
