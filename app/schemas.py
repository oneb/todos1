from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from models import TaskState

class Task(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    state: TaskState
    username: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    state: Optional[TaskState] = TaskState.TODO
    username: str

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    state: Optional[TaskState] = None
    # Username cannot be updated
