import time, jwt
import os
from datetime import datetime, timezone

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzYyMDg1NTQwLCJleHAiOjE3NjIwODkxNDB9.vK0ykYPVtPwZ56aQ_ExkII95YzAaFBE9V8_buaFxhAE"
secret = os.getenv("JWT_SECRET", "dev-secret-change-me")
alg = os.getenv("JWT_ALG", "HS256")

try:
    decoded = jwt.decode(token, secret, algorithms=[alg])
    print("Decoded payload:", decoded)
except jwt.ExpiredSignatureError:
    print("Token expired!")
except jwt.InvalidTokenError as e:
    print("Invalid token:", e)

# Compare exp vs current time
parts = token.split(".")
import base64, json
payload = json.loads(base64.urlsafe_b64decode(parts[1] + "=="))
exp = payload["exp"]
print("Exp timestamp:", exp)
print("Current timestamp:", int(time.time()))
print("Expires in seconds:", exp - int(time.time()))
