import logging
from io import BytesIO
from typing import Literal

import pdfplumber

from xtu_ems.common.exception import SessionInvalidException
from xtu_ems.common.model import ScoreBoard, Score, RankInfo
from xtu_ems.common.sess import HttpSessionHolder

logger = logging.getLogger(__name__)


def with_default(value, default):
    return value if value is not None and value.strip() != "" else default

def parse_transcript(transcript_pdf: pdfplumber.PDF) -> ScoreBoard:
    page = transcript_pdf.pages[0]
    text: str = page.extract_text_lines()[1]['text']

    scoreboard = ScoreBoard()
    # '学院: 计算机学院●网络空间安全学院 专业: 网络空间安全 学号: 202205566414 姓名: 谭嘉诚'
    scoreboard.college = text.split("学院:")[1].split("专业:")[0].strip()
    scoreboard.major = text.split("专业:")[1].split("学号:")[0].strip()
    scoreboard.student_id = text.split("学号:")[1].split("姓名:")[0].strip()
    scoreboard.name = text.split("姓名:")[1].strip()

    table = page.extract_table()
    term = 0

    # parse score list
    for col in range(len(table[0]) // 7):
        name_idx = None
        type_idx = None
        credit_idx = None
        score_idx = None
        for idx in range(col * 7, (col + 1) * 7):
            cell = table[0][idx]
            if not cell:
                continue
            content = "".join(cell.split())
            if content == "课程名称":
                name_idx = idx
            elif content == "课程性质":
                type_idx = idx
            elif content == "学分":
                credit_idx = idx
            elif content == "成绩":
                score_idx = idx
            if name_idx is not None and type_idx is not None and credit_idx is not None and score_idx is not None:
                break

        for row in table[1:-3]:
            # ['网络安全导论', '必修', '3.0', '优秀', '2022-2023-1', '']
            if not row[name_idx]:
                break
            if '学期' in row[name_idx].strip():
                term += 1
                continue

            if row[type_idx] and row[credit_idx] and row[score_idx]:
                row_type = row[type_idx].strip()
                score_type: Literal['必修', '选修', '跨学科选修'] = '跨学科选修' if row_type not in ['必修', '选修',
                                                                                                     '跨学科选修'] else row_type
                score = row[score_idx].replace("△", "").replace("*", "").strip()
                score_item = Score(name=row[name_idx].strip(),
                                   type=score_type,
                                   credit=row[credit_idx],
                                   score=score,
                                   term=term)
                scoreboard.scores.append(score_item)

    scoreboard.average_score = with_default(table[-3][2], "100")
    scoreboard.gpa = with_default(table[-3][16], "4.0")
    scoreboard.total_credit = (with_default(table[-1][0], "0"), with_default(table[-1][1], "0"))
    scoreboard.compulsory_credit = (with_default(table[-1][4], "0"), with_default(table[-1][8], "0"))
    scoreboard.elective_credit = (with_default(table[-1][9], "0"), with_default(table[-1][12], "0"))
    scoreboard.cross_course_credit = (with_default(table[-1][15], "0"), with_default(table[-1][17], "0"))
    return scoreboard


async def get_transcript_scoreboard(session: HttpSessionHolder) -> ScoreBoard:
    payload = (f"gsdygx=10530-zw-qcmrgs"
               f"&ids="
               f"&bdykcxzDms="
               f"&cytjkcxzDms="
               f"&cytjkclbDms="
               f"&cytjkcgsDms="
               f"&bjgbdykcxzDms="
               f"&bjgbdyxxkcxzDms="
               f"&djksxmDms="
               f"&cjbzmcDms="
               f"&zdyfsxmDms="
               f"&bdymaxcjbzmcDms="
               f"&cjdySzxs=")
    async with session.to_aiohttp_session() as http_session:
        url = "https://jw.xtu.edu.cn/jwglxt/bysxxcx/xscjzbdy_cxXsCount.html?gnmkdm=N558020"
        async with http_session.post(
            url=url,
            allow_redirects=False
        ) as response:
            if response.status != 200:
                raise SessionInvalidException("Failed to fetch transcript page")
            content = await response.text()
            logger.debug(content)
        url = "https://jw.xtu.edu.cn/jwglxt/bysxxcx/xscjzbdy_dyList.html?gnmkdm=N558020"
        async with http_session.post(
            url=url,
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            allow_redirects=False
        ) as response:
            if response.status != 200:
                raise SessionInvalidException("Failed to fetch transcript PDF")
            resource_url = await response.text()
            print(resource_url)
        pdf_url = "https://jw.xtu.edu.cn" + resource_url.replace("\"", "").replace("\\", "")
        logger.info(f"get pdf from [{pdf_url}]")
        async with http_session.get(
            url=pdf_url,
            allow_redirects=False
        ) as response:
            if response.status != 200:
                raise Exception("Failed to download transcript PDF")
            pdf_bytes = await response.read()
        pdf = pdfplumber.PDF(BytesIO(pdf_bytes))
        scoreboard = parse_transcript(pdf)
        return scoreboard


async def empty_transcript_scoreboard(session: HttpSessionHolder) -> ScoreBoard:
    return ScoreBoard()


async def rank_getter(session: HttpSessionHolder):
    trans = await get_transcript_scoreboard(session)
    return RankInfo(average_score=trans.average_score, gpa=trans.gpa)


async def empty_rank_getter(session: HttpSessionHolder):
    return RankInfo(average_score="0", gpa="0")


if __name__ == '__main__':
    file = "/home/leo/Project/Project/Python/GongGong/score1.pdf"
    with pdfplumber.open(file) as pdf:
        scoreboard = parse_transcript(pdf)
        print(scoreboard.model_dump_json(indent=4))
