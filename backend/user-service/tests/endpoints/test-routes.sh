#!/bin/bash

# Bash script to test user-service routes with valid requests
# Tests: POST /register, POST /login, GET /me, PUT /update-me

set -e

# Configuration
BASE_URL="${BASE_URL:-http://localhost:8002}"
API_PREFIX="/api/v1/users"
TIMEOUT=5

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test data
TEST_USER_EMAIL="testuser_$(date +%s)@example.com"
TEST_USER_PASSWORD="TestPassword123!"
TEST_USER_FIRST_NAME="John"
TEST_USER_LAST_NAME="Doe"

# Store JWT token
JWT_TOKEN=""
USER_ID=""

# Helper function to print test results
print_test() {
  echo -e "${BLUE}═══════════════════════════════════════${NC}"
  echo -e "${YELLOW}TEST: $1${NC}"
  echo -e "${BLUE}═══════════════════════════════════════${NC}"
}

print_success() {
  echo -e "${GREEN}✓ $1${NC}\n"
}

print_error() {
  echo -e "${RED}✗ $1${NC}\n"
}

# Helper function for HTTP requests
make_request() {
  local method=$1
  local endpoint=$2
  local data=$3
  local auth_header=$4

  local curl_cmd="curl -s -w '\n%{http_code}' -X $method '$BASE_URL$API_PREFIX$endpoint' \
    -H 'Content-Type: application/json' \
    --max-time $TIMEOUT"

  if [ -n "$auth_header" ]; then
    curl_cmd="$curl_cmd -H 'Authorization: Bearer $auth_header'"
  fi

  if [ -n "$data" ]; then
    curl_cmd="$curl_cmd -d '$data'"
  fi

  echo "$(eval $curl_cmd)"
}

# Helper to extract HTTP status code
get_status_code() {
  echo "$1" | tail -n1
}

# Helper to extract response body
get_response_body() {
  echo "$1" | head -n-1
}

# Helper to extract JWT from login response
extract_jwt() {
  local response=$1
  echo "$response" | grep -o '"token":"[^"]*' | cut -d'"' -f4
}

# ===== TEST 1: Register a new user =====
print_test "POST /register - Valid registration request"

REGISTER_DATA=$(cat <<EOF
{
  "email": "$TEST_USER_EMAIL",
  "password": "$TEST_USER_PASSWORD",
  "passwordConfirm": "$TEST_USER_PASSWORD",
  "firstName": "$TEST_USER_FIRST_NAME",
  "lastName": "$TEST_USER_LAST_NAME",
  "phone": "+12125550123",
  "dateOfBirth": "1990-01-15",
  "role": "learner",
  "street": "123 Main St",
  "city": "New York",
  "state": "NY",
  "country": "US",
  "zipCode": "10001"
}
EOF
)

REGISTER_RESPONSE=$(make_request "POST" "/register" "$REGISTER_DATA")
REGISTER_STATUS=$(get_status_code "$REGISTER_RESPONSE")
REGISTER_BODY=$(get_response_body "$REGISTER_RESPONSE")

echo "Status Code: $REGISTER_STATUS"
echo "Response: $REGISTER_BODY"

if [ "$REGISTER_STATUS" = "201" ] || [ "$REGISTER_STATUS" = "200" ]; then
  USER_ID=$(echo "$REGISTER_BODY" | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)
  print_success "User registered successfully (Email: $TEST_USER_EMAIL)"
else
  print_error "Registration failed with status $REGISTER_STATUS"
  exit 1
fi

# Small delay between requests
sleep 1

# ===== TEST 2: Login with registered user =====
print_test "POST /login - Valid login request"

LOGIN_DATA=$(cat <<EOF
{
  "email": "$TEST_USER_EMAIL",
  "password": "$TEST_USER_PASSWORD"
}
EOF
)

LOGIN_RESPONSE=$(make_request "POST" "/login" "$LOGIN_DATA")
LOGIN_STATUS=$(get_status_code "$LOGIN_RESPONSE")
LOGIN_BODY=$(get_response_body "$LOGIN_RESPONSE")

echo "Status Code: $LOGIN_STATUS"
echo "Response: $LOGIN_BODY"

if [ "$LOGIN_STATUS" = "200" ]; then
  JWT_TOKEN=$(extract_jwt "$LOGIN_BODY")
  if [ -n "$JWT_TOKEN" ]; then
    print_success "User logged in successfully (Token: ${JWT_TOKEN:0:20}...)"
  else
    print_error "No token in login response"
    exit 1
  fi
else
  print_error "Login failed with status $LOGIN_STATUS"
  exit 1
fi

# Small delay between requests
sleep 1

# ===== TEST 3: Get current user (protected route) =====
print_test "GET /me - Retrieve current user profile (Protected)"

GET_ME_RESPONSE=$(make_request "GET" "/me" "" "$JWT_TOKEN")
GET_ME_STATUS=$(get_status_code "$GET_ME_RESPONSE")
GET_ME_BODY=$(get_response_body "$GET_ME_RESPONSE")

echo "Status Code: $GET_ME_STATUS"
echo "Response: $GET_ME_BODY"

if [ "$GET_ME_STATUS" = "200" ]; then
  print_success "Current user profile retrieved successfully"
else
  print_error "Failed to retrieve user profile with status $GET_ME_STATUS"
  exit 1
fi

# Small delay between requests
sleep 1

# ===== TEST 4: Update user profile =====
print_test "PUT /update-me - Update user profile (Protected)"

UPDATE_DATA=$(cat <<EOF
{
  "firstName": "Jane",
  "lastName": "Smith",
  "phone": "+12125550124",
  "dateOfBirth": "1992-05-20",
  "street": "456 Oak Ave",
  "city": "Los Angeles",
  "state": "CA",
  "country": "US",
  "zipCode": "90001"
}
EOF
)

UPDATE_RESPONSE=$(make_request "PUT" "/update-me" "$UPDATE_DATA" "$JWT_TOKEN")
UPDATE_STATUS=$(get_status_code "$UPDATE_RESPONSE")
UPDATE_BODY=$(get_response_body "$UPDATE_RESPONSE")

echo "Status Code: $UPDATE_STATUS"
echo "Response: $UPDATE_BODY"

if [ "$UPDATE_STATUS" = "200" ]; then
  print_success "User profile updated successfully"
else
  print_error "Profile update failed with status $UPDATE_STATUS"
  exit 1
fi

# ===== TEST 5: Verify updated profile =====
print_test "GET /me - Verify updated profile"

VERIFY_RESPONSE=$(make_request "GET" "/me" "" "$JWT_TOKEN")
VERIFY_STATUS=$(get_status_code "$VERIFY_RESPONSE")
VERIFY_BODY=$(get_response_body "$VERIFY_RESPONSE")

echo "Status Code: $VERIFY_STATUS"
echo "Response: $VERIFY_BODY"

if [ "$VERIFY_STATUS" = "200" ]; then
  if echo "$VERIFY_BODY" | grep -q "Jane"; then
    print_success "Profile updates verified successfully"
  else
    print_error "Updated profile data not found"
    exit 1
  fi
else
  print_error "Verification failed with status $VERIFY_STATUS"
  exit 1
fi

# ===== SUMMARY =====
echo -e "\n${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}All tests passed successfully!${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo ""
echo "Summary:"
echo "  ✓ User registered: $TEST_USER_EMAIL"
echo "  ✓ User logged in with token"
echo "  ✓ User profile retrieved"
echo "  ✓ User profile updated"
echo "  ✓ Changes verified"
