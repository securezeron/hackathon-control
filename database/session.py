from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Import settings from app.core.config

DATABASE_URL = "postgresql://zeronuser:Zeron_1234@postgres:5432/zero-one-db"

engine = create_engine(DATABASE_URL,pool_timeout=5)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()