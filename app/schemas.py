from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=8,max_length=72)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8,max_length=72)


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    created_at: datetime

    class Config:
        from_attributes = True

class RefreshTokenRequest(BaseModel):
    refresh_token: str
    

class LogoutRequest(BaseModel):
    refresh_token: str
    

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"


class TaskCreate(BaseModel):
    title: str

class TaskResponse(BaseModel):
    id: int
    title: str
    completed: bool
    created_at: datetime

    class Config:
        from_attributes = True
        
class TaskUpdate(BaseModel):
    title: str | None = None
    completed: bool | None = None

class UserUpdate(BaseModel):
    name: str | None = None
    password: str | None = None
    
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
    