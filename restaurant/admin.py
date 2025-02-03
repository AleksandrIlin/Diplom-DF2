from django.contrib import admin
from restaurant.models import Reservation, Tables


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'guests', "owner")
    list_filter = ("is_active", 'date')
    search_fields = ('user__username',)


@admin.register(Tables)
class TablesAdmin(admin.ModelAdmin):
    list_display = ('number', 'status',)
