from django import forms
from users.models import CustomUser


class RegisterUserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirmation = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirmation = cleaned_data.get("password_confirmation")

        if password and password_confirmation and password != password_confirmation:
            raise forms.ValidationError("Пароли не совпадают.")

    class Meta:
        model = CustomUser
        fields = (
            "email",
            "username",
            "avatar",
            "first_name",
            "phone_number",
            "password",
            "password_confirmation",
            "country",
        )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        first_name = cleaned_data.get("first_name")

        if username.lower() and first_name.lower() in [
            "казино",
            "криптовалюта",
            "крипта",
            "биржа",
            "дешево",
            "бесплатно",
            "обман",
            "полиция",
            "радар",
        ]:
            self.add_error("username", "запрещенное слово")
            self.add_error("first_name", "запрещенное слово")

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        if phone_number and not phone_number.isdigit():
            raise forms.ValidationError("Номер телефона должен состоять только из цифр")
        return phone_number

    def clean_avatar(self):
        cleaned_data = super().clean()
        avatar = cleaned_data.get("image")

        if avatar is None:
            return None

        if avatar.size > 5 * 1024 * 1024:
            raise forms.ValidationError("Размер файла не должен превышать 5MB.")

        if not avatar.name.endswith(("jpg", "jpeg", "png")):
            raise forms.ValidationError(
                "Формат файла не соответствует требованиям. " "Формат файла должен быть *.jpg, *.jpeg, *.png"
            )

        return avatar


class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            "email",
            "username",
            "avatar",
            "first_name",
            "phone_number",
            "country",
        ]
        exclude = (
            "is_blocked",
            "owner",
        )
