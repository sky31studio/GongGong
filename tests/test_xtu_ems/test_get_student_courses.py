import os
from unittest import TestCase

from xtu_ems.ems.handler.get_student_courses import StudentCourseGetter
from xtu_ems.ems.model import InformationPackage

username = os.getenv("XTU_USERNAME")
password = os.getenv("XTU_PASSWORD")


class TestStudentCourseGetter(TestCase):
    def test_handler(self):
        from xtu_ems.ems.account import AuthenticationAccount
        from xtu_ems.ems.ems import QZEducationalManageSystem
        account = AuthenticationAccount(username=username,
                                        password=password)
        ems = QZEducationalManageSystem()
        session = ems.login(account)
        handler = StudentCourseGetter()
        resp = handler.handler(session)
        print(resp.model_dump_json(indent=4))
        self.assertIsNotNone(resp)

    def test_extra_student_courses(self):
        from xtu_ems.ems.account import AuthenticationAccount
        from xtu_ems.ems.ems import QZEducationalManageSystem
        account = AuthenticationAccount(username=username,
                                        password=password)
        ems = QZEducationalManageSystem()
        session = ems.login(account)
        handler = StudentCourseGetter()
        url = handler.url()
        with handler._get_session(session) as ems_session:
            resp = ems_session.post(url=url, data={"xnxq01id": "2022-2023-2"})
        import bs4
        res = handler._extra_info(bs4.BeautifulSoup(resp.text, "html.parser"))
        li = res.to_list()
        info = InformationPackage(student_id=username, data=li)
        print(info.model_dump_json(indent=4))
        self.assertIsNotNone(li)
