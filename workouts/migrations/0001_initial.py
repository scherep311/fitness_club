# Generated by Django 5.2 on 2025-05-04 09:29

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Trainer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fullname', models.CharField(max_length=50)),
                ('years_of_experience', models.PositiveIntegerField()),
                ('specialization', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('photo', models.ImageField(blank=True, null=True, upload_to='trainers/')),
            ],
        ),
        migrations.CreateModel(
            name='Workout',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=100)),
                ('date', models.DateField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('max_participation', models.PositiveIntegerField()),
                ('id_trainer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='workouts', to='workouts.trainer')),
            ],
        ),
        migrations.CreateModel(
            name='UserWorkout',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('active', 'Активна'), ('cancelled', 'Отменена'), ('completed', 'Завершена')], default='active', max_length=20)),
                ('recording_date', models.DateTimeField(auto_now_add=True)),
                ('id_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_workouts', to=settings.AUTH_USER_MODEL)),
                ('id_workout', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='registrations', to='workouts.workout')),
            ],
        ),
    ]
