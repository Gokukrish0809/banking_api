from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, declarative_base
from config import db_url
import os

engine = create_engine(db_url)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()

def get_db():
    """
    Dependency function to provide a database session

    Attributes 
    Session : A database session instance
    """
    db = SessionLocal()
    try :
        yield db
    finally :
        db.close()