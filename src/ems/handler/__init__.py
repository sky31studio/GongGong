from abc import ABC, abstractmethod

import requests
from bs4 import BeautifulSoup

from ems.ems import ZQEducationalManageSystem
from ems.session import Session


class Handler(ABC):
    @abstractmethod
    def handler(self, session: Session, *args, **kwargs):
        pass

    def _get_session(self, session: Session):
        sess = requests.session()
        sess.cookies.set(ZQEducationalManageSystem.SESSION_NAME, session.session_id)
        return sess


class EMSGetter(Handler):
    def handler(self, session: Session, *args, **kwargs):
        """获取学生信息"""
        with self._get_session(session) as ems_session:
            resp = ems_session.get(self.url())
            soup = BeautifulSoup(resp.text, 'html.parser')
            return self._extra_info(soup)

    @abstractmethod
    def url(self):
        pass

    @abstractmethod
    def _extra_info(self, soup: BeautifulSoup):
        table = soup.find_all('table')[-1]
        return self._extra_courses(table)

    def _extra_courses(self, table):
        pass
