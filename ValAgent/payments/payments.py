# payments/main.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import time

from deps import get_db
import models
from schemas import PaymentIntentIn, PaymentIntentOut

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("", response_model=PaymentIntentOut)
def create_payment_intent(
    payload: PaymentIntentIn,
    db: Session = Depends(get_db),
):
    # 1) Course must exist & be active
    course = (
        db.query(models.Course)
        .filter(models.Course.id == payload.course_id)
        .first()
    )
    if not course or not course.is_active:
        raise HTTPException(status_code=400, detail="Course inactive or missing")

    # 2) Basic validation on amount
    if payload.amount_cents <= 0:
        raise HTTPException(status_code=400, detail="Invalid payment amount")

    # 3) Idempotency: if already have a PAID payment for same user+course+amount, reuse it
    existing = (
        db.query(models.Payment)
        .filter(
            models.Payment.user_id == payload.user_id,
            models.Payment.course_id == payload.course_id,
            models.Payment.amount_cents == payload.amount_cents,
        )
        .order_by(models.Payment.id.desc())
        .first()
    )
    if existing and existing.status == models.PaymentStatus.PAID:
        return PaymentIntentOut(
            payment_id=existing.id,
            user_id=existing.user_id,
            course_id=existing.course_id,
            provider=existing.provider.value,
            provider_ref=existing.provider_ref,
            amount_cents=existing.amount_cents,
            currency=existing.currency,
            status=existing.status.value,
        )

    # 4) MOCK provider: create and mark PAID immediately
    provider_ref = f"MOCK-{int(time.time() * 1000)}"
    pay = models.Payment(
        user_id=payload.user_id,
        course_id=payload.course_id,
        provider=models.PaymentProvider.MOCK,
        provider_ref=provider_ref,
        amount_cents=payload.amount_cents,
        currency="USD",
        status=models.PaymentStatus.PAID,
    )
    db.add(pay)
    db.commit()
    db.refresh(pay)

    return PaymentIntentOut(
        payment_id=pay.id,
        user_id=pay.user_id,
        course_id=pay.course_id,
        provider=pay.provider.value,
        provider_ref=pay.provider_ref,
        amount_cents=pay.amount_cents,
        currency=pay.currency,
        status=pay.status.value,
    )
