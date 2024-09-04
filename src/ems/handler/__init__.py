from abc import ABC, abstractmethod

import requests

from ems.ems import ZQEducationalManageSystem
from ems.session import Session


class Handler(ABC):
    @abstractmethod
    def handler(self, session: Session, *args, **kwargs):
        pass

    def _get_session(self, session: Session):
        sess = requests.session()
        sess.cookies.set(ZQEducationalManageSystem.SESSION_NAME, session.session_id)
        return sess
