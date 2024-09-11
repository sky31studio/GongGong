"""公共基础类"""
import os


class BaseConfig(type):
    """这个配置类的元类使得配置能够和环境变量结合，这样便于docker等容器化部署时进行单项配置"""

    def __new__(mcs, name, bases, attrs):
        """创建"""
        for key, value in attrs.items():
            if key in os.environ and not callable(value):
                attrs[key] = os.environ[key]
        return type.__new__(mcs, name, bases, attrs)
