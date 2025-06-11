from django.db import models

class Trainer(models.Model):
    fullname = models.CharField(max_length=50)
    years_of_experience = models.PositiveIntegerField()
    specialization = models.CharField(max_length=100)
    description = models.TextField()
    photo = models.ImageField(upload_to='trainers/', blank=True, null=True)

    def __str__(self):
        return self.fullname

WEEKDAYS = [
    (0, 'Понедельник'),
    (1, 'Вторник'),
    (2, 'Среда'),
    (3, 'Четверг'),
    (4, 'Пятница'),
    (5, 'Суббота'),
    (6, 'Воскресенье'),
]

class Workout(models.Model):
    id_trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name='workouts')
    type = models.CharField(max_length=100)
    weekday = models.IntegerField(choices=WEEKDAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()
    max_participation = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.get_weekday_display()} {self.type} ({self.start_time}-{self.end_time})"

class UserWorkout(models.Model):
    STATUS_CHOICES = [
        ('active', 'Активна'),
        ('cancelled', 'Отменена'),
        ('completed', 'Завершена'),
    ]

    id_user = models.ForeignKey('main.User', on_delete=models.CASCADE, related_name='user_workouts')
    id_workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name='registrations')
    workout_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    recording_date = models.DateTimeField(auto_now_add=True)
    is_favorite = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.id_user} -> {self.id_workout} ({self.status})"
