from bs4 import BeautifulSoup

from ems.config import XTUEMSConfig
from ems.handler import Handler
from ems.model import ExamInfo
from ems.session import Session

_data = {
    "xnxqid": XTUEMSConfig.XTU_EMS_CURRENT_TIME
}


class StudentExamGetter(Handler):
    """获取学生考试信息"""

    def handler(self, session: Session, *args, **kwargs):
        """获取学生考试信息"""
        with self._get_session(session) as ems_session:
            resp = ems_session.post(self.url(), data=_data)
            soup = BeautifulSoup(resp.text, 'html.parser')
            return self._extra_info(soup)

    def _extra_info(self, soup: BeautifulSoup):
        exam_list = soup.find(id="dataList").find_all('tr')[1:]
        exam_list = [self._extra_exam_info(row) for row in exam_list]
        return exam_list

    def _extra_exam_info(self, row: BeautifulSoup) -> ExamInfo:
        """从表格的某一行中提取学生的考试信息"""
        tds = row.find_all('td')
        return ExamInfo(name=tds[2].text,
                        type=tds[3].text,
                        time=tds[5].text,
                        location=tds[6].text)

    def url(self):
        return XTUEMSConfig.XTU_EMS_STUDENT_EXAM_URL
