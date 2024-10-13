from datetime import datetime
from typing import List, Optional

# 1、创建初始 Pydantic模型/模式
from pydantic import BaseModel


# 1、创建初始 Pydantic模型/模式
class UserBase(BaseModel):
    id: str
    email: str=''
    is_active: bool=False
    reg_time: datetime=datetime.now()
    last_time: datetime=datetime.now()
    name: str=''
    gender: str=''
    birthday: str=''
    major: str=''
    class_: str=''
    entrance_day: str=''
    college: str=''
    class Config:
        from_attributes=True

class User(UserBase):
    password: str

class LoginUser(BaseModel):
    id: str
    password: str

class InactivateUser(BaseModel):
    id: str
    que_name:str=''

# 2、创建用于读取/返回的Pydantic模型/模式

class ReturnUser(BaseModel):
    status:int
    data:UserBase
    update_time:datetime=datetime.now()

class ReturnUsers(BaseModel):
    status:int
    data:List[UserBase]
    update_time:datetime=datetime.now()

class ReturnLogin(BaseModel):
    status:int
    data:UserBase
    update_time:datetime=datetime.now()

