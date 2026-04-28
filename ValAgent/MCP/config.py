import os

# --- Base URLs for each micro-service ---
REG_URL        = os.getenv("REG_SERVICE_URL",        "http://localhost:8080")
RAG_URL        = os.getenv("RAG_SERVICE_URL",        "http://localhost:8085")
PAYMENT_URL    = os.getenv("PAYMENT_SERVICE_URL",    "http://localhost:8084")
ENROLLMENT_URL = os.getenv("ENROLL_SERVICE_URL",     "http://localhost:8083")
DISCOUNT_URL   = os.getenv("DISCOUNT_SERVICE_URL",   "http://localhost:8082")
COURSES_URL    = os.getenv("COURSES_SERVICE_URL",    "http://localhost:8081")
EMAIL_URL       = os.getenv("EMAIL_SERVICE_URL",      "http://localhost:8090")
AUTH_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8888")