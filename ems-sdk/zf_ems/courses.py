from common.exception import *
from common.sess import HttpSessionHolder
from zf_ems.config import *


async def get_courses(session: HttpSessionHolder, year, term) -> list[dict]:
    """
    获取课程列表

    :param session: 已登录的 HttpSessionHolder 对象
    :param year: 学年，例如 "2023"
    :param term: 学期，第一学期为3, 第二学期为12
    :return: 课程列表，每个课程是一个字典
    """
    async with session.to_aiohttp_session() as http_session:
        payload = {
            "xnm": year,
            "xqm": term,
            "kzlx": "ck",
        }
        async with http_session.post(
            courses_url,
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        ) as response:
            if response.status != 200:
                raise SessionInvalidException("Failed to fetch courses")
            return await response.json()
