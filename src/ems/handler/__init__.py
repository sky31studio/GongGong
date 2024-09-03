from abc import ABC, abstractmethod

from ems.session import Session


class Handler(ABC):
    @abstractmethod
    def handler(self, session: Session, *args, **kwargs):
        pass
