from abc import ABC, abstractmethod
from typing import Generic, TypeVar

import requests
from bs4 import BeautifulSoup

from xtu_ems.ems.config import RequestConfig
from xtu_ems.ems.ems import QZEducationalManageSystem
from xtu_ems.ems.session import Session

_R = TypeVar("_R")
"""返回值类型"""


class Handler(ABC, Generic[_R]):
    @abstractmethod
    def handler(self, session: Session, *args, **kwargs) -> _R:
        """同步函数处理"""
        pass

    @abstractmethod
    async def async_handler(self, session: Session, *args, **kwargs) -> _R:
        """异步处理"""
        pass

    def _get_session(self, session: Session):
        sess = requests.session()
        sess.cookies.set(QZEducationalManageSystem.SESSION_NAME, session.session_id)
        return sess


class EMSGetter(Handler[_R]):
    def handler(self, session: Session, *args, **kwargs) -> _R:
        """获取学生信息"""
        with self._get_session(session) as ems_session:
            resp = ems_session.get(self.url(), timeout=RequestConfig.XTU_EMS_REQUEST_TIMEOUT)
            soup = BeautifulSoup(resp.text, 'html.parser')
            return self._extra_info(soup)

    async def async_handler(self, session: Session, *args, **kwargs) -> _R:
        """异步获取学生信息"""
        from aiohttp import ClientSession
        async with ClientSession(cookies={QZEducationalManageSystem.SESSION_NAME: session.session_id}) as ems_session:
            resp = await ems_session.get(self.url(), timeout=RequestConfig.XTU_EMS_REQUEST_TIMEOUT)
            soup = BeautifulSoup(await resp.text(), 'html.parser')
            return self._extra_info(soup)

    @abstractmethod
    def url(self):
        pass

    @abstractmethod
    def _extra_info(self, soup: BeautifulSoup):
        pass


class EMSPoster(EMSGetter[_R]):
    def handler(self, session: Session, *args, **kwargs) -> _R:
        """获取学生信息"""
        with self._get_session(session) as ems_session:
            resp = ems_session.post(url=self.url(), data=self._data(), timeout=RequestConfig.XTU_EMS_REQUEST_TIMEOUT)
            soup = BeautifulSoup(resp.text, 'html.parser')
            return self._extra_info(soup)

    async def async_handler(self, session: Session, *args, **kwargs) -> _R:
        """异步获取学生信息"""
        from aiohttp import ClientSession
        async with ClientSession(cookies={QZEducationalManageSystem.SESSION_NAME: session.session_id}) as ems_session:
            resp = await ems_session.post(url=self.url(), data=self._data(),
                                          timeout=RequestConfig.XTU_EMS_REQUEST_TIMEOUT)
            soup = BeautifulSoup(await resp.text(), 'html.parser')
            return self._extra_info(soup)

    @abstractmethod
    def _data(self):
        pass
