# test_token_generator.py
from jose import jwt
import datetime
import uuid

# Match your User Service's JWT configuration
JWT_SECRET = "jwt_secret_key"  # Must match User Service
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 24

def generate_test_tokens():
    """Generate test tokens matching User Service format"""
    
    # Sample user data (MongoDB ObjectId as string)
    users = [
        {
            "id": "507f1f77bcf86cd799439012",  # MongoDB ObjectId string
            "role": "instructor",
            "email": "instructor@example.com"
        },
        {
            "id": "507f1f77bcf86cd799439012",
            "role": "student", 
            "email": "student@example.com"
        },
        {
            "id": "507f1f77bcf86cd799439013",
            "role": "admin",
            "email": "admin@example.com"
        }
    ]
    
    tokens = {}
    
    for user in users:
        # Create payload matching User Service format
        payload = {
            "userId": user["id"],  # User Service uses "userId"
            "role": user["role"],
            "email": user["email"],
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXPIRE_HOURS),
            "iat": datetime.datetime.utcnow()
        }
        
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        tokens[user["role"]] = {
            "token": token,
            "user_id": user["id"],
            "role": user["role"]
        }
    
    return tokens

if __name__ == "__main__":
    tokens = generate_test_tokens()
    
    print("=== Test JWT Tokens (Matching User Service Format) ===")
    print(f"JWT Secret: {JWT_SECRET}")
    print(f"Algorithm: {JWT_ALGORITHM}")
    print(f"Expire Hours: {JWT_EXPIRE_HOURS}")
    print("\n" + "="*50 + "\n")
    
    for role, data in tokens.items():
        print(f"{role.upper()} Token:")
        print(f"User ID: {data['user_id']}")
        print(f"Role: {data['role']}")
        print(f"Token: {data['token']}")
        print("-" * 50)