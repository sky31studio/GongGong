import time
from datetime import datetime

from xtu_ems.common.exception import ServiceUnavailableException
from xtu_ems.common.model import ExamInfoList, ExamInfo
from xtu_ems.common.sess import HttpSessionHolder
from xtu_ems.common.term import get_term_year, get_term_id
from xtu_ems.zf_ems.config import exams_url


def parse_exams(exams_list) -> ExamInfoList:
    """
    解析考试信息

    :param exams_list: 原始考试列表
    :return: 解析后的考试列表
    """
    exams = ExamInfoList()
    for exam in exams_list:
        exam_name = exam.get("kcmc", "").strip()
        exam_time = exam.get("kssj", "").strip()  # "2026-01-10(10:30-12:30)"
        if "(" in exam_time and ")" in exam_time:
            start_str = exam_time.split("(")[0]
            time_range = exam_time.split("(")[1].split(")")[0]
            start_time_str, end_time_str = time_range.split("-")
            start_time = datetime.strptime(f"{start_str} {start_time_str}", "%Y-%m-%d %H:%M")
            end_time = datetime.strptime(f"{start_str} {end_time_str}", "%Y-%m-%d %H:%M")
        else:
            start_time = exam_time
            end_time = exam_time

        location = exam.get("cdmc", "").strip()
        exam_type = exam.get("khfs", "考试").strip()
        exam = ExamInfo(name=exam_name, start_time=start_time,
                        end_time=end_time, location=location, type=exam_type)
        exams.exams.append(exam)
    return exams


async def get_exams(session: HttpSessionHolder, year=None, term=None) -> ExamInfoList:
    """
    获取成绩单

    :param session: 已登录的 HttpSessionHolder 对象
    :return: 考试安排信息列表
    """
    if session.metadata.get("zf_account_not_found"):
        raise ServiceUnavailableException(service_name="ZF EMS", message="ZF account not found")
    date = datetime.now().date()
    if year is None or term is None:
        year = get_term_year(date)
        term = get_term_id(date)
    # xnm=2025&xqm=3&ksmcdmb_id=&kch=&kc=&ksrq=&kkbm_id=&_search=false&nd=1763601573923&queryModel.showCount=15&queryModel.currentPage=1&queryModel.sortName=+&queryModel.sortOrder=asc&time=1

    term = 3 if term == 1 else 12
    payload = (
        f"xnm={year}"
        f"&xqm={term}"
        f"&ksmcdmb_id="
        f"&kch="
        f"&kc="
        f"&ksrq="
        f"&kkbm_id="
        f"&_search=false"
        f"&nd={int(time.time() * 1000)}"
        f"&queryModel.showCount=9999"
        f"&queryModel.currentPage=1"
        f"&queryModel.sortName=+"
        f"&queryModel.sortOrder=asc"
        f"&time=1"
    )

    async with session.to_aiohttp_session() as http_session:
        async with http_session.post(exams_url,
                                     data=payload,
                                     headers={"Content-Type": "application/x-www-form-urlencoded"}
                                     ) as response:
            if response.status != 200:
                raise ServiceUnavailableException(service_name="ZF EMS Exam Service",
                                                  message="Cannot access exam service")
            resp_json = await response.json()
            print(resp_json)
            exams_list = resp_json.get("items", [])
            return parse_exams(exams_list)
