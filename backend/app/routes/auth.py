"""
Authentication routes - login, registration, and current user.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.models.teacher import Teacher
from app.schemas.auth import LoginRequest, LoginResponse
from app.schemas.teacher import TeacherCreate, TeacherResponse
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_teacher(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Teacher:
    """
    Dependency to get the current authenticated teacher.
    Validates JWT token and returns Teacher object.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = AuthService.verify_token(token)
    if token_data is None or token_data.teacher_id is None:
        raise credentials_exception
    
    teacher = AuthService.get_teacher_by_id(db, UUID(token_data.teacher_id))
    if teacher is None:
        raise credentials_exception
    
    return teacher


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate teacher and return JWT token.
    Uses phone number as username.
    """
    teacher = AuthService.authenticate_teacher(db, request.phone, request.password)
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid phone or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = AuthService.create_access_token(teacher.id)
    return LoginResponse(access_token=access_token)


@router.post("/register", response_model=TeacherResponse)
def register(request: TeacherCreate, db: Session = Depends(get_db)):
    """
    Register a new teacher account.
    """
    # Check if phone already exists
    existing = db.query(Teacher).filter(Teacher.phone == request.phone).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered"
        )
    
    # Create new teacher
    teacher = Teacher(
        name=request.name,
        phone=request.phone,
        password_hash=AuthService.hash_password(request.password),
        role=request.role,
        language_preference=request.language_preference,
        school_name=request.school_name,
        district=request.district,
        state=request.state,
    )
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    
    return teacher


@router.get("/me", response_model=TeacherResponse)
def get_me(current_teacher: Teacher = Depends(get_current_teacher)):
    """
    Get current authenticated teacher's profile.
    """
    return current_teacher


@router.patch("/me/language", response_model=TeacherResponse)
def update_language(
    language: str,
    current_teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    Update current teacher's language preference.
    """
    if language not in ["en", "kn", "hi"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid language. Must be 'en', 'kn', or 'hi'"
        )
    
    current_teacher.language_preference = language
    db.commit()
    db.refresh(current_teacher)
    return current_teacher
