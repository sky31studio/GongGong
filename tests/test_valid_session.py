import os
from unittest import TestCase

from xtu_ems.ems.handler.valid_session import SessionValidator
from xtu_ems.ems.session import Session

username = os.getenv("XTU_USERNAME")
password = os.getenv("XTU_PASSWORD")


class TestSessionValidator(TestCase):
    def test_handler(self):
        validator = SessionValidator()
        from xtu_ems.ems.account import AuthenticationAccount
        from xtu_ems.ems.ems import QZEducationalManageSystem
        account = AuthenticationAccount(username=username,
                                        password=password)
        ems = QZEducationalManageSystem()
        session = ems.login(account)
        res = validator.handler(session=session)
        self.assertTrue(res)

    def test_handler_with_invalid_session(self):
        validator = SessionValidator()
        session = Session(session_id="6258ADBA22E73B91E06BD45EBFA9AEBD")
        res = validator.handler(session=session)
        self.assertFalse(res)
