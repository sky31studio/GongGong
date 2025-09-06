from datetime import timedelta

from common.model import *
from qz_ems.config import XTUEMSConfig
from qz_ems.handler.abs import *


def _extra_classroom_info(row: BeautifulSoup) -> ClassroomStatus:
    """从表格的某一行中提取教室的信息"""
    tds = row.find_all('td')[:6]
    status = [td.text.strip() for td in tds[1:]]
    return ClassroomStatus(name=tds[0].text.strip(), status=status)


class TodayClassroomStatusGetter(EMSPoster[CategoryClassroomBoard]):
    """查询教室状态"""

    def _data(self):
        return {'xzlx': "0"}

    def _extra_info(self, soup: BeautifulSoup):
        classroom = soup.find(id="dataList").find_all('tr')[2:]
        classroom = [_extra_classroom_info(row) for row in classroom]
        return ClassroomBoard(classrooms=classroom, date=datetime.now().date()).to_category()

    def url(self):
        return XTUEMSConfig.XTU_EMS_STUDENT_FREE_ROOM_URL


class TomorrowClassroomStatusGetter(TodayClassroomStatusGetter):
    """查询教室状态"""

    def _data(self):
        return {'xzlx': "1"}

    def _extra_info(self, soup: BeautifulSoup):
        classroom = soup.find(id="dataList").find_all('tr')[2:]
        classroom = [_extra_classroom_info(row) for row in classroom]
        return ClassroomBoard(classrooms=classroom,
                              date=datetime.now().date() + timedelta(days=1)).to_category()


class AssignedClassroomStatusGetter(TodayClassroomStatusGetter):
    def __init__(self, day: int = 0):
        super().__init__()
        self.day = day

    """查询教室状态"""

    def _data(self):
        return {'xzlx': str(self.day)}

    @staticmethod
    def today():
        return AssignedClassroomStatusGetter(0)

    @staticmethod
    def tomorrow():
        return AssignedClassroomStatusGetter(1)
