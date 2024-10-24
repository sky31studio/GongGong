import os
from unittest import TestCase

username = os.getenv("XTU_USERNAME")
password = os.getenv("XTU_PASSWORD")


class TestTeachingCalendarGetter(TestCase):
    def test_handler(self):
        """测试获取教学日历"""
        from xtu_ems.ems.account import AuthenticationAccount
        from xtu_ems.ems.ems import QZEducationalManageSystem
        account = AuthenticationAccount(username=username,
                                        password=password)
        ems = QZEducationalManageSystem()
        session = ems.login(account)
        from xtu_ems.ems.handler.get_teaching_calendar import TeachingCalendarGetter
        handler = TeachingCalendarGetter()
        resp = handler.handler(session)
        print(resp.model_dump_json())
        self.assertIsNotNone(resp)

    def test_async_handler(self):
        """测试异步获取教学日历"""
        from xtu_ems.ems.account import AuthenticationAccount
        from xtu_ems.ems.ems import QZEducationalManageSystem
        account = AuthenticationAccount(username=username,
                                        password=password)
        ems = QZEducationalManageSystem()
        session = ems.login(account)
        from xtu_ems.ems.handler.get_teaching_calendar import TeachingCalendarGetter
        handler = TeachingCalendarGetter()
        import asyncio
        resp = asyncio.run(handler.async_handler(session))
        print(resp.model_dump_json())
        self.assertIsNotNone(resp)
