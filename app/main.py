from fastapi import FastAPI
from app.routers import task_routes, auth_routes
from app.database import engine, Base
from app.models.task_model import Task

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(task_routes.router)
# app.include_router(auth_routes.router)
