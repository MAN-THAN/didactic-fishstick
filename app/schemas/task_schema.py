from pydantic import BaseModel
from datetime import datetime

class TaskCreate(BaseModel):
    title : str
    description : str | None = None

class TaskSchema(BaseModel):
    title : str
    description : str | None = None
    id : int
    created_at : datetime
    updated_at : datetime
    is_completed : bool

    model_config = {
        "from_attributes": True
    }
    
class TaskResponse(BaseModel):
    msg : str
    task : TaskSchema
   