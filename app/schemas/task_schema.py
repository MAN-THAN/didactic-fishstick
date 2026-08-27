from pydantic import BaseModel

class TaskCreate(BaseModel):
    title : str
    description : str | None

class TaskSchema(BaseModel):
    title : str
    description : str | None
    id : str
    createdAt : str
    updatedAt : str | None = None
    isCompleted : bool
    
class TaskResponse(BaseModel):
    msg : str
    task : TaskSchema
   