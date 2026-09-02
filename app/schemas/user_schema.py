from pydantic import BaseModel
from datetime import datetime

class User_Response(BaseModel):
    first_name : str
    last_name : str
    email : str
    created_at : datetime

    model_config = {
        "from_attributes": True
    }
