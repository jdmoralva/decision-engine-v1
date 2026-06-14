from __future__ import annotations

import json
import logging
from contextlib import contextmanager
from contextvars import ContextVar, Token
from time import perf_counter


_request_id_var: ContextVar[str | None] = ContextVar("decision_engine_request_id", default=None)


def get_request_id() -> str | None:
    return _request_id_var.get()


def set_request_id(request_id: str | None) -> Token:
    return _request_id_var.set(request_id)


def reset_request_id(token: Token) -> None:
    _request_id_var.reset(token)


@contextmanager
def request_context(request_id: str | None):
    token = set_request_id(request_id)
    try:
        yield
    finally:
        reset_request_id(token)


def log_event(logger: logging.Logger, level: int, event: str, **fields: object) -> None:
    payload = {"event": event, **fields}
    request_id = get_request_id()
    if request_id is not None and "request_id" not in payload:
        payload["request_id"] = request_id
    logger.log(level, json.dumps(payload, default=str, sort_keys=True))


def now_seconds() -> float:
    return perf_counter()
