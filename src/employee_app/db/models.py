"""C-6 tables (architecture 6.1). No update or delete operation exists for
employees or audit rows anywhere in the application."""

from datetime import date, datetime, timezone

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Index, Integer, String, TypeDecorator
from sqlalchemy.engine import Dialect
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

NAME_LENGTH = 100
EMAIL_LENGTH = 254
ROLE_HR_ADMINISTRATOR = "hr_administrator"


class UTCDateTime(TypeDecorator[datetime]):
    """Stores UTC as naive text (SQLite has no zones) and returns aware UTC."""

    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value: datetime | None, dialect: Dialect) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            raise ValueError("naive datetime is not allowed")
        return value.astimezone(timezone.utc).replace(tzinfo=None)

    def process_result_value(self, value: datetime | None, dialect: Dialect) -> datetime | None:
        return None if value is None else value.replace(tzinfo=timezone.utc)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(NAME_LENGTH))
    username_normalized: Mapped[str] = mapped_column(String(NAME_LENGTH))
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(32), default=ROLE_HR_ADMINISTRATOR)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    auth_version: Mapped[int] = mapped_column(Integer, default=0)
    failed_login_count: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime)

    __table_args__ = (Index("ux_user_username_normalized", "username_normalized", unique=True),)


class Employee(Base):
    __tablename__ = "employee"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(NAME_LENGTH))
    last_name: Mapped[str] = mapped_column(String(NAME_LENGTH))
    email: Mapped[str] = mapped_column(String(EMAIL_LENGTH))
    email_normalized: Mapped[str] = mapped_column(String(EMAIL_LENGTH))
    phone: Mapped[str] = mapped_column(String(10))
    department: Mapped[str] = mapped_column(String(NAME_LENGTH))
    job_title: Mapped[str] = mapped_column(String(NAME_LENGTH))
    joining_date: Mapped[date] = mapped_column(Date)

    __table_args__ = (Index("ux_employee_email_normalized", "email_normalized", unique=True),)


class AuditRecord(Base):
    __tablename__ = "audit_record"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employee.id"))
    created_by_user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    created_at: Mapped[datetime] = mapped_column(UTCDateTime)

    __table_args__ = (Index("ux_audit_record_employee_id", "employee_id", unique=True),)
