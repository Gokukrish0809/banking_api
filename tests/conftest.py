from decimal import Decimal
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.main import app
from app.models.accounts import Customer, CustomerInput

# in‐memory SQLite for fast, ephemeral state
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Create all tables once at session start
@pytest.fixture(scope="session")
def create_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# Clear all tables before each test function
@pytest.fixture(autouse=True)
def clear_tables(create_test_db):
    sess = TestingSessionLocal()

    for tbl in reversed(Base.metadata.sorted_tables):
        sess.execute(tbl.delete())
    sess.commit()
    sess.close()


# Provide a clean session to each test
@pytest.fixture
def db_session(create_test_db):
    sess = TestingSessionLocal()
    try:
        yield sess
    finally:
        sess.close()


# Override FastAPI get_db dependency for endpoint tests
@pytest.fixture
def client(db_session, monkeypatch):
    def _get_test_db():
        try:
            yield db_session
        finally:
            pass

    monkeypatch.setattr("app.database.get_db", _get_test_db)
    return TestClient(app)


@pytest.fixture
def mock_customer_record():
    return Customer(name="Bob", email="bob@example.com")


@pytest.fixture
def mock_customer_input():
    return CustomerInput(
        name="Bob", email="bob@example.com", initial_deposit=Decimal("100.0")
    )
