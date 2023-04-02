from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URL ="postgresql://postgres:postgres@ktms-database.cms5s3jnyltw.ap-south-1.rds.amazonaws.com:5432/ktms"

engine =create_engine(
    SQLALCHEMY_DATABASE_URL,
    # connect_args={"check_same_thread":False}
    )

SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)

Base = declarative_base()