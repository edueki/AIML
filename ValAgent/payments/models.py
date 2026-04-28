from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    Text,
    Boolean,
    Enum,
    TIMESTAMP,
    CHAR,
)
from sqlalchemy.sql import func
from db import Base
import enum


class DiscountType(str, enum.Enum):
    PERCENT = "PERCENT"
    AMOUNT = "AMOUNT"


class Discount(Base):
    __tablename__ = "discounts"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    code = Column(String(64), nullable=False, unique=True)
    type = Column(Enum(DiscountType), nullable=False)
    value = Column(Integer, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class Course(Base):
    __tablename__ = "courses"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    title = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False, unique=True)

    short_desc = Column(String(500), nullable=True)
    long_desc = Column(Text, nullable=True)

    price_cents = Column(Integer, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)


class PaymentStatus(str, enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    FAILED = "FAILED"


class PaymentProvider(str, enum.Enum):
    MOCK = "MOCK"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    # No ForeignKeys — user_id and course_id owned by other services
    user_id = Column(BigInteger, nullable=False)
    course_id = Column(BigInteger, nullable=False)
    discount_id = Column(BigInteger, nullable=True)

    provider = Column(Enum(PaymentProvider), nullable=False, default=PaymentProvider.MOCK)
    provider_ref = Column(String(128), nullable=False, unique=True)

    amount_cents = Column(Integer, nullable=False)
    currency = Column(CHAR(3), nullable=False, default="USD")

    status = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING)

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
