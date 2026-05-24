import logging
import re

logger = logging.getLogger(__name__)

OFF_TOPIC_KEYWORDS = [
    "write code", "python script", "javascript", "algorithm", "math problem",
    "solve equation", "creative writing", "poem", "story", "politics",
    "election", "recipe", "weather", "sports score", "stock price",
]

SUPPORT_KEYWORDS = [
    "order", "product", "billing", "invoice", "payment", "refund", "return",
    "shipping", "delivery", "account", "password", "subscription", "cancel",
    "complaint", "broken", "damaged", "missing", "wrong", "help", "support",
    "warranty", "exchange", "track", "status", "charge", "price", "discount",
    "coupon", "promo", "upgrade", "downgrade", "error", "issue", "problem",
]

# PII patterns
_CC_PATTERN = re.compile(r"\b(?:\d[ -]?){13,16}\b")
_SSN_PATTERN = re.compile(r"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b")
_PASSWORD_PATTERN = re.compile(r"(?i)(password\s*[:=]\s*\S+)")


class GuardrailsEngine:
    def is_on_topic(self, message: str) -> bool:
        lower = message.lower()

        # Explicit off-topic check
        if any(kw in lower for kw in OFF_TOPIC_KEYWORDS):
            logger.info("Off-topic message detected: %s", message[:80])
            return False

        # If it contains support-related keywords, it's on-topic
        if any(kw in lower for kw in SUPPORT_KEYWORDS):
            return True

        # Short greetings and general questions are allowed
        if len(message.split()) <= 8:
            return True

        return True  # Default: allow and let the LLM handle it

    def contains_pii(self, text: str) -> bool:
        if _CC_PATTERN.search(text):
            return True
        if _SSN_PATTERN.search(text):
            return True
        if _PASSWORD_PATTERN.search(text):
            return True
        return False

    def sanitize_response(self, text: str) -> str:
        text = _CC_PATTERN.sub("[REDACTED-CC]", text)
        text = _SSN_PATTERN.sub("[REDACTED-SSN]", text)
        text = _PASSWORD_PATTERN.sub("password: [REDACTED]", text)
        return text

    def get_system_prompt(self, company_name: str = "Our Company") -> str:
        return (
            f"You are a helpful customer care assistant for {company_name}. "
            "Your role is to assist customers with their queries professionally and empathetically.\n\n"
            "Rules:\n"
            "1. Only answer questions related to customer support\n"
            "2. Be polite, clear, and concise\n"
            "3. If you don't know something, say so honestly\n"
            "4. Never make up information\n"
            "5. Always use the provided context to answer\n"
            "6. If context is insufficient, acknowledge limitations\n"
            "7. Keep responses under 150 words\n"
            "8. End responses with a follow-up question when appropriate"
        )

    def off_topic_response(self) -> str:
        return (
            "I'm here to help with customer support questions. "
            "Could you please ask me something related to our products or services?"
        )
