import datetime

from xtu_ems.common.exception import *
from xtu_ems.common.model import CourseList, CourseInfo
from xtu_ems.common.sess import HttpSessionHolder
from xtu_ems.common.term import get_term_year, get_term_id
from xtu_ems.zf_ems.config import *


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
        weeks = course.get("zcd", "").replace("周", "")
        # 周次可能的情况： 1-5周(单),8-12周(双),13周,19-20周
        # 需要解析成 1,3,5,8,10,12,13,19-20
        # 先按逗号分割
        weeks_parts = weeks.split(",")
        parsed_weeks = []
        for part in weeks_parts:
            part = part.strip()
            if part == "":
                continue
            if "(" in part and ")" in part:
                range_part = part.split("(")[0]
                if "单" in part:
                    start, end = map(int, range_part.split("-"))
                    parsed_weeks.extend([str(i) for i in range(start, end + 1) if i % 2 == 1])
                elif "双" in part:
                    start, end = map(int, range_part.split("-"))
                    parsed_weeks.extend([str(i) for i in range(start, end + 1) if i % 2 == 0])
            else:
                parsed_weeks.append(part)
        course_info.weeks = ",".join(parsed_weeks)
        jc = course.get("jc", "1-2节")
        course_info.start_time = int(jc.split("-")[0])
        course_info.duration = int(jc.split("-")[1].replace("节", "")) - course_info.start_time + 1
        course_info.day = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][
            int(course.get("xqj", "1")) - 1]
        courses.append(course_info)
    return CourseList(courses=courses)

def normalize_term(term: int) -> int:
    """
    将用户输入的学期编号转换为 EMS 接口使用的学期编码。

    :param term: 学期编号，可为逻辑编号 1/2 或 EMS 编码 3/12。
    :type term: int
    :return: 与 EMS 接口兼容的学期编码。
    :rtype: int
    """
    if term == 1:
        return 3
    if term == 2:
        return 12
    return term

async def get_courses(session: HttpSessionHolder, year=None, term=None) -> CourseList:
    """
    获取课程列表

    :param session: 已登录的 HttpSessionHolder 对象
    :param year: 学年，例如 "2023"
    :param term: 学期，第一学期为3, 第二学期为12
    :return: 课程列表，每个课程是一个字典
    """
    if session.metadata.get("zf_account_not_found"):
        raise ServiceUnavailableException(service_name="ZF EMS", message="ZF account not found")
    date = datetime.datetime.now().date()
    if year is None or term is None:
        year = get_term_year(date)
        term = get_term_id(date)
    payload_term = normalize_term(term)  
    async with session.to_aiohttp_session() as http_session:
        payload = {
            "xnm": year,
            "xqm": payload_term,
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
