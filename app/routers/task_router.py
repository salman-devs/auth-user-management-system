from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Task
from app.schemas import TaskCreate, TaskResponse
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