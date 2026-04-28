from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schemas import SignupIn, SignupOut, LoginIn, LoginOut, MeOut
from security import hash_password, verify_password, create_access_token
from deps import get_db, get_current_user
from models import User

router = APIRouter(prefix="", tags=["auth"])

@router.post("/signup", response_model=SignupOut, status_code=201)
def signup(payload: SignupIn, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail={
                "ok": False,
                "message": "Email already registered. Please use a different email or sign in."
            },
        )

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        name=payload.name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "ok": True,
        "status_code": 201,
        "message": f"User '{user.name}' registered successfully.",
        "data": {
            "user_id": user.id,
            "email": user.email,
            "name": user.name
        }
    }

@router.post("/login", response_model=LoginOut)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail={
                "ok": False,
                "message": "Invalid email or password. Please check your credentials and try again."
            },
        )

    token = create_access_token(sub=str(user.id))

    return {
        "ok": True,
        "status_code": 200,
        "message": f"Login successful. Welcome back, {user.name}!",
        "data": {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "user_id": user.id,
                "email": user.email,
                "name": user.name
            }
        }
    }