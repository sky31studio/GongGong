"""
通用的异常定义

包括下面这些异常：
- ServiceUnavailableException: 服务不可用异常
- InvalidUsernameOrPasswordException: 用户名或密码无效异常
- AccountNotFoundException: 账号未找到异常
- AccountDisabledException: 账号被禁用异常
- SessionInvalidException: 会话无效异常
"""


class UninitializedAccountException(Exception):
    """未初始化账号异常"""

    def __init__(self, account, message: str = "账号未初始化"):
        """
        初始化 UninitializedAccountException 实例

        :param account: 账号
        :param message: 错误信息
        """
        self.account = account
        """账号"""
        self.message = message
        """错误信息"""
        super().__init__(self.message)

    def __str__(self):
        return f"UninitializedAccountError: {self.message} (Account: {self.account})"


class ServiceUnavailableException(Exception):
    """服务不可用异常"""

    def __init__(self, service_name: str, message: str = "服务不可用"):
        """
        初始化 ServiceUnavailableException 实例

        :param service_name: 服务名称
        :param message: 错误信息
        """
        self.service_name = service_name
        """服务名称"""
        self.message = message
        """错误信息"""
        super().__init__(self.message)

    def __str__(self):
        return f"ServiceUnavailableError: {self.message} (Service: {self.service_name})"


class InvalidUsernameOrPasswordException(Exception):
    """用户名或密码无效异常"""

    def __init__(self, username: str, message: str = "用户名或密码无效"):
        """
        初始化 InvalidUsernameOrPasswordException 实例

        :param username: 用户名
        :param message: 错误信息
        """
        self.username = username
        """用户名"""
        self.message = message
        """错误信息"""
        super().__init__(self.message)

    def __str__(self):
        return f"InvalidUsernameOrPasswordError: {self.message} (Username: {self.username})"


class AccountNotFoundException(Exception):
    """账号未找到异常"""

    def __init__(self, account: str, message: str = "账号未找到"):
        """
        初始化 AccountNotFoundException 实例

        :param account: 账号
        :param message: 错误信息
        """
        self.account = account
        """账号"""
        self.message = message
        """错误信息"""
        super().__init__(self.message)

    def __str__(self):
        return f"AccountNotFoundError: {self.message} (Account: {self.account})"


class AccountDisabledException(Exception):
    """账号被禁用异常"""

    def __init__(self, account: str, message: str = "账号被禁用"):
        """
        初始化 AccountDisabledException 实例

        :param account: 账号
        :param message: 错误信息
        """
        self.account = account
        """账号"""
        self.message = message
        """错误信息"""
        super().__init__(self.message)

    def __str__(self):
        return f"AccountDisabledError: {self.message} (Account: {self.account})"


class SessionInvalidException(Exception):
    """会话无效异常"""

    def __init__(self, message: str = "会话无效"):
        """
        初始化 SessionInvalidException 实例

        :param message: 错误信息
        """
        self.message = message
        """错误信息"""
        super().__init__(self.message)

    def __str__(self):
        return f"SessionInvalidError: {self.message}"


class ZfAccountNotFoundException(Exception):
    """正方教务系统中账号未找到异常"""

    def __init__(self, message: str = "账号未找到"):
        """
        初始化 AccountNotFoundException 实例

        :param message: 错误信息
        """
        """账号"""
        self.message = message
        """错误信息"""
        super().__init__(self.message)

    def __str__(self):
        return f"AccountNotFoundError: {self.message}"


class GmsAccountNotFoundException(Exception):
    """研究生教务系统中账号未找到异常"""

    def __init__(self, message: str = "账号未找到"):
        """
        初始化 AccountNotFoundException 实例

        :param message: 错误信息
        """
        """账号"""
        self.message = message
        """错误信息"""
        super().__init__(self.message)

    def __str__(self):
        return f"AccountNotFoundError: {self.message}"
