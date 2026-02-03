import datetime

from xtu_ems.common.exception import *
from xtu_ems.common.model import CourseList, CourseInfo
from xtu_ems.common.sess import HttpSessionHolder
from xtu_ems.graduate_ems.config import get_term_code


def parse_course_time(rows: list[dict]) -> CourseList:
    """
    解析课程时间

    :param rows: 每一行的课程
    :return: 解析后的课程列表
    """
    time_order = {
        "上午1": 1,
        "上午2": 2,
        "上午3": 3,
        "上午4": 4,
        "下午1": 5,
        "下午2": 6,
        "下午3": 7,
        "下午4": 8,
        "晚上1": 9,
        "晚上2": 10,
        "晚上3": 11,
        "无节次": 12
    }

    # 按照mc字段排序
    rows.sort(key=lambda e: time_order[e["mc"]])
    parsed_courses = []
    for idx, z in enumerate(["z1", "z2", "z3", "z4", "z5", "z6", "z7"]):  # idx: 1 ... 7; z: z1 ... z7
        for i in range(11):  # 0 ... 10
            courses_info = rows[i].get(z)
            if not courses_info or courses_info.strip() == "":
                continue
            courses_list = courses_info.split("<br/>")
            # 可能需要和其他行的课程合并，如果名字相同

            for course in courses_list:
                section = 0
                for j in range(i, 11):
                    if rows[j].get(z) and course in rows[j].get(z):
                        section += 1
                        rows[j][z] = rows[j][z].replace(course, "").strip()
                        if rows[j][z] == "" or rows[j][z] == "<br/>":
                            rows[j][z] = None
                    else:
                        break
                # 科学计算方法(物理学（硕士）)[11-16周]范楚辉[研究生院第三阶梯]
                parsed_courses.append(CourseInfo(
                    name=course.split("(")[0].strip(),  # 科学计算方法
                    weeks=course.split("[")[1].split("]")[0].replace("周", "").strip(),  # 11-16
                    day=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][idx],  # 星期几
                    start_time=i + 1,  # 开始节次
                    duration=section,  # 持续节次
                    teacher=course.split("]")[1].split("[")[0].strip(),  # 范楚辉
                    classroom=course.split("[")[-1].split("]")[0].strip()  # 研究生院第三阶梯
                ))
    return CourseList(courses=parsed_courses)


async def get_course_link(session: HttpSessionHolder) -> str:
    """
    获取课程链接

    :return: 课程链接
    """
    import re
    async with session.to_aiohttp_session() as http_session:
        async with http_session.get("https://gmsstu.xtu.edu.cn/index") as response:
            if response.status != 200:
                raise SessionInvalidException("Failed to access index page")
            text = await response.text()

            # <li><a href="/TXlIZWFydFdpbGxHb09ucHlnbC94c2tiY3gvaW5kZXgjMzY0M2I3MDktZTljYy00YWZkLTkyMTMtMTYwMjk0OWQxNTk3" target="mainFrame" title="学生课表查询">学生课表查询</a></li>
            match = re.search(r'<a href="/([^"]+)" target="mainFrame" title="学生课表查询">', text)
            if not match:
                raise ServiceUnavailableException("Course link not found")
            page_url = "https://gmsstu.xtu.edu.cn/" + match.group(1)
        async with http_session.get(page_url) as response:
            if response.status != 200:
                raise ServiceUnavailableException("Failed to access course page")
            text = await response.text()
            text = text.split("function GetList_ew() {")[1]
            match = re.search(r"url:\s*'/([^']+)'", text)
            if not match:
                raise ServiceUnavailableException("Course form action not found")
            # 选择匹配的第二个项目
            url = match.group(1)
            return "https://gmsstu.xtu.edu.cn/" + url


async def get_courses(session: HttpSessionHolder) -> CourseList:
    """
    获取课程列表

    :param session: 已登录的 HttpSessionHolder 对象
    :return: 课程列表，每个课程是一个字典
    """
    async with session.to_aiohttp_session() as http_session:
        payload = {
            "kblx": "xs",
            "termcode": get_term_code(datetime.datetime.now().date())
        }
        url = await get_course_link(session)
        async with http_session.post(
            url=url,
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        ) as response:
            if response.status != 200:
                raise SessionInvalidException("Failed to fetch courses")
            result = await response.json()
            return parse_course_time(result['rows'])
