import os
from unittest import TestCase

username = os.getenv("XTU_USERNAME")
password = os.getenv("XTU_PASSWORD")


class TestZQEducationalManageSystem(TestCase):
    def test_login(self):
        """测试登录"""
        from ems.account import AuthenticationAccount
        from ems.ems import ZQEducationalManageSystem
        account = AuthenticationAccount(username=username,
                                        password=password)
        ems = ZQEducationalManageSystem()
        session = ems.login(account)
        self.assertIsNotNone(session)