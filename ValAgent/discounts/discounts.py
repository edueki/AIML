from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from decimal import Decimal
from typing import List, Optional

from deps import get_db, get_current_user
import models
from schemas import (
    DiscountApplyIn, DiscountApplyOut,
    DiscountSeedIn, DiscountOut
)

router = APIRouter(prefix="/discount", tags=["discount"])

def _final_price_cents(price_cents: int, disc_type: Optional[str], disc_value: Optional[Decimal]) -> int:
    if not disc_type or disc_value is None:
        return max(0, int(price_cents))
    if disc_type == "PERCENT":
        pct = float(disc_value)
        pct = max(0.0, min(100.0, pct))
        return max(0, int(round(price_cents * (1.0 - pct / 100.0))))
    # AMOUNT
    amount_cents = int(round(float(disc_value) * 100))
    return max(0, price_cents - amount_cents)


@router.post("/apply", response_model=DiscountApplyOut)
def apply_discount(payload: DiscountApplyIn, db: Session = Depends(get_db)):
    # Course must exist & be active
    course = db.query(models.Course).filter(
        models.Course.id == payload.course_id,
        models.Course.is_active.is_(True)
    ).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    disc = db.query(models.Discount).filter(
        models.Discount.code == payload.code,
        models.Discount.is_active.is_(True)
    ).first()

    if not disc:
        # Training-simple: return original price if code invalid
        return DiscountApplyOut(
            course_id=course.id,
            original_price_cents=course.price_cents,
            discount_id=None,
            discount_type=None,
            discount_value=None,
            final_price_cents=course.price_cents
        )

    final_cents = _final_price_cents(course.price_cents, disc.type.value, disc.value)
    return DiscountApplyOut(
        course_id=course.id,
        original_price_cents=course.price_cents,
        discount_id=disc.id,
        discount_type=disc.type.value,
        discount_value=float(disc.value),
        final_price_cents=final_cents
    )

# ---------- Optional helpers for seeding & viewing during tests ----------

@router.post("/seed", response_model=List[DiscountOut])
def seed_discounts(items: List[DiscountSeedIn], db: Session = Depends(get_db)):
    out: List[DiscountOut] = []
    for it in items:
        # skip duplicate codes
        exists = db.query(models.Discount).filter(models.Discount.code == it.code).first()
        if exists:
            out.append(DiscountOut(
                id=exists.id, code=exists.code, type=exists.type.value,
                value=float(exists.value), is_active=bool(exists.is_active)
            ))
            continue
        obj = models.Discount(code=it.code, type=models.DiscountType(it.type), value=Decimal(str(it.value)), is_active=it.is_active)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        out.append(DiscountOut(
            id=obj.id, code=obj.code, type=obj.type.value, value=float(obj.value), is_active=bool(obj.is_active)
        ))
    return out

@router.get("", response_model=List[DiscountOut])
def list_discounts(db: Session = Depends(get_db)):
    rows = db.query(models.Discount).order_by(models.Discount.id.desc()).all()
    return [
        DiscountOut(
            id=r.id, code=r.code, type=r.type.value, value=float(r.value), is_active=bool(r.is_active)
        ) for r in rows
    ]
