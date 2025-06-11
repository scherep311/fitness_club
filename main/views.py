from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date, datetime
import re
from .forms import UserRegisterForm, UserLoginForm, ProfileUpdateForm
from subscriptions.models import Subscription
from workouts.models import UserWorkout
from subscriptions.utils import get_date_for_weekday, get_actual_frozen_days_left


def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Регистрация прошла успешно!")
            return redirect('home')
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
    else:
        form = UserRegisterForm()
    return render(request, 'main/register.html', {'form': form})


class CustomLoginView(LoginView):
    template_name = 'main/login.html'
    authentication_form = UserLoginForm
    redirect_authenticated_user = True

    def form_invalid(self, form):
        messages.error(self.request, "Неправильный номер телефона или пароль.")
        return super().form_invalid(form)


@login_required
def home_view(request):
    user = request.user
    subscription = Subscription.objects.filter(id_user=user).order_by('-start_date').first()

    remaining_days = None
    frozen_days_left = None

    if subscription:
        if subscription.is_frozen:
            frozen_days_left = get_actual_frozen_days_left(subscription)
            remaining_days = subscription.remaining_days_at_freeze
        else:
            remaining_days = max((subscription.end_date - date.today()).days, 0)
            frozen_days_left = subscription.frozen_days_left

    # Тренировки
    upcoming_workouts = []
    user_workouts = UserWorkout.objects.select_related('id_workout', 'id_workout__id_trainer') \
        .filter(id_user=user, status='active')

    now_time = datetime.now()
    for uw in user_workouts:
        workout_date = uw.workout_date
        workout_datetime = datetime.combine(workout_date, uw.id_workout.start_time)
        if workout_datetime >= now_time:
            upcoming_workouts.append({
                'type': uw.id_workout.type,
                'trainer': uw.id_workout.id_trainer.fullname,
                'start': uw.id_workout.start_time.strftime("%H:%M"),
                'end': uw.id_workout.end_time.strftime("%H:%M"),
                'date': workout_date,
            })

    upcoming_workouts = sorted(upcoming_workouts, key=lambda w: (w['date'], w['start']))

    return render(request, 'main/home.html', {
        'subscription': subscription,
        'upcoming_workouts': upcoming_workouts,
        'frozen_days_left': frozen_days_left,
        'remaining_days': remaining_days
    })


def about_view(request):
    services = [
        "Личный тренер", "Индивидуальные программы", "Коррекция питания",
        "Фитнес тестирование", "Солярии", "Фитнес-бар", "Полотенца и шкафчики",
        "Тренажерный зал", "Бокс"
    ]
    return render(request, 'main/about.html', {'services': services})


@login_required
def profile_settings_view(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Изменения успешно сохранены.')
            return redirect('profile_settings')
        else:
            messages.error(request, 'Ошибка при сохранении профиля.')
    else:
        form = ProfileUpdateForm(instance=user)
    return render(request, 'main/settings.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "Вы вышли из аккаунта.")
    return redirect('login')
