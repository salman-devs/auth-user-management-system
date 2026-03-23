from fastapi import FastAPI
from app import models
from app.database import engine
from app.routers.auth_router import router as auth_router
from app.routers.user_router import router as user_router
from app.routers.task_router import router as task_router

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Auth User Management System",
    version="1.0.0",
    description="FastAPI backend for authentication, user management, JWT auth, and role-based access control.",
)

@app.get("/")
def root():
    return {"message": "Auth User Management System API is running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}



app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(user_router, prefix="/users", tags=["Users"])
app.include_router(task_router, prefix="/tasks",tags=["Tasks"])