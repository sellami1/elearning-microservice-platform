from typing import Optional
from jose import jwt, JWTError, ExpiredSignatureError
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .config import get_settings

settings = get_settings()

JWT_SECRET_KEY = settings.jwt_secret
JWT_ALGORITHM = settings.jwt_algorithm

security = HTTPBearer()

def decode_jwt(token: str):
    """
    Decodes a JWT token using the HS256 algorithm and the shared secret.
    Maps Node.js camelCase 'userId' to Pythonic 'user_id'.
    """
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
        )

        return {
            "user_id": payload.get("userId"),
            "role": payload.get("role"),
        }

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    return decode_jwt(token)

security_optional = HTTPBearer(auto_error=False)

def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_optional)):
    if credentials:
        return decode_jwt(credentials.credentials)
    return None

def require_role(allowed_roles: list[str]):
    """
    Dependency factor for role-based access control.
    """
    def role_checker(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role")
        
        if user_role not in allowed_roles:
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role {user_role} not authorized. Requires one of: {allowed_roles}"
            )
        return current_user
    return role_checker

def get_current_instructor(current_user: dict = Depends(require_role(["instructor"]))):
    return current_user

def get_current_student(current_user: dict = Depends(require_role(["student"]))):
    return current_user
