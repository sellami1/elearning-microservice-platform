#!/usr/bin/env bash

# End-to-end endpoint checks for course-service.
# Covers public, instructor-only, learner-only, and protected CRUD flows.

set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8001}"
API_PREFIX="/api/v1"
TIMEOUT="${TIMEOUT:-15}"

# JWT secret used by course-service (docker-compose default compatible).
JWT_SECRET="${COURSE_BACKEND_JWT_SECRET_KEY:-change-me-course-secret}"

# Deterministic test users (24-char ObjectId-like strings)
INSTRUCTOR_ID="${INSTRUCTOR_ID:-507f1f77bcf86cd799439011}"
LEARNER_ID="${LEARNER_ID:-507f1f77bcf86cd799439012}"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

COURSE_ID=""
LESSON_ID=""

print_test() {
  echo -e "${BLUE}=======================================${NC}"
  echo -e "${YELLOW}TEST: $1${NC}"
  echo -e "${BLUE}=======================================${NC}"
}

pass() {
  echo -e "${GREEN}PASS${NC} $1"
}

fail() {
  echo -e "${RED}FAIL${NC} $1"
  exit 1
}

# base64url helper for JWT generation
b64url() {
  openssl base64 -A | tr '+/' '-_' | tr -d '='
}

make_jwt() {
  local user_id="$1"
  local role="$2"
  local header payload signature signing_input

  header='{"alg":"HS256","typ":"JWT"}'
  payload=$(printf '{"userId":"%s","role":"%s"}' "$user_id" "$role")

  signing_input="$(printf '%s' "$header" | b64url).$(printf '%s' "$payload" | b64url)"
  signature=$(printf '%s' "$signing_input" | openssl dgst -binary -sha256 -hmac "$JWT_SECRET" | b64url)

  printf '%s.%s\n' "$signing_input" "$signature"
}

INSTRUCTOR_TOKEN="$(make_jwt "$INSTRUCTOR_ID" "instructor")"
LEARNER_TOKEN="$(make_jwt "$LEARNER_ID" "learner")"

# HTTP helpers
request_json() {
  local method="$1"
  local endpoint="$2"
  local token="${3:-}"
  local body="${4:-}"

  local auth_args=()
  if [[ -n "$token" ]]; then
    auth_args=(-H "Authorization: Bearer $token")
  fi

  if [[ -n "$body" ]]; then
    curl -sS -m "$TIMEOUT" -X "$method" \
      "${BASE_URL}${API_PREFIX}${endpoint}" \
      -H "Content-Type: application/json" \
      "${auth_args[@]}" \
      -d "$body" \
      -w "\n%{http_code}"
  else
    curl -sS -m "$TIMEOUT" -X "$method" \
      "${BASE_URL}${API_PREFIX}${endpoint}" \
      -H "Content-Type: application/json" \
      "${auth_args[@]}" \
      -w "\n%{http_code}"
  fi
}

request_form() {
  local method="$1"
  local endpoint="$2"
  local token="$3"
  shift 3

  curl -sS -m "$TIMEOUT" -X "$method" \
    "${BASE_URL}${API_PREFIX}${endpoint}" \
    -H "Authorization: Bearer $token" \
    "$@" \
    -w "\n%{http_code}"
}

request_public() {
  local method="$1"
  local endpoint="$2"

  curl -sS -m "$TIMEOUT" -X "$method" \
    "${BASE_URL}${endpoint}" \
    -w "\n%{http_code}"
}

status_code() {
  tail -n1
}

body_only() {
  sed '$d'
}

extract_id() {
  # Extract first JSON field named "id"
  grep -oE '"id":"[^"]+"' | head -n1 | cut -d '"' -f4
}

assert_status() {
  local got="$1"
  local expected="$2"
  local label="$3"

  if [[ "$got" == "$expected" ]]; then
    pass "$label (status $got)"
  else
    fail "$label expected status $expected, got $got"
  fi
}

assert_status_any() {
  local got="$1"
  local allowed_csv="$2"
  local label="$3"

  IFS=',' read -r -a allowed <<< "$allowed_csv"
  for s in "${allowed[@]}"; do
    if [[ "$got" == "$s" ]]; then
      pass "$label (status $got)"
      return 0
    fi
  done
  fail "$label expected one of [$allowed_csv], got $got"
}

print_test "GET /health"
R=$(request_public GET "/health")
S=$(printf '%s' "$R" | status_code)
B=$(printf '%s' "$R" | body_only)
assert_status "$S" "200" "health check"
printf 'Response: %s\n' "$B"

print_test "GET /"
R=$(request_public GET "/")
S=$(printf '%s' "$R" | status_code)
B=$(printf '%s' "$R" | body_only)
assert_status "$S" "200" "root endpoint"
printf 'Response: %s\n' "$B"

print_test "GET /api/v1/courses/ (public)"
R=$(request_json GET "/courses/" "" "")
S=$(printf '%s' "$R" | status_code)
assert_status "$S" "200" "list courses public"

