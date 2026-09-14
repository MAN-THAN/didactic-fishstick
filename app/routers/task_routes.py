from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.task_model import Task

from app.services import task_service
from app.schemas.task_schema import TaskCreate, TaskResponse, TaskUpdate, TaskListResponse
from app.models.user_model import User
from app.dependencies.auth_dependency import get_current_user

router = APIRouter(prefix='/tasks', tags=['Tasks'], dependencies=[Depends(get_current_user)])

@router.get('/', response_model=TaskListResponse)
def get_tasks(search: str | None = None, page : int = Query(1, ge=1), limit : int = Query(10, ge=1, le=100), status: str = 'all', sort : str ='newest', current_user:User = Depends(get_current_user), db: Session = Depends(get_db)):
    return task_service.get_tasks(search, page, limit, status, sort, current_user, db)

@router.get('/{task_id}', response_model=TaskResponse)
def get_task(task_id : int, current_user:User = Depends(get_current_user),  db: Session = Depends(get_db)):
    return task_service.get_task(task_id, current_user, db)

@router.post('/', response_model=TaskResponse)
def create_task(task : TaskCreate, current_user:User = Depends(get_current_user), db: Session = Depends(get_db)):
    return task_service.create_task(task, current_user, db)

@router.put('/{task_id}', response_model=TaskResponse)
def update_task(task_id : int, task : TaskUpdate, current_user:User = Depends(get_current_user), db : Session = Depends(get_db)):
    return task_service.update_task(task_id, task, current_user, db)

@router.delete('/{task_id}')
def delete_task(task_id : int, current_user:User = Depends(get_current_user), db : Session = Depends(get_db)):
    return task_service.delete_task(task_id, current_user, db)

@router.patch('/task_status/{task_id}', response_model=TaskResponse)
def update_task_status(task_id : int, current_user:User = Depends(get_current_user), db : Session = Depends(get_db)):
    return task_service.update_task_status(task_id, current_user, db)


    

