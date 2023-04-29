from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

#remember to expert DB_PASSWORD = "yourpass" before starting uvicorn server. 
# If not, this code line will return None
DB_PASSWORD = os.environ.get('DB_PASSWORD')

# SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"
SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://root:{DB_PASSWORD}@localhost:3306/serversiderendering"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base() 