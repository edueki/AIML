from fastapi import FastAPI
import uvicorn
from signup import UserSignup
from users import UserValidation
from  pydantic import BaseModel

app = FastAPI()


class SignUpData(BaseModel):
    username: str
    password: str
    email: str


class LoginData(BaseModel):
    username: str
    password: str


@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/signin")
def signin(data: LoginData):
    obj = UserValidation()
    response = obj.user_validation(data.username)
    if response:
        return {"status": "user exists"}
    else:
        return {"status": "user not exists"}

@app.post("/signup")
def signup(data: SignUpData):
    # print (data)
    obj = UserSignup()
    obj.create_user(data.username, data.password, data.email)
    return {"status": f"user {data.username} created successfully"}

uvicorn.run(app, host="0.0.0.0", port=8000)

