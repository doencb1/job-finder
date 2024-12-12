from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

# Trang chủ: chuyển hướng tới danh sách công việc
def home(request):
    return redirect('job_list')

urlpatterns = [
    path('admin/', admin.site.urls),           # Trang quản trị
    path('', home, name='home'),               # Trang chủ
    path('accounts/', include('accounts.urls')),  # URL của đăng nhập/đăng ký/đăng xuất
    path('jobs/', include('jobs.urls')),       # URL của danh sách công việc
]