print_test "POST /api/v1/courses/ (instructor)"
R=$(request_form POST "/courses/" "$INSTRUCTOR_TOKEN" \
  -F "title=Test Course $(date +%s)" \
  -F "description=Course created by endpoint test script" \
  -F "short_description=API test course" \
  -F "price=19.99" \
  -F "category=Programming" \
  -F "subcategory=Python" \
  -F "level=beginner" \
  -F "duration_hours=10" \
  -F "published=true" \
  -F "is_featured=false")
S=$(printf '%s' "$R" | status_code)
B=$(printf '%s' "$R" | body_only)
assert_status "$S" "201" "create course"
COURSE_ID=$(printf '%s' "$B" | extract_id)
[[ -n "$COURSE_ID" ]] || fail "create course returned no id"
printf 'Course ID: %s\n' "$COURSE_ID"

print_test "GET /api/v1/courses/{course_id} (public)"
R=$(request_json GET "/courses/${COURSE_ID}" "" "")
S=$(printf '%s' "$R" | status_code)
assert_status "$S" "200" "get course by id"

print_test "PUT /api/v1/courses/{course_id} (instructor)"
R=$(request_form PUT "/courses/${COURSE_ID}" "$INSTRUCTOR_TOKEN" \
  -F "title=Updated Course Title" \
  -F "price=29.99" \
  -F "is_featured=true")
S=$(printf '%s' "$R" | status_code)
assert_status "$S" "200" "update course"

print_test "GET /api/v1/courses/instructor/mine"
R=$(request_json GET "/courses/instructor/mine" "$INSTRUCTOR_TOKEN" "")
S=$(printf '%s' "$R" | status_code)
assert_status "$S" "200" "instructor mine"

print_test "POST /api/v1/lessons/ (instructor)"
R=$(request_form POST "/lessons/" "$INSTRUCTOR_TOKEN" \
  -F "title=Intro Lesson" \
  -F "description=Text lesson for API tests" \
  -F "content_type=text" \
  -F "duration_minutes=15" \
  -F "is_preview=true" \
  -F "is_published=true" \
  -F "course_id=${COURSE_ID}" \
  -F "content_url=https://example.com/lesson-content")
S=$(printf '%s' "$R" | status_code)
B=$(printf '%s' "$R" | body_only)
assert_status "$S" "201" "create lesson"
LESSON_ID=$(printf '%s' "$B" | extract_id)
[[ -n "$LESSON_ID" ]] || fail "create lesson returned no id"
printf 'Lesson ID: %s\n' "$LESSON_ID"

print_test "GET /api/v1/lessons/course/{course_id}"
R=$(request_json GET "/lessons/course/${COURSE_ID}" "" "")
S=$(printf '%s' "$R" | status_code)
assert_status "$S" "200" "list lessons by course"

print_test "GET /api/v1/lessons/{lesson_id}"
R=$(request_json GET "/lessons/${LESSON_ID}" "" "")
S=$(printf '%s' "$R" | status_code)
assert_status "$S" "200" "get lesson"

print_test "PUT /api/v1/lessons/{lesson_id}"
R=$(request_form PUT "/lessons/${LESSON_ID}" "$INSTRUCTOR_TOKEN" \
  -F "title=Updated Intro Lesson" \
  -F "duration_minutes=20")
S=$(printf '%s' "$R" | status_code)
assert_status "$S" "200" "update lesson"

print_test "POST /api/v1/enrollments/ (learner)"
R=$(request_json POST "/enrollments/" "$LEARNER_TOKEN" "{\"course_id\":\"${COURSE_ID}\"}")
S=$(printf '%s' "$R" | status_code)
assert_status_any "$S" "200,201" "enroll in course"

print_test "GET /api/v1/enrollments/me (learner)"
R=$(request_json GET "/enrollments/me" "$LEARNER_TOKEN" "")
S=$(printf '%s' "$R" | status_code)
assert_status "$S" "200" "my enrollments"

print_test "GET /api/v1/enrollments/course/{course_id}/enrollments (instructor)"
R=$(request_json GET "/enrollments/course/${COURSE_ID}/enrollments" "$INSTRUCTOR_TOKEN" "")
S=$(printf '%s' "$R" | status_code)
assert_status "$S" "200" "course enrollments"

print_test "GET /api/v1/enrollments/instructor (instructor)"
R=$(request_json GET "/enrollments/instructor" "$INSTRUCTOR_TOKEN" "")
S=$(printf '%s' "$R" | status_code)
assert_status "$S" "200" "instructor enrollments overview"

print_test "DELETE /api/v1/lessons/{lesson_id}"
R=$(request_json DELETE "/lessons/${LESSON_ID}" "$INSTRUCTOR_TOKEN" "")
S=$(printf '%s' "$R" | status_code)
assert_status "$S" "204" "delete lesson"

print_test "DELETE /api/v1/courses/{course_id}"
R=$(request_json DELETE "/courses/${COURSE_ID}" "$INSTRUCTOR_TOKEN" "")
S=$(printf '%s' "$R" | status_code)
assert_status "$S" "204" "delete course"

echo -e "\n${GREEN}=======================================${NC}"
echo -e "${GREEN}All course-service endpoint tests passed${NC}"
echo -e "${GREEN}=======================================${NC}"
