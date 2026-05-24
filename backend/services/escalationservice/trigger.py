import logging
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

logger = logging.getLogger(__name__)

NEGATIVE_KEYWORDS = [
    "angry", "frustrated", "terrible", "awful", "worst", "hate",
    "useless", "disgusting", "refund", "lawsuit", "scam", "fraud",
    "cheat", "cancel",
]

HUMAN_KEYWORDS = ["human", "agent", "representative", "person", "operator", "supervisor"]


class EscalationDecision(BaseModel):
    should_escalate: bool
    reason: str
    priority: str  # low / medium / high
    timestamp: datetime


class EscalationEngine:
    def analyze_sentiment(self, text: str) -> str:
        lower = text.lower()
        negative_hits = sum(1 for kw in NEGATIVE_KEYWORDS if kw in lower)
        if negative_hits >= 2:
            return "negative"
        if negative_hits == 1:
            return "negative"
        return "neutral"

    def should_escalate(
        self,
        session_id: str,
        user_message: str,
        bot_confidence: float,
        turn_count: int,
    ) -> EscalationDecision:
        lower = user_message.lower()
        sentiment = self.analyze_sentiment(user_message)

        # Condition 1: Low confidence
        if bot_confidence < 0.70:
            logger.info("Escalation triggered: low confidence (%.2f) for session %s", bot_confidence, session_id)
            return EscalationDecision(
                should_escalate=True,
                reason="Bot confidence below threshold",
                priority="medium",
                timestamp=datetime.utcnow(),
            )

        # Condition 2: Negative sentiment after multiple turns
        if sentiment == "negative" and turn_count > 2:
            logger.info("Escalation triggered: negative sentiment after %d turns for session %s", turn_count, session_id)
            return EscalationDecision(
                should_escalate=True,
                reason="Negative sentiment detected in extended conversation",
                priority="high",
                timestamp=datetime.utcnow(),
            )

        # Condition 3: Long unresolved conversation
        if turn_count > 10:
            logger.info("Escalation triggered: long conversation (%d turns) for session %s", turn_count, session_id)
            return EscalationDecision(
                should_escalate=True,
                reason="Unresolved conversation exceeded 10 turns",
                priority="medium",
                timestamp=datetime.utcnow(),
            )

        # Condition 4: User explicitly requests human
        if any(kw in lower for kw in HUMAN_KEYWORDS):
            logger.info("Escalation triggered: user requested human agent for session %s", session_id)
            return EscalationDecision(
                should_escalate=True,
                reason="User explicitly requested human agent",
                priority="high",
                timestamp=datetime.utcnow(),
            )

        return EscalationDecision(
            should_escalate=False,
            reason="",
            priority="low",
            timestamp=datetime.utcnow(),
        )

    def generate_escalation_message(self) -> str:
        return (
            "I understand your concern. Let me connect you with a specialist "
            "who can better assist you. Please hold on."
        )
