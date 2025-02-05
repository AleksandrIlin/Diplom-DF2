from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta
from users.models import CustomUser


class Tables(models.Model):
    """Модель столов"""

    STATUS_CHOICES = [
        ("available", "Свободен"),
        ("reserved", "Зарезервирован"),
    ]

    number = models.CharField(max_length=10, verbose_name="Номер стола")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="available", verbose_name="Статус")
    capacity = models.IntegerField(verbose_name="Вместимость", help_text="Введите максимальное количество гостей")

    def __str__(self):
        return f"Стол {self.number} - {self.get_status_display()} (вместимость: {self.capacity})"

    class Meta:
        verbose_name = "Стол"
        verbose_name_plural = "Столы"
        ordering = ["status", "number"]


class Reservation(models.Model):
    """Модель бронирования"""

    STATUS_CHOICES = [
        ("Сonfirm", "Подтверждено"),
        ("Reserved", "В ожидании"),
        ('Canceled', 'Отменено'),
    ]

    owner = models.ForeignKey(
        CustomUser,
        verbose_name="Владелец",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    name = models.CharField(max_length=100, verbose_name='Имя пользователя', help_text="Введите имя")
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    date = models.DateField()
    time = models.TimeField(verbose_name='Время бронирования')
    guests = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    table = models.ForeignKey(Tables, on_delete=models.CASCADE, verbose_name="Стол", related_name="reservations")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Reserved")

    def __str__(self):
        return f"Бронирование от {self.name} на {self.date} в {self.time} на {self.guests} гостей"

    def is_table_available(self):
        return not Reservation.objects.filter(
            table=self.table,
            date=self.date,
            time=self.time
        ).exists()

    class Meta:
        verbose_name = "Резервирование"
        verbose_name_plural = "Резервирования"
        ordering = ["guests", "date"]
        permissions = [
            ("can_view_all_reservation", "can view all reservation"),
            ("can_view_reservations", "Can view reservations"),
        ]
