"""链接会话模块，用于存储会话信息"""


class Session(dict):
    """会话类，用于存储会话信息"""
    ID_IDX = '_session_id'

    def __init__(self, session_id: str) -> None:
        super().__init__()
        self.session_id = session_id

    @property
    def session_id(self) -> str:
        return self[Session.ID_IDX]

    @session_id.setter
    def session_id(self, session_id: str) -> None:
        self[Session.ID_IDX] = session_id
