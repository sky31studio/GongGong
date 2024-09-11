from bs4 import BeautifulSoup, Tag

from xtu_ems.ems.config import XTUEMSConfig
from xtu_ems.ems.handler import EMSGetter
from xtu_ems.ems.model import CourseInfo, CourseTable


class StudentCourseGetter(EMSGetter):

    def url(self):
        return XTUEMSConfig.XTU_EMS_STUDENT_COURSE_URL

    def _extra_info(self, soup: BeautifulSoup):
        class_table = soup.find(id="kbtable")
        return self._extra_student_courses(class_table)

    def _extra_student_courses(self, class_table: BeautifulSoup):
        table = CourseTable()
        for time, row in enumerate(class_table.find_all("tr")):
            for week, td in enumerate(row.find_all("td")):

                if td.text.strip() == "":
                    courses = []
                else:
                    course_content = td.find(class_="kbcontent")
                    if course_content is None:
                        continue
                    courses = self._extra_courses(course_content)
                table[week].append(courses)
        return table

    def _extra_courses(self, td: Tag, course_name=None) -> list[CourseInfo]:
        """提起某一天的课程信息"""
        course_name = course_name or td.contents[0].text
        teacher = td.find_next(title='老师')
        weeks = teacher.find_next(title='周次(节次)')
        classroom = weeks.find_next(title='教室')
        course = CourseInfo(name=course_name, teacher=teacher.text, weeks=weeks.text.split('(')[0],
                            classroom=classroom.text)
        next_c = classroom.find_next_sibling(string='---------------------')
        ret = [course]
        if next_c is not None:
            ret += self._extra_courses(next_c, course_name)
        return ret
