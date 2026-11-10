from sqlalchemy import create_engine,URL
from sqlalchemy.orm import sessionmaker,DeclarativeBase,Session
from typing import Annotated
from fastapi import Depends
from ..core.config import Config

settings = Config()

DB_URL = URL.create(
    drivername= settings.drivername,
    database= settings.database,
    host=settings.host,
    password=settings.password,
    port=settings.port,
    username= settings.uname
)

engine = create_engine(DB_URL)

SessionLocal = sessionmaker(bind=engine,autoflush=False)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try :
        yield db
    finally :
        db.close()

db_service = Annotated[Session,Depends(get_db)]