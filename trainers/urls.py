from django.urls import path
from .views import trainer_list_view

urlpatterns = [
    path('', trainer_list_view, name='trainers'),  # /trainers/
]