from django.urls import path
from .views import subscription_list_view, buy_subscription_view, fake_payment_page, freeze_subscription_view, unfreeze_subscription_view, payment_success_view, payment_redirect_view

urlpatterns = [
    path('', subscription_list_view, name='subscription_list'),
    path('buy/<int:sub_id>/', buy_subscription_view, name='buy_subscription'),
    path('payment/confirm/', payment_redirect_view, name='payment_redirect'),  # Путь на confirm_purchase
    path('payment/', fake_payment_page, name='fake_payment_page'),             # Финальная оплата
    path('freeze/', freeze_subscription_view, name='freeze_subscription'),
    path('unfreeze/', unfreeze_subscription_view, name='unfreeze_subscription'),
    path('payment/success/', payment_success_view, name='payment_success'),
]