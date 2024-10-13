from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

# 1、从database.py导入Base类
from .database import Base


# User继承Base类
class User(Base):
    # 表名
    __tablename__ = "users"

    # 2、创建模型属性/列，使用Column来表示 SQLAlchemy 中的默认值。
    id = Column(String, primary_key=True, index=True)
    password = Column(String)
    email = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    last_time = Column(DateTime)
    reg_time = Column(DateTime)
    name = Column(String)
    gender=Column(String)
    birthday=Column(String)
    major=Column(String)
    class_=Column(String)
    entrance_day=Column(String)
    college=Column(String)
    # 3、创建关系
    # 当访问 user 中的属性items时，如 中my_user.items，它将有一个ItemSQLAlchemy 模型列表（来自items表），这些模型具有指向users表中此记录的外键
    # 当您访问my_user.items时，SQLAlchemy 实际上会从items表中的获取一批记录并在此处填充进去。
    # 同样，当访问 Item中的属性owner时，它将包含表中的UserSQLAlchemy 模型users。使用owner_id属性/列及其外键来了解要从users表中获取哪条记录。

