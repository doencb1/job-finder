from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('subjects/', include('subjects.urls', namespace='subjects')),
    path('', lambda request: redirect('accounts:login'), name='home'),  # Chuyển hướng URL gốc
]
