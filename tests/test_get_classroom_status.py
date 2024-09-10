import json
import os
from unittest import TestCase

from ems.handler.get_classroom_status import ClassroomStatusGetter, ClassroomStatusGetterTomorrow

username = os.getenv("XTU_USERNAME")
password = os.getenv("XTU_PASSWORD")


class TestClassroomStatusGetter(TestCase):
    def test_handler(self):
        from ems.account import AuthenticationAccount
        from ems.ems import QZEducationalManageSystem
        account = AuthenticationAccount(username=username,
                                        password=password)
        ems = QZEducationalManageSystem()
        session = ems.login(account)
        handler = ClassroomStatusGetter()
        resp = handler.handler(session)
        print(json.dumps(resp, indent=4, default=lambda o: o.__dict__, ensure_ascii=False))
        self.assertIsNotNone(resp)


class TestClassroomStatusGetterTomorrow(TestCase):
    def test_handler(self):
        from ems.account import AuthenticationAccount
        from ems.ems import QZEducationalManageSystem
        account = AuthenticationAccount(username=username,
                                        password=password)
        ems = QZEducationalManageSystem()
        session = ems.login(account)
        handler = ClassroomStatusGetterTomorrow()
        resp = handler.handler(session)
        print(json.dumps(resp, indent=4, default=lambda o: o.__dict__, ensure_ascii=False))
        self.assertIsNotNone(resp)
