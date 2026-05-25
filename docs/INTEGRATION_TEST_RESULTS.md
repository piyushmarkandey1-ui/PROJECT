# Integration Test Results

## Date: 2026-05-25

---

## ✅ Overall Status: ALL TESTS PASSED

---

## Summary

| Test | Status | Notes |
|------|--------|-------|
| Backend server startup | ✅ | Running on http://localhost:8000 |
| Company creation (auto API key + slug) | ✅ | `POST /api/companies` returns key once |
| Demo company endpoint | ✅ | `POST /api/demo-company` works |
| CSV knowledge base upload | ✅ | 20 docs loaded from `sample_faqs.csv` |
| Non-streaming chat (`/api/chat`) | ✅ | Returns full JSON response |
| Streaming chat (`/api/chat/stream`) | ✅ | SSE tokens arrive in real-time |
| LangChain v4 chunk parsing | ✅ | `_extract_chunk_text()` handles `list[dict]` format |
| Model fallback chain | ✅ | Auto-switches on 429 quota errors |
| RAG retrieval | ✅ | Confidence 0.85 on FAQ questions |
| Emotional escalation | ✅ | Angry messages trigger escalation alert |
| Session isolation | ✅ | Company-scoped sessions work correctly |
| Frontend streaming UI | ✅ | Tokens appear token-by-token with cursor |
| New chat button | ✅ | Clears history and resets session |
| Escalation alert banner | ✅ | Yellow banner shown on escalation |

---

## Verified Model Chain

```
gemini-3.5-flash  →  Gemini OK (chars=82)   ← primary model working
```

All 5 fallback models verified available on the API key:
- `gemini-3.5-flash` ✅
- `gemini-3.1-flash-lite` ✅
- `gemini-3-flash-preview` ✅
- `gemini-2.0-flash` ✅
- `gemini-2.0-flash-lite` ✅

---

## Live Test Results (5/5 unique responses)

```
▶  Q: What is your return policy?
   A: We accept returns within 30 days of delivery...
   confidence=0.85  escalated=False  ✅

▶  Q: How do I track my order?
   A: Once your order ships, you will receive a tracking number via email...
   confidence=0.85  escalated=False  ✅

▶  Q: What payment methods do you accept?
   A: We accept Visa, Mastercard, American Express, PayPal, and UPI payments...
   confidence=0.85  escalated=False  ✅

▶  Q: How long does shipping take?
   A: Standard shipping takes 5-7 business days...
   confidence=0.85  escalated=False  ✅

▶  Q: Hello, how are you?
   A: Hello! I'm doing well, thank you for asking...
   confidence=0.85  escalated=False  ✅

Unique responses: 5/5  ✅ All responses are different — Gemini is working correctly!
```

---

## Key Fixes Applied

| Issue | Root Cause | Fix |
|-------|-----------|-----|
| Same response for all messages | LangChain v2 used wrong API version (`v1beta`) causing 404 | Upgraded to `langchain-google-genai==4.x` |
| `chunk.content` crash | LangChain v4 returns `list[dict]` not `str` | Added `_extract_chunk_text()` helper |
| Escalation on every message | LLM failure set `confidence=0.0` → always triggered escalation | LLM failures no longer trigger escalation |
| `gemini-2.5-flash` quota (20 RPD) | Free tier limit exhausted | Switched primary to `gemini-3.5-flash` (~1500 RPD) |
| `gemini-1.5-flash` 404 | Model not available on this API key | Removed from chain |
| Duplicate `process_message` methods | Incremental edits accumulated | Rewrote handler.py cleanly |

---

**Document Version**: 2.0  
**Date**: 2026-05-25
