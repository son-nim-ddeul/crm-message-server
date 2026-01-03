import sqlite_vec
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from src.config import settings
import os

Base = declarative_base()


def load_vec_extension(dbapi_connection, connection_record):
    dbapi_connection.enable_load_extension(True)
    dbapi_connection.load_extension(sqlite_vec.loadable_path())
    dbapi_connection.enable_load_extension(False)


# Ensure database directory exists
db_dir = os.path.dirname(settings.rds_db_path)
if db_dir:
    os.makedirs(db_dir, exist_ok=True)

# RDS Engine
rds_engine = create_engine(
    f"sqlite:///{settings.rds_db_path}",
    connect_args={"check_same_thread": False}
)
RDS_SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=rds_engine)

# Vector DB Engine
vector_engine = create_engine(
    f"sqlite:///{settings.vector_db_path}",
    connect_args={"check_same_thread": False}
)
# Load sqlite-vec extension for the vector engine
event.listen(vector_engine, "connect", load_vec_extension)
Vector_SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=vector_engine)


def get_rds_db():
    db = RDS_SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_vector_db():
    db = Vector_SessionLocal()
    try:
        yield db
    finally:
        db.close()

