from __future__ import annotations

from sqlalchemy.orm import Session, sessionmaker


class SqlAlchemyCreditRequestsRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory
