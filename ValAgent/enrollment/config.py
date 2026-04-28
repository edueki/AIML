import os
from dotenv import load_dotenv
load_dotenv()

class Settings:
    # TEMP: hardcode to prove the app uses TCP, not localhost/socket
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://prreddy:db1234@127.0.0.1:3306/courses"
    )
    JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")
    JWT_ALG = os.getenv("JWT_ALG", "HS256")
    JWT_EXPIRES_MIN = int(os.getenv("JWT_EXPIRES_MIN", "60"))

settings = Settings()
print("DB_URL >>>", settings.DATABASE_URL)  # DEBUG
