import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models import Base, get_db

# Shared Test Database Configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
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
    Creates a new database session for a test, wrapping it in a transaction.
    The transaction is rolled back after each test to maintain isolation.
    """
    connection = engine.connect()
    transaction = connection.begin()
    db = TestingSessionLocal(bind=connection)

    try:
        yield db
    finally:
        transaction.rollback()  # Rollback the transaction to keep the database clean
        db.close()
        connection.close()


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
