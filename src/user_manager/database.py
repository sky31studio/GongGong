from contextlib import asynccontextmanager

import aioredis
from aioredis import Redis
from fastapi import FastAPI
from sqlalchemy import Boolean, Column, String, DateTime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from user_manager.config import DatabaseConfig, RedisConfig

# 设置数据库的URL
SQLALCHEMY_DATABASE_URL = DatabaseConfig.USER_MANAGER_DATABASE_URL
# 创建数据库引擎
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,  # 数据库连接地址
    echo=False,  # 打印SQL语句
    # connect_args={"check_same_thread": False}    # 解决多线程问题  sqlite使用
)
# 会话创建器
SessionLocal = sessionmaker(bind=engine)
# 映射
Base = declarative_base()


# User继承Base类
class User(Base):
    """用户表"""
    # 表名
    __tablename__ = "users"

    id = Column(String(50), primary_key=True, index=True)
    password = Column(String(50))
    email = Column(String(50), unique=True, index=True)
    is_active = Column(Boolean, default=True)
    last_time = Column(DateTime)
    reg_time = Column(DateTime)
    name = Column(String(50))
    gender = Column(String(50))
    birthday = Column(String(50))
    major = Column(String(50))
    class_ = Column(String(50))
    entrance_day = Column(String(50))
    college = Column(String(50))


Base.metadata.create_all(bind=engine)


# 2、创建依赖项
# Dependency
def get_db():
    """获取数据库会话"""
    # 我们需要每个请求有一个独立的数据库会话/连接（SessionLocal），
    db = SessionLocal()
    # 我们的依赖项将创建一个新的 SQLAlchemy SessionLocal，
    # 它将在单个请求中使用，然后在请求完成后关闭它。
    try:
        yield db
    finally:
        print('被关闭了')
        db.close()


async def create_redis() -> Redis:
    """新建redis数据库连接"""
    return await aioredis.from_url(RedisConfig.USER_MANAGER_REDIS_URL, decode_responses=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """将redis绑定在fastapi上"""
    app.state.redis = await create_redis()
    # print("init redis success")
    yield
    await app.state.redis.close()
