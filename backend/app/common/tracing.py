"""Request/job tracing helpers and a tiny structured logger."""
from __future__ import annotations

import json
import logging
import sys
import uuid
from contextvars import ContextVar

_request_id: ContextVar[str | None] = ContextVar("request_id", default=None)

_logger = logging.getLogger("swissspeak")
if not _logger.handlers:
    _handler = logging.StreamHandler(sys.stdout)
    _handler.setFormatter(logging.Formatter("%(message)s"))
    _logger.addHandler(_handler)
    _logger.setLevel(logging.INFO)


def new_request_id() -> str:
    return str(uuid.uuid4())


def set_request_id(request_id: str) -> None:
    _request_id.set(request_id)


def get_request_id() -> str | None:
    return _request_id.get()


def log(level: str, event: str, **fields) -> None:
    """Emit a structured JSON log line. Never include raw tokens/secrets."""
    payload = {"event": event, "level": level, "request_id": get_request_id()}
    payload.update(fields)
    try:
        line = json.dumps(payload, default=str, ensure_ascii=False)
    except Exception:
        line = json.dumps({"event": event, "level": level})
    getattr(_logger, level if level in ("info", "warning", "error", "debug") else "info")(line)


def info(event: str, **fields) -> None:
    log("info", event, **fields)


def warning(event: str, **fields) -> None:
    log("warning", event, **fields)


def error(event: str, **fields) -> None:
    log("error", event, **fields)
