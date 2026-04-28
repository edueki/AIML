# test_mysql_conn.py
from sqlalchemy import create_engine, text
engine = create_engine("mysql+pymysql://prreddy:db1234@127.0.0.1:3306/courses", pool_pre_ping=True)
with engine.connect() as c:
    print(c.execute(text("SELECT 1")).scalar())
