"""教务系统模块"""
from abc import ABC, abstractmethod

from ems.account import AuthenticationAccount
from ems.session import Session


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
    """智强教务系统"""

    def login(self, account: AuthenticationAccount) -> Session:
        pass

    def get_courses(self, session: Session):
        pass

    def get_scores(self, session: Session):
        pass

    def get_exams(self, session: Session):
        pass
