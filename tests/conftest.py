import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base, get_db
from app.main import app
import os
import shutil

# Use a test-specific SQLite database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """
    Sets up the test database schema and test storage directory.
    Runs once for the entire test session.
    """
    Base.metadata.create_all(bind=engine)
    os.makedirs("test_storage", exist_ok=True)
    
    # Override settings so PDFs are saved in a test folder
    from app.core.config import settings
    settings.storage_dir = "test_storage"
    
    yield # Let tests run
    
    # Teardown after session completes
    Base.metadata.drop_all(bind=engine)
    shutil.rmtree("test_storage", ignore_errors=True)
    if os.path.exists("test.db"):
        try:
            os.remove("test.db")
        except:
            pass

@pytest.fixture
def db():
    """
    Provides a SQLAlchemy session scoped to a single test.
    Transactions are rolled back automatically.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db):
    """
    Provides a FastAPI TestClient with the get_db dependency overridden to use the test DB session.
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass
            
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
