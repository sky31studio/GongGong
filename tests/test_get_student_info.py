import os
from unittest import TestCase

username = os.getenv("XTU_USERNAME")
password = os.getenv("XTU_PASSWORD")


class TestStudentInfoHandler(TestCase):
    def test_handler(self):
        from ems.account import AuthenticationAccount
        from ems.ems import ZQEducationalManageSystem
        account = AuthenticationAccount(username=username,
                                        password=password)
        ems = ZQEducationalManageSystem()
        session = ems.login(account)
        from ems.handler.get_student_info import StudentInfoGetrrer
        handler = StudentInfoGetrrer()
        resp = handler.handler(session)
        self.assertIsNotNone(resp)
