from django.shortcuts import render, get_object_or_404, redirect
from .models import Subscription
from datetime import date, timedelta
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.timezone import now
from subscriptions.utils import get_actual_frozen_days_left

def subscription_list_view(request):
    subscriptions = Subscription.objects.filter(id_user__isnull=True)
    has_active = False
    if request.user.is_authenticated:
        has_active = Subscription.objects.filter(id_user=request.user, end_date__gte=date.today()).exists()
    return render(request, 'subscriptions/list.html', {
        'subscriptions': subscriptions,
        'has_active': has_active
    })

@login_required
def buy_subscription_view(request, sub_id):
    template_sub = get_object_or_404(Subscription, id=sub_id, id_user__isnull=True)

    existing = Subscription.objects.filter(id_user=request.user, end_date__gte=date.today())
    if existing.exists():
        messages.warning(request, 'У вас уже есть активный абонемент.')
        return redirect('subscription_list')

    if request.method == 'POST':
        email = request.POST.get('email')

        # Сохраняем данные для оплаты
        request.session['payment_data'] = {
            'sub_id': sub_id,
            'email': email,
            'price': str(template_sub.price),
            'name': template_sub.name
        }

        return redirect('fake_payment_page')

    return render(request, 'subscriptions/confirm_purchase.html', {'sub': template_sub})

@login_required
def fake_payment_page(request):
    data = request.session.get('payment_data')
    if not data:
        messages.error(request, 'Нет данных для оплаты')
        return redirect('subscription_list')

    return render(request, 'subscriptions/payment_redirect.html', {
        'data': data,
        'sub_id': data['sub_id']
    })

@login_required
def freeze_subscription_view(request):
    if request.method != 'POST':
        messages.error(request, 'Неправильный метод запроса.')
        return redirect('home')
    
    active_sub = Subscription.objects.filter(
        id_user=request.user,
        end_date__gte=date.today(),
        is_frozen=False
    ).first()

    if not active_sub:
        messages.warning(request, 'Нет активного абонемента для заморозки')
        return redirect('home')

    if active_sub.frozen_days_left is not None and active_sub.frozen_days_left <= 0:
        messages.warning(request, 'У вас закончились дни заморозки.')
        return redirect('home')

    # Сохраняем оставшиеся дни на момент заморозки
    active_sub.remaining_days_at_freeze = (active_sub.end_date - date.today()).days
    active_sub.is_frozen = True
    active_sub.freeze_date = date.today()

    if active_sub.frozen_days_left is None:
        active_sub.frozen_days_left = active_sub.max_freeze_days or 0

    active_sub.save()
    messages.success(request, f'Абонемент заморожен. Осталось дней заморозки: {active_sub.frozen_days_left}')
    return redirect('home')


@login_required
def unfreeze_subscription_view(request):
    frozen_sub = Subscription.objects.filter(
        id_user=request.user,
        is_frozen=True
    ).first()

    if not frozen_sub or not frozen_sub.freeze_date:
        messages.warning(request, 'У вас нет замороженного абонемента.')
        return redirect('home')

    days_frozen = (date.today() - frozen_sub.freeze_date).days
    days_frozen = max(days_frozen, 0)

    frozen_sub.end_date += timedelta(days=days_frozen)
    frozen_sub.frozen_days_left = max(frozen_sub.frozen_days_left - days_frozen, 0)

    frozen_sub.is_frozen = False
    frozen_sub.freeze_date = None
    frozen_sub.remaining_days_at_freeze = None  # сброс

    frozen_sub.save()
    messages.success(request, f'Абонемент разморожен. Осталось дней заморозки: {frozen_sub.frozen_days_left}')
    return redirect('home')



@login_required
def payment_redirect_view(request):
    data = request.session.get('payment_data')
    if not data:
        messages.error(request, 'Данные оплаты не найдены.')
        return redirect('subscription_list')

    return render(request, 'subscriptions/payment_redirect.html', {'data': data})

def payment_success_view(request):
    data = request.session.get('payment_data')
    if not data:
        messages.error(request, 'Нет данных об оплате.')
        return redirect('subscription_list')

    sub_template = get_object_or_404(Subscription, id=data['sub_id'], id_user__isnull=True)

    # Вычисляем срок действия
    duration_map = {
        'Месячный': 30,
        '3 месяца': 90,
        'Годовой': 365,
        '1 неделя': 7,
        '2 месяца': 60,
        'Полугодовой': 180,
    }
    today = date.today()
    duration = next((v for k, v in duration_map.items() if k in sub_template.name), 30)
    end_date = today + timedelta(days=duration)

    # Создаём новый абонемент
    Subscription.objects.create(
        id_user=request.user,
        name=sub_template.name,
        price=sub_template.price,
        start_date=today,
        end_date=end_date,
        is_frozen=False,
        frozen_days_left=None,
        freeze_date=None,
        max_freeze_days=sub_template.max_freeze_days or 0,
    )

    messages.success(request, 'Оплата прошла успешно. Абонемент активирован!')
    return redirect('home')