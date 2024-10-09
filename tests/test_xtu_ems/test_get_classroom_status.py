import json
import os
from unittest import TestCase

from xtu_ems.ems.handler.get_classroom_status import TodayClassroomStatusGetter, TomorrowClassroomStatusGetter

username = os.getenv("XTU_USERNAME")
password = os.getenv("XTU_PASSWORD")


class TestTodayClassroomStatusGetter(TestCase):
    def test_handler(self):
        from xtu_ems.ems.account import AuthenticationAccount
        from xtu_ems.ems.ems import QZEducationalManageSystem
        account = AuthenticationAccount(username=username,
                                        password=password)
        ems = QZEducationalManageSystem()
        session = ems.login(account)
        handler = TodayClassroomStatusGetter()
        resp = handler.handler(session)
        print(json.dumps(resp, indent=4, ensure_ascii=False, default=str))
        self.assertIsNotNone(resp)


class TestTomorrowClassroomStatusGetter(TestCase):
    def test_handler(self):
        from xtu_ems.ems.account import AuthenticationAccount
        from xtu_ems.ems.ems import QZEducationalManageSystem
        account = AuthenticationAccount(username=username,
                                        password=password)
        ems = QZEducationalManageSystem()
        session = ems.login(account)
        handler = TomorrowClassroomStatusGetter()
        resp = handler.handler(session)
        print(json.dumps(resp, indent=4, ensure_ascii=False, default=str))
        self.assertIsNotNone(resp)
