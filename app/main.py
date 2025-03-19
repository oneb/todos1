from fastapi import FastAPI, Depends, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy.orm import Session
import uvicorn
import os
from typing import Optional
from pathlib import Path

from models import Task
import schemas
from database import get_db

app = FastAPI(title="Tasks API")

# Serve the frontend 
frontend_dir = Path(__file__).parent.parent / "frontend"
app.mount("/js", StaticFiles(directory=str(frontend_dir / "js")), name="js")
app.mount("/css", StaticFiles(directory=str(frontend_dir / "css")), name="css")

@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open(frontend_dir / "index.html") as f:
        return f.read()

@app.get("/api/tasks/", response_model=list[schemas.Task])
def read_tasks(
    username: Optional[str] = Query(None, description="Filter tasks by username"),
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """
    List tasks with pagination, optionally filter by username.
    """
    query = db.query(Task)
    if username:
        query = query.filter(Task.username == username)
    tasks = query.offset(skip).limit(limit).all()
    
    return tasks

@app.post("/api/tasks/", response_model=schemas.Task)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    db_task = Task(
        title=task.title, 
        description=task.description,
        state=task.state,
        username=task.username
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.get("/api/tasks/{task_id}", response_model=schemas.Task)
def read_task(
    task_id: int, 
    db: Session = Depends(get_db)
):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@app.put("/api/tasks/{task_id}", response_model=schemas.Task)
def update_task(
    task_id: int, 
    task: schemas.TaskUpdate, 
    db: Session = Depends(get_db)
):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Update fields
    update_data = task.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_task, key, value)
    
    db.commit()
    db.refresh(db_task)
    return db_task

@app.delete("/api/tasks/{task_id}", response_model=schemas.Task)
def delete_task(
    task_id: int, 
    db: Session = Depends(get_db)
):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(db_task)
    db.commit()
    return db_task

if __name__ == "__main__":
    if not (os.path.isfile("/certs/cert.pem") and os.path.isfile("/certs/key.pem")):
        print("error: certificates missing")
        exit(1)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        ssl_keyfile="/certs/key.pem",
        ssl_certfile="/certs/cert.pem"
    )
