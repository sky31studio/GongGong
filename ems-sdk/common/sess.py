from http.cookies import Morsel

from aiohttp import CookieJar



class HttpSessionHolder:
    """
    HTTP回话持有者

    主要用于存储HTTP回话的相关信息, 提供序列化和反序列化功能
    """
    
    def __init__(self, cookies: CookieJar = None):
        """
        初始化 HttpSessionHolder 实例
        
        :param cookies: HTTP cookies
        """
        self.cookies = cookies if cookies is not None else CookieJar()

    def to_dict(self) -> list[dict]:
        """
        将回话信息转换为字典格式
        
        :return: 包含回话信息的字典
        """
        return [cookie.__dict__ for cookie in self.cookies]

    @classmethod
    def from_dict(cls, cookies: list[dict]) -> "HttpSessionHolder":
        """
        从字典格式创建回话持有者实例
        
        :param cookies: 包含回话信息的字典
        :return: SessionHolder 实例
        """
        jar = CookieJar()
        for cookie in cookies:
            morsel = Morsel()
            morsel.__dict__ = cookie
            jar.update_cookies({morsel.key: morsel})

        return cls(cookies=jar)
