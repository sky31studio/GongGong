import json
import os
from unittest import TestCase

username = os.getenv("XTU_USERNAME")
password = os.getenv("XTU_PASSWORD")


class TestStudentTranscriptGetter(TestCase):
    def test_handler(self):
        from xtu_ems.ems.account import AuthenticationAccount
        from xtu_ems.ems.ems import QZEducationalManageSystem
        account = AuthenticationAccount(username=username,
                                        password=password)
        ems = QZEducationalManageSystem()
        session = ems.login(account)
        from xtu_ems.ems.handler.get_students_transcript import StudentTranscriptGetter
        handler = StudentTranscriptGetter()
        resp = handler.handler(session)
        print(json.dumps(resp.dict(), indent=4, ensure_ascii=False, default=str))
        self.assertIsNotNone(resp)
