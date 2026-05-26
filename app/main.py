from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel
from starlette.middleware.sessions import SessionMiddleware

from app.config import get_settings
from app.database import engine
from app.models.meal import DetectedFoodItem, FoodPhoto, MealEntry
from app.models.profile import UserProfile
from app.models.user import User
from app.routers.auth import router as auth_router
from app.routers.meals import router as meals_router
from app.routers.profile import router as profile_router
from app.services.oauth_service import configure_oauth_clients


settings = get_settings()

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET_KEY,
    same_site="lax",
    https_only=False,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8081",
        "http://127.0.0.1:8081",
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:3000",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        settings.FRONTEND_URL,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)
    configure_oauth_clients()


@app.get("/")
def root():
    return {"message": "Fit it backend is running"}


app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(meals_router)
