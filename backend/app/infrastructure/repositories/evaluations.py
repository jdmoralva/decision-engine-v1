from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session, sessionmaker


@dataclass(frozen=True)
class PersistedEvaluationVersions:
    workflow_version_id: str | None
    variable_catalog_version_id: str | None
    parameter_set_id: str | None
    pipeline_version: str
    rule_set_version: str


class SqlAlchemyEvaluationsRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory
