"""Initial migration — create all tables

Revision ID: 0001
Revises:
Create Date: 2024-01-01 00:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column(
            "role",
            sa.Enum("superadmin", "admin", "teacher", "student", "parent", name="userrole"),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), default=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # 2. refresh_tokens
    op.create_table(
        "refresh_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("token_hash", sa.String(64), unique=True, nullable=False),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked", sa.Boolean(), default=False, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # 3. tenant_settings
    op.create_table(
        "tenant_settings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("logo", sa.String(500), nullable=True),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("address", sa.String(500), nullable=True),
        sa.Column("currency", sa.String(10), default="UZS", nullable=False),
        sa.Column(
            "language",
            sa.Enum("uz", "ru", "en", name="language"),
            default="uz",
            nullable=False,
        ),
        sa.Column("working_days", postgresql.JSONB(), nullable=True),
        sa.Column("working_hours", postgresql.JSONB(), nullable=True),
        sa.Column("telegram_bot_token", sa.String(255), nullable=True),
        sa.Column(
            "subscription_plan",
            sa.Enum("free", "starter", "pro", "enterprise", name="subscriptionplan"),
            default="free",
            nullable=False,
        ),
        sa.Column("subscription_expiry", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # 4. teachers
    op.create_table(
        "teachers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("email", sa.String(255), unique=True, nullable=True),
        sa.Column("subjects", postgresql.JSONB(), nullable=True),
        sa.Column("salary", sa.Integer(), default=0, nullable=False),
        sa.Column(
            "salary_type",
            sa.Enum("fixed", "percent", name="salarytype"),
            default="fixed",
            nullable=False,
        ),
        sa.Column("salary_percent", sa.Float(), nullable=True),
        sa.Column("joined_date", sa.Date(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("active", "inactive", name="teacherstatus"),
            default="active",
            nullable=False,
        ),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("avatar", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # 5. students
    op.create_table(
        "students",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("parent_phone", sa.String(50), nullable=True),
        sa.Column("parent_name", sa.String(200), nullable=True),
        sa.Column("address", sa.String(500), nullable=True),
        sa.Column("birth_date", sa.Date(), nullable=True),
        sa.Column("enrolled_date", sa.Date(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("active", "inactive", "graduated", "frozen", name="studentstatus"),
            default="active",
            nullable=False,
        ),
        sa.Column("balance", sa.Integer(), default=0, nullable=False),
        sa.Column("total_paid", sa.Integer(), default=0, nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("avatar", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # 6. groups
    op.create_table(
        "groups",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("subject", sa.String(255), nullable=False),
        sa.Column(
            "teacher_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("teachers.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("days", postgresql.JSONB(), nullable=True),
        sa.Column("start_time", sa.String(5), nullable=True),
        sa.Column("end_time", sa.String(5), nullable=True),
        sa.Column("room", sa.String(100), nullable=True),
        sa.Column("max_students", sa.Integer(), default=12, nullable=False),
        sa.Column("monthly_fee", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("active", "inactive", "completed", name="groupstatus"),
            default="active",
            nullable=False,
        ),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("level", sa.String(100), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # 7. student_groups (M2M)
    op.create_table(
        "student_groups",
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("students.id", ondelete="CASCADE"), nullable=False),
        sa.Column("group_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("groups.id", ondelete="CASCADE"), nullable=False),
        sa.Column("enrolled_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("student_id", "group_id"),
    )

    # 8. attendance_records
    op.create_table(
        "attendance_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("group_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("groups.id", ondelete="CASCADE"), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("taken_by", sa.String(255), nullable=True),
        sa.Column("records", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("group_id", "date", name="uq_attendance_group_date"),
    )

    # 9. payments
    op.create_table(
        "payments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("students.id", ondelete="CASCADE"), nullable=False),
        sa.Column("group_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("groups.id", ondelete="CASCADE"), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("discount", sa.Integer(), default=0, nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("month", sa.String(20), nullable=True),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column(
            "method",
            sa.Enum("cash", "card", "transfer", name="paymentmethod"),
            default="cash",
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("paid", "partial", "pending", "overdue", name="paymentstatus"),
            default="paid",
            nullable=False,
        ),
        sa.Column("received_by", sa.String(255), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # 10. homeworks
    op.create_table(
        "homeworks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("group_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("groups.id", ondelete="CASCADE"), nullable=False),
        sa.Column("teacher_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("assigned_date", sa.Date(), nullable=True),
        sa.Column(
            "type",
            sa.Enum("homework", "exam", "test", "project", name="homeworktype"),
            default="homework",
            nullable=False,
        ),
        sa.Column("max_score", sa.Integer(), default=100, nullable=False),
        sa.Column("results", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # 11. notifications
    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column(
            "type",
            sa.Enum("info", "success", "warning", "error", name="notificationtype"),
            default="info",
            nullable=False,
        ),
        sa.Column("is_read", sa.Boolean(), default=False, nullable=False),
        sa.Column("date", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("link", sa.String(500), nullable=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=True,
        ),
    )

    # Indexes
    op.create_index("ix_students_status", "students", ["status"])
    op.create_index("ix_groups_status", "groups", ["status"])
    op.create_index("ix_payments_student_id", "payments", ["student_id"])
    op.create_index("ix_payments_date", "payments", ["date"])
    op.create_index("ix_attendance_records_group_date", "attendance_records", ["group_id", "date"])
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])


def downgrade() -> None:
    op.drop_table("notifications")
    op.drop_table("homeworks")
    op.drop_table("payments")
    op.drop_table("attendance_records")
    op.drop_table("student_groups")
    op.drop_table("groups")
    op.drop_table("students")
    op.drop_table("teachers")
    op.drop_table("tenant_settings")
    op.drop_table("refresh_tokens")
    op.drop_table("users")

    for enum_name in [
        "userrole", "language", "subscriptionplan", "salarytype",
        "teacherstatus", "studentstatus", "groupstatus",
        "paymentmethod", "paymentstatus", "homeworktype", "notificationtype",
    ]:
        sa.Enum(name=enum_name).drop(op.get_bind(), checkfirst=True)
