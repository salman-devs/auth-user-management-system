from fastapi import Depends, HTTPException
from app.models import User
from app.routers.user_router import get_current_user


def require_role(role: str):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != role:
            raise HTTPException(status_code=403, detail="Access denied")
        return current_user
    return role_checker