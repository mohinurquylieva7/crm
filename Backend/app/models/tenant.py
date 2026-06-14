import enum
import uuid
from datetime import date
from sqlalchemy import String, Date, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from app.database import Base
from app.models.mixins import TimestampMixin


class Language(str, enum.Enum):
    uz = "uz"
    ru = "ru"
    en = "en"


class SubscriptionPlan(str, enum.Enum):
    free = "free"
    starter = "starter"
    pro = "pro"
    enterprise = "enterprise"


class TenantSettings(TimestampMixin, Base):
    __tablename__ = "tenant_settings"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    logo: Mapped[str | None] = mapped_column(String(500), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="UZS", nullable=False)
    language: Mapped[Language] = mapped_column(
        SAEnum(Language), default=Language.uz, nullable=False
    )
    working_days: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    working_hours: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    telegram_bot_token: Mapped[str | None] = mapped_column(String(255), nullable=True)
    subscription_plan: Mapped[SubscriptionPlan] = mapped_column(
        SAEnum(SubscriptionPlan), default=SubscriptionPlan.free, nullable=False
    )
    subscription_expiry: Mapped[date | None] = mapped_column(Date, nullable=True)
