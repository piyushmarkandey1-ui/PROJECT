import logging
from datetime import datetime
from typing import Optional, List, Dict, Tuple

from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Enhanced emotional keyword categories
NEGATIVE_KEYWORDS = [
    "angry", "frustrated", "terrible", "awful", "worst", "hate",
    "useless", "disgusting", "refund", "lawsuit", "scam", "fraud",
    "cheat", "cancel", "furious", "outraged", "livid", "enraged",
    "annoyed", "irritated", "exasperated", "infuriated", "pissed",
]

POSITIVE_KEYWORDS = [
    "happy", "great", "excellent", "amazing", "fantastic", "wonderful",
    "love", "appreciate", "thank", "thanks", "perfect", "superb",
]

NEUTRAL_KEYWORDS = [
    "question", "ask", "inquire", "help", "please", "curious",
]

URGENCY_KEYWORDS = [
    "urgent", "immediately", "asap", "right now", "quickly",
    "emergency", "critical", "important", "hurry",
]

HUMAN_KEYWORDS = ["human", "agent", "representative", "person", "operator", "supervisor", "real person"]


class EmotionalState(BaseModel):
    sentiment: str  # positive / negative / neutral
    urgency: str  # low / medium / high
    emotion: Optional[str] = None  # happy, angry, etc.
    intensity: float = 0.5  # 0.0 to 1.0


class EscalationDecision(BaseModel):
    should_escalate: bool
    reason: str
    priority: str  # low / medium / high
    emotional_state: EmotionalState
    timestamp: datetime
    context_summary: Optional[str] = None


