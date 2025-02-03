from django.core.management import BaseCommand

from users.models import CustomUser


class Command(BaseCommand):
    """Кастомная команда для создания администратора сервера"""
    def handle(self, *args, **options):
        user = CustomUser.objects.create(email="admin@example.com")
        user.set_password("12345")
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save()

