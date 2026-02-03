import asyncio
import datetime
import time

from xtu_ems.common.exception import SessionInvalidException, ServiceUnavailableException
from xtu_ems.common.model import CategoryClassroomBoard, ClassroomStatus, ClassroomBoard
from xtu_ems.common.sess import HttpSessionHolder
from xtu_ems.common.term import get_term_year, get_term_id
from xtu_ems.zf_ems.calendar import get_calendar


def _bits_of_list(ls: list[int]) -> int:
    result = 0
    for i in ls:
        result |= 1 << (i - 1)
    return result


class ClassroomQueryData(dict):
    def __init__(self, year, term, weeks: list[int], day_of_week: int, sections: list[int], time=0):
        super().__init__()
        self.year = year
        self.term = term
        self.weeks = weeks
        self.day_of_week = day_of_week
        self.sections = sections
        self.time = time

    def __repr__(self):
        return (f'xqh_id=02'
                f'&xnm={self.year}'
                f'&xqm={self.term}'
                f'&cdlb_id=01'
                f'&jyfs=0'
                f'&zcd={_bits_of_list(self.weeks)}'
                f'&xqj={self.day_of_week}'
                f'&jcd={_bits_of_list(self.sections)}'
                f'&_search=false'
                f'&nd={int(time.time() * 1000)}'  # 当前时间戳，防止缓存
                f'&queryModel.showCount=99999'
                f'&queryModel.currentPage=1'
                f'&queryModel.sortName=cdbh+'
                f'&queryModel.sortOrder=asc'
                f'&time={self.time}')


async def _get_classroom(session: HttpSessionHolder, query: ClassroomQueryData) -> list[str]:
    """
    获取教室状态

    :param session: 已登录的 HttpSessionHolder 对象
    :param query: 查询参数
    :return: 空闲的教室名称，列表
    """
    headers = {
        'Host': 'jw.xtu.edu.cn',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    # print(query.__dict__)
    payload = query.__repr__()
    print(payload)
    async with session.to_aiohttp_session() as http_session:
        async with http_session.post(
            "https://jw.xtu.edu.cn/jwglxt/cdjy/cdjy_cxKxcdlb.html?doType=query&gnmkdm=N2155",
            data=payload,
            headers=headers,
            allow_redirects=False
        ) as response:
            if response.status != 200:
                raise SessionInvalidException("Failed to fetch today's classroom status")
            data = await response.json()
            return [item['cdmc'] for item in data['items']]


async def get_all_day_classroom(session: HttpSessionHolder, day: datetime.date,
                                term_start_at: datetime.date) -> CategoryClassroomBoard:
    """
    获取指定日期全天候空教室

    :param session: 已登录的 HttpSessionHolder 对象
    :param day: 指定的日期
    :param term_start_at: 学期开始日期
    :return: 空教室状态面板
    """
    year = get_term_year(term_start_at)
    term = get_term_id(term_start_at)
    term = 3 if term == 1 else 12
    week = (day - term_start_at).days // 7 + 1
    day_of_week = day.weekday() + 1
    queries = [
        ClassroomQueryData(year, term, [week], day_of_week, [1, 2], 0),
        ClassroomQueryData(year, term, [week], day_of_week, [3, 4], 1),
        ClassroomQueryData(year, term, [week], day_of_week, [5, 6], 2),
        ClassroomQueryData(year, term, [week], day_of_week, [7, 8], 3),
        ClassroomQueryData(year, term, [week], day_of_week, [9, 10, 11], 4),
    ]
    tasks = [_get_classroom(session, query) for query in queries]
    classroom_cols = await asyncio.gather(*tasks)
    merge_classrooms = [*classroom_cols[0],
                        *classroom_cols[1],
                        *classroom_cols[2],
                        *classroom_cols[3],
                        *classroom_cols[4]]
    merge_classrooms = list(set(merge_classrooms))
    merge_classrooms.sort()
    classrooms_list = [
        ClassroomStatus(name=classroom, status=[
            ("空" if classroom in classroom_cols[i] else "满")
            for i in range(5)])
        for classroom in merge_classrooms
    ]
    return ClassroomBoard(
        date=day,
        classrooms=classrooms_list
    ).to_category()


async def get_today_classroom(session: HttpSessionHolder) -> CategoryClassroomBoard:
    if session.metadata.get("zf_account_not_found"):
        raise ServiceUnavailableException(service_name="ZF EMS", message="ZF account not found")
    cal = await get_calendar(session)
    return await get_all_day_classroom(session, datetime.datetime.now().date(), cal.start)


async def get_tomorrow_classroom(session: HttpSessionHolder) -> CategoryClassroomBoard:
    if session.metadata.get("zf_account_not_found"):
        raise ServiceUnavailableException(service_name="ZF EMS", message="ZF account not found")
    cal = await get_calendar(session)
    return await get_all_day_classroom(session, datetime.datetime.now().date() + datetime.timedelta(days=1), cal.start)
