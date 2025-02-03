import random
import string

from config.settings import EMAIL_HOST_USER
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView

from restaurant.models import Reservation
from users.forms import RegisterUserCreationForm
from users.models import CustomUser


class RegisterView(CreateView):
    """Представление регистрации пользователя"""
    form_class = RegisterUserCreationForm
    template_name = "users/register.html"
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        user = form.save(commit=False)  # Не сохраняем в БД сразу
        user.is_active = False
        user.set_password(form.cleaned_data['password'])
        user = form.save()
        login(self.request, user)
        self.send_welcome_email(user.email)
        return super().form_valid(form)

    def send_welcome_email(self, user_email):
        subject = "Добро пожаловать в наш сервис"
        activation_link = f"http://127.0.0.1:8000/users/confirm-email/{user_email}/"
        message = (
            f"Спасибо, что зарегистрировались в нашем сервисе!\n\n "
            f"Пожалуйста, подтвердите ваш адрес электронной почты, перейдя по следующей ссылке:\n "
            f"{activation_link}\n\n "
            f"Мы рады видеть вас среди наших пользователей."
        )
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [user_email]
        send_mail(subject, message, from_email, recipient_list)


class ConfirmEmailView(View):
    """Представление подтверждения почты"""
    def get(self, request, user_email):
        user = get_object_or_404(CustomUser, email=user_email)
        activation_link = f"http://127.0.0.1:8000/users/login/"
        if user.is_active:
            return HttpResponse("Ваш адрес электронной почты уже подтвержден!")

        user.is_active = True
        user.save()
        messages.success(request, "Ваш адрес электронной почты был успешно подтвержден! Вы можете войти.")
        return HttpResponseRedirect(reverse('users:login'))


class UserListView(ListView):
    """Представление вывода всех пользователей"""
    model = CustomUser
    template_name = "users/user_list.html"
    context_object_name = "user_list"

    def get_queryset(self):
        return CustomUser.objects.all()




class UserDetailView(DetailView):
    """Представление детальной информации о пользователе"""
    model = CustomUser
    template_name = "users/user_profile.html"
    context_object_name = "user_profile"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object  # Получаем текущего пользователя
        reservations = Reservation.objects.filter(owner=user)  # Получаем бронирования для этого пользователя
        context["reservations"] = reservations

        print(f":User  {user.username}, Reservations Count: {reservations.count()}")

        return context


class BlockUserView(LoginRequiredMixin, View):
    """Представление блокировки пользователя"""
    def get(self, request, user_id):
        user = get_object_or_404(CustomUser, id=user_id)
        return render(request, "users/user_block.html", {"user": user})

    def post(self, request, user_id):
        user = get_object_or_404(CustomUser, id=user_id)

        if not request.user.has_perm("users.can_block_users"):
            return HttpResponseForbidden("У вас нет прав для блокировки рассылки.")

        is_blocked = request.POST.get("is_blocked")
        user.is_blocked = is_blocked == "on"
        user.save()
        return redirect("users:user_list")


class PasswordResetView(View):
    """Представление сброса пароля пользователя"""
    def get(self, request):
        return render(request, "users/password_reset.html")

    def post(self, request):
        email = request.POST.get("email")
        try:
            user = CustomUser.objects.get(email=email)
            new_password = "".join(random.choices(string.ascii_letters + string.digits, k=8))
            user.password = make_password(new_password)
            user.save()
            send_mail(
                subject="Ваш новый пароль",
                message=f"Здравствуйте!\nВаш новый пароль: {new_password}",
                from_email=EMAIL_HOST_USER,
                recipient_list=[user.email],
            )
            messages.success(request, "Новый пароль отправлен на ваш email.")
            return redirect("users:login")
        except CustomUser.DoesNotExist:
            messages.error(request, "Пользователь с таким email не найден.")
            return render(request, "users/password_reset.html")


class ChangePasswordView(LoginRequiredMixin, View):
    """Представление смены пароля пользователя"""
    def get(self, request):
        form = PasswordChangeForm(user=request.user)
        return render(request, "users/change_password.html", {"form": form})

    def post(self, request):
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)

            send_mail(
                subject="Ваш пароль был изменен",
                message=f"Здравствуйте, {user.username}!\n\nВаш пароль был успешно изменен.",
                from_email=EMAIL_HOST_USER,
                recipient_list=[user.email],
            )

            messages.success(request, "Ваш пароль был успешно изменен!")
            return redirect("users:change_password")

        messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
        return render(request, "users/change_password.html", {"form": form})


