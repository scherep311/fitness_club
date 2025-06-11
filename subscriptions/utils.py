from datetime import date, timedelta


def is_subscription_active(subscription):
    if not subscription:
        return False
    if subscription.is_frozen:
        return False
    if subscription.end_date < date.today():
        return False
    return True

def get_date_for_weekday(weekday: int) -> date:
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    return start_of_week + timedelta(days=weekday)
from datetime import date


from datetime import date

def get_actual_frozen_days_left(subscription):
    if not subscription.is_frozen or not subscription.freeze_date or subscription.frozen_days_left is None:
        return 0

    days_passed = (date.today() - subscription.freeze_date).days
    days_left = subscription.frozen_days_left - days_passed
    return max(days_left, 0)
