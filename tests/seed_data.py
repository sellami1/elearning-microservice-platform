import os
import random
import requests
import json
import time


class Console:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    CYAN = "\033[36m"


def _trim(text, limit=220):
    if text is None:
        return ""
    text = str(text).strip().replace("\n", " ")
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def print_section(title):
    print(f"\n{Console.BOLD}{Console.CYAN}{'=' * 16} {title} {'=' * 16}{Console.RESET}")


def print_step(message):
    print(f"{Console.BLUE}[..]{Console.RESET} {message}")


def print_status_ok(label, status_code=None):
    suffix = f" {Console.DIM}(HTTP {status_code}){Console.RESET}" if status_code else ""
    print(f"{Console.GREEN}[OK]{Console.RESET} {label}{suffix}")


def print_status_warn(label, status_code=None):
    suffix = f" {Console.DIM}(HTTP {status_code}){Console.RESET}" if status_code else ""
    print(f"{Console.YELLOW}[WARN]{Console.RESET} {label}{suffix}")


def print_status_fail(label, status_code=None, detail=None):
    suffix = f" {Console.DIM}(HTTP {status_code}){Console.RESET}" if status_code else ""
    print(f"{Console.RED}[FAIL]{Console.RESET} {label}{suffix}")
    if detail:
        print(f"{Console.RED}       error:{Console.RESET} {_trim(detail)}")


def parse_error_message(response):
    try:
        payload = response.json()
    except Exception:
        return _trim(response.text)

    if isinstance(payload, dict):
        if "detail" in payload:
            return _trim(payload.get("detail"))
        if "message" in payload:
            return _trim(payload.get("message"))
        if "errors" in payload:
            return _trim(json.dumps(payload.get("errors")))

    return _trim(payload)

# --- Config ---
# Adjust these URLs depending on whether you're hitting the API Gateway (port 80) or services directly
USER_SERVICE_URL = "http://localhost:8002/api/v1/users"

# Static password for all seeded users (instructors and learners)
USER_PASSWORD = "StrongPass1!"
COURSE_SERVICE_URL = "http://localhost:8001/api/v1"

# Create a local folder for mock media files
MEDIA_DIR = "./mock_media"
os.makedirs(MEDIA_DIR, exist_ok=True)

# Generate dummy files for upload testing
THUMBNAIL_PATH = os.path.join(MEDIA_DIR, "thumbnail.png")
VIDEO_PATH = os.path.join(MEDIA_DIR, "lesson_video.mp4")
DOC_PATH = os.path.join(MEDIA_DIR, "lesson_doc.pdf")

for path, content in [(THUMBNAIL_PATH, b"fake image"), (VIDEO_PATH, b"fake video"), (DOC_PATH, b"fake pdf")]:
    if not os.path.exists(path):
        with open(path, "wb") as f:
            f.write(content)

# --- Data Generators ---
INSTRUCTOR_NAMES = [
    ("Alice", "Nguyen"),
    ("Omar", "Harris"),
    ("Nina", "Patel"),
    ("Lucas", "Kim"),
    ("Sofia", "Garcia"),
]

LEARNER_NAMES = [
    ("Ethan", "Brown"),
    ("Mia", "Lopez"),
    ("Noah", "Wright"),
    ("Lina", "Davis"),
    ("Ava", "Clark"),
]


def build_user_payload(email, first_name, last_name, role, index):
    return {
        "email": email,
        "password": USER_PASSWORD,
        "passwordConfirm": USER_PASSWORD,
        "firstName": first_name,
        "lastName": last_name,
        "phone": f"+12125550{100 + index}",
        "role": role,
        "dateOfBirth": "1994-06-15",
        "street": "123 Seed Street",
        "city": "Seedville",
        "state": "CA",
        "country": "US",
        "zipCode": f"9000{index}",
    }


INSTRUCTORS = [
    build_user_payload(
        f"instructor{i + 1}@example.com",
        first,
        last,
        "instructor",
        i + 1,
    )
    for i, (first, last) in enumerate(INSTRUCTOR_NAMES)
]

LEARNERS = [
    build_user_payload(
        f"learner{i + 1}@example.com",
        first,
        last,
        "learner",
        i + 1,
    )
    for i, (first, last) in enumerate(LEARNER_NAMES)
]

CATEGORIES = ["Programming", "Design", "Business", "Marketing", "Music"]
LEVELS = ["beginner", "intermediate", "advanced"]

