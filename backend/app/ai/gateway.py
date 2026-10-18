"""AI capability gateway (spec 02 §4).

A small application-owned interface over text + speech providers. LiteLLM is used
for text when a real provider is configured; otherwise a deterministic fake
provider keeps dev/tests free and offline. Speech dialect quality is a launch
gate handled through voice-profile evaluation, not assumed here.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.ai.fake_provider import FakeSpeechProvider, validate_audio
from app.config import get_settings


class TextGateway:
    def generate_structured(self, *, route_alias: str, messages: List[dict],
                            schema: Optional[dict] = None, limits: Optional[dict] = None) -> Dict[str, Any]:
        raise NotImplementedError


class FakeTextGateway(TextGateway):
    """Deterministic text responses for tests (no external calls)."""

    def generate_structured(self, *, route_alias, messages, schema=None, limits=None) -> Dict[str, Any]:
        return {"ok": True, "route": route_alias, "content": {}, "tokens": 0, "cost_microunits": 0,
                "provider": "fake"}


class LiteLLMTextGateway(TextGateway):
    """Text generation via the existing LiteLLM helper, behind this interface."""

    def __init__(self) -> None:
        self._llm = None

    def _client(self):
        if self._llm is None:
            # Imported lazily so litellm is optional for the core app/tests.
            from vtlib.generative_llm import GenerativeLLM

            settings = get_settings()
            self._llm = GenerativeLLM({
                "OPENAI_APIKEY": settings.openai_apikey,
                "ANTHROPIC_API_KEY": settings.anthropic_api_key,
                "GOOGLE_GENAI_APIKEY": settings.google_genai_apikey,
            })
        return self._llm

    def generate_structured(self, *, route_alias, messages, schema=None, limits=None) -> Dict[str, Any]:
        response, meta = self._client().call(messages, response_format="json",
                                             max_tokens=(limits or {}).get("max_tokens"))
        return {"ok": response is not None, "route": route_alias, "content": response,
                "tokens": meta.get("tokens", 0), "cost_microunits": 0, "provider": "litellm"}


def get_text_gateway() -> TextGateway:
    settings = get_settings()
    if settings.ai_text_provider.lower() == "litellm":
        return LiteLLMTextGateway()
    return FakeTextGateway()


def get_speech_provider():
    settings = get_settings()
    # Only the fake provider ships enabled. Real providers require a passed
    # voice-profile evaluation before their routes are enabled in app_config.
    if settings.speech_provider.lower() == "fake":
        return FakeSpeechProvider()
    return FakeSpeechProvider()


__all__ = ["get_text_gateway", "get_speech_provider", "validate_audio"]
