from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')), 
    path('subscriptions/', include('subscriptions.urls')), 
    path('schedule/', include('workouts.urls')),
    path('trainers/', include('trainers.urls')),
    path('login/', LoginView.as_view(template_name='main/login.html'), name='login'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)