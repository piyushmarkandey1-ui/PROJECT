"""
End-to-end test script for the Customer Care Bot pipeline.

Usage:
    cd backend
    python test_bot.py
"""
import asyncio
import os
import sys

# Make sure backend root is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load .env BEFORE importing any project modules
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# Validate API key early
from core.config import get_settings
settings = get_settings()
if not settings.GEMINI_API_KEY:
    print("❌  GEMINI_API_KEY is not set in .env — aborting tests.")
    sys.exit(1)

from database.chromadb_client import get_document_count
from services.chatservice.handler import ChatHandler
from services.ragservice.embedder import KnowledgeBaseBuilder
from services.sessionservice.memory import SessionManager

FAQ_PATH = os.path.join(os.path.dirname(__file__), "data", "sample_faqs.csv")

TEST_MESSAGES = [
    "What is your return policy?",
    "I want a refund for my order",
    "I am very angry, this is terrible service!",
    "What are your shipping options?",
    "I need to speak to a human agent",
]


async def run_tests() -> bool:
    print("\n" + "=" * 62)
    print("   Customer Care Bot — End-to-End Test Suite")
    print("=" * 62)

    # ── 1. Seed knowledge base ──────────────────────────────────────────
    print("\n📚  Seeding knowledge base…")
    builder = KnowledgeBaseBuilder()
    count = builder.build_from_csv(FAQ_PATH, force_reload=True)
    print(f"    Total docs in KB: {get_document_count()}")

    # ── 2. Create session & handler ─────────────────────────────────────
    session_manager = SessionManager()
    session_id = session_manager.create_session()
    handler = ChatHandler()

    print(f"\n🔑  Session: {session_id}\n")
    print("-" * 62)

    results = []
    total_confidence = 0.0
    escalations = 0
    failures: list[str] = []

    for i, message in enumerate(TEST_MESSAGES, 1):
        print(f"\n[{i}/{len(TEST_MESSAGES)}] 👤  {message}")
        try:
            resp = await handler.process_message(
                session_id=session_id,
                user_message=message,
            )
            print(f"       🤖  {resp.response}")
            print(
                f"       📊  confidence={resp.confidence:.2f}  "
                f"escalated={resp.is_escalated}  "
                f"sources={len(resp.retrieved_sources)}"
            )
            total_confidence += resp.confidence
            if resp.is_escalated:
                escalations += 1
            results.append({"passed": True, **resp.model_dump()})
        except Exception as exc:
            print(f"       ❌  ERROR: {exc}")
            failures.append(f"Test {i} ({message!r}): {exc}")
            results.append({"passed": False, "message": message, "error": str(exc)})

    # ── Summary ─────────────────────────────────────────────────────────
    passed = sum(1 for r in results if r["passed"])
    avg_conf = total_confidence / max(passed, 1)

    print("\n" + "=" * 62)
    print("   SUMMARY")
    print("=" * 62)
    print(f"   Messages tested   : {len(TEST_MESSAGES)}")
    print(f"   Passed            : {passed}/{len(TEST_MESSAGES)}")
    print(f"   Avg confidence    : {avg_conf:.2f}")
    print(f"   Escalations       : {escalations}")

    if failures:
        print("\n   ❌  Failures:")
        for f in failures:
            print(f"      • {f}")
        print()
    else:
        print("\n   ✅  All tests passed\n")

    print("=" * 62 + "\n")
    return len(failures) == 0


if __name__ == "__main__":
    # Windows-safe event loop
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    success = asyncio.run(run_tests())
    sys.exit(0 if success else 1)
