from datetime import datetime

from aioredis import Redis
from sqlalchemy.orm import Session

from src.xtu_ems.ems.account import AuthenticationAccount
from src.xtu_ems.ems.ems import QZEducationalManageSystem
from src.xtu_ems.ems.handler.get_student_info import StudentInfoGetter
from src.user_manager import database, schemas
from src.user_manager.config import RedisConfig


# 通过 ID 查询单个用户
def get_user_by_id(db: Session, id: str):
    """
    获取用户信息
    Args:
        db： 数据库会话连接
        id：用户id

    Returns:
        如果用户存在则返回用户信息，否则返回None
    """
    return db.query(database.User).filter(database.User.id == id).first()

# 单例模式
handler = StudentInfoGetter()
ems = QZEducationalManageSystem()

# 通过 ID 激活账户
def activate_user_by_id(db: Session, id: str, password: str):
    """
    通过id激活用户同时更新JSESSIONID
    Args:
        db： 数据库会话连接
        id：用户id
        password：用户密码

    Returns:
        如果登录成功则返回JSESSIONID，否则返回None
    """
    account = AuthenticationAccount(username=id, password=password)

    db_user = get_user_by_id(db, id)
    try:
        session = ems.login(account)

        resp = handler.handler(session).dict()
        # print(resp)
        # for key, value in resp.items():
        #     setattr(db_user, key, value.replace("\xa0", ""))

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
    """
    通过id失活用户
    Args:
        db： 数据库会话连接
        id：用户id

    Returns:
        如果用户存在则标记用户账户失活，否则返回None
    """
    db_user = get_user_by_id(db, id)
    if db_user:
        db_user.is_active = False
        db.commit()  # 提交更改到数据库
        return db_user
    else:
        return None  # 如果用户不存在，返回 None 或抛出异常


# # 查询多个用户
# def get_users(db: Session, skip: int = 0, limit: int = 100):
#     """
#     获取用户列表（已弃用）
#     Args:
#         db： 数据库会话连接
#         skip：数据偏移量
#         limit：限制结果数量
#
#     Returns:
#         如果登录成功则返回JSESSIONID，否则返回None
#     """
#     return db.query(database.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.User):
    """
    通过id激活用户同时更新JSESSIONID
    Args:
        db： 数据库会话连接
        user：用户id

    Returns:
        如果注册成功则返回数据库db_user对象
    """
    # 创建一个 SQLAlchemy 模型实例
    db_user = database.User(
        **{**user.dict(), 'is_active': False, 'reg_time': datetime.now(), 'last_time': datetime.now()})

    # 使用add来将该实例对象添加到数据库。
    db.add(db_user)

    # 使用commit来对数据库的事务提交（以便保存它们）。
    db.commit()
    return db_user


async def cache_session(rd: Redis, session_id: str, user_id: str):
    """
    将JSESSIONID缓存进redis中，键为前缀_学号
    Args:
        db： redis会话连接
        session_id：用户的JSESSIONID

    Returns:
        None
    """

    # 添加数据，time秒后自动清除
    await rd.setex(name=RedisConfig.SESS_PREFIX + user_id, time=RedisConfig.EXPIRE_TIME, value=session_id)
