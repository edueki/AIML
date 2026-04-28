# app/routers/courses.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional


from deps import get_db
import models
from schemas import CourseOut, CourseListOut
from schemas import CourseCreateIn, CourseCreateOut

router = APIRouter(prefix="/courses", tags=["courses"])

@router.get("", response_model=CourseListOut)
def list_courses(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(default=None, description="Search text"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    include_inactive: bool = False,
):
    query = db.query(models.Course)

    if not include_inactive:
        query = query.filter(models.Course.is_active.is_(True))

    if q:
        # Simple LIKE search (MySQL is case-insensitive with utf8mb4_unicode_ci)
        like = f"%{q}%"
        query = query.filter(
            or_(
                models.Course.title.like(like),
                models.Course.short_desc.like(like),
                models.Course.long_desc.like(like),
            )
        )

    total = query.count()
    rows = (
        query.order_by(models.Course.created_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )

    items = [
        CourseOut(
            id=r.id,
            title=r.title,
            slug=r.slug,
            short_desc=r.short_desc,
            long_desc=r.long_desc,
            price_cents=r.price_cents,
            is_active=bool(r.is_active),
        )
        for r in rows
    ]
    return {"items": items, "total": total}

@router.get("/{course_id}", response_model=CourseOut)
def get_course(course_id: int, db: Session = Depends(get_db)):
    r = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Course not found")
    return CourseOut(
        id=r.id,
        title=r.title,
        slug=r.slug,
        short_desc=r.short_desc,
        long_desc=r.long_desc,
        price_cents=r.price_cents,
        is_active=bool(r.is_active),
    )

@router.post("/seed", response_model=List[CourseCreateOut])
def seed_courses(courses: List[CourseCreateIn], db: Session = Depends(get_db)):
    """
    Insert one or multiple courses quickly for testing/training.
    """
    added = []
    for c in courses:
        # check if slug already exists
        existing = db.query(models.Course).filter(models.Course.slug == c.slug).first()
        if existing:
            continue  # skip duplicates
        obj = models.Course(
            title=c.title,
            slug=c.slug,
            short_desc=c.short_desc,
            long_desc=c.long_desc,
            price_cents=c.price_cents,
            is_active=c.is_active,
        )
        db.add(obj)
        db.commit()
        db.refresh(obj)
        added.append(CourseCreateOut(id=obj.id, title=obj.title))
    return added

