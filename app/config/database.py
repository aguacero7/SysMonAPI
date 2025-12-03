import os
import time
from sqlmodel import Session, SQLModel, create_engine

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://user:mdpsecret@localhost:5432/apidb")
engine = create_engine(DATABASE_URL, echo=True, pool_pre_ping=True, pool_recycle=3600)

def get_session():
    with Session(engine) as session:
        yield session

def init_db():
    for i in range(5):
        try:
            SQLModel.metadata.create_all(engine)
            return
        except Exception as e:
            if i < 4:
                time.sleep(5)
            else:
                raise
