from django.urls import path
from .views import schedule_view, register_workout_view, cancel_workout_view, toggle_favorite_view

urlpatterns = [
    path('', schedule_view, name='schedule'),
    path('register/<int:workout_id>/', register_workout_view, name='register_workout'),
    path('cancel/<int:workout_id>/', cancel_workout_view, name='cancel_workout'),
    path('favorite/<int:workout_id>/', toggle_favorite_view, name='toggle_favorite'),

]