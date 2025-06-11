from django.shortcuts import render, get_object_or_404
from workouts.models import Trainer

def trainer_list_view(request):
    trainers = Trainer.objects.all()
    return render(request, 'trainers/trainers_list.html', {'trainers': trainers})

