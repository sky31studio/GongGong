"""教务系统模块"""
import json
from abc import ABC, abstractmethod

import requests

from ems.account import AuthenticationAccount
from ems.config import XTUEMSConfig
from ems.session import Session
from util.captcha import ImageDetector


class EducationalManageSystem(ABC):
    """教务系统类"""

    @abstractmethod
    def login(self, account: AuthenticationAccount) -> Session:
        """教务系统登陆，返回登陆session"""
        pass

    @abstractmethod
    def get_courses(self, session: Session):
        """从校务系统中获取课程"""
        pass

    @abstractmethod
    def get_scores(self, session: Session):
        """从教务系统中获取成绩"""
        pass

    @abstractmethod
    def get_exams(self, session: Session):
        """从校务系统中获取考试安排"""
        pass


class ZQEducationalManageSystem(EducationalManageSystem):
    """
    智强教务系统
    """
    SESSION_NAME = "JSESSIONID"

    def __init__(self) -> None:
        super().__init__()
        self.captcha = ImageDetector()

    def login(self, account: AuthenticationAccount) -> Session:
        with requests.session() as ems_session:
            resp = ems_session.get(XTUEMSConfig.XTU_EMS_CAPTCHA_URL)
            session_id = resp.cookies.get(ZQEducationalManageSystem.SESSION_NAME)
            session = Session(session_id=session_id)
            captcha = self.captcha.verify(resp.content)
            resp = ems_session.post(XTUEMSConfig.XTU_EMS_SIG_URL)
            signature = json.loads(resp.content).get("data")
            encoded = self._signature(account.username, account.password, signature)
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            resp = ems_session.post(XTUEMSConfig.XTU_EMS_LOGIN_URL, data={
                "USERNAME": account.username,
                "PASSWORD": account.password,
                "encoded": encoded,
                "RANDOMCODE": captcha,
            }, headers=headers, allow_redirects=False)
            if resp.status_code != 302:
                raise Exception("登陆失败")
        return session

    def _signature(self, username: str, password: str, signature: str):
        """
        智强教务系统签名算法
        Args:
            username: 用户名
            password: 密码
            signature: 加密签名

        Returns:
            返回签名后的密码

        """
        # 将data按照'#'分割成列表
        split = signature.split("#")
        # 创建code字符串
        code = username + "%%%" + password
        # 初始化编码结果的StringBuilder（在Python中使用列表模拟）
        encoded = []
        # 获取code的长度
        length = len(code)
        # 初始化偏移量b
        b = 0
        # 遍历code中的每个字符
        for i in range(length):
            if i < 20:
                # 追加code中的当前字符
                encoded.append(code[i])
                # 追加split[0]中从b开始的由split[1][i]指定数量的字符
                for _ in range(ord(split[1][i]) - ord('0')):
                    encoded.append(split[0][b])
                    b += 1
            else:
                # 追加code从索引20开始的剩余部分
                encoded.extend(code[20:])
                break

        # 将列表转换为字符串并返回
        return ''.join(encoded)

    def get_courses(self, session: Session):
        pass

    def get_scores(self, session: Session):
        pass

    def get_exams(self, session: Session):
        pass
