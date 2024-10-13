"""配置类，这些配置可以被这个包下的所有代码公用，同时修改配置不影响业务逻辑"""
import time

from xtu_ems.basic import BaseConfig



class DatabaseConfig(metaclass=BaseConfig):
    """数据库链接"""
    USER_MANAGER_DATABASE_URL: str = "mysql+pymysql://root:123456@localhost:3306/user_manager"

class RedisConfig(metaclass=BaseConfig):
    """数据库链接"""

    USER_MANAGER_REDIS_URL: str = "redis://:@localhost/0?encoding=utf-8"
    SESS_PREFIX = 'SESS_'
    EXPIRE_TIME=3600

