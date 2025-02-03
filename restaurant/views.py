from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError, PermissionDenied
from django.views.generic import TemplateView
from django.views.generic import View
from django.http import HttpResponse
from django.contrib import messages
from django.views.generic import FormView, DeleteView, UpdateView, ListView, DetailView
from django.urls import reverse_lazy
from .forms import ReservationForm
from .models import Tables, Reservation
from django.contrib.auth.mixins import LoginRequiredMixin


class HomePageView(View):
    """Представление главной страницы"""
    template_name = "restaurant/home.html"

    def get(self, request):
        return render(request, self.template_name)


class AboutRestaurantView(View):
    """Представление страницы о ресторане"""
    template_name = "restaurant/about_restaurant.html"

    def get(self, request):
        return render(request, self.template_name)


class ReservationListView(LoginRequiredMixin, ListView):
    """Представление списка всех бронирований"""
    model = Reservation
    form_class = ReservationForm
    template_name = 'restaurant/reservation_list.html'
    context_object_name = "reservation_list"

    def get_queryset(self):
        # Здесь вы можете определить свой queryset
        return Reservation.objects.all()


class ReservationDetailView(LoginRequiredMixin, DetailView):
    """Представление детальной информации о бронировании"""
    model = Reservation
    template_name = 'restaurant/reservation_detail.html'
    context_object_name = "reservation_detail"

    def get(self, request, id):
        reservation = get_object_or_404(Reservation, id=id)
        return render(request, 'restaurant/reservation_detail.html', {'reservation': reservation})


class ReservationView(FormView):
    """Представление бронирования стола"""
    template_name = 'restaurant/reservation.html'
    form_class = ReservationForm

    def form_valid(self, form):
        table = form.cleaned_data['table']
        date = form.cleaned_data['date']
        time = form.cleaned_data['time']

        # Создаем объект Reservation для проверки доступности стола
        reservation = Reservation(
            table=table,
            date=date,
            time=time,
            guests=form.cleaned_data['guests'],
            name=form.cleaned_data['name'],
            email=form.cleaned_data['email'],
            phone=form.cleaned_data['phone']
        )

        # Проверяем доступность стола
        if not reservation.is_table_available():
            messages.error(self.request, 'К сожалению, этот стол уже забронирован на выбранное время. '
                                         'Пожалуйста, выберите другой стол или время.')
            return self.form_invalid(form)

        try:
            reservation.owner = self.request.user  # Привязываем текущего пользователя как владельца
            reservation.save()  # Сохраняем в БД
            messages.success(self.request, 'Ваша бронь успешно создана!')
            return redirect('restaurant:confirm_reservation', reservation_id=reservation.id)
        except ValidationError as e:
            messages.error(self.request, 'Ошибка: ' + str(e))
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Произошла ошибка с вашей бронью. Пожалуйста, исправьте ошибки ниже.')
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["available_tables"] = Tables.objects.filter(status="available")
        context["all_tables"] = Tables.objects.all()  # Добавляем все столы
        return context


class ConfirmReservationView(TemplateView):
    """Представление подтверждения бронирования"""
    template_name = 'restaurant/confirm_reservation.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reservation_id = self.kwargs.get('reservation_id')

        try:
            context['reservation_data'] = Reservation.objects.get(id=reservation_id)
        except Reservation.DoesNotExist:
            context['reservation_data'] = None

        return context

    def post(self, request, *args, **kwargs):
        reservation_id = self.kwargs.get('reservation_id')
        try:
            reservation = Reservation.objects.get(id=reservation_id)
            reservation.status = 'confirmed'

            # Проверяем доступность стола перед сохранением
            if not reservation.is_table_available():
                messages.error(request, 'Стол уже забронирован на это время.')
                return redirect('restaurant:home')

            reservation.save()
            messages.success(request, 'Ваше бронирование подтверждено!')
            return redirect('restaurant:home')
        except Reservation.DoesNotExist:
            messages.error(request, 'Бронирование не найдено.')
            return redirect('restaurant:home')


class CancelReservationView(LoginRequiredMixin, DeleteView):
    """Представление отмены брони"""
    model = Reservation
    template_name = 'restaurant/confirm_reservation_delete.html'  # Укажите путь к вашему шаблону, если нужен

    def get_object(self, queryset=None):
        # Получите объект по первичному ключу (pk)
        return super().get_object(queryset)

    def get_success_url(self):
        # Используйте правильное имя поля owner
        user_id = self.object.owner.id if self.object.owner else None  # Проверяем, есть ли владелец
        self.object.table.status = "available"
        self.object.table.save()
        return reverse_lazy('users:user_profile', kwargs={'pk': user_id}) if user_id else reverse_lazy(
            'default_redirect_url')


class ReservationDeleteView(DeleteView):

    model = Reservation
    template_name = 'restaurant/reservation_delete.html'  # Убедитесь, что этот шаблон существует
    success_url = reverse_lazy('restaurant:reservation_list')

    def get_object(self, queryset=None):
        # Получите объект по первичному ключу (pk)
        return super().get_object(queryset)


class ReservationUpdateView(UpdateView, LoginRequiredMixin):
    """Представление редактирование бронирования"""
    model = Reservation
    form_class = ReservationForm
    template_name = 'restaurant/reservation.html'
    success_url = reverse_lazy("users:user_profile")

    def form_valid(self, form):
        try:
            form.save()
            return super().form_valid(form)
        except ValidationError as e:
            form.add_error(None, e)  # Добавляем ошибку в форму
            return self.form_invalid(form)


class ContactsView(View):
    """Представление контактов и обратной связи"""
    @staticmethod
    def get(request):
        return render(request, 'restaurant/contacts.html')

    @staticmethod
    def post(request):
        name = request.POST.get('name')
        massage = request.POST.get('massage')
        return HttpResponse(f"Спасибо, {name}. Сообщение получено.")


class UpdateReservationStatusView(View):
    def post(self, request, reservation_id):
        reservation = get_object_or_404(Reservation, id=reservation_id)
        new_status = request.POST.get('status')

        # Получаем список доступных статусов
        valid_statuses = [status[0] for status in Reservation.STATUS_CHOICES]

        if new_status in valid_statuses:
            reservation.status = new_status
            reservation.save()

        return redirect('restaurant:reservation_list')
