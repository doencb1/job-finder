import requests
import pandas as pd
import google.generativeai as genai

# Hàm đăng nhập và lấy token
def login_and_get_token(login_url, username, password):
    credentials = {
        "username": username,
        "password": password,
        "grant_type": "password",
        "client_id": "education_client",
        "client_secret": "password"
    }

    try:
        response = requests.post(login_url, data=credentials, verify=False)
        if response.status_code == 200:
            return response.json().get('access_token')
        return None
    except Exception as e:
        print(f"Lỗi khi gọi API đăng nhập: {e}")
        return None

def extract_subjects_from_block(block):
    subjects = []
    
    # Nếu block có thông tin môn học trực tiếp
    if 'subjectName' in block:
        subjects.append({
            "Subject Name": block.get('displaySubjectName', block.get('subjectName', 'N/A')).strip(),
            "Subject Mark": block.get('subjectMark', 'N/A'),
            "Char Mark": block.get('charMark', 'N/A'),
            "Mark4": block.get('mark4', 'N/A')
        })
    
    # Nếu block có listProgramSubject, duyệt qua danh sách đó
    if 'listProgramSubject' in block and isinstance(block['listProgramSubject'], list):
        for subject in block['listProgramSubject']:
            subjects.append({
                "Subject Name": subject.get('displaySubjectName', 'N/A').strip(),
                "Subject Mark": subject.get('subjectMark', 'N/A'),
                "Char Mark": subject.get('charMark', 'N/A'),
                "Mark4": subject.get('mark4', 'N/A')
            })

    # Nếu block có children, duyệt qua children
    if 'children' in block and isinstance(block['children'], list):
        for child_block in block['children']:
            subjects.extend(extract_subjects_from_block(child_block))
    
    return subjects


# Hàm xử lý dữ liệu từ API và chuyển đổi sang DataFrame
def process_response_to_table(data):
    allowed_subjects = [
        "Trí tuệ nhân tạo",
        "Khai phá dữ liệu",
        "Tiếng Anh chuyên ngành công nghệ thông tin",
        "Học máy",
        "Nhập môn lập trình",
        "Lập trình Python",
        "Công nghệ Web",
        "Lập trình Windows",
        "Phân tích và thiết kế hệ thống thông tin",
        "Quản trị Hệ thống thông tin",
        "Hệ quản trị cơ sở dữ liệu",
        "Mạng máy tính",
        "An toàn và bảo mật thông tin",
        "Kiến trúc máy tính",
        "Linux và phần mềm mã nguồn mở"
    ]

    if 'content' in data:
        subjects = []
        for block in data['content']:
            # Gọi hàm để duyệt qua tất cả các môn học trong block
            subjects.extend(extract_subjects_from_block(block))

        # Lọc chỉ các môn học nằm trong danh sách cho phép
        filtered_subjects = [subject for subject in subjects if subject["Subject Name"] in allowed_subjects]

        # Nếu tìm được môn học, chuyển thành DataFrame
        if filtered_subjects:
            return pd.DataFrame(filtered_subjects)
        else:
            return pd.DataFrame([{"Message": "No allowed subjects found"}])
    else:
        return pd.DataFrame([{"Message": "No content in API response"}])

GEMINI_API_KEY = 'AIzaSyBkVxCotZpQO4KlS6LKuDUPpwLNf9f0NQs'
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# Hàm lấy nhận xét và gợi ý công việc từ Gemini
def get_gemini_comment_and_suggestion(grades):
    prompt = (
    f"Given the following IT subject grades: {grades}, provide a detailed comment in Vietnamese about the performance in each subject, including strengths and areas for improvement. Then suggest one specific job in English from the following list: Developer, Business Analyst, AI, Software Engineer or Network. Format the response as: 'Comment: [Your detailed comment here in Vietnamese]. Suggested job: [Job title here in English].'"
)

    print("Prompt sent to Gemini:", prompt)  # Debug prompt

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
        valid_jobs = ['Developer', 'Business Analyst', 'AI', 'Network','Software Engineer']
        if job_title not in valid_jobs:
            job_title = "Developer"  # Default nếu không hợp lệ
        
        return comment, job_title
    except Exception as e:
        print(f"Error in Gemini response: {e}")
        return "Không thể lấy nhận xét từ Gemini.", "Developer"

# Hàm tìm kiếm công việc từ Adzuna
def search_job(job_title):
    ADZUNA_API_KEY = "4cceccbea4e827a4c899a8a55f0f995b"
    ADZUNA_APP_ID = "296baac4"
    url = "https://api.adzuna.com/v1/api/jobs/us/search/1"
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_API_KEY,
        "what": job_title,
        "results_per_page": 10
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            jobs = []
            for result in data.get('results', []):
                jobs.append({
                    "title": result.get('title'),
                    "company": result.get('company', {}).get('display_name', "Không xác định"),
                    "location": result.get('location', {}).get('display_name', "Không xác định"),
                    "url": result.get('redirect_url')
                })
            return jobs
        else:
            print(f"Error fetching jobs: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error in job search: {e}")
        return []

# View xử lý trang gợi ý
def suggest(request):
    token = request.session.get('access_token')
    if not token:
        return redirect('accounts:login')

    url = "https://sinhvien1.tlu.edu.vn/education/api/studentsubjectmark/checkFinishedEducationProgramOfStudent/tree/studentId/113"
    headers = {'Authorization': f'Bearer {token}'}

    try:
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            data = response.json()
            # Lấy dữ liệu điểm
            df = process_response_to_table(data)
            if not df.empty:
                grades = df.to_dict('records')
                grades_text = json.dumps(grades)

                # Lấy nhận xét và công việc được gợi ý từ Gemini
                comment, suggested_job = get_gemini_comment_and_suggestion(grades_text)
                # Tìm kiếm công việc trên Adzuna
                jobs = search_job(suggested_job)
            
                return render(request, 'subjects/suggest.html', {
                    'comment': comment,
                    'suggested_job': suggested_job,
                    'jobs': jobs
                })
            else:
                return render(request, 'subjects/suggest.html', {
                    'error': "Không có dữ liệu để hiển thị."
                })
        else:
            return render(request, 'subjects/suggest.html', {
                'error': f"Lỗi khi lấy dữ liệu từ API: {response.status_code}"
            })
    except Exception as e:
        return render(request, 'subjects/suggest.html', {
            'error': f"Lỗi hệ thống: {e}"
        })