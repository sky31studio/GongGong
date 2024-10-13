from contextlib import asynccontextmanager

import aioredis
from aioredis import Redis
from fastapi import FastAPI
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
# 1、创建数据库表
Base.metadata.create_all(bind=engine)


# 2、创建依赖项
# Dependency
def get_db():
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
    return await aioredis.from_url(RedisConfig.USER_MANAGER_REDIS_URL, decode_responses=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = await create_redis()
    # print("init redis success")
    yield
    await app.state.redis.close()
