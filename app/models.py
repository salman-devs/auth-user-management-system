from datetime import datetime

from sqlalchemy import Column,Integer,String,DateTime,Boolean,ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    __tablename__="users"
    
    id = Column(Integer,primary_key=True,index=True)
    name = Column(String(100),nullable=False)
    email = Column(String(100),unique=True,index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20),default="user")
    created_at = Column(DateTime,default=datetime.utcnow)

    tasks=relationship("Task", back_populates="owner", cascade="all, delete")



class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    completed = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 

    owner = relationship("User", back_populates="tasks")
