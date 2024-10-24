import json
import os
from unittest import TestCase

from xtu_ems.ems.handler.get_student_exam import StudentExamGetter

username = os.getenv("XTU_USERNAME")
password = os.getenv("XTU_PASSWORD")


class TestStudentExamGetter(TestCase):
    def test_handler(self):
        """测试获取学生考试信息"""
        from xtu_ems.ems.account import AuthenticationAccount
        from xtu_ems.ems.ems import QZEducationalManageSystem
        account = AuthenticationAccount(username=username,
                                        password=password)
        ems = QZEducationalManageSystem()
        session = ems.login(account)
        handler = StudentExamGetter()
        resp = handler.handler(session)
        print(json.dumps(resp, indent=4, ensure_ascii=False, default=str))
        self.assertIsNotNone(resp)

    def test_async_handler(self):
        """测试异步获取学生考试信息"""
        from xtu_ems.ems.account import AuthenticationAccount
        from xtu_ems.ems.ems import QZEducationalManageSystem
        account = AuthenticationAccount(username=username,
                                        password=password)
        ems = QZEducationalManageSystem()
        session = ems.login(account)
        handler = StudentExamGetter()
        import asyncio
        resp = asyncio.run(handler.async_handler(session))
        print(json.dumps(resp, indent=4, ensure_ascii=False, default=str))
        self.assertIsNotNone(resp)
