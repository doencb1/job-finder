from django.shortcuts import render, redirect
from django.contrib import messages
from subjects.utils import login_and_get_token

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        login_url = "https://sinhvien1.tlu.edu.vn/education/oauth/token"
        token = login_and_get_token(login_url, username, password)

        if token:
            request.session['access_token'] = token  # Lưu token vào session
            return redirect('subjects:dashboard')  # Chuyển đến dashboard
        else:
            messages.error(request, "Đăng nhập thất bại. Vui lòng kiểm tra lại tài khoản hoặc mật khẩu.")
    
    return render(request, 'accounts/login.html')
def logout_view(request):
    logout(request)
    return redirect('accounts:login')