# main.py

from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from jose import jwt
from config import settings

class ValidateResponse(BaseModel):
    valid: bool
    sub: str
    iat: int
    exp: int

app = FastAPI(title="AI Course Enrollment API (Training)")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/auth/validate", response_model=ValidateResponse)
def validate_token(authorization: str = Header(None, alias="Authorization")):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")

    token = authorization.split("Bearer ")[1]
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        # jose.jwt raises JWTError for signature/format issues
        raise HTTPException(status_code=401, detail="Invalid token signature or format")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    return ValidateResponse(
        valid=True,
        sub   = payload.get("sub"),
        iat   = payload.get("iat"),
        exp   = payload.get("exp")
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8888, reload=True)
