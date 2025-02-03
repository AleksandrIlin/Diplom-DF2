from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from users.apps import UsersConfig
from users.views import (
    BlockUserView,
    ChangePasswordView,
    ConfirmEmailView,
    PasswordResetView,
    RegisterView,
    UserDetailView,
    UserListView,
)

app_name = UsersConfig.name

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(template_name="users/login.html"), name="login"),
    path("logout/", LogoutView.as_view(next_page="restaurant:home"), name="logout"),
    path(
        "confirm-email/<str:user_email>/",
        ConfirmEmailView.as_view(),
        name="confirm_email",
    ),
    path("user_list/", UserListView.as_view(), name="user_list"),
    path("user_block/<int:user_id>", BlockUserView.as_view(), name="user_block"),
    path("password_reset/", PasswordResetView.as_view(), name="password_reset"),
    path("change-password/", ChangePasswordView.as_view(), name="change_password"),
    path("profile/<int:pk>", UserDetailView.as_view(), name="user_profile"),
]
