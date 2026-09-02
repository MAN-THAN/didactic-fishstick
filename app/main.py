from fastapi import FastAPI
from app.routers import task_routes, auth_routes, user_routes
from app.database import engine, Base
from app.models.task_model import Task
# cors middleware
from fastapi.middleware.cors import CORSMiddleware


Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(task_routes.router)
app.include_router(auth_routes.router)
app.include_router(user_routes.router)
