from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from app.config.config import settings

load_dotenv() 

DATABASE_URL = settings.DATABASE_URL


# 1. إنشاء الـ Engine (المحرك)
engine = create_engine(DATABASE_URL)

# 2. إنشاء مصنع الجلسات SessionMaker المرتبط بالـ Engine
SessionLocal  = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
