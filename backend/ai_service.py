# ─────────────────────────────────────────────
# ai_service.py — thin re-export shim
# All logic lives in backend/agents/
# ─────────────────────────────────────────────

from agents.intent_agent import detect_intent
from agents.chat_agent import real_estate_chat
from agents.extract_agent import extract_requirements

__all__ = [
    "detect_intent",
    "real_estate_chat",
    "extract_requirements",
]