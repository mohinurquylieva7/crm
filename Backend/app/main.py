import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from app.config import settings
from app.exceptions import validation_exception_handler
from app.routers import (
    health, auth, students, teachers, groups,
    attendance, payments, homework, notifications,
    reports,
)
from app.routers import settings as settings_router
from app.routers import uploads


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
    yield


app = FastAPI(
    title="EduCRM Pro API",
    version="1.0.0",
    description="O'quv markaz boshqaruv tizimi",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.mount("/media", StaticFiles(directory=settings.MEDIA_ROOT), name="media")

ROUTERS = [
    (health.router,              ""),
    (auth.router,                "/api/v1/auth"),
    (students.router,            "/api/v1/students"),
    (teachers.router,            "/api/v1/teachers"),
    (groups.router,              "/api/v1/groups"),
    (attendance.router,          "/api/v1/attendance"),
    (payments.router,            "/api/v1/payments"),
    (homework.router,            "/api/v1/homework"),
    (notifications.router,       "/api/v1/notifications"),
    (reports.router,             "/api/v1/reports"),
    (settings_router.router,     "/api/v1/settings"),
    (uploads.router,             "/api/v1/uploads"),
]

for router, prefix in ROUTERS:
    app.include_router(router, prefix=prefix)