class EscalationEngine:
    def analyze_emotional_state(self, text: str) -> EmotionalState:
        """Enhanced emotional analysis with sentiment, urgency, and intensity."""
        lower = text.lower()
        
        # Count keyword hits
        negative_hits = sum(1 for kw in NEGATIVE_KEYWORDS if kw in lower)
        positive_hits = sum(1 for kw in POSITIVE_KEYWORDS if kw in lower)
        urgency_hits = sum(1 for kw in URGENCY_KEYWORDS if kw in lower)
        
        # Determine sentiment
        if negative_hits > positive_hits:
            sentiment = "negative"
            if negative_hits >= 3:
                emotion = "angry"
                intensity = 0.9
            elif negative_hits >= 2:
                emotion = "frustrated"
                intensity = 0.7
            else:
                emotion = "dissatisfied"
                intensity = 0.5
        elif positive_hits > negative_hits:
            sentiment = "positive"
            emotion = "happy"
            intensity = min(0.9, 0.5 + (positive_hits * 0.15))
        else:
            sentiment = "neutral"
            emotion = None
            intensity = 0.3
        
        # Determine urgency
        if urgency_hits >= 2:
            urgency = "high"
        elif urgency_hits == 1:
            urgency = "medium"
        else:
            urgency = "low"
        
        logger.debug(
            "Emotional analysis: sentiment=%s, urgency=%s, emotion=%s, intensity=%.2f",
            sentiment, urgency, emotion, intensity
        )
        
        return EmotionalState(
            sentiment=sentiment,
            urgency=urgency,
            emotion=emotion,
            intensity=intensity
        )

    def should_escalate(
        self,
        session_id: str,
        user_message: str,
        bot_confidence: float,
        turn_count: int,
        conversation_history: Optional[List[Dict]] = None,
    ) -> EscalationDecision:
        """Enhanced escalation decision with emotional intelligence and context."""
        lower = user_message.lower()
        emotional_state = self.analyze_emotional_state(user_message)
        
        # Build context summary for escalation
        context_summary = None
        if conversation_history:
            recent = conversation_history[-5:]
            context_summary = "\n".join([
                f"{msg['role'].capitalize()}: {msg['content'][:100]}"
                for msg in recent
            ])

        # Condition 1: Extreme negative emotion with high urgency
        if emotional_state.sentiment == "negative" and emotional_state.intensity > 0.8 and emotional_state.urgency == "high":
            logger.warning(
                "Escalation triggered: extreme negative emotion (%.2f) + high urgency for session %s",
                emotional_state.intensity, session_id
            )
            return EscalationDecision(
                should_escalate=True,
                reason=f"Extreme {emotional_state.emotion or 'negative'} emotion with high urgency detected",
                priority="high",
                emotional_state=emotional_state,
                timestamp=datetime.utcnow(),
                context_summary=context_summary,
            )

        # Condition 2: Negative sentiment with any urgency after 2 turns
        if emotional_state.sentiment == "negative" and emotional_state.urgency != "low" and turn_count > 2:
            logger.info(
                "Escalation triggered: negative sentiment + urgency after %d turns for session %s",
                turn_count, session_id
            )
            return EscalationDecision(
                should_escalate=True,
                reason=f"{emotional_state.emotion or 'Negative'} sentiment with {emotional_state.urgency} urgency in extended conversation",
                priority="high",
                emotional_state=emotional_state,
                timestamp=datetime.utcnow(),
                context_summary=context_summary,
            )

        # Condition 3: Low confidence
        if bot_confidence < 0.70:
            logger.info("Escalation triggered: low confidence (%.2f) for session %s", bot_confidence, session_id)
            return EscalationDecision(
                should_escalate=True,
                reason="Bot confidence below threshold",
                priority="medium",
                emotional_state=emotional_state,
                timestamp=datetime.utcnow(),
                context_summary=context_summary,
            )

        # Condition 4: Very negative sentiment even without urgency
        if emotional_state.sentiment == "negative" and emotional_state.intensity > 0.7:
            logger.info(
                "Escalation triggered: very negative sentiment (%.2f) for session %s",
                emotional_state.intensity, session_id
            )
            return EscalationDecision(
                should_escalate=True,
                reason=f"Very {emotional_state.emotion or 'negative'} sentiment detected",
                priority="high",
                emotional_state=emotional_state,
                timestamp=datetime.utcnow(),
                context_summary=context_summary,
            )

        # Condition 5: Long unresolved conversation
        if turn_count > 10:
            logger.info("Escalation triggered: long conversation (%d turns) for session %s", turn_count, session_id)
            return EscalationDecision(
                should_escalate=True,
                reason="Unresolved conversation exceeded 10 turns",
                priority="medium",
                emotional_state=emotional_state,
                timestamp=datetime.utcnow(),
                context_summary=context_summary,
            )

        # Condition 6: User explicitly requests human
        if any(kw in lower for kw in HUMAN_KEYWORDS):
            logger.info("Escalation triggered: user requested human agent for session %s", session_id)
            return EscalationDecision(
                should_escalate=True,
                reason="User explicitly requested human agent",
                priority="high",
                emotional_state=emotional_state,
                timestamp=datetime.utcnow(),
                context_summary=context_summary,
            )

        return EscalationDecision(
            should_escalate=False,
            reason="",
            priority="low",
            emotional_state=emotional_state,
            timestamp=datetime.utcnow(),
            context_summary=context_summary,
        )

    def generate_escalation_message(self, emotional_state: Optional[EmotionalState] = None) -> str:
        """Generate empathetic escalation message based on emotional state."""
        if emotional_state:
            if emotional_state.sentiment == "negative" and emotional_state.intensity > 0.7:
                return (
                    "I'm so sorry you're feeling this way. I can tell this is really important to you. "
                    "Let me connect you immediately with a specialist who can give this their full attention. "
                    "Please hold on while I transfer you."
                )
            elif emotional_state.urgency == "high":
                return (
                    "I understand this is urgent. Let me get you over to our priority support team right away. "
                    "They'll be with you shortly."
                )
        
        return (
            "I understand your concern. Let me connect you with a specialist "
            "who can better assist you. Please hold on."
        )

    def get_empathetic_greeting(self, emotional_state: Optional[EmotionalState] = None) -> str:
        """Get an empathetic greeting based on emotional state."""
        if not emotional_state:
            return "Hi there! How can I help you today?"
        
        if emotional_state.sentiment == "negative":
            if emotional_state.intensity > 0.7:
                return "I'm sorry you're having a tough time. Let's see how I can help."
            return "I'm here to help. What's going on?"
        elif emotional_state.sentiment == "positive":
            return "Great to hear! How can I assist you today?"
        
        return "Hi there! How can I help you today?"
