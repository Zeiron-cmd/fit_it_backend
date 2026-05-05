from fastapi import FastAPI

from app.database import create_db_and_tables
from app.routers import auth

app = FastAPI(title="Fit it Backend")


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


app.include_router(auth.router)


@app.get("/")
def root():
    return {"message": "Fit it backend is running"}