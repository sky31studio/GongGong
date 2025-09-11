import datetime

from common.exception import *
from common.model import CourseList, CourseInfo
from common.sess import HttpSessionHolder
from common.term import get_term_year, get_term_id
from zf_ems.config import *


def parse_course_time(courses_list) -> CourseList:
    """
    解析课程时间

    :param courses_list: 原始课程列表
    :return: 解析后的课程列表
    """
    courses = []
    for course in courses_list:
        course_info = CourseInfo()
        course_info.name = course.get("kcmc", "")
        course_info.teacher = course.get("xm", "")
        course_info.classroom = course.get("cdmc", "")
        course_info.weeks = course.get("zcd", "").replace("周", "")
        jc = course.get("jc", "1-2节")
        course_info.start_time = int(jc.split("-")[0])
        course_info.duration = int(jc.split("-")[1].replace("节", "")) - course_info.start_time + 1
        course_info.day = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][
            int(course.get("xqj", "1")) - 1]
        courses.append(course_info)
    return CourseList(courses=courses)


async def get_courses(session: HttpSessionHolder, year=None, term=None) -> CourseList:
    """
    获取课程列表

    :param session: 已登录的 HttpSessionHolder 对象
    :param year: 学年，例如 "2023"
    :param term: 学期，第一学期为3, 第二学期为12
    :return: 课程列表，每个课程是一个字典
    """
    date = datetime.datetime.now().date()
    if year is None or term is None:
        year = get_term_year(date)
        term = get_term_id(date)
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
            result = await response.json()
            return parse_course_time(result['kbList'])
