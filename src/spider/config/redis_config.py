from xtu_ems.basic import BaseConfig


class RedisConfig(metaclass=BaseConfig):
    """Redis配置"""

    REDIS_HOST = 'localhost'
    """Redis 主机"""
    REDIS_PORT = 6379
    """Redis 端口"""
    REDIS_PASSWORD = None
    """Redis 密码"""
    REDIS_DB = 0
    """Redis 数据库"""
    REDIS_DECODE_RESPONSES = True
    """Redis 解码响应"""
