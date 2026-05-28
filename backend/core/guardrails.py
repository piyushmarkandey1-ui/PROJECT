"""
GuardrailsEngine — topic filtering and PII sanitization.

Responsibilities:
  1. is_on_topic()       — reject clearly off-topic messages before hitting the LLM
  2. contains_pii()      — detect PII in text (CC, SSN, passwords)
  3. sanitize_response() — redact PII patterns from LLM output
  4. get_system_prompt() — build the company-specific system prompt for Gemini
  5. off_topic_response()— canned response for off-topic messages
"""
import logging
import re

logger = logging.getLogger(__name__)

# Messages containing these keywords are rejected before reaching the LLM
OFF_TOPIC_KEYWORDS = [
    "write code", "python script", "javascript", "algorithm", "math problem",
    "solve equation", "creative writing", "poem", "story", "politics",
    "election", "recipe", "weather", "sports score", "stock price",
]

# Messages containing these keywords are always allowed through
SUPPORT_KEYWORDS = [
    "order", "product", "billing", "invoice", "payment", "refund", "return",
    "shipping", "delivery", "account", "password", "subscription", "cancel",
    "complaint", "broken", "damaged", "missing", "wrong", "help", "support",
    "warranty", "exchange", "track", "status", "charge", "price", "discount",
    "coupon", "promo", "upgrade", "downgrade", "error", "issue", "problem",
]

# PII detection patterns
_CC_PATTERN = re.compile(r"\b(?:\d[ -]?){13,16}\b")
_SSN_PATTERN = re.compile(r"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b")
_PASSWORD_PATTERN = re.compile(r"(?i)(password\s*[:=]\s*\S+)")


class GuardrailsEngine:
    """
    Lightweight guardrails layer applied before and after LLM calls.

    Usage in ChatHandler:
        if not guardrails.is_on_topic(user_message):
            return guardrails.off_topic_response()
        ...
        bot_response = guardrails.sanitize_response(llm_output)
    """

    def is_on_topic(self, message: str) -> bool:
        """
        Return False only for clearly off-topic messages (coding, politics, recipes, etc.).
        Default is True — let the LLM handle ambiguous cases.
        """
        lower = message.lower()

        if any(kw in lower for kw in OFF_TOPIC_KEYWORDS):
            logger.info("Off-topic message detected: %s", message[:80])
            return False

        if any(kw in lower for kw in SUPPORT_KEYWORDS):
            return True

        # Short messages (greetings, single words) are always allowed
        if len(message.split()) <= 8:
            return True

        return True  # Default: allow — LLM will handle gracefully

    def contains_pii(self, text: str) -> bool:
        """Return True if text contains credit card, SSN, or password patterns."""
        return bool(
            _CC_PATTERN.search(text)
            or _SSN_PATTERN.search(text)
            or _PASSWORD_PATTERN.search(text)
        )

    def sanitize_response(self, text: str) -> str:
        """Redact PII patterns from LLM output before returning to the user."""
        text = _CC_PATTERN.sub("[REDACTED-CC]", text)
        text = _SSN_PATTERN.sub("[REDACTED-SSN]", text)
        text = _PASSWORD_PATTERN.sub("password: [REDACTED]", text)
        return text

    def get_system_prompt(self, company_name: str = "Our Company") -> str:
        """
        Build the system prompt injected into every Gemini request.
        Includes company name, core principles, and empathetic response examples.
        RAG context and session history are appended to this in ChatHandler.
        """
        return (
            f"You are a senior customer support assistant for {company_name}. "
            "Your goal is to resolve customer issues with concrete, useful help.\n\n"
            "Response policy (must follow):\n"
            "1. Be highly specific, actionable, and concrete. Give clear step-by-step instructions, options, timelines, or exact actions the customer can take immediately.\n"
            "2. Use the provided knowledge context as the primary source of truth.\n"
            "3. If exact details are missing, do NOT just give a generic refusal or immediately ask them to contact support. Provide standard troubleshooting steps, practical workarounds, or state what exact information is needed.\n"
            "4. Never invent policies, prices, order details, or guarantees not in context.\n"
            "5. Keep a warm, empathetic tone, especially for frustrated customers.\n"
            "6. Focus on immediate resolution first, ask 1-2 targeted follow-up questions to narrow down the problem, and offer escalation only as a last resort.\n"
            "7. Keep responses concise (usually 80-180 words), but complete.\n"
            f"8. Stay limited to support topics for {company_name}.\n\n"
            "Answer structure:\n"
            "- Start with a brief acknowledgment of the customer's issue.\n"
            "- Provide a direct answer and next best actions in bullet points when helpful.\n"
            "- Mention relevant source-backed details when available.\n"
            "- End with a practical follow-up question that can unblock resolution.\n\n"
            "If no relevant knowledge is available:\n"
            "- Be transparent that you do not have that exact policy/detail yet.\n"
            "- Still provide safe, practical next steps (what to check, what details to share).\n"
            "- Offer escalation to a human agent for account-specific decisions."
        )

    def off_topic_response(self) -> str:
        """Canned response returned when is_on_topic() returns False."""
        return (
            "I can help with customer support issues like orders, billing, refunds, delivery, "
            "account access, and product problems. Share your issue and any order/account details "
            "you can provide, and I will guide you step by step."
        )
