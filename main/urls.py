from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView
from .views import register_view, CustomLoginView, profile_settings_view
from workouts.views import  cancel_workout_view, toggle_favorite_view

urlpatterns = [
    path('', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('register/', register_view, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('settings/', profile_settings_view, name='profile_settings'),
    path('cancel/<int:workout_id>/', cancel_workout_view, name='cancel_workout'),
    path('favorite/<int:workout_id>/', toggle_favorite_view, name='toggle_favorite'),
]
