from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Task
from app.schemas import TaskCreate, TaskResponse,TaskUpdate
from app.routers.user_router import get_current_user

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", response_model=TaskResponse)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    new_task = Task(
        title=task.title,
        user_id=current_user.id
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task


@router.get("/", response_model=list[TaskResponse])
def get_tasks(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    tasks = db.query(Task).filter(Task.user_id == current_user.id).all()
    return tasks


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task: TaskUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    db_task = db.query(Task).filter(Task.id == task_id).first()

    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    
    if db_task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    if task.title is not None:
        db_task.title = task.title

    if task.completed is not None:
        db_task.completed = task.completed

    db.commit()
    db.refresh(db_task)

    return db_task