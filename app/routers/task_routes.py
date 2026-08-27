from fastapi import APIRouter
from app.services import task_service
from app.schemas.task_schema import TaskCreate, TaskResponse

router = APIRouter(prefix='/tasks', tags=['Tasks'])

@router.get('/')
def get_tasks():
    return task_service.getTasks()

@router.get('/{task_id}', response_model=TaskResponse)
def get_task(task_id : str):
    return task_service.getTask(task_id)

@router.post('/', response_model=TaskResponse)
def create_task(task : TaskCreate):
    return task_service.createTask(task)

@router.put('/{task_id}', response_model=TaskResponse)
def update_task(task_id : str, task : TaskCreate):
    return task_service.updateTask(task_id, task)

@router.delete('/{task_id}', response_model=TaskResponse)
def delete_task(task_id : str):
    return task_service.deleteTask(task_id)

@router.patch('/task_status/{task_id}')
def update_task_status(task_id : str):
    return task_service.updateTaskStatus(task_id)


    

