from bs4 import BeautifulSoup

from ems.config import XTUEMSConfig
from ems.handler import Handler
from ems.session import Session
from ems.student_info import StudentBasicInfo


class StudentInfoGetrrer(Handler):
    """获取学生信息"""

    def __init__(self):
        super().__init__()

    def handler(self, session: Session, *args, **kwargs):
        """获取学生信息"""
        with self._get_session(session) as ems_session:
            resp = ems_session.get(XTUEMSConfig.XTU_EMS_STUDENT_INFO_URL)
            # 提取resp中的表格信息，并且解析出学生的基本信息
            soup = BeautifulSoup(resp.text, 'html.parser')
            return self._extra_student_info(soup)

    def _extra_student_info(self, soup: BeautifulSoup) -> StudentBasicInfo:
        """从表格中提取学生的基本信息"""
        student_info = {}
        rows = soup.find(id='xjkpTable').find_all('tr')
        # 提取学生的基本信息
        for row in rows:
            skip = 0
            for cell in row.find_all('td'):
                if cell.text.__contains__('：'):
                    key, value = cell.text.split('：')
                else:
                    if skip == 1:
                        skip = 0
                        continue
                    key = cell.text or ''
                    value = cell.find_next('td')
                    value = value.text if value else ''
                    skip = 1
                if key not in student_info:
                    student_info[key] = value
        info = {
            'student_id': student_info.get('学号'),
            'name': student_info.get('姓名'),
            'college': student_info.get('院系', ''),
            'major': student_info.get('专业', ''),
            'class_': student_info.get('班级', ''),
            'gender': student_info.get('性别', ''),
            'birthday': student_info.get('出生日期', ''),
            'entrance_day': student_info.get('入学日期', ''),
        }
        return StudentBasicInfo(**info)
