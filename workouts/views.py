from django.shortcuts import render, get_object_or_404, redirect
from datetime import datetime, date, timedelta
from django.contrib.auth.decorators import login_required
from .models import Workout, UserWorkout, Trainer
from subscriptions.models import Subscription
from subscriptions.utils import is_subscription_active
from django.contrib import messages

@login_required
def schedule_view(request):
    subscription = Subscription.objects.filter(id_user=request.user).order_by('-start_date').first()
    if not subscription:
        messages.error(request, 'У вас нет абонемента.')
        return redirect('subscription_list')

    week_offset = int(request.GET.get('week', 0))
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)

    WEEKDAY_SHORT = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    weekdays = [{
        'index': i,
        'name': WEEKDAY_SHORT[i],
        'date': start_of_week + timedelta(days=i),
    } for i in range(7)]

    selected_day = int(request.GET.get('day', today.weekday()))
    actual_date = start_of_week + timedelta(days=selected_day)

    workouts = Workout.objects.filter(weekday=selected_day).select_related('id_trainer').order_by('start_time')

    # Получаем ID тренировок, на которые пользователь записан именно на выбранную дату
    user_workout_ids_for_day = set(
        UserWorkout.objects.filter(
            id_user=request.user,
            status='active',
            workout_date=actual_date
        ).values_list('id_workout_id', flat=True)
    )

    favorites = UserWorkout.objects.select_related('id_workout', 'id_workout__id_trainer') \
        .filter(id_user=request.user, is_favorite=True)
    favorite_workout_ids = set(fav.id_workout.id for fav in favorites)

    # Формируем список моих тренировок с датами для таба "Мои записи"
    my_user_workouts_raw = UserWorkout.objects.select_related('id_workout', 'id_workout__id_trainer') \
        .filter(id_user=request.user, status='active').order_by('workout_date', 'id_workout__start_time')

    my_workouts = []
    now_time = datetime.now()

    for record in my_user_workouts_raw:
        w = record.id_workout
        date_of = record.workout_date
        dt = datetime.combine(date_of, w.start_time)
        if dt >= now_time:
            my_workouts.append({
                'id': record.id,
                'type': w.type,
                'trainer': w.id_trainer.fullname,
                'date': date_of,
                'start': w.start_time,
                'end': w.end_time,
            })

    for w in workouts:
        w.active_count = w.registrations.filter(status='active').count()
        w.free_spots = w.max_participation - w.active_count
        dt = datetime.combine(actual_date, w.end_time)
        w.is_future = dt > datetime.now()

    return render(request, 'workouts/schedule.html', {
        'weekdays': weekdays,
        'selected_day': selected_day,
        'actual_date': actual_date,
        'workouts': workouts,
        'subscription': subscription,
        'my_workouts': my_workouts,
        'favorites': favorites,
        'week_offset': week_offset,
        'favorite_workout_ids': favorite_workout_ids,
        'user_workout_ids_for_day': user_workout_ids_for_day,
    })


@login_required
def register_workout_view(request, workout_id):
    subscription = Subscription.objects.filter(id_user=request.user).order_by('-start_date').first()
    if not is_subscription_active(subscription):
        messages.error(request, 'Вы не можете записаться без активного абонемента.')
        return redirect('schedule')

    workout = get_object_or_404(Workout, id=workout_id)

    week_offset = int(request.POST.get('week', 0))
    day = int(request.POST.get('day', workout.weekday))

    today = date.today()
    start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
    workout_date = start_of_week + timedelta(days=workout.weekday)

    if UserWorkout.objects.filter(id_user=request.user, id_workout=workout, workout_date=workout_date, status='active').exists():
        messages.warning(request, 'Вы уже записаны на эту тренировку в выбранную дату.')
        return redirect(f'/schedule/?week={week_offset}&day={day}')

    count = UserWorkout.objects.filter(id_workout=workout, workout_date=workout_date, status='active').count()
    if count >= workout.max_participation:
        messages.error(request, 'На эту тренировку нет свободных мест.')
        return redirect(f'/schedule/?week={week_offset}&day={day}')

    UserWorkout.objects.create(
        id_user=request.user,
        id_workout=workout,
        workout_date=workout_date,
        status='active'
    )

    messages.success(request, 'Вы успешно записались на тренировку.')
    return redirect(f'/schedule/?week={week_offset}&day={day}')


@login_required
def cancel_workout_view(request, workout_id):
    record = get_object_or_404(UserWorkout, id=workout_id, id_user=request.user)
    record.status = 'cancelled'
    record.save()
    messages.success(request, 'Запись отменена.')
    return redirect('schedule')


@login_required
def toggle_favorite_view(request, workout_id):
    week = request.POST.get('week', 0)
    day = request.POST.get('day', 0)
    
    workout = get_object_or_404(Workout, id=workout_id)
    favorites = UserWorkout.objects.filter(
        id_user=request.user,
        id_workout=workout,
        is_favorite=True
    )

    if favorites.exists():
        for fav in favorites:
            if fav.status == 'inactive':
                fav.delete()
            else:
                fav.is_favorite = False
                fav.save()
    else:
        UserWorkout.objects.create(
            id_user=request.user,
            id_workout=workout,
            is_favorite=True,
            status='inactive'
        )

    return redirect(f'/schedule/?week={week}&day={day}')
