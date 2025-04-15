from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.auth import router as auth_router
from app.users import router as users_router
from app.projects import router as projects_router
from app.tasks import router as tasks_router
from app.sprints import router as sprints_router
from app.database import init_db

app = FastAPI(
    title="Task Management System API",
    description="API for managing projects, tasks and sprints",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None,
    openapi_url="/api/v1/openapi.json"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение статических файлов
app.mount("/static", StaticFiles(directory="static"), name="static")

# Включение роутеров
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(users_router, prefix="/api/v1/users", tags=["Users"])
app.include_router(projects_router, prefix="/api/v1/projects", tags=["Projects"])
app.include_router(tasks_router, prefix="/api/v1/tasks", tags=["Tasks"])
app.include_router(sprints_router, prefix="/api/v1/sprints", tags=["Sprints"])

@app.on_event("startup")
async def startup_event():
    await init_db()