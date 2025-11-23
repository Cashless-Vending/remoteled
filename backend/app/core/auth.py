"""
Authentication utilities for Firebase ID tokens and password hashing (legacy)
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
import bcrypt
from psycopg2.extras import RealDictCursor
from app.core.database import get_db
from app.services.firebase_admin import firebase_admin_service

# Security configuration (legacy JWT - kept for backward compatibility)
SECRET_KEY = "your-secret-key-change-in-production"  # TODO: Move to environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# HTTP Bearer token scheme
security = HTTPBearer()


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
    """Create a new JWT access token (legacy)"""
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": email,
        "id": admin_id,
        "exp": expire
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    cursor: RealDictCursor = Depends(get_db)
) -> dict:
    """
    Get the current authenticated user from Firebase ID token.
    Falls back to legacy JWT for backward compatibility.
    """
    token = credentials.credentials
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Try Firebase ID token first
    firebase_user = await firebase_admin_service.verify_id_token(token)
    if firebase_user:
        email = firebase_user.get("email")
        uid = firebase_user.get("uid")
        
        if not email or not uid:
            raise credentials_exception
        
        # Check if user exists in database, create if not
        cursor.execute(
            "SELECT id, email, role FROM admins WHERE email = %s",
            (email,)
        )
        user = cursor.fetchone()
        
        if not user:
            # Auto-create admin user for Firebase authenticated users
            cursor.execute(
                """
                INSERT INTO admins (email, password_hash, role)
                VALUES (%s, %s, %s)
                RETURNING id, email, role
                """,
                (email, '', 'admin')
            )
            cursor.connection.commit()
            user = cursor.fetchone()
        
        return dict(user)
    
    # Fall back to legacy JWT token
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        admin_id: str = payload.get("id")
        
        if email is None or admin_id is None:
            raise credentials_exception
            
    except JWTError:
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
