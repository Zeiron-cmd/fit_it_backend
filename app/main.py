from fastapi import FastAPI
from sqlmodel import SQLModel

from app.database import engine
from app.models.user import User
from app.models.profile import UserProfile
from app.routers.auth import router as auth_router
from app.routers.profile import router as profile_router


app = FastAPI(title="Fit it Backend")


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


@app.get("/")
def root():
    return {"message": "Fit it backend is running"}


app.include_router(auth_router)
app.include_router(profile_router)