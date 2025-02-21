from bs4 import BeautifulSoup, Tag, NavigableString, PageElement

from xtu_ems.ems.config import XTUEMSConfig
from xtu_ems.ems.handler import EMSPoster
from xtu_ems.ems.model import CourseInfo, CourseTable, CourseList, _get_day_name


class StudentCourseGetter(EMSPoster[CourseList]):

    def _data(self):
        return {'xnxq01id': XTUEMSConfig.get_current_term()}

    def url(self):
        return XTUEMSConfig.XTU_EMS_STUDENT_COURSE_URL

    def _extra_info(self, soup: BeautifulSoup):
        class_table = soup.find(id="kbtable")
        return self._extra_student_courses(class_table).to_list()

    def _extra_student_courses(self, class_table: BeautifulSoup):
        try:
            table = CourseTable()
            for time, row in enumerate(class_table.find_all("tr")):
                for week, td in enumerate(row.find_all("td")):

                    if td.text.strip() == "":
                        courses = []
                    else:
                        course_content = td.find(class_="kbcontent")
                        if course_content is None:
                            continue
                        courses = self._extra_courses(course_content, day=week, start=(time - 1) * 2 + 1)
                    table[week].append(courses)
            return table
        except Exception as e:
            raise e

    def _extra_courses(self, td: Tag, day=0, start=1) -> list[CourseInfo]:
        """提起某一天的课程信息"""
        courses: list[CourseInfo] = []
        contents = self.get_leaf_nodes(td)
        course = CourseInfo(start_time=start, day=_get_day_name(day))
        for i, c in enumerate(contents):
            if isinstance(c, NavigableString):
                if c.strip() == '---------------------':
                    courses.append(course)
                    course = CourseInfo(start_time=start, day=_get_day_name(day))
                elif c.startswith("上课节次"):
                    course.duration = int(c.text.split('：')[1].split('节')[0])
                else:
                    course.name = c.strip()
            elif isinstance(c, Tag):
                if "title" not in c.attrs:
                    continue
                match c.attrs["title"]:
                    case "教室":
                        course.classroom = c.text.strip()
                    case "老师":
                        course.teacher = c.text.strip()
                    case "周次(节次)":
                        course.weeks = c.text.split('(')[0].strip()
                    case _:
                        pass
        if course.name is not "":
            courses.append(course)
        return courses

    def get_leaf_nodes(self, t: Tag):
        if len(t) < 2:
            return [t]
        content: list[PageElement] = []
        for c in t.contents:
            if isinstance(c, NavigableString):
                content.append(c)
            elif isinstance(c, Tag):
                content.extend(self.get_leaf_nodes(c))
        return content
