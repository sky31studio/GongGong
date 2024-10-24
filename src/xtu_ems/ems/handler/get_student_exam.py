from bs4 import BeautifulSoup

from xtu_ems.ems.config import XTUEMSConfig
from xtu_ems.ems.handler import EMSPoster
from xtu_ems.ems.model import ExamInfo


class StudentExamGetter(EMSPoster[list[ExamInfo]]):
    """获取学生考试信息"""

    def _data(self):
        return {
            "xnxqid": XTUEMSConfig.get_current_term()
        }

    def _extra_info(self, soup: BeautifulSoup):
        exam_list = soup.find(id="dataList").find_all('tr')[1:]
        exam_list = [self._extra_exam_info(row) for row in exam_list]
        return exam_list

    def _extra_exam_info(self, row: BeautifulSoup) -> ExamInfo:
        """从表格的某一行中提取学生的考试信息"""
        tds = row.find_all('td')
        return ExamInfo(name=tds[2].text.strip(),
                        type=tds[3].text.strip(),
                        time=tds[5].text.strip(),
                        location=tds[6].text.strip())

    def url(self):
        return XTUEMSConfig.XTU_EMS_STUDENT_EXAM_URL
