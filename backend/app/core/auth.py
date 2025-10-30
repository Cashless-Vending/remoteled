"""
Authentication utilities for RemoteLED Admin Console
Handles JWT tokens, password hashing, and user verification
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from psycopg2.extras import RealDictCursor
from app.core.database import get_db
from pydantic import BaseModel

# Security configuration
SECRET_KEY = "your-secret-key-change-in-production"  # TODO: Move to env variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Bearer token security
security = HTTPBearer()


class TokenData(BaseModel):
    """Token payload data"""
    email: Optional[str] = None
    user_id: Optional[str] = None


class User(BaseModel):
    """User model for authentication"""
    id: str
    email: str
    role: str


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password for storing"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> TokenData:
    """Decode and verify a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token_data = TokenData(email=email, user_id=user_id)
        return token_data
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    cursor: RealDictCursor = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user from JWT token
    Use this to protect endpoints: user = Depends(get_current_user)
    """
    token = credentials.credentials
    token_data = decode_token(token)
    
    # Fetch user from database
    cursor.execute(
        "SELECT id, email, role FROM admins WHERE email = %s",
        (token_data.email,)
    )
    user_data = cursor.fetchone()
    
    if user_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return User(**user_data)


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    cursor: RealDictCursor = Depends(get_db)
) -> Optional[User]:
    """
    Dependency to optionally get the current user (doesn't raise if not authenticated)
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials, cursor)
    except HTTPException:
        return None

