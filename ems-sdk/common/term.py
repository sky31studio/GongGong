import datetime
from datetime import date


def get_term_year(d: date) -> int:
    """
    获取当前学年

    学年从每年的8月开始，到次年的7月结束
    例如：
    - 2023年8月到2024年7月是2023-2024学年
    - 2024年8月到2025年7月是2024-2025学年

    :param d: 日期时间对象
    :return: 学年开始的年份
    例如，2023-2024学年返回2023
    """
    year = d.year
    month = d.month
    if month < 8:
        return year - 1
    else:
        return year


def get_term_id(d: date) -> int:
    """
    获取当前学期

    学期分为两个：
    - 第1学期：8月到次年1月
    - 第2学期：2月到7月

    :param d: 日期时间对象
    :return: 学期编号，1或2

    """
    month = d.month
    return 2 if 2 <= month <= 7 else 1


def get_current_term():
    """获取当前学期"""
    d = datetime.datetime.now().date()
    return f"{get_term_year(d)}-{get_term_year(d) + 1}-{get_term_id(d)}"
