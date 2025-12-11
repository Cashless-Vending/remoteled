"""
Authentication utilities for JWT tokens and password hashing
Simple PostgreSQL-based authentication (no Firebase)
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
import bcrypt
from psycopg2.extras import RealDictCursor
from app.core.database import get_db

# Security configuration
SECRET_KEY = "remoteled-secret-key-2024-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days for demo

# HTTP Bearer token scheme
security = HTTPBearer(auto_error=False)  # Don't auto-error, we'll handle it


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(email: str, admin_id: str) -> str:
    """Create a new JWT access token"""
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": email,
        "id": str(admin_id),
        "exp": expire
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Verify a JWT token and return the payload"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    cursor: RealDictCursor = Depends(get_db)
) -> dict:
    """
    Get the current authenticated user from JWT token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not credentials:
        raise credentials_exception
    
    token = credentials.credentials
    
    # Verify JWT token
    payload = verify_token(token)
    if not payload:
        raise credentials_exception
    
    email: str = payload.get("sub")
    admin_id: str = payload.get("id")
    
    if email is None or admin_id is None:
        raise credentials_exception
    
    # Verify user exists in database
    cursor.execute(
        "SELECT id, email, role FROM admins WHERE id = %s AND email = %s",
        (admin_id, email)
    )
    user = cursor.fetchone()
    
    if user is None:
        raise credentials_exception
    
    return dict(user)


async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    cursor: RealDictCursor = Depends(get_db)
) -> Optional[dict]:
    """
    Get the current user if authenticated, or None if not.
    Useful for endpoints that work both with and without auth.
    """
    if not credentials:
        return None
    
    token = credentials.credentials
    payload = verify_token(token)
    
    if not payload:
        return None
    
    email: str = payload.get("sub")
    admin_id: str = payload.get("id")
    
    if email is None or admin_id is None:
        return None
    
    cursor.execute(
        "SELECT id, email, role FROM admins WHERE id = %s AND email = %s",
        (admin_id, email)
    )
    user = cursor.fetchone()
    
    return dict(user) if user else None
