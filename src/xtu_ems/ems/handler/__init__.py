from abc import ABC, abstractmethod

import requests
from bs4 import BeautifulSoup

from xtu_ems.ems.config import RequestConfig
from xtu_ems.ems.ems import QZEducationalManageSystem
from xtu_ems.ems.session import Session


class Handler(ABC):
    @abstractmethod
    def handler(self, session: Session, *args, **kwargs):
        pass

    def _get_session(self, session: Session):
        sess = requests.session()
        sess.cookies.set(QZEducationalManageSystem.SESSION_NAME, session.session_id)
        return sess


class EMSGetter(Handler):
    def handler(self, session: Session, *args, **kwargs):
        """获取学生信息"""
        with self._get_session(session) as ems_session:
            resp = ems_session.get(self.url(), timeout=RequestConfig.XTU_EMS_REQUEST_TIMEOUT)
            soup = BeautifulSoup(resp.text, 'html.parser')
            return self._extra_info(soup)

    @abstractmethod
    def url(self):
        pass

    @abstractmethod
    def _extra_info(self, soup: BeautifulSoup):
        pass


class EMSPoster(EMSGetter):
    def handler(self, session: Session, *args, **kwargs):
        """获取学生信息"""
        with self._get_session(session) as ems_session:
            resp = ems_session.post(self.url(), self._data(), timeout=RequestConfig.XTU_EMS_REQUEST_TIMEOUT)
            soup = BeautifulSoup(resp.text, 'html.parser')
            return self._extra_info(soup)

    @abstractmethod
    def _data(self):
        pass
