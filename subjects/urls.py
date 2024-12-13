from django.urls import path
from . import views

app_name = 'subjects'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('suggest/', views.suggest_job, name='suggest'),  # URL cho gợi ý
]
