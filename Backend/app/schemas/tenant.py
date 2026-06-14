from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import date, datetime
from app.models.tenant import Language, SubscriptionPlan


class TenantSettingsUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    currency: Optional[str] = None
    language: Optional[Language] = None
    working_days: Optional[list[str]] = None
    working_hours: Optional[dict] = None
    telegram_bot_token: Optional[str] = None
    subscription_plan: Optional[SubscriptionPlan] = None
    subscription_expiry: Optional[date] = None


class TenantSettingsOut(BaseModel):
    id: UUID
    name: str
    logo: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    currency: str
    language: Language
    working_days: Optional[list] = None
    working_hours: Optional[dict] = None
    telegram_bot_token: Optional[str] = None
    subscription_plan: SubscriptionPlan
    subscription_expiry: Optional[date] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
