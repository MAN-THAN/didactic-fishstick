from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.task_model import Task

from app.services import task_service
from app.schemas.task_schema import TaskCreate, TaskResponse
from app.models.user_model import User
from app.dependencies.auth_dependency import get_current_user
router = APIRouter(prefix='/tasks', tags=['Tasks'], dependencies=[Depends(get_current_user)])

@router.get('/')
def get_tasks(current_user:User = Depends(get_current_user), db: Session = Depends(get_db)):
    return task_service.getTasks(current_user, db)

@router.get('/{task_id}', response_model=TaskResponse)
def get_task(task_id : int,  db: Session = Depends(get_db)):
    return task_service.getTask(task_id, db)

@router.post('/', response_model=TaskResponse)
def create_task(task : TaskCreate, current_user:User = Depends(get_current_user), db: Session = Depends(get_db)):
    return task_service.createTask(task, current_user, db)

@router.put('/{task_id}', response_model=TaskResponse)
def update_task(task_id : int, task : TaskCreate, db : Session = Depends(get_db)):
    return task_service.updateTask(task_id, task, db)

@router.delete('/{task_id}')
def delete_task(task_id : int, db : Session = Depends(get_db)):
    return task_service.deleteTask(task_id, db)

@router.patch('/task_status/{task_id}')
def update_task_status(task_id : int, db : Session = Depends(get_db)):
    return task_service.updateTaskStatus(task_id, db)


    

