import datetime

from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from . import crud, schemas
from .crud import deactivate_user_by_id, cache_session
from .database import get_db, lifespan

app = FastAPI(lifespan=lifespan)


# 获取用户列表
@app.get("/users", response_model=schemas.ReturnUsers)
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return schemas.ReturnUsers(status=1, data=users)


# 获取单个用户信息
@app.get("/users/{user_id}", response_model=schemas.ReturnUser)
def read_user(user_id: str, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        return schemas.ReturnUser(status=0, data=schemas.UserBase(id=user_id))

    return schemas.ReturnUser(status=1, data=db_user)


# 登录
@app.post("/users/login", response_model=schemas.ReturnLogin)
async def login_user(user: schemas.LoginUser, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_id(db, id=user.id)

    if db_user:
        if db_user.password == user.password and db_user.is_active:
            db_user.last_time = datetime.datetime.now()
            db.commit()
            return schemas.ReturnLogin(status=1, data=db_user)
    else:
        # 用户不存在 创建用户
        db_user = crud.create_user(db=db, user=schemas.User(**user.model_dump()))
    # 激活账号并更新账户信息
    session_id = crud.activate_user_by_id(db, id=user.id, password=user.password)
    if session_id:
        await cache_session(app.state.redis, session_id, user.id)
        return schemas.ReturnLogin(status=1, data=db_user)
    return schemas.ReturnLogin(status=0, data=db_user)


@app.post("/users/inactivate", response_model=schemas.ReturnLogin)
async def inactivate_user(user: schemas.InactivateUser, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_id(db, id=user.id)
    if db_user:

        session_id = crud.activate_user_by_id(db, id=user.id, password=user.password)
        if session_id:
            await cache_session(app.state.redis, session_id, user.id)
            return schemas.ReturnLogin(status=1, data=db_user)
        else:
            deactivate_user_by_id(db, id=user.id)
        return schemas.ReturnLogin(status=1, data=db_user)

    return schemas.ReturnLogin(status=0, data=schemas.UserBase(id=user.id))
