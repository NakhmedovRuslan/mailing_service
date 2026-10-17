from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = "Создание группы"

    def handle(self, *args, **options):
        Group.objects.get_or_create(name="Менеджер")

        self.stdout.write(self.style.SUCCESS("Группа создана"))
