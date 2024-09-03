"""校务系统信息"""
from pydantic import BaseModel


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
