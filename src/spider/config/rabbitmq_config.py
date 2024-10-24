from xtu_ems.basic import BaseConfig


class MQConfig(metaclass=BaseConfig):
    """消息队列配置"""

    MQ_HOST = 'localhost'
    """消息队列主机"""
    MQ_PORT = 5672
    """消息队列端口"""
    MQ_USERNAME = 'guest'
    """消息队列用户名"""
    MQ_PASSWORD = 'guest'
    """消息队列密码"""
    MQ_VIRTUAL_HOST = '/'
    """消息队列虚拟主机"""
    MQ_PREFETCH_COUNT = 1
    """消息队列预取数量"""
