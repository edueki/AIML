# enrollments/main.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from deps import get_db
import models
from schemas import EnrollmentCreateIn, EnrollmentCreateOut, EnrollmentOut

router = APIRouter(prefix="", tags=["enrollment"])


@router.post("/enrollment", response_model=EnrollmentCreateOut, status_code=201)
def create_enrollment(
    payload: EnrollmentCreateIn,
    db: Session = Depends(get_db),
):
    """
    Enrollment happens AFTER payment.
    Payload MUST contain:
      - user_id
      - course_id
      - payment_id  (from payment-service)
    """

    # 1) Idempotency: If already enrolled for same user+course, return existing
    existing = (
        db.query(models.Enrollment)
        .filter(
            models.Enrollment.user_id == payload.user_id,
            models.Enrollment.course_id == payload.course_id,
        )
        .first()
    )

    if existing:
        return EnrollmentCreateOut(
            enrollment_id=existing.id,
            status=existing.status,
        )

    # 2) Create new enrollment (PAID, since payment-first flow)
    enroll = models.Enrollment(
        user_id=payload.user_id,
        course_id=payload.course_id,
        payment_id=payload.payment_id,
        status=models.EnrollmentStatus.PAID,
    )
    db.add(enroll)
    db.commit()
    db.refresh(enroll)

    return EnrollmentCreateOut(
        enrollment_id=enroll.id,
        status=enroll.status,
    )


@router.get("/enrollment/{enrollment_id}", response_model=EnrollmentOut)
def get_enrollment(
    enrollment_id: int,
    db: Session = Depends(get_db),
):
    e = db.query(models.Enrollment).filter(
        models.Enrollment.id == enrollment_id
    ).first()

    if not e:
        raise HTTPException(status_code=404, detail="Enrollment not found")

    return EnrollmentOut(
        id=e.id,
        user_id=e.user_id,
        course_id=e.course_id,
        payment_id=e.payment_id,
        status=e.status,
    )
