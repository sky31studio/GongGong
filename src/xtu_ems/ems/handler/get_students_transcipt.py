from io import BytesIO

import pandas as pd
from pdfplumber import PDF

from xtu_ems.ems.config import XTUEMSConfig
from xtu_ems.ems.handler import Handler
from xtu_ems.ems.model import ScoreBoard, Score
from xtu_ems.ems.session import Session

_data = {
    "xs0101id": "",
    "cjtype": "",
    "sjlj": ["110", "120"],
    "sjcj": "2",
    "bblx": "all"
}


class StudentTranscriptGetter(Handler):
    """通过教务系统获取成绩单，并且解析成结构化数据"""

    def handler(self, session: Session, *args, **kwargs):
        with self._get_session(session) as ems_session:
            resp = ems_session.post(self.url(), data=_data)
            if resp.status_code == 200:
                pdf = PDF(BytesIO(resp.content))
                for page in pdf.pages:
                    for table in page.extract_tables():
                        df = pd.DataFrame(table)
                        return self._extra_info(df)

    def url(self):
        return XTUEMSConfig.XTU_EMS_STUDENT_TRANSCRIPT_URL

    def _extra_info(self, df: pd.DataFrame):
        scoreboard = ScoreBoard()
        for row in df.values:
            if not isinstance(row[0], str) or row[0] == "课程名称":
                continue
            if not row[1]:
                self._parse_score(scoreboard, row[0])
                continue
            s = Score(name=row[0],
                      type=row[1],
                      credit=(row[2]),
                      score=row[3],
                      term=row[4])
            scoreboard.scores.append(s)
            if row[5]:
                s = Score(name=row[5],
                          type=row[6],
                          credit=row[7],
                          score=row[8],
                          term=row[9])
                scoreboard.scores.append(s)
        return scoreboard

    def _parse_score(self, scoreboard: ScoreBoard, detail: str):
        pieces = detail.split(' ')
        total = {}
        for i, piece in enumerate(pieces):
            chunks = piece.split('：')
            if len(chunks) == 1:
                pieces[i + 1] = chunks[0] + pieces[i + 1]
                continue
            if len(chunks) == 3:
                total[chunks[1]] = chunks[2]
                continue
            k, vs = chunks
            total[k] = vs
        for k, v in total.items():
            match k:
                case '总学分要求':
                    _, h = scoreboard.total_credit
                    scoreboard.total_credit = (v, h)
                case '已修总学分':
                    t, _ = scoreboard.total_credit
                    scoreboard.total_credit = (t, v)
                case '必修学分要求':
                    _, h = scoreboard.compulsory_credit
                    scoreboard.compulsory_credit = (v, h)
                case '已修必修学分':
                    t, _ = scoreboard.compulsory_credit
                    scoreboard.compulsory_credit = (t, v)
                case '选修学分要求':
                    _, h = scoreboard.elective_credit
                    scoreboard.elective_credit = (v, h)
                case '已修选修学分':
                    t, _ = scoreboard.elective_credit
                    scoreboard.elective_credit = (t, v)
                case '跨学科选修学分要求':
                    _, h = scoreboard.cross_course_credit
                    scoreboard.cross_course_credit = (v, h)
                case '跨学科选修学分':
                    t, _ = scoreboard.cross_course_credit
                    scoreboard.cross_course_credit = (t, v)
                case '平均学分绩点':
                    scoreboard.gpa = v
                case '平均成绩':
                    scoreboard.average_score = v
                case 'CET4':
                    scoreboard.cet4 = v
                case 'CET6':
                    scoreboard.cet6 = v
