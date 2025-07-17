from pydantic import BaseModel,EmailStr
from sqlalchemy import UUID
from typing import Optional
from uuid import UUID


class RegisterUser(BaseModel):
    name:str
    email:EmailStr
    password:str
    description:Optional[str]

    class Config:
        orm_mode = True

class GetUsers(BaseModel):
    name:str
    description:Optional[str]

    class Config:
        orm_mode = True


class RegisterGroup(BaseModel):
    name:str
    admin_user:str
    description:Optional[str]

    class Config:
        orm_mode = True

# class HumanMessage(BaseModel):
#     message:str

# class AgentMessage(BaseModel):
#     message:str

# class SendRequest(BaseModel):
#     to_user:UUID


class SendRequest(BaseModel):
    from_id:UUID
    to_name:str
    group_id:UUID

    class Config:
        orm_mode = True



class GetTheUser(BaseModel):
    name:str
    email:EmailStr
    hashed_password:str
    description:Optional[str]

    class Config:
        orm_mode = True

