from datetime import datetime
from typing import List

from pydantic import BaseModel


class UserBase(BaseModel):
    id: str
    email: str = ''
    is_active: bool = False
    reg_time: datetime = datetime.now()
    last_time: datetime = datetime.now()
    name: str = ''
    gender: str = ''
    birthday: str = ''
    major: str = ''
    class_: str = ''
    entrance_day: str = ''
    college: str = ''

    class Config:
        from_attributes = True
        """启用orm自动转换，允许从数据对象的属性中获取值"""


class User(UserBase):
    password: str


class LoginUser(BaseModel):
    """登录请求的包装"""
    id: str
    password: str


class InactivateUser(BaseModel):
    """失活请求的包装"""
    id: str
    que_name: str = ''


# 创建用于读取/返回的Pydantic模型/模式

class ReturnUser(BaseModel):
    """单用户信息查询响应的包装"""
    status: int
    data: UserBase
    update_time: datetime = datetime.now()


class ReturnUsers(BaseModel):
    """用户列表响应的包装"""
    status: int
    data: List[UserBase]
    update_time: datetime = datetime.now()


class ReturnLogin(BaseModel):
    """登录响应的包装"""
    status: int
    data: UserBase
    update_time: datetime = datetime.now()
