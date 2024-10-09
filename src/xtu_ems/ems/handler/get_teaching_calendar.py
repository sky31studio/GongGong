from datetime import datetime

from bs4 import BeautifulSoup

from xtu_ems.ems.config import XTUEMSConfig
from xtu_ems.ems.handler import EMSGetter
from xtu_ems.ems.model import TeachingCalendar


class TeachingCalendarGetter(EMSGetter):
    def url(self):
        return XTUEMSConfig.XTU_EMS_TEACHING_WEEKS_URL

    def _extra_info(self, soup: BeautifulSoup):
        term_id = soup.find(id='xnxq01id').find('option')
        start_year = int(term_id.text.split('-')[0])
        table = soup.find(id='kbtable')
        start_month = 1
        for td in table.find_all('td'):
            if '月' in td.text:
                sec_month = td.text.replace('月', '')
                start_month = int(sec_month) - 1
                break
        start_day = int(table.find_all('td')[1].text)
        start = datetime(year=start_year, month=start_month, day=start_day)
        return TeachingCalendar(start=start, term_id=term_id.text)
