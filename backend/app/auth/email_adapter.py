"""Transactional email adapter.

``console`` writes the magic link to the structured log (development/tests).
Real providers implement ``send`` behind the same interface; secrets come from
the environment, never from MongoDB.
"""
from __future__ import annotations

from app.common import tracing
from app.config import get_settings

# In-memory capture for tests (console provider appends here).
SENT_MESSAGES: list[dict] = []


class EmailAdapter:
    async def send_magic_link(self, *, to_email: str, link: str, purpose: str) -> None:
        raise NotImplementedError


class ConsoleEmailAdapter(EmailAdapter):
    async def send_magic_link(self, *, to_email: str, link: str, purpose: str) -> None:
        # Never log the full token in production providers; console is dev-only.
        SENT_MESSAGES.append({"to": to_email, "link": link, "purpose": purpose})
        tracing.info("email_magic_link_console", to=to_email, purpose=purpose, link=link)


def get_email_adapter() -> EmailAdapter:
    settings = get_settings()
    provider = settings.email_provider.lower()
    if provider == "console":
        return ConsoleEmailAdapter()
    # Placeholder for SMTP/provider adapters (wired when EMAIL_PROVIDER is set).
    return ConsoleEmailAdapter()
