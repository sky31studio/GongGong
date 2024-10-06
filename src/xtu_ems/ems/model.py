"""校务系统信息"""
from datetime import datetime
from typing import Tuple, Literal, TypeVar, Generic

from pydantic import BaseModel

T = TypeVar('T')


class InformationPackage(BaseModel, Generic[T]):
    """信息包"""

    student_id: str
    """学生id"""
    data: T
    """数据"""
    update_time: datetime = datetime.now()
    """更新时间"""


class StudentBasicInfo(BaseModel):
    """学生基本信息"""
    student_id: str
    """学号"""
    name: str
    """姓名"""
    gender: str
    """性别"""
    birthday: str
    """出生日期"""
    major: str
    """专业"""
    class_: str
    """班级"""
    entrance_day: str
    """入学日期"""
    college: str
    """学院"""


class CourseInfo(BaseModel):
    """课程基本信息"""

    name: str
    """课程名称"""
    teacher: str
    """老师"""
    classroom: str
    """教室"""
    weeks: str
    """周次(节次)"""
    start_time: int
    """开始上课节次"""
    duration: int
    """结束上课节次"""
    day: str
    """星期"""


def _get_day_name(day: int):
    """
    获取星期几的课程表
    Args:
        day: 星期几

    Returns:
        返回星期几的课程表
    """
    return [
        'Monday',
        'Tuesday',
        'Wednesday',
        'Thursday',
        'Friday',
        'Saturday',
        'Sunday'][day]


class CourseTable(BaseModel):
    """课程表数据结构"""
    Sunday: list[list[CourseInfo]] = []
    Monday: list[list[CourseInfo]] = []
    Tuesday: list[list[CourseInfo]] = []
    Wednesday: list[list[CourseInfo]] = []
    Thursday: list[list[CourseInfo]] = []
    Friday: list[list[CourseInfo]] = []
    Saturday: list[list[CourseInfo]] = []

    def __getitem__(self, item):
        # 判断item是否是一个int，如果为int，则返回相应的课程表
        if isinstance(item, int):
            return self.__getattribute__(_get_day_name(item))
        # 如果不是int，则返回相应的课程表
        return self.__getattribute__(item)

    def to_list(self):
        """从课程表中提取课程列表"""
        ret = []
        for day in self.__dict__.values():
            for course in day:
                ret += course
        return ret


class Score(BaseModel):
    """成绩信息"""

    name: str
    """课程名称"""
    score: str
    """成绩。"""
    credit: str
    """学分"""
    type: Literal['必修', '选修', '跨学科选修']
    """成绩类型"""
    term: int
    """学期"""


class ScoreBoard(BaseModel):
    """成绩信息"""

    scores: list[Score] = []
    """成绩列表"""
    total_credit: Tuple[str, str] = (0, 0)
    """总学分"""
    elective_credit: Tuple[str, str] = (0, 0)
    """选修课学分"""
    compulsory_credit: Tuple[str, str] = (0, 0)
    """必修课学分"""
    cross_course_credit: Tuple[str, str] = (0, 0)
    """跨学科选修学分"""
    average_score: str = 0
    """平均分"""
    gpa: str = 0
    """总绩点"""

    cet4: str = None
    """CET4 成绩"""
    cet6: str = None
    """CET6 成绩"""


class ExamInfo(BaseModel):
    """考试信息"""

    name: str = ""
    """考试名称"""
    time: str = None
    """考试时间"""
    location: str = None
    """考试地点"""
    type: str = '考试'
    """考核方式"""


class ClassroomStatus(BaseModel):
    """教室信息"""

    name: str = ""
    """教室名称"""
    status: list[str] = []
    """教室状态"""


class TeachingCalendar(BaseModel):
    """教学日历"""

    start: datetime = None
    """开始时间"""
    term_id: str = ""
    """学期"""
