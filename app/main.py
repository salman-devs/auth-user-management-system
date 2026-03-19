from fastapi import FastAPI
from app.database import engine
from app import models
from app.routers.auth_router import router as auth_router
from app.routers.user_router import router as user_router


models.Base.metadata.create_all(bind=engine)

app=FastAPI()

app.include_router(auth_router,prefix="/auth",tags=["Auth"])
app.include_router(user_router,prefix="/users",tags=["Users"])