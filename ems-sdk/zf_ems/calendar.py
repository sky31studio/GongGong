import datetime

import bs4

from common.exception import SessionInvalidException
from common.model import TeachingCalendar
from common.sess import HttpSessionHolder
from common.term import get_current_term


def parse_calendar(data) -> TeachingCalendar:
    """
    解析教学周历数据

    :param data: 原始数据
    :return: 解析后的教学周历对象
    """
    # 2025-2026学年1学期(2025-09-01至2026-01-18)
    # 解析出来的格式为 2025-09-01 2026-01-18
    date_range = data.split("学期(")[1].strip().replace(")", "")
    start_date_str = date_range.split("至")[0].strip()
    end_date_str = date_range.split("至")[1].strip().replace(")", "")
    term_id = get_current_term()
    start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()
    # 计算周数，向上取整
    delta_days = (end_date - start_date).days
    weeks = (delta_days + 1) // 7
    if (delta_days + 1) % 7 != 0:
        weeks += 1
    calendar = TeachingCalendar(
        start=start_date,
        weeks=weeks,
        term_id=term_id
    )
    return calendar


async def get_calendar(session: HttpSessionHolder) -> TeachingCalendar:
    """
    获取教学周历

    :param session: 已登录的 HttpSessionHolder 对象
    :param year: 学年，例如 "2023"
    :param term: 学期，第一学期为3, 第二学期为12
    :return: 教学周历对象
    """
    async with session.to_aiohttp_session() as http_session:
        async with http_session.get(
            "https://jw.xtu.edu.cn/jwglxt/xtgl/index_cxAreaFive.html?localeKey=zh_CN&gnmkdm=index",
            allow_redirects=False
        ) as response:
            if response.status != 200:
                raise SessionInvalidException("Failed to fetch teaching calendar page")
            text = await response.text()
            # 从返回的 HTML 中提取教学周历数据
            soup = bs4.BeautifulSoup(text, "html.parser")
            target_msg = soup.find_all("th")[1].text
            calendar = parse_calendar(target_msg)
            return calendar
