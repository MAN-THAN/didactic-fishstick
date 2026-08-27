from pydantic import BaseModel

class UserRegister(BaseModel):
    firstName : str
    lastName : str
    emailId : str
    contactNumber : str
    password : str

class UserLogin(BaseModel):
    contactNumber : str
    password : str