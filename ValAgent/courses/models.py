from sqlalchemy import (
    Column, BigInteger, Integer, String, Text, Boolean, Enum, ForeignKey, TIMESTAMP, CHAR
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from db import Base
import enum

class EnrollmentStatus(str, enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    CANCELLED = "CANCELLED"

class DiscountType(str, enum.Enum):
    PERCENT = "PERCENT"
    AMOUNT = "AMOUNT"

class PaymentStatus(str, enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    FAILED = "FAILED"

class PaymentProvider(str, enum.Enum):
    MOCK = "MOCK"

class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(120), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())

    enrollments = relationship("Enrollment", back_populates="user")

class Course(Base):
    __tablename__ = "courses"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    slug = Column(String(200), nullable=False, unique=True)
    short_desc = Column(String(500), nullable=False)
    long_desc = Column(Text)
    price_cents = Column(Integer, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())

    enrollments = relationship("Enrollment", back_populates="course")

class Discount(Base):
    __tablename__ = "discounts"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    code = Column(String(64), nullable=False, unique=True)
    type = Column(Enum(DiscountType), nullable=False)
    value = Column(String(10), nullable=False)  # store as string to match DECIMAL; cast when using
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())

class Enrollment(Base):
    __tablename__ = "enrollments"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(BigInteger, ForeignKey("courses.id", ondelete="RESTRICT"), nullable=False)
    discount_id = Column(BigInteger, ForeignKey("discounts.id", ondelete="SET NULL"), nullable=True)
    status = Column(Enum(EnrollmentStatus), nullable=False, default=EnrollmentStatus.PENDING)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())

    user = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")

class Payment(Base):
    __tablename__ = "payments"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    enrollment_id = Column(BigInteger, ForeignKey("enrollments.id", ondelete="CASCADE"), nullable=False)
    provider = Column(Enum(PaymentProvider), nullable=False, default=PaymentProvider.MOCK)
    provider_ref = Column(String(128), nullable=False, unique=True)
    amount_cents = Column(Integer, nullable=False)
    currency = Column(CHAR(3), nullable=False, default="USD")
    status = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
