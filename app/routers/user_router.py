from fastapi import APIRouter,Depends,HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.utils.jwt_handler import verify_access_token

oauth2_scheme=OAuth2PasswordBearer(tokenUrl="/auth/login")

router=APIRouter()

def get_current_user(
        token:str=Depends(oauth2_scheme),
        db:Session=Depends(get_db)
):
    payload=verify_access_token(token)
    
    if not payload:
        raise HTTPException(status_code=401,detail="invalid or expired token")

    user_id=payload.get("user_id")

    if not user_id:
        raise HTTPException(status_code=401,detail="Invalid token payload")
    
    db_user=db.query(User).filter(User.id==user_id).first()

    if not db_user:
        raise HTTPException(status_code=401,detail="User not found")
    return db_user

@router.get("/me")

def read_users_me(current_user:User=Depends(get_current_user)):
    return current_user


def get_current_admin(current_user:User=Depends(get_current_user)):
    if current_user.role!="admin":
        raise HTTPException(status_code=403,detail="Access denied")
    return current_user

@router.get("/all")

def get_all_users(
    current_admin:User=Depends(get_current_admin),
    db:Session=Depends(get_db)
):
    users=db.query(User).all()
    return users
