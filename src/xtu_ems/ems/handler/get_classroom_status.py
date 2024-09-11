from bs4 import BeautifulSoup

from xtu_ems.ems.config import XTUEMSConfig
from xtu_ems.ems.handler import EMSPoster
from xtu_ems.ems.model import ClassroomStatus


class ClassroomStatusGetter(EMSPoster):
    """查询教室状态"""

    def _data(self):
        return {'xzlx': "1"}

    def _extra_info(self, soup: BeautifulSoup):
        classroom = soup.find(id="dataList").find_all('tr')[2:]
        classroom = [self._extra_classroom_info(row) for row in classroom]
        return classroom

    def _extra_classroom_info(self, row: BeautifulSoup) -> ClassroomStatus:
        """从表格的某一行中提取教室的信息"""
        tds = row.find_all('td')
        status = [td.text for td in tds[1:]]
        return ClassroomStatus(name=tds[0].text.strip(), status=status)

    def url(self):
        return XTUEMSConfig.XTU_EMS_STUDENT_FREE_ROOM_URL


class ClassroomStatusGetterTomorrow(ClassroomStatusGetter):
    """查询教室状态"""

    def _data(self):
        return {'xzlx': "2"}
