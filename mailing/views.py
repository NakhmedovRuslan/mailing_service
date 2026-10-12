from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView
from django.urls import reverse_lazy
from .models import MailingModel, Recipient, Message, Attempt
from .services import send_mailing, MailingNotAllowedError


################ ГЛАВНАЯ ################

class IndexView(TemplateView):
    template_name = "mailing/index.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        data["total_mailings"] = MailingModel.objects.count()
        data["active_mailings"] = MailingModel.objects.filter(
            status=MailingModel.STATUS_STARTED
        ).count()
        data["total_recipients"] = Recipient.objects.count()

        return data

################ МОДЕЛЬ ПОЛУЧАТЕЛЬ РАССЫЛКИ (Recipient) ##################

class RecipientListView(LoginRequiredMixin, ListView):
    model = Recipient
    template_name = "mailing/recipient_list.html"
    context_object_name = "recipient_list"
    ordering = ("-id",)

class RecipientDetailView(LoginRequiredMixin, DetailView):
    model = Recipient
    template_name = "mailing/recipient_detail.html"
    context_object_name = "recipient"


class RecipientCreateView(LoginRequiredMixin, CreateView):
    model = Recipient
    template_name = "mailing/recipient_form.html"
    fields = ["email", "full_name", "comments"]
    context_object_name = "recipient_form"
    success_url = reverse_lazy("mailing:recipient_list")


class RecipientUpdateView(LoginRequiredMixin, UpdateView):
    model = Recipient
    template_name = "mailing/recipient_form.html"
    fields = ["email", "full_name", "comments"]

    def get_success_url(self):
        return reverse_lazy("mailing:recipient_detail", args=[self.kwargs["pk"]])


class RecipientDeleteView(LoginRequiredMixin, DeleteView):
    model = Recipient
    template_name = "mailing/recipient_confirm_delete.html"
    success_url = reverse_lazy("mailing:recipient_list")


################ МОДЕЛЬ СООБЩЕНИЯ (Message) ##################

class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = "mailing/message_list.html"
    context_object_name = "message_list"


class MessageDetailView(LoginRequiredMixin, DetailView):
    model = Message
    template_name = "mailing/message_detail.html"
    context_object_name = "message"


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    template_name = "mailing/message_form.html"
    fields = ["message_title", "message_text"]
    context_object_name = "message_form"
    success_url = reverse_lazy("mailing:message_list")


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    template_name = "mailing/message_form.html"
    fields = ["message_title", "message_text"]

    def get_success_url(self):
        return reverse_lazy("mailing:message_detail", args=[self.object.pk])


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    template_name = "mailing/message_confirm_delete.html"
    success_url = reverse_lazy("mailing:message_list")


################ МОДЕЛЬ РАССЫЛКА (MailingModel) ##################


class MailingListView(LoginRequiredMixin, ListView):
    model = MailingModel
    template_name = "mailing/mailing_list.html"
    context_object_name = "mailing_list"
    ordering = ("-id",)


class MailingDetailView(LoginRequiredMixin, DetailView):
    model = MailingModel
    template_name = "mailing/mailing_detail.html"
    context_object_name = "mailing"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()
        return obj

class MailingCreateView(LoginRequiredMixin, CreateView):
    model = MailingModel
    template_name = "mailing/mailing_form.html"
    fields = ["start_time", "end_time", "message", "recipients"]
    success_url = reverse_lazy("mailing:mailing_list")


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = MailingModel
    template_name = "mailing/mailing_form.html"
    fields = ["start_time", "end_time", "message", "recipients"]
    success_url = reverse_lazy("mailing:mailing_list")


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = MailingModel
    template_name = "mailing/mailing_confirm_delete.html"
    success_url = reverse_lazy("mailing:mailing_list")

class MailingSendView(LoginRequiredMixin, View):
    def post(self, request, pk):
        mailing = get_object_or_404(MailingModel, pk=pk)
        try:
            send_mailing(mailing)
        except MailingNotAllowedError as exc:
            messages.error(request, str(exc))
        else:
            messages.success(request, f"Рассылка №{mailing.pk} запущена.")
        return redirect("mailing:mailing_detail", pk=mailing.pk)

################ МОДЕЛЬ ПОПЫТКА ОТПРАВКИ (Attempt) ##################

class AttemptListView(LoginRequiredMixin, ListView):
    model = Attempt
    template_name = "mailing/attempt_list.html"
    context_object_name = "attempt_list"
    ordering = ("-attempted_at",)
    paginate_by = 50


class AttemptDetailView(LoginRequiredMixin, DetailView):
    model = Attempt
    template_name = "mailing/attempt_detail.html"
    context_object_name = "attempt"