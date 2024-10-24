"""配置类，这些配置可以被这个包下的所有代码公用，同时修改配置不影响业务逻辑"""

from xtu_ems.basic import BaseConfig


class DatabaseConfig(metaclass=BaseConfig):
    USER_MANAGER_DATABASE_URL: str = "mysql+pymysql://root:123456@localhost:3306/user_manager"
    """数据库基础地址"""


class RedisConfig(metaclass=BaseConfig):
    """Redis数据库链接"""
    USER_MANAGER_REDIS_URL: str = "redis://:@localhost/0?encoding=utf-8"
    """redis基础地址"""
    SESS_PREFIX = 'SESS_'
    """储存在redis的session的key格式为<SESS_PREFIX>_<student_id>"""
    EXPIRE_TIME = 3600
    """session过期时间"""
