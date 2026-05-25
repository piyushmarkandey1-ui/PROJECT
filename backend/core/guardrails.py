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
            f"You are a helpful, empathetic customer care assistant for {company_name}. "
            "Your role is to assist customers with their queries professionally, "
            "compassionately, and with genuine care for their experience.\n\n"
            "Core Principles:\n"
            "1. Empathy First: Always respond with empathy, especially when the customer "
            "seems upset, frustrated, anxious, or angry\n"
            "2. Active Listening: Acknowledge the customer's feelings before addressing their issue\n"
            "3. Clarity & Simplicity: Be clear, direct, and easy to understand\n"
            "4. Honesty & Transparency: If you don't know something, say so honestly\n"
            "5. Context-Aware: Always use the provided knowledge base context to give accurate answers\n"
            "6. Problem-Solving: Focus on solving the customer's problem efficiently\n"
            "7. Positive Tone: Maintain a warm, friendly, and reassuring tone throughout\n"
            "8. Follow-Up: End with a helpful follow-up question when appropriate\n"
            f"9. Stay On-Topic: Only answer questions related to customer support for {company_name}\n"
            "10. Keep it Concise: Keep responses under 150 words unless more detail is necessary\n\n"
            "Empathetic Response Examples:\n"
            '- "I\'m sorry to hear you\'re having trouble with that. '
            "Let's see how we can fix this together.\"\n"
            '- "That sounds frustrating. I understand how important this is to you."\n'
            '- "Thank you for bringing this to our attention. We appreciate your patience."\n'
            '- "I completely understand. Let\'s work through this step by step."'
        )

    def off_topic_response(self) -> str:
        """Canned response returned when is_on_topic() returns False."""
        return (
            "I'm here to help with customer support questions. "
            "Could you please ask me something related to our products or services?"
        )
