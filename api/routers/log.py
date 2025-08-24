# api/routers/log.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from core import schemas
from core.database import get_db
from core.repositories.log import LogRepository
from core.services.log import LogService

router = APIRouter(
    prefix="/api/v1",
    tags=["Logs"]
)

def get_log_service(db: Session = Depends(get_db)) -> LogService:
    repo = LogRepository(db)
    return LogService(repo)

@router.get("/log/{task_id}", response_model=List[schemas.Log])
def get_logs_for_task(task_id: str, service: LogService = Depends(get_log_service)):
    return service.get_logs_for_task(task_id)

@router.post("/log", response_model=schemas.Log, status_code=status.HTTP_201_CREATED)
def create_log(log: schemas.LogCreate, service: LogService = Depends(get_log_service)):
    return service.create_log(log)
