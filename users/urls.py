from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from django.urls import path, reverse_lazy

from users.apps import UsersConfig
from users.views import CustomLoginView, RegisterView, email_verification

from . import views

app_name = UsersConfig.name

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path(
        "login/",
        CustomLoginView.as_view(template_name="users/login.html"),
        name="login",
    ),
    path("logout/", LogoutView.as_view(next_page="mailing:index"), name="logout"),
    path("confirm_email/<str:token>/", email_verification, name="confirm_email"),
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="registration/password_reset_form.html",
            email_template_name="registration/password_reset_email.html",
            subject_template_name="registration/password_reset_subject.txt",
            success_url=reverse_lazy("users:password_reset_done"),
        ),
        name="password_reset",
    ),

    # Сообщение об отправке письма
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="registration/password_reset_done.html"
        ),
        name="password_reset_done",
    ),

    # Установка нового пароля
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm.html",
            success_url=reverse_lazy("users:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),

    # Успешная смена пароля
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path("", views.UserListView.as_view(), name="user_list"),
    path("<int:pk>/block/", views.UserBlockView.as_view(), name="user_block"),
]
