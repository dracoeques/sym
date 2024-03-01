import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine


def local_session():
    POSTGRES_URL = os.getenv("db_url", "localhost")
    POSTGRES_USER = os.getenv("db_user", "postgres")
    POSTGRES_PW = os.getenv("db_password", "")
    POSTGRES_DB = os.getenv("db_name", "")
    #POSTGRES_PORT = os.getenv("db_port", "5432")

    DATABASE_STR = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PW}@{POSTGRES_URL}/{POSTGRES_DB}"

    db_engine = create_engine(DATABASE_STR)
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    return db_engine, session_factory