# api/routers/task.py
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session
from typing import List
from core import schemas
from core.database import get_db
from core.repositories.task import TaskRepository
from core.services.task import TaskService

router = APIRouter(
    prefix="/api/v1",
    tags=["Tasks"]
)

def get_task_service(db: Session = Depends(get_db)) -> TaskService:
    repo = TaskRepository(db)
    return TaskService(repo)

@router.get("/tasks", response_model=List[schemas.Task])
def get_all_tasks(service: TaskService = Depends(get_task_service)):
    return service.get_all_tasks()

@router.post("/task", response_model=schemas.Task, status_code=status.HTTP_201_CREATED)
def create_task(task: schemas.TaskCreate, service: TaskService = Depends(get_task_service)):
    return service.create_task(task)

@router.put("/task/{task_id}", response_model=schemas.Task)
def update_task(task_id: str, task_update: schemas.TaskUpdate, service: TaskService = Depends(get_task_service)):
    return service.update_task(task_id, task_update)

@router.delete("/task/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str, service: TaskService = Depends(get_task_service)):
    service.delete_task(task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/tasks/stats", response_model=schemas.TaskStats)
def get_task_stats(service: TaskService = Depends(get_task_service)):
    return service.get_task_stats()