def register_and_login(user_data):
    """Registers a user and logs them in to get the JWT token."""
    print_step(f"User {user_data['email']} ({user_data['role']})")
    
    # 1. Register
    reg_res = requests.post(f"{USER_SERVICE_URL}/register", json=user_data)
    if reg_res.status_code in [200, 201]:
        print_status_ok("register", reg_res.status_code)
    else:
        detail = parse_error_message(reg_res)
        if "already exists" in reg_res.text.lower() or "already" in detail.lower():
            print_status_warn("register (user likely already exists)", reg_res.status_code)
        else:
            print_status_fail("register", reg_res.status_code, detail)
    
    # Note: If your backend strictly requires email verification before login, 
    # you might need to manually update MongoDB (`isVerified: true`) here,
    # or expose a dev endpoint to verify bypassing emails. We will attempt login.
    time.sleep(1) # tiny wait to avoid rate limits if any

    # 2. Login
    login_payload = {"email": user_data["email"], "password": user_data["password"]}
    login_res = requests.post(f"{USER_SERVICE_URL}/login", json=login_payload)
    
    if login_res.status_code == 200:
        token = login_res.json().get("token")
        if token:
            print_status_ok("login (token acquired)", login_res.status_code)
        else:
            print_status_fail("login (token missing in response)", login_res.status_code, parse_error_message(login_res))
        return token
    else:
        print_status_fail("login", login_res.status_code, parse_error_message(login_res))
        return None

def create_course(token, title, category, level):
    """Creates a course as an instructor and returns the course ID."""
    print_step(f"Create course '{title}'")
    url = f"{COURSE_SERVICE_URL}/courses/"
    headers = {"Authorization": f"Bearer {token}"}
    
    data = {
        "title": title,
        "description": f"This is a description for {title}.",
        "short_description": "Brief course summary.",
        "price": str(random.choice([0.0, 9.99, 19.99, 49.99])),
        "category": category,
        "level": level,
        "published": "True"
    }
    
    with open(THUMBNAIL_PATH, "rb") as f:
        files = {"thumbnail_file": ("thumbnail.jpg", f, "image/jpeg")}
        res = requests.post(url, headers=headers, data=data, files=files)
        
    if res.status_code == 201:
        course_id = res.json().get("id")
        print_status_ok(f"course created id={course_id}", res.status_code)
        return course_id
    else:
        print_status_fail("create course", res.status_code, parse_error_message(res))
        return None

def create_lesson(token, course_id, title, content_type, filepath):
    """Creates a lesson for a given course."""
    print_step(f"Create lesson '{title}' ({content_type}) for course={course_id}")
    url = f"{COURSE_SERVICE_URL}/lessons/"
    headers = {"Authorization": f"Bearer {token}"}
    
    data = {
        "title": title,
        "content_type": content_type,
        "course_id": course_id,
        "is_published": "True",
        "duration_minutes": str(random.randint(5, 60))
    }
    
    filename = os.path.basename(filepath)
    mimetype = "video/mp4" if content_type == "video" else "application/pdf"
    
    with open(filepath, "rb") as f:
        files = {"content_file": (filename, f, mimetype)}
        res = requests.post(url, headers=headers, data=data, files=files)
        
    if res.status_code == 201:
        print_status_ok(f"lesson created id={res.json().get('id')}", res.status_code)
    else:
        print_status_fail("create lesson", res.status_code, parse_error_message(res))

def enroll_learner(token, course_id):
    """Enrolls a learner in a course."""
    print_step(f"Enroll learner in course={course_id}")
    url = f"{COURSE_SERVICE_URL}/enrollments/"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"course_id": course_id}
    
    res = requests.post(url, headers=headers, json=payload)
    if res.status_code == 201:
        print_status_ok("enrollment created", res.status_code)
    elif res.status_code == 200:
        print_status_warn("already enrolled", res.status_code)
    else:
        print_status_fail("enroll", res.status_code, parse_error_message(res))

def main():
    print_section("Seed Start")
    print(f"{Console.DIM}User service: {USER_SERVICE_URL}{Console.RESET}")
    print(f"{Console.DIM}Course service: {COURSE_SERVICE_URL}{Console.RESET}")
    print_section("1) Instructors + Courses + Lessons")
    instructor_tokens = []
    course_ids = []
    
    for idx, inst in enumerate(INSTRUCTORS):
        token = register_and_login(inst)
        if token:
            instructor_tokens.append(token)
            # Each instructor makes 2 courses
            for j in range(1, 3):
                c_title = f"{inst['firstName']}'s Masterclass {j}"
                c_cat = random.choice(CATEGORIES)
                c_lvl = random.choice(LEVELS)
                cid = create_course(token, c_title, c_cat, c_lvl)
                
                if cid:
                    course_ids.append(cid)
                    # Add 2 lessons per course
                    create_lesson(token, cid, "Introduction Video", "video", VIDEO_PATH)
                    create_lesson(token, cid, "Reading Materials", "pdf", DOC_PATH)

    print_section("2) Learners + Enrollments")
    if not course_ids:
        print_status_warn("No courses available to enroll in. Skipping learner enrollments.")
        return
        
    for lrn in LEARNERS:
        token = register_and_login(lrn)
        if token:
            # Enroll the learner in 3 random courses
            courses_to_enroll = random.sample(course_ids, min(3, len(course_ids)))
            for cid in courses_to_enroll:
                enroll_learner(token, cid)

    print_section("Seed Completed")
    print_status_ok(f"Created/used instructors={len(INSTRUCTORS)}, learners={len(LEARNERS)}, courses_attempted={len(INSTRUCTORS) * 2}, courses_created={len(course_ids)}")

if __name__ == "__main__":
    main()
