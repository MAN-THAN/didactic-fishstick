from fastapi import HTTPException
from app.models.task_model import Task
from sqlalchemy import select
from sqlalchemy.orm import Session


def getTasks(current_user, db: Session):
    stmt = select(Task).where(Task.user_id == current_user.id)
    result = db.execute(stmt).scalars().all()
    return {'msg' : 'Successful', 'task_list' : result}

def getTask(task_id, db: Session):
    stmt = select(Task).where(Task.id == task_id)
    result = db.execute(stmt)
    task = result.scalar_one_or_none()
    if(task is None):
        raise HTTPException(status_code=404, detail='Not Found')
    return {'msg' : 'Successful', 'task' : task}

def createTask(task, current_user, db : Session):
    new_task = Task(title = task.title, description = task.description, user_id=current_user.id)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return {
        'msg' : 'Task CREATED SUCCESSFULLY!!!', 'task' : new_task
    }

def updateTask(task_id, updated_task, db : Session):
    stmt = select(Task).where(Task.id == task_id)
    result = db.execute(stmt)
    task = result.scalar_one_or_none()
    if(task is None):
        raise HTTPException(status_code=404, detail='Not Found')
    
    task.title = updated_task.title
    task.description = updated_task.description
    db.commit()
    db.refresh(task)
    return {
        'msg' : f'TaskId {task_id} updated successfully', 'task' : task
    }

def deleteTask(task_id, db : Session):
    stmt = select(Task).where(Task.id == task_id)
    result = db.execute(stmt)
    task = result.scalar_one_or_none()

    if(task is None):
        raise HTTPException(status_code=404, detail='Not Found')
    db.delete(task)
    db.commit()
    return {
        'msg' : f'Taskid {task_id} deleted successfully!!!'
    }

def updateTaskStatus(task_id, db :Session):
    stmt = select(Task).where(Task.id == task_id)
    result = db.execute(stmt)
    task = result.scalar_one_or_none()
    if(task is None):
        raise HTTPException(status_code=404, detail='Not Found')
    
    task.is_completed = not task.is_completed
    db.commit()
    db.refresh(task)
    return {
        'msg' : 'Task status changed successfully!!',
        'task' : task
    }






    

