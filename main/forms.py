from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import re

User = get_user_model()

class UserRegisterForm(UserCreationForm):
    phone_number = forms.CharField(label="Номер телефона", widget=forms.TextInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(label="Имя", widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label="Фамилия", widget=forms.TextInput(attrs={'class': 'form-control'}))
    birth_date = forms.DateField(label="Дата рождения", widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label="Подтверждение пароля", widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['phone_number', 'first_name', 'last_name', 'birth_date', 'email', 'password1', 'password2']
        error_messages = {
            'email': {
                'invalid': 'Введите корректный email.',
                'required': 'Email обязателен.',
            },
            'password1': {
                'required': 'Введите пароль.',
            },
            'password2': {
                'required': 'Повторите пароль.',
            },
        }

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if not re.fullmatch(r'8\d{10}', phone):
            raise ValidationError("Некорректный номер.")
        if User.objects.filter(phone_number=phone).exists():
            raise ValidationError("Номер уже зарегистрирован.")
        return phone

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not re.fullmatch(r'[^@]+@[^@]+\.[^@]+', email):
            raise ValidationError("Введите корректный email.")
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email уже используется.")
        return email

    def clean_password1(self):
        password = self.cleaned_data.get('password1')

        if len(password) < 8:
            raise ValidationError("Пароль должен быть не менее 8 символов.")

        if not re.fullmatch(r'[A-Za-z0-9]+', password):
            raise ValidationError("Пароль должен содержать только латиницу и цифры.")

        return password

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(label="Номер телефона", widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class ProfileUpdateForm(forms.ModelForm):
    birth_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False,
        label='Дата рождения'
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'birth_date']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
        }
