import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.models import Base, get_db

# Shared Test Database Configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"  # Use sqlite:///:memory: for In-Memory tests
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def setup_database():
    """
    Creates the Test Database and drops it after the tests are done.
    This fixture is shared across all tests.
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(setup_database):
    """
    Creates a new database session for a test, which is rolled back after the test.
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module")
def client_with_db(setup_database):
    """
    Creates a TestClient with a database session.
    This is shared across all test files.
    """

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    # Override the dependency in FastAPI app
    app.dependency_overrides[get_db] = override_get_db

    client = TestClient(app)
    yield client

    # Clear the overrides after tests are done
    app.dependency_overrides.clear()


@pytest.fixture(scope="function", autouse=True)
def clear_tables(db_session):
    """
    Clears all tables before each test to ensure isolation.
    """
    meta = Base.metadata
    for table in reversed(meta.sorted_tables):
        db_session.execute(table.delete())
    db_session.commit()
