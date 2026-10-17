from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_control, cache_page
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from .forms import MailingForm, MessageForm, RecipientForm
from .models import Attempt, MailingModel, Message, Recipient
from .services import MailingNotAllowedError, send_mailing

################ КОНТРОЛЛЕР ГЛАВНАЯ ################


@method_decorator(cache_control(max_age=60), name="dispatch")
class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "mailing/index.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        data["total_mailings"] = MailingModel.objects.filter().count()
        data["active_mailings"] = MailingModel.objects.filter(
            status=MailingModel.STATUS_STARTED
        ).count()
        data["total_recipients"] = Recipient.objects.filter().count()

        return data


################ КОНТРОЛЛЕР ПОЛУЧАТЕЛЬ РАССЫЛКИ (Recipient) ##################


class RecipientListView(LoginRequiredMixin, ListView):
    model = Recipient
    template_name = "mailing/recipient_list.html"
    context_object_name = "recipient_list"
    ordering = ("-id",)

    def get_queryset(self):
        user = self.request.user
        if user.has_perm("mailing.can_view_all_recipients"):
            return Recipient.objects.all()
        return Recipient.objects.filter(owner=user)


class RecipientDetailView(LoginRequiredMixin, DetailView):
    model = Recipient
    template_name = "mailing/recipient_detail.html"
    context_object_name = "recipient"

    def get_queryset(self):
        user = self.request.user
        if user.has_perm("mailing.can_view_all_recipients"):
            return Recipient.objects.all()
        return Recipient.objects.filter(owner=user)


