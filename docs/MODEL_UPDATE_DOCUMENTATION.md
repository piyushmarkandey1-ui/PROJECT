# Model & LLM Update Documentation

## Current Configuration (2026-05-25)

| Setting | Value |
|---------|-------|
| Primary model | `gemini-3.5-flash` |
| Fallback chain | `gemini-3.1-flash-lite` → `gemini-3-flash-preview` → `gemini-2.0-flash` → `gemini-2.0-flash-lite` |
| LLM framework | `langchain-google-genai==4.x` |
| Max tokens | `1024` |
| Temperature | `0.3` |
| Streaming | Enabled (`streaming=True`, `astream()`) |

---

## LangChain Version History

### v2.0.0 (original — broken)
- Used `v1beta` API endpoint
- `gemini-1.5-flash` not available → 404 errors
- `chunk.content` was `str`
- `max_output_tokens` parameter name

### v4.2.3 (current — working)
- Uses `google-genai` SDK internally
- `chunk.content` is now `list[dict]` → requires `_extract_chunk_text()`
- `max_tokens` parameter name (not `max_output_tokens`)
- `GOOGLE_API_KEY` env var required (not just `google_api_key` kwarg)
- `streaming=True` + `astream()` for token-by-token delivery

**Critical fix in `handler.py`:**
```python
def _extract_chunk_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            part.get("text", "")
            for part in content
            if isinstance(part, dict) and part.get("type") == "text"
        )
    return ""
```

---

## Model Selection Rationale

### Why `gemini-3.5-flash` as primary?
- Separate quota pool from `gemini-2.x` models
- ~1500 RPD on free tier (vs 20 RPD for `gemini-2.5-flash`)
- Fast response times suitable for customer care

### Why not `gemini-2.5-flash`?
- Only 20 RPD on free tier — exhausted in minutes during testing
- Caused all messages to return the same error response

### Why not `gemini-1.5-flash`?
- Not available on this API key (404 error)
- Removed from all configurations

### Fallback Chain Design
Each model in the chain has an independent quota counter. When one hits 429:
1. The error is caught by `_is_quota_error()`
2. The next model in `LLM_FALLBACK_MODELS` is tried
3. If all 5 models fail, a user-friendly rate-limit message is shown
4. The frontend handles `{ reset: true }` SSE events to clear partial tokens

---

## Changing the Primary Model

Update `.env`:
```env
LLM_MODEL=gemini-3.5-flash
```

Or to use a different model:
```env
LLM_MODEL=gemini-2.0-flash-lite
```

Available models on this API key (verified 2026-05-25):
```
gemini-3.5-flash
gemini-3.1-flash-lite
gemini-3.1-flash-image-preview
gemini-3-flash-preview
gemini-3-pro-preview
gemini-2.5-flash
gemini-2.5-flash-lite
gemini-2.0-flash
gemini-2.0-flash-lite
gemini-2.0-flash-001
```

---

## Free Tier Quota Reference (2026)

| Model | RPD | RPM | Notes |
|-------|-----|-----|-------|
| gemini-3.5-flash | ~1500 | 15 | Recommended primary |
| gemini-3.1-flash-lite | ~1500 | 15 | Good fallback |
| gemini-2.0-flash-lite | 1500 | 30 | Highest RPM |
| gemini-2.0-flash | 200 | 15 | Lower RPD |
| gemini-2.5-flash | 250 | 10 | Avoid as primary |
| gemini-2.5-pro | 100 | 5 | Very limited |

Quotas reset at **midnight Pacific time** daily.

---

## Upgrading LangChain

```bash
pip install --upgrade langchain-google-genai langchain-core
```

After upgrading, verify `chunk.content` format hasn't changed:
```python
import asyncio, os
os.environ['GOOGLE_API_KEY'] = 'your-key'
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

async def test():
    llm = ChatGoogleGenerativeAI(model='gemini-3.5-flash', max_tokens=20, streaming=True)
    async for chunk in llm.astream([HumanMessage(content='Hi')]):
        print(type(chunk.content), repr(chunk.content))
        break

asyncio.run(test())
```

If `chunk.content` is `list`, `_extract_chunk_text()` handles it.  
If it reverts to `str`, `_extract_chunk_text()` still handles it (first branch).
