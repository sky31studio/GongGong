from datetime import datetime

from aioredis import Redis
from sqlalchemy.orm import Session

from user_manager import database, schemas
from user_manager.config import RedisConfig
from xtu_ems.ems.account import AuthenticationAccount
from xtu_ems.ems.ems import QZEducationalManageSystem
from xtu_ems.ems.handler.get_student_info import StudentInfoGetter


def get_user(db: Session, user_id: str):
    return db.query(database.User).filter(database.User.id == user_id).first()


# 通过 ID 查询单个用户
def get_user_by_id(db: Session, id: str):
    """
    通过id查询用户

    Args:
        db: 数据库连接
        id: 用户id

    Returns
        如果用户存在则返回用户信息，否则返回None
    """
    return db.query(database.User).filter(database.User.id == id).first()


# 单例模式
handler = StudentInfoGetter()
ems = QZEducationalManageSystem()


# 通过 ID 激活账户
def activate_user_by_id(db: Session, id: str, password: str):
    """
    通过id激活用户

    Args:
        db: 数据库连接
        id: 用户id
        password: 用户密码

    Returns:
        如果用户存在则返回用户信息，否则返回None
    """
    account = AuthenticationAccount(username=id, password=password)

    db_user = get_user(db, id)
    try:
        session = ems.login(account)

        resp = handler.handler(session).model_dump()

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


def deactivate_user_by_id(db: Session, id: str):
    """
    通过id失活用户
    Args:
        db: 数据库连接
        id: 用户id

    Returns:
        如果用户存在则返回用户信息，否则返回None
    """
    db_user = get_user(db, id)
    if db_user:
        db_user.is_active = False
        db.commit()  # 提交更改到数据库
        return db_user
    else:
        return None  # 如果用户不存在，返回 None 或抛出异常


def get_users(db: Session, skip: int = 0, limit: int = 100):
    """
    查询多个用户

    Args:
        db: 数据库连接
        skip: 跳过的用户数量
        limit: 限制返回的用户数量

    Returns:
        包含用户信息的列表

    """
    return db.query(database.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.User):
    """
    创建用户

    Args:
        db: 数据库连接
        user: 用户信息

    Returns:
        包含用户信息的列表
    """
    db_user = database.User(
        **{**user.model_dump(), 'is_active': False, 'reg_time': datetime.now(), 'last_time': datetime.now()})

    db.add(db_user)

    db.commit()
    return db_user


async def cache_session(rd: Redis, session_id: str, user_id: str):
    """
    缓存session
    Args:
        rd: redis 连接
        session_id: session值
        user_id: 用户id
    """
    await rd.setex(name=f'{RedisConfig.SESS_PREFIX}{user_id}',
                   time=RedisConfig.EXPIRE_TIME,
                   value=session_id)
