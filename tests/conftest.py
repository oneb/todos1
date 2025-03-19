import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app")))

from database import Base, get_db
from main import app
import models

TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def test_db():
    """Create test database tables and provide session."""
    Base.metadata.create_all(bind=engine)
    
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield
    
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def client(test_db):
    """Create a test client with the test database."""
    with TestClient(app) as client:
        yield client

@pytest.fixture(scope="function")
def sample_data(test_db):
    """Create sample data in the test database."""
    db = TestingSessionLocal()
    
    task1 = models.Task(username="testuser", title="Test Task 1", state=models.TaskState.TODO)
    task2 = models.Task(username="testuser", title="Test Task 2", state=models.TaskState.DONE)
    task3 = models.Task(username="otheruser", title="Other User Task", state=models.TaskState.TODO)
    
    db.add_all([task1, task2, task3])
    db.commit()
    
    db.refresh(task1)
    db.refresh(task2)
    db.refresh(task3)
    
    task_ids = {
        "task1": task1.id,
        "task2": task2.id,
        "task3": task3.id
    }
    
    db.close()
    
    return task_ids