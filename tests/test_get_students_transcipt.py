import json
import os
from unittest import TestCase

username = os.getenv("XTU_USERNAME")
password = os.getenv("XTU_PASSWORD")


class TestStudentTranscriptGetter(TestCase):
    def test_handler(self):
        from ems.account import AuthenticationAccount
        from ems.ems import ZQEducationalManageSystem
        account = AuthenticationAccount(username=username,
                                        password=password)
        ems = ZQEducationalManageSystem()
        session = ems.login(account)
        from ems.handler.get_students_transcipt import StudentTranscriptGetter
        handler = StudentTranscriptGetter()
        resp = handler.handler(session)
        print(json.dumps(resp.dict(), indent=4, ensure_ascii=False))
        self.assertIsNotNone(resp)
