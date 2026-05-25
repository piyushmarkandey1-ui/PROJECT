import logging
import os
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


def _extract_chunk_text(content) -> str:
    """
    LangChain-google-genai v4 changed chunk.content from str → list[dict].
    Handle both formats safely.
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            part.get("text", "")
            for part in content
            if isinstance(part, dict) and part.get("type") == "text"
        )
    return ""


def _is_quota_error(error_str: str) -> bool:
    return (
        "429" in error_str
        or "RESOURCE_EXHAUSTED" in error_str
        or "quota" in error_str.lower()
        or "Too Many Requests" in error_str
    )


def _make_llm(model: str, settings) -> ChatGoogleGenerativeAI:
    os.environ["GOOGLE_API_KEY"] = settings.GEMINI_API_KEY
    return ChatGoogleGenerativeAI(
        model=model,
        temperature=0.3,
        max_tokens=settings.MAX_TOKENS,
        streaming=True,
    )


class ChatHandler:
    def __init__(self):
        self._settings = get_settings()
        self._retriever = Retriever()
        self._session_manager = SessionManager()
        self._escalation_engine = EscalationEngine()
        self._guardrails = GuardrailsEngine()
        self._models = [self._settings.LLM_MODEL] + self._settings.fallback_model_list
        logger.info("ChatHandler ready. Model chain: %s", " → ".join(self._models))

    async def _stream_with_fallback(self, system_prompt: str, user_message: str) -> tuple[str, str]:
        """Try each model in chain. Returns (response_text, model_used)."""
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message),
        ]
        last_error = None

        for model_name in self._models:
            try:
                llm = _make_llm(model_name, self._settings)
                chunks = []
                async for chunk in llm.astream(messages):
                    text = _extract_chunk_text(chunk.content)
                    if text:
                        chunks.append(text)
                response = "".join(chunks)
                if response:
                    logger.info("Gemini OK (model=%s, chars=%d)", model_name, len(response))
                    return response, model_name
            except Exception as e:
                last_error = e
                if _is_quota_error(str(e)):
                    logger.warning("Quota hit on %s, trying next model...", model_name)
                    continue
                else:
                    raise

        raise last_error

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

        # ── Step 3: RAG retrieval ───────────────────────────────────────
        retrieved_docs = self._retriever.retrieve(user_message, company_slug)
        context = self._retriever.format_context(retrieved_docs)
        is_relevant = self._retriever.is_relevant(user_message, company_slug)
        confidence = 0.85 if is_relevant else 0.55

        # ── Step 4: Build system prompt ─────────────────────────────────
        system_content = self._guardrails.get_system_prompt(company_name)
        if context:
            system_content += f"\n\n{context}"
        if session_summary:
            system_content += f"\n\nConversation so far:\n{session_summary}"

        # ── Step 5: LLM call with fallback chain ────────────────────────
        llm_failed = False
        bot_response = ""
        try:
            bot_response, _ = await self._stream_with_fallback(system_content, user_message)
        except Exception as e:
            llm_failed = True
            error_str = str(e)
            logger.error("All models failed. Last error: %s", error_str[:300])
            if _is_quota_error(error_str):
                bot_response = "All AI models are currently rate-limited. Please wait a minute and try again."
            else:
                bot_response = "I'm sorry, I'm having trouble right now. Please try again."
                confidence = 0.0

        # ── Step 6: Escalation (only when LLM succeeded) ────────────────
        escalation_triggered = False
        escalation = self._escalation_engine.should_escalate(
            session_id, user_message, confidence, turn_count, history
        )
        if not llm_failed and escalation.should_escalate:
            escalation_triggered = True
            bot_response = self._escalation_engine.generate_escalation_message(
                escalation.emotional_state
            )
            logger.info("Escalation triggered for session %s: %s", session_id, escalation.reason)

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
            is_escalated=escalation_triggered,
            escalation_reason=escalation.reason if escalation_triggered else None,
            retrieved_sources=sources,
            turn_count=len(updated_history),
            timestamp=datetime.utcnow(),
        )
