"""
Authentication API endpoints
Handles user registration, login, and profile
"""
from fastapi import APIRouter, Depends, HTTPException, status
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel, EmailStr
from app.core.database import get_db
from app.core.auth import hash_password, verify_password, create_access_token, get_current_user
from app.core.admin_logger import log_admin_action

router = APIRouter(prefix="/auth", tags=["authentication"])


# Request/Response models
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict


class UserResponse(BaseModel):
    id: str
    email: str
    role: str


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(
    data: RegisterRequest,
    cursor: RealDictCursor = Depends(get_db)
):
    """
    Register a new admin user
    """
    # Check if user already exists
    cursor.execute("SELECT id FROM admins WHERE email = %s", (data.email,))
    if cursor.fetchone():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate password strength (basic validation)
    if len(data.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long"
        )
    
    # Hash password and create user
    password_hash = hash_password(data.password)
    
    try:
        cursor.execute(
            """
            INSERT INTO admins (email, password_hash, role)
            VALUES (%s, %s, 'admin')
            RETURNING id, email, role, created_at
            """,
            (data.email, password_hash)
        )
        new_admin = cursor.fetchone()
        cursor.connection.commit()
        
        # Log the registration
        log_admin_action(
            admin_email=new_admin['email'],
            action='REGISTER',
            details=f"New admin registered: {new_admin['email']}",
            admin_id=new_admin['id']
        )
        
        # Create access token
        access_token = create_access_token(new_admin['email'], new_admin['id'])
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": new_admin['id'],
                "email": new_admin['email'],
                "role": new_admin['role']
            }
        }
    except Exception as e:
        cursor.connection.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )


@router.post("/login", response_model=TokenResponse)
def login(
    data: LoginRequest,
    cursor: RealDictCursor = Depends(get_db)
):
    """
    Login with email and password
    Returns JWT access token
    """
    # Find user by email
    cursor.execute(
        "SELECT id, email, password_hash, role FROM admins WHERE email = %s",
        (data.email,)
    )
    admin = cursor.fetchone()
    
    if not admin or not verify_password(data.password, admin['password_hash']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Log the login
    log_admin_action(
        admin_email=admin['email'],
        action='LOGIN',
        details=f"Admin logged in: {admin['email']}",
        admin_id=admin['id']
    )
    
    # Create access token
    access_token = create_access_token(admin['email'], admin['id'])
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": admin['id'],
            "email": admin['email'],
            "role": admin['role']
        }
    }


@router.post("/logout")
def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout (client-side token removal)
    This endpoint mainly serves to log the logout action
    """
    log_admin_action(
        admin_email=current_user['email'],
        action='LOGOUT',
        details=f"Admin logged out: {current_user['email']}",
        admin_id=current_user['id']
    )
    
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get current authenticated user information
    """
    return {
        "id": current_user['id'],
        "email": current_user['email'],
        "role": current_user['role']
    }

