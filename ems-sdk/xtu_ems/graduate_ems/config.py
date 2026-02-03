import datetime

from xtu_ems.common.term import get_term_year, get_term_id


def get_term_code(day: datetime.date):
    """
    获取当前学期

    学期分为两个：
    - 第1学期：8月到次年1月
    - 第2学期：2月到7月

    :param day: 日期时间对象
    :return: 学期编号，1或2

    """
    year = get_term_year(day)
    term_id = get_term_id(day)
    base_code = 51
    code = base_code + (year - 2025) * 2 + (term_id - 1)
    return code
