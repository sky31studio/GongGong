from datetime import datetime

from aioredis import Redis
from sqlalchemy.orm import Session

from xtu_ems.ems.account import AuthenticationAccount
from xtu_ems.ems.ems import QZEducationalManageSystem
from xtu_ems.ems.handler.get_student_info import StudentInfoGetter
from . import models, schemas
from .config import RedisConfig


def get_user(db: Session, user_id: str):
    return db.query(models.User).filter(models.User.id == user_id).first()


# 通过 ID 查询单个用户
def get_user_by_id(db: Session, id: str):
    return db.query(models.User).filter(models.User.id == id).first()


# 通过 ID 激活账户
def activate_user_by_id(db: Session, id: str, password: str):
    account = AuthenticationAccount(username=id, password=password)
    ems = QZEducationalManageSystem()
    db_user = get_user(db, id)
    try:
        session = ems.login(account)
        handler = StudentInfoGetter()
        resp = handler.handler(session).dict()

        for key, value in resp.items():
            setattr(db_user, key, value.replace("\xa0", ""))
        db_user.is_active = True
        db_user.password = password
        db_user.last_time = datetime.now()
        # 提交更改
        db.commit()
        return session.session_id
    except Exception as e:
        print(e)

    return None


# 通过 ID 失活账户
def deactivate_user_by_id(db: Session, id: str):
    db_user = get_user(db, id)
    if db_user:
        db_user.is_active = False
        db.commit()  # 提交更改到数据库
        return db_user
    else:
        return None  # 如果用户不存在，返回 None 或抛出异常


# 查询多个用户
def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.User):
    # 使用您的数据创建一个 SQLAlchemy 模型实例。
    db_user = models.User(
        **{**user.model_dump(), 'is_active': False, 'reg_time': datetime.now(), 'last_time': datetime.now()})

    # 使用add来将该实例对象添加到您的数据库。
    db.add(db_user)

    # 使用commit来对数据库的事务提交（以便保存它们）。
    db.commit()
    return db_user


async def cache_session(rd: Redis, session_id: str, user_id: str):
    print(session_id)
    # 添加数据，3600秒后自动清除
    await rd.setex(name=RedisConfig.SESS_PREFIX + user_id, time=RedisConfig.EXPIRE_TIME, value=session_id)
    value = await rd.get(name='vvv')
    print(value)
