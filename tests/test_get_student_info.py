import json
import os
from unittest import TestCase

username = os.getenv("XTU_USERNAME")
password = os.getenv("XTU_PASSWORD")


class TestStudentInfoHandler(TestCase):
    def test_handler(self):
        from ems.account import AuthenticationAccount
        from ems.ems import QZEducationalManageSystem
        account = AuthenticationAccount(username=username,
                                        password=password)
        ems = QZEducationalManageSystem()
        session = ems.login(account)
        from ems.handler.get_student_info import StudentInfoGetter
        handler = StudentInfoGetter()
        resp = handler.handler(session)
        print(json.dumps(resp, indent=4, default=lambda o: o.__dict__, ensure_ascii=False))
        self.assertIsNotNone(resp)
