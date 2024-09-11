import json
import os
from unittest import TestCase

from ems.handler.get_student_courses import StudentCourseGetter

username = os.getenv("XTU_USERNAME")
password = os.getenv("XTU_PASSWORD")


class TestStudentCourseGetter(TestCase):
    def test_handler(self):
        from ems.account import AuthenticationAccount
        from ems.ems import QZEducationalManageSystem
        account = AuthenticationAccount(username=username,
                                        password=password)
        ems = QZEducationalManageSystem()
        session = ems.login(account)
        handler = StudentCourseGetter()
        resp = handler.handler(session)
        print(json.dumps(resp.dict(), indent=4, ensure_ascii=False, default=str))
        self.assertIsNotNone(resp)
