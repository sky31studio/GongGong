import logging
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from bs4 import BeautifulSoup

from common.sess import HttpSessionHolder
from qz_ems.config import RequestConfig

_R = TypeVar("_R")
"""返回值类型"""

logger = logging.getLogger('xtu-ems.handler')


class SessionInvalidException(Exception):
    pass


def get_async_session(session: HttpSessionHolder):
    sess = session.to_aiohttp_session()
    sess.headers.setdefault('User-Agent',
                            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                            'Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.41')
    return sess


class Handler(ABC, Generic[_R]):

    @abstractmethod
    async def async_handler(self, session: HttpSessionHolder, *args, **kwargs) -> _R:
        """异步处理"""
        pass


class EMSGetter(Handler[_R]):

    async def async_handler(self, session: HttpSessionHolder, *args, **kwargs) -> _R:
        """异步获取学生信息"""
        async with get_async_session(session) as ems_session:
            logger.debug(f'[{self.__class__.__name__}] 正在异步获取数据-{self.url()}')
            resp = await ems_session.get(self.url(), timeout=RequestConfig.XTU_EMS_REQUEST_TIMEOUT,
                                         allow_redirects=False)
            return self._do_with_response(await resp.text())

    def _do_with_response(self, response):
        """处理响应"""
        try:
            soup = BeautifulSoup(response, 'html.parser')
            return self._extra_info(soup)
        except AttributeError:
            logger.exception(f'[{self.__class__.__name__}] 解析成绩单失败')
            raise SessionInvalidException()
        except IndexError:
            logger.exception(f'[{self.__class__.__name__}] 解析成绩单失败')
            raise SessionInvalidException()

    @abstractmethod
    def url(self):
        pass

    @abstractmethod
    def _extra_info(self, soup: BeautifulSoup):
        pass


class EMSPoster(EMSGetter[_R]):

    async def async_handler(self, session: HttpSessionHolder, *args, **kwargs) -> _R:
        """异步获取学生信息"""
        async with get_async_session(session) as ems_session:
            logger.debug(f'[{self.__class__.__name__}] 正在异步获取数据-{self.url()}')
            resp = await ems_session.post(url=self.url(), data=self._data(),
                                          timeout=RequestConfig.XTU_EMS_REQUEST_TIMEOUT, allow_redirects=False)
            return self._do_with_response(await resp.text())

    @abstractmethod
    def _data(self):
        pass
