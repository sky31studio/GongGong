from http.cookies import Morsel

from aiohttp import ClientSession, CookieJar
from aiohttp.abc import AbstractCookieJar


class HttpSessionHolder:
    """
    HTTP回话持有者

    主要用于存储HTTP回话的相关信息, 提供序列化和反序列化功能
    """

    def __init__(self, cookies: AbstractCookieJar = None, metadata: dict = None):
        """
        初始化 HttpSessionHolder 实例

        :param cookies: aiohttp 的 CookieJar 对象，默认为空
        """
        self.cookie_jar: CookieJar = cookies if cookies is not None else CookieJar()
        self.metadata: dict = metadata if metadata is not None else {}

    def to_dict(self) -> list[dict]:
        """
        将回话信息转换为字典格式

        :return: 包含回话信息的字典
        """
        cookie_list = [
            {
                "key": cookie.key,
                "value": cookie.value,
                "coded_val": cookie.coded_value,
                "host": cookie["domain"],
                "path": cookie["path"],
            } for cookie in self.cookie_jar
        ]
        return cookie_list

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
            morsel.set(cookie["key"], cookie["value"], cookie["coded_val"])
            morsel["domain"] = cookie["host"]
            morsel["path"] = cookie["path"]
            jar.update_cookies({morsel.key: morsel})

        return cls(cookies=jar)

    @classmethod
    def from_aiohttp_session(cls, session: ClientSession) -> "HttpSessionHolder":
        """
        从 aiohttp 的 ClientSession 创建回话持有者实例

        :param session: aiohttp 的 ClientSession 对象
        :return: SessionHolder 实例
        """
        return cls(cookies=session.cookie_jar)

    def to_aiohttp_session(self) -> ClientSession:
        """
        将回话持有者转换为 aiohttp 的 ClientSession

        :return: aiohttp 的 ClientSession 对象
        """
        return ClientSession(cookie_jar=self.cookie_jar)

    @classmethod
    def from_token(cls, token: str) -> "HttpSessionHolder":
        """
        从token字符串反序列化为HttpSessionHolder对象

        :param token: 通过to_token方法生成的字符串
        :return: HttpSessionHolder对象
        """
        import json
        import base64
        json_str = base64.urlsafe_b64decode(token.encode()).decode()
        cookies = json.loads(json_str)
        session = cls.from_dict(cookies["cookies"])
        session.metadata = cookies.get("metadata", {})
        return session

    def to_token(self) -> str:
        """
        将HttpSessionHolder对象序列化为字符串

        :return: 可通过from_token方法反序列化的字符串
        """
        import json
        import base64
        payload = {
            "cookies": self.to_dict(),
            "metadata": self.metadata
        }
        json_str = json.dumps(payload)
        token = base64.urlsafe_b64encode(json_str.encode()).decode()
        return token
