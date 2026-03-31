from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.database import get_db
from app.models import User

from app.schemas import (
    LogoutRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
    ForgotPasswordRequest,
)

from app.utils.hashing import hash_password, verify_password
from app.utils.jwt_handler import (
    create_access_token,
    create_refresh_token,
    verify_access_token,
)
from app.utils.token_blacklist import blacklisted_tokens
from app.utils.tokens import generate_token
from app.schemas import ResetPasswordRequest
router = APIRouter()



@router.post("/signup", response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed = hash_password(user.password)

    new_user = User(
        name=user.name,
        email=user.email,
        hashed_password=hashed,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user



@router.post("/login", response_model=TokenResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    
    if not db_user.is_active:
        raise HTTPException(status_code=403, detail="Account deactivated")

    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(
        data={
            "user_id": db_user.id,
            "email": db_user.email,
            "role": db_user.role,
        }
    )

    refresh_token = create_refresh_token(
        data={
            "user_id": db_user.id
        }
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }



@router.post("/refresh", response_model=TokenResponse)
def refresh_token(data: RefreshTokenRequest, db: Session = Depends(get_db)):
    payload = verify_access_token(data.refresh_token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    if payload.get("token_type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")

    user_id = payload.get("user_id")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid refresh token payload")

    db_user = db.query(User).filter(User.id == user_id).first()

    if not db_user:
        raise HTTPException(status_code=401, detail="User not found")

    
    if not db_user.is_active:
        raise HTTPException(status_code=403, detail="Account deactivated")

    new_access_token = create_access_token(
        data={
            "user_id": db_user.id,
            "email": db_user.email,
            "role": db_user.role,
        }
    )

    return {
        "access_token": new_access_token,
        "refresh_token": None,
        "token_type": "bearer",
    }



@router.post("/logout")
def logout(data: LogoutRequest):
    payload = verify_access_token(data.refresh_token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    if payload.get("token_type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")

    blacklisted_tokens.add(data.refresh_token)

    return {"message": "Logged out successfully"}



@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()

    
    if not user or not user.is_active:
        return {"message": "If email exists, reset link sent"}

    token = generate_token()

    user.reset_token = token
    user.reset_token_expiry = datetime.utcnow() + timedelta(minutes=15)

    db.commit()

    print(f"RESET TOKEN: {token}")

    return {"message": "Reset link sent"}

@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.reset_token == request.token).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid token")

    if user.reset_token_expiry < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Token expired")

    
    user.hashed_password = hash_password(request.new_password)

    
    user.reset_token = None
    user.reset_token_expiry = None

    db.commit()

    return {"message": "Password reset successful"}