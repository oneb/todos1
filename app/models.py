from sqlalchemy import Column, Integer, String, Enum, DateTime
from sqlalchemy.sql import func
import enum
from database import Base, engine

class TaskState(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"  # Currently unused
    DONE = "done"

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    title = Column(String)
    description = Column(String, nullable=True)  # Currently unused
    state = Column(Enum(TaskState), default=TaskState.TODO)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
