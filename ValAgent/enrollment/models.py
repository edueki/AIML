# models.py
from sqlalchemy import Column, BigInteger, Integer, String, Enum
from db import Base
import enum


class EnrollmentStatus(str, enum.Enum):
    PAID = "PAID"
    PENDING = "PENDING"
    CANCELLED = "CANCELLED"


class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    user_id = Column(BigInteger, nullable=False)
    course_id = Column(BigInteger, nullable=False)
    payment_id = Column(BigInteger, nullable=False)

    status = Column(
        Enum(EnrollmentStatus),
        nullable=False,
        default=EnrollmentStatus.PAID,
    )
