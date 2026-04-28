from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings

# DEBUG: show effective URL (without password) via engine repr
print("Creating engine for:", settings.DATABASE_URL.replace(":db1234@", ":****@"))

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def fetch_active_courses():
    with engine.connect() as c:
        rows = c.execute(text("""
            SELECT id, title, short_desc, long_desc, price_cents, slug
            FROM courses
            WHERE is_active = 1
            ORDER BY id ASC
        """)).mappings().all()
    return list(rows)
