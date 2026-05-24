import logging
from datetime import datetime

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from core.config import get_settings
from core.guardrails import GuardrailsEngine
from models.schemas import ChatResponse
from services.escalationservice.trigger import EscalationEngine
from services.ragservice.retriever import Retriever
from services.sessionservice.memory import SessionManager

logger = logging.getLogger(__name__)


class ChatHandler:
    def __init__(self):
        settings = get_settings()
        self._llm = ChatGoogleGenerativeAI(
            model=settings.LLM_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.3,
            max_output_tokens=settings.MAX_TOKENS,
        )
        self._retriever = Retriever()
        self._session_manager = SessionManager()
        self._escalation_engine = EscalationEngine()
        self._guardrails = GuardrailsEngine()

    async def process_message(
        self,
        session_id: str,
        user_message: str,
        company_slug: str = "default",
        company_name: str = "Our Company",
    ) -> ChatResponse:

        # ── Step 1: Guardrails ──────────────────────────────────────────
        if not self._guardrails.is_on_topic(user_message):
            off_topic = self._guardrails.off_topic_response()
            self._session_manager.add_message(company_slug, session_id, "user", user_message)
            self._session_manager.add_message(company_slug, session_id, "assistant", off_topic)
            history = self._session_manager.get_history(company_slug, session_id)
            return ChatResponse(
                session_id=session_id,
                response=off_topic,
                confidence=1.0,
                is_escalated=False,
                retrieved_sources=[],
                turn_count=len(history),
                timestamp=datetime.utcnow(),
            )

        # ── Step 2: Session context ─────────────────────────────────────
        session_summary = self._session_manager.get_session_summary(company_slug, session_id)
        history = self._session_manager.get_history(company_slug, session_id)
        turn_count = len(history)

        # ── Step 3: RAG retrieval (company-specific) ────────────────────
        retrieved_docs = self._retriever.retrieve(user_message, company_slug)
        context = self._retriever.format_context(retrieved_docs)
        is_relevant = self._retriever.is_relevant(user_message, company_slug)
        confidence = 0.85 if is_relevant else 0.55

        # ── Step 4: Build prompt ────────────────────────────────────────
        system_content = self._guardrails.get_system_prompt(company_name)
        if context:
            system_content += f"\n\n{context}"
        if session_summary:
            system_content += f"\n\nConversation so far:\n{session_summary}"

        # ── Step 5: LLM call (async) ────────────────────────────────────
        bot_response = ""
        try:
            messages = [
                SystemMessage(content=system_content),
                HumanMessage(content=user_message),
            ]
            ai_response = await self._llm.ainvoke(messages)
            bot_response = ai_response.content
        except Exception as e:
            logger.error("LLM call failed: %s", e)
            bot_response = (
                "I'm sorry, I'm having trouble processing your request right now. "
                "Please try again in a moment."
            )
            confidence = 0.0

        # ── Step 6: Escalation check ────────────────────────────────────
        escalation = self._escalation_engine.should_escalate(
            session_id, user_message, confidence, turn_count
        )
        if escalation.should_escalate:
            bot_response = self._escalation_engine.generate_escalation_message()

        # ── Step 7: Sanitise & persist ──────────────────────────────────
        bot_response = self._guardrails.sanitize_response(bot_response)
        self._session_manager.add_message(company_slug, session_id, "user", user_message)
        self._session_manager.add_message(company_slug, session_id, "assistant", bot_response)

        updated_history = self._session_manager.get_history(company_slug, session_id)
        sources = list({doc.source for doc in retrieved_docs})

        return ChatResponse(
            session_id=session_id,
            response=bot_response,
            confidence=round(confidence, 2),
            is_escalated=escalation.should_escalate,
            escalation_reason=escalation.reason if escalation.should_escalate else None,
            retrieved_sources=sources,
            turn_count=len(updated_history),
            timestamp=datetime.utcnow(),
        )
