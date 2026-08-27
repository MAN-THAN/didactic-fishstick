from fastapi import FastAPI
from app.routers import task_routes, auth_routes

app = FastAPI()

app.include_router(task_routes.router)
app.include_router(auth_routes.router)