class RecipientCreateView(LoginRequiredMixin, CreateView):
    model = Recipient
    template_name = "mailing/recipient_form.html"
    form_class = RecipientForm
    context_object_name = "recipient_form"
    success_url = reverse_lazy("mailing:recipient_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class RecipientUpdateView(LoginRequiredMixin, UpdateView):
    model = Recipient
    template_name = "mailing/recipient_form.html"
    form_class = RecipientForm

    def get_success_url(self):
        return reverse_lazy("mailing:recipient_detail", args=[self.kwargs["pk"]])

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Recipient.objects.all()
        return Recipient.objects.filter(owner=user)


class RecipientDeleteView(LoginRequiredMixin, DeleteView):
    model = Recipient
    template_name = "mailing/recipient_confirm_delete.html"
    success_url = reverse_lazy("mailing:recipient_list")

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Recipient.objects.all()
        return Recipient.objects.filter(owner=user)


################ КОНТРОЛЛЕР СООБЩЕНИЯ (Message) ##################


class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = "mailing/message_list.html"
    context_object_name = "message_list"

    def get_queryset(self):
        user = self.request.user
        if user.has_perm("mailing.can_view_all_messages"):
            return Message.objects.all()
        return Message.objects.filter(owner=user)


class MessageDetailView(LoginRequiredMixin, DetailView):
    model = Message
    template_name = "mailing/message_detail.html"
    context_object_name = "message"

    def get_queryset(self):
        user = self.request.user
        if user.has_perm("mailing.can_view_all_messages"):
            return Message.objects.all()
        return Message.objects.filter(owner=user)


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    template_name = "mailing/message_form.html"
    form_class = MessageForm
    context_object_name = "message_form"
    success_url = reverse_lazy("mailing:message_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    template_name = "mailing/message_form.html"
    form_class = MessageForm

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Message.objects.all()
        return Message.objects.filter(owner=user)

    def get_success_url(self):
        return reverse_lazy("mailing:message_detail", args=[self.object.pk])


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    template_name = "mailing/message_confirm_delete.html"
    success_url = reverse_lazy("mailing:message_list")

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Message.objects.all()
        return Message.objects.filter(owner=user)


################ КОНТРОЛЛЕР РАССЫЛКА (MailingModel) ##################


class MailingListView(LoginRequiredMixin, ListView):
    model = MailingModel
    template_name = "mailing/mailing_list.html"
    context_object_name = "mailing_list"
    ordering = ("-id",)

    def get_queryset(self):
        user = self.request.user
        if user.has_perm("mailing.can_view_all_mailings"):
            return MailingModel.objects.all()
        return MailingModel.objects.filter(owner=user)


class MailingDetailView(LoginRequiredMixin, DetailView):
    model = MailingModel
    template_name = "mailing/mailing_detail.html"
    context_object_name = "mailing"

    def get_queryset(self):
        user = self.request.user
        if user.has_perm("mailing.can_view_all_mailings"):
            return MailingModel.objects.all()
        return MailingModel.objects.filter(owner=user)

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()
        return obj


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = MailingModel
    template_name = "mailing/mailing_form.html"
    form_class = MailingForm
    success_url = reverse_lazy("mailing:mailing_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = MailingModel
    template_name = "mailing/mailing_form.html"
    form_class = MailingForm
    success_url = reverse_lazy("mailing:mailing_list")

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return MailingModel.objects.all()
        return MailingModel.objects.filter(owner=user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = MailingModel
    template_name = "mailing/mailing_confirm_delete.html"
    success_url = reverse_lazy("mailing:mailing_list")

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return MailingModel.objects.all()
        return MailingModel.objects.filter(owner=user)


class MailingSendView(LoginRequiredMixin, View):
    def post(self, request, pk):
        if request.user.is_superuser:
            mailing = get_object_or_404(MailingModel, pk=pk)
        else:
            mailing = get_object_or_404(MailingModel, pk=pk, owner=request.user)
        try:
            if mailing.is_disabled:
                raise MailingNotAllowedError("Рассылка отключена менеджером")
            send_mailing(mailing)
        except MailingNotAllowedError as exc:
            messages.error(request, str(exc))
        else:
            messages.success(request, f"Рассылка №{mailing.pk} запущена.")
        return redirect("mailing:mailing_detail", pk=mailing.pk)


class MailingDisableView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "mailing.can_disable_mailing"
    raise_exception = True

    def post(self, request, pk):
        mailing = get_object_or_404(MailingModel, pk=pk)
        mailing.is_disabled = True
        mailing.save()
        return redirect("mailing:mailing_list")


################ КОНТРОЛЛЕР ПОПЫТКА ОТПРАВКИ (Attempt) ##################


class AttemptListView(LoginRequiredMixin, ListView):
    model = Attempt
    template_name = "mailing/attempt_list.html"
    context_object_name = "attempt_list"
    ordering = ("-attempted_at",)

    def get_queryset(self):
        user = self.request.user
        if user.has_perm("mailing.can_view_all_mailings"):
            return Attempt.objects.all()
        return Attempt.objects.filter(mailing__owner=user)


class AttemptDetailView(LoginRequiredMixin, DetailView):
    model = Attempt
    template_name = "mailing/attempt_detail.html"
    context_object_name = "attempt"

    def get_queryset(self):
        user = self.request.user
        if user.has_perm("mailing.can_view_all_mailings"):
            return Attempt.objects.all()
        return Attempt.objects.filter(mailing__owner=user)


################ КОНТРОЛЛЕР СТАТИСТИКА ##################


@method_decorator(cache_page(60), name="dispatch")
class StatisticsView(LoginRequiredMixin, TemplateView):
    template_name = "mailing/statistics.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        if self.request.user.is_superuser or self.request.user.has_perm(
            "mailing.can_view_all_mailings"
        ):
            mailings = MailingModel.objects.all()
            attempts = Attempt.objects.all()
        else:
            mailings = MailingModel.objects.filter(owner=self.request.user)
            attempts = Attempt.objects.filter(mailing__owner=self.request.user)

        data["total_mailings"] = mailings.count()
        data["success"] = attempts.filter(status=Attempt.STATUS_SUCCESS).count()
        data["failed"] = attempts.filter(status=Attempt.STATUS_FAILED).count()

        return data
