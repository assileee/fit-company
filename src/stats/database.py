from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import os

DATABASE_URL = os.getenv("STATS_DATABASE_URL", "postgresql://postgres@stats-db:5432/stats")

engine = create_engine(DATABASE_URL)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()

def init_db():
    import models
    Base.metadata.create_all(bind=engine)
