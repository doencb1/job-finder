import random
import requests
import google.generativeai as genai
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import json  # Thêm import json để xử lý định dạng JSON trả về

# Cấu hình API Gemini (cần thay đổi API Key của bạn)
GEMINI_API_KEY = 'AIzaSyBkVxCotZpQO4KlS6LKuDUPpwLNf9f0NQs'
ADZUNA_API_KEY = '4cceccbea4e827a4c899a8a55f0f995b'
ADZUNA_APP_ID = '296baac4'

# Initialize Gemini model
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# Function to get Gemini comment and suggestion
def get_gemini_comment_and_suggestion(grades):
    # Create prompt yêu cầu Gemini trả lời với nhận xét và gợi ý công việc
    prompt = f"Given the following IT subject grades: {grades}, provide a detailed comment in Vietnamese about the performance in each subject, including strengths and areas for improvement. Then suggest one specific job in English from the following list: Developer, Business Analyst, AI, or Network. Format the response as: 'Comment: [Your detailed comment here in Vietnamese]. Suggested job: [Job title here in English].'"

    try:
        # Get response from Gemini API
        response = model.generate_content(prompt)
        response_text = response.text.strip()

        # Tách nhận xét và công việc từ phản hồi của Gemini
        comment = ""
        job_title = "Developer"  # Default job title
        if "Comment:" in response_text and "Suggested job:" in response_text:
            parts = response_text.split("Suggested job:")
            comment = parts[0].replace("Comment:", "").strip()
            job_title = parts[1].strip()
        
        # Đảm bảo công việc được gợi ý nằm trong danh sách cho phép
        valid_jobs = ['Developer', 'Business Analyst', 'AI', 'Network']
        if job_title not in valid_jobs:
            job_title = "Developer"  # Default nếu không hợp lệ
        
        return comment, job_title
    
    except Exception as e:
        print(f"Error in getting response from Gemini: {e}")
        return "Error in generating comment.", "Developer"


# Function to search for job using Adzuna API
def search_job(job_title):
    url = "https://api.adzuna.com/v1/api/jobs/us/search/1"  # Khu vực tìm kiếm (us)
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_API_KEY,
        "what": job_title,  # Từ khóa tìm kiếm
        "results_per_page": 10  # Số lượng kết quả muốn hiển thị
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Kiểm tra lỗi HTTP
        data = response.json()
        
        # Xử lý kết quả trả về
        if "results" in data and data["results"]:
            jobs = data["results"]
            job_list = []
            for job in jobs:
                job_list.append({
                    "title": job["title"],
                    "company": job.get("company", {}).get("display_name", "Không xác định"),
                    "location": job.get("location", {}).get("display_name", "Không xác định"),
                    "url": job["redirect_url"]
                })
            return job_list
        else:
            print("No results found in Adzuna response")
            return None
    
    except requests.exceptions.RequestException as e:
        print(f"Error in getting jobs from Adzuna: {e}")
        return None



# Hàm tạo điểm số ngẫu nhiên
def generate_random_grades():
    subjects = ["Programming", "Database", "Networking", "CyberSecurity", "AI"]
    grades = {subject: random.randint(50, 100) for subject in subjects}
    return grades

# Hàm lấy công việc từ API Adzuna
def fetch_jobs_from_api(query):
    url = f"https://api.adzuna.com/v1/api/jobs/us/search/1?app_id={ADZUNA_APP_ID}&app_key={ADZUNA_API_KEY}&what={query}&content-type=application/json"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        results = data.get('results', [])
        jobs = []
        for result in results:
            job = {
                'title': result.get('title'),
                'description': result.get('description'),
                'location': result.get('location', {}).get('display_name', 'Không xác định'),
                'url': result.get('redirect_url'),
            }
            jobs.append(job)
        return jobs
    else:
        return []

# Main function to integrate the process
@login_required
def job_list(request):
    # Bước 1: Tạo điểm số ngẫu nhiên
    grades = generate_random_grades()
    
    # Bước 2: Nhận xét và gợi ý công việc từ Gemini
    comment, job_title = get_gemini_comment_and_suggestion(grades)

    # Bước 3: Tìm kiếm công việc từ Adzuna (nhiều kết quả)
    jobs = search_job(job_title)
    error_message = None

    if not jobs:
        error_message = f"Không tìm thấy công việc cho '{job_title}'."

    return render(request, 'jobs/job_list.html', {
        'grades': grades,
        'comment': comment,
        'job_title': job_title,
        'jobs': jobs,
        'error_message': error_message
    })


