from fastapi import HTTPException
import uuid
from datetime import datetime, timezone
task_list = []

def getTasks():
    return {'msg' : 'Successful', 'task_list' : task_list}

def getTask(task_id):
    task = next((task for task in task_list if task['id'] == task_id), None)
    if(task is None):
        raise HTTPException(status_code=404, detail='Task Not found')

    return {'msg' : 'Successful', 'task' : task}

def createTask(task):
    newTask = {'title': task.title, 'description' : task.description, 'id' : str(uuid.uuid4()), 'isCompleted' : False, 'createdAt' : datetime.now(timezone.utc).isoformat()}
    task_list.append(newTask)
    return {
        'msg' : 'Task CREATED SUCCESSFULLY!!!', 'task' : newTask
    }

def updateTask(task_id, updated_task):
    task = next((task for task in task_list if task['id'] == task_id), None)
    if(task is None):
        raise HTTPException(status_code=404, detail='Task Not found')
    task['title'] = updated_task.title
    task['description'] = updated_task.description
    task['updatedAt'] = datetime.now(timezone.utc).isoformat()
    return {
        'msg' : f'TaskId {task_id} updated successfully', 'task' : task
    }

def deleteTask(task_id):
    global task_list
    task = next((task for task in task_list if task['id'] == task_id), None)
    if(task is None):
        raise HTTPException(status_code=404, detail='Task Not found')
    task_list = [task for task in task_list if task['id'] != task_id]
    return {
        'msg' : f'Taskid {task_id} deleted successfully!!!', 'task' : task
    }

def updateTaskStatus(task_id):
    task = next((task for task in task_list if task['id'] == task_id), None)
    if(task is None):
        raise HTTPException(status_code=404, detail='Task Not Found!')
    
    task['isCompleted'] = not task['isCompleted']
    return {
        'msg' : 'Task status changed successfully!!',
        'task' : task
    }






    

