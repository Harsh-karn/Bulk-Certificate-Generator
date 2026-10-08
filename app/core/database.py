from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Create SQLAlchemy engine. 
# check_same_thread=False is needed for SQLite to work correctly with FastAPI's async/multi-thread environment
engine = create_engine(
    settings.database_url, 
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
)

# SessionLocal is a factory for creating new database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our SQLAlchemy models
Base = declarative_base()

def get_db():
    """
    Dependency function to provide a database session for a request.
    Ensures the session is closed after the request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
