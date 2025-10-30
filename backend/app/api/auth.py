"""
Authentication API endpoints
Login, registration, logout, token refresh
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    get_current_user,
    User,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS
)

router = APIRouter(prefix="/auth", tags=["authentication"])


# Request/Response models
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    role: str = "admin"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class UserResponse(BaseModel):
    id: str
    email: str
    role: str
    created_at: str


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    request: RegisterRequest,
    cursor: RealDictCursor = Depends(get_db)
):
    """
    Register a new admin user
    Note: In production, this should be protected or disabled after initial setup
    """
    # Check if user already exists
    cursor.execute(
        "SELECT id FROM admins WHERE email = %s",
        (request.email,)
    )
    existing_user = cursor.fetchone()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    password_hash = get_password_hash(request.password)
    
    # Insert new admin
    cursor.execute(
        """
        INSERT INTO admins (email, password_hash, role)
        VALUES (%s, %s, %s)
        RETURNING id, email, role, created_at
        """,
        (request.email, password_hash, request.role)
    )
    user = cursor.fetchone()
    
    return UserResponse(
        id=str(user["id"]),
        email=user["email"],
        role=user["role"],
        created_at=user["created_at"].isoformat()
    )


@router.post("/login", response_model=TokenResponse)
def login(
    request: LoginRequest,
    response: Response,
    cursor: RealDictCursor = Depends(get_db)
):
    """
    Login with email and password
    Returns JWT access token and sets httpOnly refresh token cookie
    """
    # Find user by email
    cursor.execute(
        "SELECT id, email, password_hash, role FROM admins WHERE email = %s",
        (request.email,)
    )
    user = cursor.fetchone()
    
    # Verify user exists and password is correct
    if not user or not verify_password(request.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    cursor.execute(
        "UPDATE admins SET last_login = %s WHERE id = %s",
        (datetime.utcnow(), user["id"])
    )
    
    # Create tokens
    token_data = {"sub": user["email"], "user_id": str(user["id"])}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    # Set refresh token in httpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60  # 7 days in seconds
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert to seconds
        user={
            "id": str(user["id"]),
            "email": user["email"],
            "role": user["role"]
        }
    )


@router.post("/logout")
def logout(response: Response):
    """
    Logout user by clearing the refresh token cookie
    """
    response.delete_cookie(key="refresh_token")
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information
    Requires valid JWT token
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        role=current_user.role,
        created_at=""  # Not fetched in get_current_user
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_access_token(
    refresh_token: str,
    response: Response,
    cursor: RealDictCursor = Depends(get_db)
):
    """
    Refresh access token using refresh token from cookie
    """
    from app.core.auth import decode_token
    
    # Decode refresh token
    try:
        token_data = decode_token(refresh_token)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Fetch user
    cursor.execute(
        "SELECT id, email, role FROM admins WHERE email = %s",
        (token_data.email,)
    )
    user = cursor.fetchone()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Create new access token
    new_token_data = {"sub": user["email"], "user_id": str(user["id"])}
    access_token = create_access_token(new_token_data)
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user={
            "id": str(user["id"]),
            "email": user["email"],
            "role": user["role"]
        }
    )

