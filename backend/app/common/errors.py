"""Structured API errors with a stable JSON shape (spec 04 §1)."""
from __future__ import annotations

from typing import Any, Optional

from fastapi import HTTPException


class ApiError(HTTPException):
    """HTTPException carrying a machine-readable error code.

    Rendered by the global handler as::

        {"error": {"code", "message", "request_id", "retry_after_seconds"}}
    """

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        *,
        retry_after_seconds: Optional[int] = None,
        headers: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=message, headers=headers)
        self.code = code
        self.message = message
        self.retry_after_seconds = retry_after_seconds


def bad_request(message: str, code: str = "BAD_REQUEST") -> ApiError:
    return ApiError(400, code, message)


def unauthorized(message: str = "Authentication required.", code: str = "UNAUTHENTICATED") -> ApiError:
    return ApiError(401, code, message)


def forbidden(message: str = "Insufficient permission.", code: str = "FORBIDDEN") -> ApiError:
    return ApiError(403, code, message)


def not_found(message: str = "Not found.", code: str = "NOT_FOUND") -> ApiError:
    return ApiError(404, code, message)


def conflict(message: str, code: str = "CONFLICT") -> ApiError:
    return ApiError(409, code, message)


def gone(message: str, code: str = "GONE") -> ApiError:
    return ApiError(410, code, message)


def unprocessable(message: str, code: str = "VALIDATION_ERROR") -> ApiError:
    return ApiError(422, code, message)


def rate_limited(message: str = "Too many requests.", retry_after: int = 60) -> ApiError:
    return ApiError(
        429,
        "RATE_LIMITED",
        message,
        retry_after_seconds=retry_after,
        headers={"Retry-After": str(retry_after)},
    )


def unavailable(message: str, code: str = "UNAVAILABLE", retry_after: int = 60) -> ApiError:
    return ApiError(
        503,
        code,
        message,
        retry_after_seconds=retry_after,
        headers={"Retry-After": str(retry_after)},
    )
