import logging

from xtu_ems.common.exception import *
from xtu_ems.common.sess import HttpSessionHolder
from xtu_ems.zf_ems.config import *

logger = logging.getLogger(__name__)


async def sso_auth(session: HttpSessionHolder) -> HttpSessionHolder:
    """
    使用统一身份认证系统进行登录验证

    :param session: HttpSessionHolder 对象，用于存储会话信息
    :return: 更新后的 HttpSessionHolder 对象
    """
    async with session.to_aiohttp_session() as http_session:
        target_url = "https://jw.xtu.edu.cn/sso/zfiotlogin"
        async with http_session.get(target_url) as response:
            logger.debug(f"Accessing application URL response status: {response.status}")
            # 查看请求最后一次重定向的 URL
            final_url = str(response.url)
            if not final_url.startswith(homepage_url_prefix):
                raise ZfAccountNotFoundException("Account not found in ZF EMS")
            return HttpSessionHolder.from_aiohttp_session(http_session)
