from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from time import time

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
    ResetPasswordRequest,
)

from app.utils.hashing import hash_password, verify_password
from app.utils.jwt_handler import (
    create_access_token,
    create_refresh_token,
    verify_access_token,  
)
from app.utils.token_blacklist import blacklisted_tokens
from app.utils.tokens import generate_token

router = APIRouter()

login_attempts = {}


def is_blocked(email: str):
    attempts = login_attempts.get(email, [])
    attempts = [t for t in attempts if time() - t < 60]

    if len(attempts) >= 5:
        return True

    login_attempts[email] = attempts
    return False



@router.post("/signup", response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed = hash_password(user.password)
    token = generate_token()

    new_user = User(
        name=user.name,
        email=user.email,
        hashed_password=hashed,
        verification_token=token,
        is_verified=False,
        is_active=True
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    print(f"VERIFY TOKEN: {token}")

    return new_user



@router.post("/login", response_model=TokenResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not db_user.is_active:
        raise HTTPException(status_code=403, detail="Account deactivated")

    if not db_user.is_verified:
        raise HTTPException(status_code=403, detail="Please verify your email first")

    if is_blocked(user.email):
        raise HTTPException(status_code=429, detail="Too many login attempts. Try later.")

    if not verify_password(user.password, db_user.hashed_password):
        attempts = login_attempts.get(user.email, [])
        attempts.append(time())
        login_attempts[user.email] = attempts
        raise HTTPException(status_code=401, detail="Invalid credentials")

    login_attempts.pop(user.email, None)

    access_token = create_access_token(
        data={
            "user_id": db_user.id,
            "email": db_user.email,
            "role": db_user.role,
        }
    )

    refresh_token = create_refresh_token(
        data={
            "user_id": db_user.id,
            "token_type": "refresh"
        }
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }



@router.post("/refresh", response_model=TokenResponse)
def refresh_token(data: RefreshTokenRequest, db: Session = Depends(get_db)):

    
    if data.refresh_token in blacklisted_tokens:
        raise HTTPException(status_code=401, detail="Token blacklisted")

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

    new_refresh_token = create_refresh_token(
        data={
            "user_id": db_user.id,
            "token_type": "refresh"
        }
    )

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
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

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account deactivated")

    if not user.reset_token_expiry or user.reset_token_expiry < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Token expired")

    user.hashed_password = hash_password(request.new_password)
    user.reset_token = None
    user.reset_token_expiry = None

    db.commit()

    return {"message": "Password reset successful"}



@router.post("/verify-email")
def verify_email(token: str = Query(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.verification_token == token).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid token")

    if user.is_verified:
        return {"message": "Email already verified"}

    user.is_verified = True
    user.verification_token = None

    db.commit()

    return {"message": "Email verified successfully"}
