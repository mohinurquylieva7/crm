from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app import schemas, crud
from app.database import Base, engine, get_db, SessionLocal
from app.models import User
from app.auth import (
    verify_password,
    create_access_token,
    get_current_user,
)
from app.seed import seed_database

Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: demo ma'lumotlarni qo'shadi"""
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield


app = FastAPI(title="NexusCRM API", version="2.0.0", description="Professional CRM System", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── AUTH ────────────────────────────────────────────────────────────────────
@app.post("/api/auth/login", response_model=schemas.Token)
def login(data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, data.email)
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(401, "Email yoki parol noto'g'ri")
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer", "user": user}


@app.get("/api/auth/me", response_model=schemas.UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


# ─── USERS (Admin only) ─────────────────────────────────────────────────────
@app.get("/api/users", response_model=List[schemas.UserResponse])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(403, "Faqat admin uchun")
    return db.query(User).order_by(User.created_at.desc()).all()


@app.post("/api/users", response_model=schemas.UserResponse)
def create_user_by_admin(
    data: schemas.UserRegister,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(403, "Faqat admin uchun")
    existing = crud.get_user_by_email(db, data.email)
    if existing:
        raise HTTPException(400, "Bu email allaqachon mavjud")
    return crud.create_user(db, data)


@app.delete("/api/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(403, "Faqat admin uchun")
    if user_id == current_user.id:
        raise HTTPException(400, "O'zingizni o'chira olmaysiz")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "Foydalanuvchi topilmadi")
    db.delete(user)
    db.commit()
    return {"ok": True}


# ─── DASHBOARD ───────────────────────────────────────────────────────────────
@app.get("/api/dashboard/stats")
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.get_dashboard_stats(db)


# ─── CUSTOMERS ───────────────────────────────────────────────────────────────
@app.get("/api/customers", response_model=List[schemas.Customer])
def list_customers(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.get_customers(db, skip=skip, limit=limit, search=search)


@app.post("/api/customers", response_model=schemas.Customer)
def create_customer(
    customer: schemas.CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.create_customer(db, customer)


@app.get("/api/customers/{customer_id}", response_model=schemas.Customer)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    c = crud.get_customer(db, customer_id)
    if not c:
        raise HTTPException(404, "Customer not found")
    return c


@app.put("/api/customers/{customer_id}", response_model=schemas.Customer)
def update_customer(
    customer_id: int,
    data: schemas.CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    c = crud.update_customer(db, customer_id, data)
    if not c:
        raise HTTPException(404, "Customer not found")
    return c


@app.delete("/api/customers/{customer_id}")
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not crud.delete_customer(db, customer_id):
        raise HTTPException(404, "Customer not found")
    return {"ok": True}


# ─── DEALS ───────────────────────────────────────────────────────────────────
@app.get("/api/deals", response_model=List[schemas.Deal])
def list_deals(
    skip: int = 0,
    limit: int = 100,
    stage: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.get_deals(db, skip=skip, limit=limit, stage=stage)


@app.post("/api/deals", response_model=schemas.Deal)
def create_deal(
    deal: schemas.DealCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.create_deal(db, deal)


@app.get("/api/deals/{deal_id}", response_model=schemas.Deal)
def get_deal(
    deal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    d = crud.get_deal(db, deal_id)
    if not d:
        raise HTTPException(404, "Deal not found")
    return d


@app.put("/api/deals/{deal_id}", response_model=schemas.Deal)
def update_deal(
    deal_id: int,
    data: schemas.DealUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    d = crud.update_deal(db, deal_id, data)
    if not d:
        raise HTTPException(404, "Deal not found")
    return d


@app.delete("/api/deals/{deal_id}")
def delete_deal(
    deal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not crud.delete_deal(db, deal_id):
        raise HTTPException(404, "Deal not found")
    return {"ok": True}


# ─── TASKS ───────────────────────────────────────────────────────────────────
@app.get("/api/tasks", response_model=List[schemas.Task])
def list_tasks(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.get_tasks(db, skip=skip, limit=limit, status=status)


@app.post("/api/tasks", response_model=schemas.Task)
def create_task(
    task: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.create_task(db, task)


@app.put("/api/tasks/{task_id}", response_model=schemas.Task)
def update_task(
    task_id: int,
    data: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    t = crud.update_task(db, task_id, data)
    if not t:
        raise HTTPException(404, "Task not found")
    return t


@app.delete("/api/tasks/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not crud.delete_task(db, task_id):
        raise HTTPException(404, "Task not found")
    return {"ok": True}


# ─── ACTIVITIES ──────────────────────────────────────────────────────────────
@app.get("/api/activities", response_model=List[schemas.Activity])
def list_activities(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.get_activities(db, skip=skip, limit=limit)


@app.post("/api/activities", response_model=schemas.Activity)
def create_activity(
    activity: schemas.ActivityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.create_activity(db, activity)


# ─── SERVE FRONTEND ──────────────────────────────────────────────────────────
@app.get("/")
def serve_frontend():
    return FileResponse("index.html")
