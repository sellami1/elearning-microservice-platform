from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from fastapi import HTTPException, status, Header, Depends
from .config import get_settings

settings = get_settings()

def create_jwt_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT token (matching User Service format)"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    # Match User Service format: { userId: payload.id, role: payload.role }
    if "userId" in to_encode and "sub" in to_encode:
        to_encode["userId"] = to_encode["sub"]
        del to_encode["sub"]
    
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return encoded_jwt

def verify_jwt_token(token: str) -> Dict[str, Any]:
    """Verify JWT token (expecting User Service format: { userId, role })"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        
        # Check for User Service token format (userId instead of sub)
        user_id = payload.get("userId")
        if not user_id:
            # Fallback to standard JWT 'sub' claim
            user_id = payload.get("sub")
            if not user_id:
                raise credentials_exception
        
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """
    Extract and validate JWT token from Authorization header
    Returns user info or raises HTTPException
    """
    if authorization is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Convert to string and strip whitespace
    auth_header = str(authorization).strip()
    
    # Check if it starts with "Bearer "
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme. Use 'Bearer <token>'",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract token
    token = auth_header[7:]  # Remove "Bearer " prefix
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Validate token
    payload = verify_jwt_token(token)
    
    # Extract user info from JWT payload (User Service format: userId, role)
    user_id = payload.get("userId") or payload.get("sub")  # Try userId first, then sub
    role = payload.get("role", "student")  # student, instructor, admin
    email = payload.get("email", "")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload: missing user ID",
        )
    
    # Check if role is valid
    valid_roles = ["student", "instructor", "admin"]
    if role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid role in token. Must be one of: {', '.join(valid_roles)}"
        )
    
    return {
        "user_id": str(user_id),  # Ensure it's string (MongoDB ObjectId as string)
        "role": role,
        "email": email,
        "token_payload": payload  # Include full payload for debugging
    }

def require_role(required_role: str):
    """
    Dependency to check if user has required role
    """
    def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
        user_role = current_user.get("role", "student")
        
        # Admin can do anything
        if user_role == "admin":
            return current_user
        
        # Check if user has required role
        if user_role != required_role:
            allowed_roles = [required_role]
            if required_role != "admin":
                allowed_roles.append("admin")
                
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of these roles: {', '.join(allowed_roles)}. You have role: {user_role}"
            )
        return current_user
    return role_checker

def get_current_instructor(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Convenience dependency for instructor role"""
    if current_user["role"] not in ["instructor", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requires instructor or admin role"
        )
    return current_user

def get_current_admin(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Convenience dependency for admin role"""
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requires admin role"
        )
    return current_user

def get_current_student(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Convenience dependency for student role"""
    if current_user["role"] not in ["student", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requires student or admin role"
        )
    return current_user