from django.shortcuts import render, redirect
from django.contrib import messages
from .utils import process_response_to_table, get_gemini_comment_and_suggestion, search_job
import requests

def dashboard(request):
    token = request.session.get('access_token')
    if not token:
        return redirect('accounts:login')

    url = "https://sinhvien1.tlu.edu.vn/education/api/studentsubjectmark/checkFinishedEducationProgramOfStudent/tree/studentId/113"
    headers = {'Authorization': f'Bearer {token}'}

    try:
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            data = response.json()
            df = process_response_to_table(data)
            if not df.empty:
                # Chuyển DataFrame thành bảng HTML
                table_html = df.to_html(classes='table table-bordered table-striped', index=False)
                return render(request, 'subjects/dashboard.html', {'table_html': table_html})
            else:
                return render(request, 'subjects/dashboard.html', {'error': "Không có dữ liệu để hiển thị."})
        else:
            return render(request, 'subjects/dashboard.html', {'error': f"Lỗi khi lấy dữ liệu từ API: {response.status_code}"})
    except Exception as e:
        return render(request, 'subjects/dashboard.html', {'error': f"Lỗi hệ thống: {e}"})

def suggest_job(request):
    token = request.session.get('access_token')
    if not token:
        return redirect('accounts:login')

    url = "https://sinhvien1.tlu.edu.vn/education/api/studentsubjectmark/checkFinishedEducationProgramOfStudent/tree/studentId/113"
    headers = {'Authorization': f'Bearer {token}'}

    try:
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            data = response.json()
            df = process_response_to_table(data)

            if not df.empty:
                # Chuyển DataFrame thành chuỗi điểm để gửi cho Gemini
                grades_text = ", ".join([f"{row['Subject Name']} ({row['Subject Mark']})" for _, row in df.iterrows()])
                
                # Gọi Gemini để lấy nhận xét và gợi ý công việc
                comment, suggested_job = get_gemini_comment_and_suggestion(grades_text)
                
                # Tìm công việc dựa trên gợi ý từ Gemini
                job_list = search_job(suggested_job)

                return render(request, 'subjects/suggest.html', {
                    'comment': comment,
                    'suggested_job': suggested_job,
                    'job_list': job_list
                })
            else:
                return render(request, 'subjects/suggest.html', {'error': "Không có dữ liệu để hiển thị."})
        else:
            return render(request, 'subjects/suggest.html', {'error': f"Lỗi khi lấy dữ liệu từ API: {response.status_code}"})
    except Exception as e:
        return render(request, 'subjects/suggest.html', {'error': f"Lỗi hệ thống: {e}"})
