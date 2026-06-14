from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import Optional
from app import models, schemas
from app.auth import get_password_hash
from datetime import datetime


# ─── AUTH ─────────────────────────────────────────────────────────────────────
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, data: schemas.UserRegister):
    user = models.User(
        full_name=data.full_name,
        email=data.email,
        hashed_password=get_password_hash(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ─── DASHBOARD ────────────────────────────────────────────────────────────────
def get_dashboard_stats(db: Session):
    total_customers = db.query(models.Customer).count()
    total_deals = db.query(models.Deal).count()
    won_deals = db.query(models.Deal).filter(models.Deal.stage == "won").count()
    lost_deals = db.query(models.Deal).filter(models.Deal.stage == "lost").count()
    pipeline_value = (
        db.query(func.sum(models.Deal.value))
        .filter(models.Deal.stage.notin_(["won", "lost"]))
        .scalar()
        or 0
    )
    won_value = (
        db.query(func.sum(models.Deal.value))
        .filter(models.Deal.stage == "won")
        .scalar()
        or 0
    )
    total_tasks = db.query(models.Task).count()
    pending_tasks = db.query(models.Task).filter(models.Task.status != "done").count()
    recent_activities = (
        db.query(models.Activity)
        .order_by(models.Activity.created_at.desc())
        .limit(5)
        .all()
    )

    # Pipeline by stage
    stages = ["new", "contacted", "proposal", "negotiation", "won", "lost"]
    pipeline_by_stage = []
    for stage in stages:
        count = db.query(models.Deal).filter(models.Deal.stage == stage).count()
        val = (
            db.query(func.sum(models.Deal.value))
            .filter(models.Deal.stage == stage)
            .scalar()
            or 0
        )
        pipeline_by_stage.append({"stage": stage, "count": count, "value": round(val, 2)})

    # Conversion rate
    conversion_rate = round((won_deals / total_deals * 100) if total_deals > 0 else 0, 1)

    return {
        "total_customers": total_customers,
        "total_deals": total_deals,
        "won_deals": won_deals,
        "lost_deals": lost_deals,
        "pipeline_value": round(pipeline_value, 2),
        "won_value": round(won_value, 2),
        "total_tasks": total_tasks,
        "pending_tasks": pending_tasks,
        "conversion_rate": conversion_rate,
        "recent_activities": recent_activities,
        "pipeline_by_stage": pipeline_by_stage,
    }


# ─── CUSTOMERS ────────────────────────────────────────────────────────────────
def get_customers(db: Session, skip=0, limit=100, search=None):
    q = db.query(models.Customer)
    if search:
        q = q.filter(
            or_(
                models.Customer.name.ilike(f"%{search}%"),
                models.Customer.email.ilike(f"%{search}%"),
                models.Customer.company.ilike(f"%{search}%"),
            )
        )
    return q.order_by(models.Customer.created_at.desc()).offset(skip).limit(limit).all()


def get_customer(db: Session, customer_id: int):
    return db.query(models.Customer).filter(models.Customer.id == customer_id).first()


def create_customer(db: Session, data: schemas.CustomerCreate):
    obj = models.Customer(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_customer(db: Session, customer_id: int, data: schemas.CustomerUpdate):
    obj = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if not obj:
        return None
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    obj.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(obj)
    return obj


def delete_customer(db: Session, customer_id: int):
    obj = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True


# ─── DEALS ────────────────────────────────────────────────────────────────────
def get_deals(db: Session, skip=0, limit=100, stage=None):
    q = db.query(models.Deal)
    if stage:
        q = q.filter(models.Deal.stage == stage)
    return q.order_by(models.Deal.created_at.desc()).offset(skip).limit(limit).all()


def get_deal(db: Session, deal_id: int):
    return db.query(models.Deal).filter(models.Deal.id == deal_id).first()


def create_deal(db: Session, data: schemas.DealCreate):
    obj = models.Deal(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_deal(db: Session, deal_id: int, data: schemas.DealUpdate):
    obj = db.query(models.Deal).filter(models.Deal.id == deal_id).first()
    if not obj:
        return None
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    obj.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(obj)
    return obj


def delete_deal(db: Session, deal_id: int):
    obj = db.query(models.Deal).filter(models.Deal.id == deal_id).first()
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True


# ─── TASKS ────────────────────────────────────────────────────────────────────
def get_tasks(db: Session, skip=0, limit=100, status=None):
    q = db.query(models.Task)
    if status:
        q = q.filter(models.Task.status == status)
    return q.order_by(models.Task.created_at.desc()).offset(skip).limit(limit).all()


def create_task(db: Session, data: schemas.TaskCreate):
    obj = models.Task(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_task(db: Session, task_id: int, data: schemas.TaskUpdate):
    obj = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not obj:
        return None
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    obj.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(obj)
    return obj


def delete_task(db: Session, task_id: int):
    obj = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True


# ─── ACTIVITIES ───────────────────────────────────────────────────────────────
def get_activities(db: Session, skip=0, limit=50):
    return (
        db.query(models.Activity)
        .order_by(models.Activity.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_activity(db: Session, data: schemas.ActivityCreate):
    obj = models.Activity(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj
