from fastapi import FastAPI
from sqlmodel import SQLModel

from app.database import engine
from app.models.user import User
from app.models.profile import UserProfile
from app.models.meal import FoodPhoto, MealEntry, DetectedFoodItem
from app.routers.auth import router as auth_router
from app.routers.profile import router as profile_router
from app.routers.meals import router as meals_router

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Fit it Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:3000",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


@app.get("/")
def root():
    return {"message": "Fit it backend is running"}


app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(meals_router)