from django.contrib import admin


from mailing.models import Recipient, Message, MailingModel, Attempt


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'comments')
    search_fields = ('email', 'full_name')
    ordering = ('email',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('message_title', 'message_text')
    search_fields = ('message_title',)


@admin.register(MailingModel)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'start_time', 'end_time', 'message')
    list_filter = ('status',)
    search_fields = ('message__message_title',)


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ('id', 'mailing', 'status', 'attempted_at')
    list_filter = ('status',)
    search_fields = ('mailing__id', 'server_response')
    readonly_fields = ('attempted_at',)



