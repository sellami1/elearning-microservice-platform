import requests
import os

url = "http://localhost:8001/api/v1/lessons/"

# Create a dummy video file
with open("test_video.mp4", "wb") as f:
    f.write(b"dummy video content")

# When using requests with files, data dictionary is sent as form fields
# and files dictionary/list is sent as file parts.
# Correct structure:
payload = {
    'title': 'Test Lesson',
    'description': 'Test Description',
    'content_type': 'video', 
    'course_id': '91f7d68a-df8d-4157-9b68-ba762a014135',
    'duration_minutes': '10',
    'order_index': '0',
    'is_preview': 'true',
    'is_published': 'true'
}

# The key 'content_file' matches the parameter name in the FastAPI endpoint
files = {
    'content_file': ('test_video.mp4', open('test_video.mp4', 'rb'), 'video/mp4')
}

# Replace with a valid token
token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI1MDdmMWY3N2JjZjg2Y2Q3OTk0MzkwMTEiLCJyb2xlIjoiaW5zdHJ1Y3RvciIsImVtYWlsIjoiaW5zdHJ1Y3RvckBleGFtcGxlLmNvbSIsImV4cCI6MTc3MDcyNjQ1MywiaWF0IjoxNzcwNjQwMDUzfQ.pc2t5OuAW8PJ_X_BPPg1tF3VrdJcvENmhrZ8roISTpA"

headers = {
    'Authorization': token
}

try:
    response = requests.post(url, headers=headers, data=payload, files=files)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
finally:
    if os.path.exists("test_video.mp4"):
        os.remove("test_video.mp4")
