"""配置类，这些配置可以被这个包下的所有代码公用，同时修改配置不影响业务逻辑"""
from basic import BaseConfig


class EMSConfig(metaclass=BaseConfig):
    EMS_BASE_URL: str = "https://jwxt.xtu.edu.cn/jsxsd/"
