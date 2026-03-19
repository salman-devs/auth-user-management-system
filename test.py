from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from app.database import get_db
from app.utils.jwt_handler import verify_access_token

oauth_scheme=OAuth2PasswordBearer(tokenUrl="/auth/login")


router=APIRouter()

def get_current_user(
        token:str=Depends(oauth_scheme),
        db:Session=Depends(get_db)       
):
    payload=verify_access_token(token)

    if not payload:
        raise HTTPException(status_code=401,detail="invalid or expire token")
    user_id=payload.get("user_id")

    if not user_id:
        raise HTTPException(status_code=401,detail="invalid token payload")
    
    db_user=db.query()