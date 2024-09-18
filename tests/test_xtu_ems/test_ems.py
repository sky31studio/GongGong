import os
from unittest import TestCase

username = os.getenv("XTU_USERNAME")
password = os.getenv("XTU_PASSWORD")


class TestZQEducationalManageSystem(TestCase):
    def test_login(self):
        """测试登录"""
        from xtu_ems.ems.account import AuthenticationAccount
        from xtu_ems.ems.ems import QZEducationalManageSystem
        account = AuthenticationAccount(username=username,
                                        password=password)
        ems = QZEducationalManageSystem()
        session = ems.login(account)
        self.assertIsNotNone(session)
