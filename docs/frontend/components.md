# Frontend Component Specification

---

## ChatWidget

**File:** `src/components/ChatWidget.jsx`

The main chat component. Manages the full lifecycle: session creation, streaming, escalation, and new-chat reset.

### Key Behaviours

- **Session persistence** — session ID stored in `localStorage` under `care_bot_session_id`
- **Streaming** — uses `sendMessageStream()` from `api.js`; tokens appear token-by-token
- **Model fallback** — if backend sends `{ reset: true }` SSE event, accumulated tokens are cleared and streaming continues from the new model
- **Escalation** — sets `isEscalated = true` when `metadata.is_escalated` is true in the SSE done event
- **Auto-scroll** — `useEffect` scrolls to bottom whenever `messages` or `loading` changes
- **Auto-grow textarea** — textarea grows up to 5 lines, resets on send

### State
```javascript
sessionId       // string — synced with localStorage
messages        // Message[]
input           // string
loading         // boolean
error           // string | null
isEscalated     // boolean
```

### Message Shape
```typescript
{
  role: 'user' | 'assistant'
  content: string
  timestamp: string          // ISO string
  _id?: number               // Date.now() — only on bot messages
  _streaming?: boolean       // true while tokens are arriving
}
```

### handleSend Flow
```
1. Append user message to messages[]
2. Append empty bot message { _streaming: true, _id: Date.now() }
3. Call sendMessageStream() — update bot message content on each token
4. On done: sync session_id, mark _streaming: false, check is_escalated
5. On error: replace bot message content with error text
```

---

## MessageBubble

**File:** `src/components/MessageBubble.jsx`

Renders a single message bubble for user or assistant.

### Props
| Prop | Type | Description |
|------|------|-------------|
| `message` | object | `{ role, content, timestamp, _streaming? }` |

### Behaviour
- User messages: right-aligned, blue background (`bg-blue-600 text-white`)
- Bot messages: left-aligned, white background (`bg-white text-gray-800`)
- While `_streaming: true`: shows a blinking cursor (`animate-pulse`) and hides the timestamp
- After streaming: cursor disappears, timestamp appears

### Streaming Cursor
```jsx
{message._streaming && (
  <span className="inline-block w-0.5 h-4 bg-gray-500 ml-0.5 animate-pulse align-middle" />
)}
```

---

## TypingIndicator

**File:** `src/components/TypingIndicator.jsx`

Three bouncing dots shown while `loading` is true AND the bot message content is still empty (i.e., before the first token arrives).

### Props
| Prop | Type | Description |
|------|------|-------------|
| `visible` | boolean | Controls render |

### Usage in ChatWidget
```jsx
<TypingIndicator visible={loading && messages[messages.length - 1]?.content === ''} />
```

---

## EscalationAlert

**File:** `src/components/EscalationAlert.jsx`

Yellow warning banner shown when the backend sets `is_escalated: true`.

### Props
| Prop | Type | Description |
|------|------|-------------|
| `visible` | boolean | Controls render |
| `onDismiss` | function | Called when × is clicked |

### Appearance
```
⚠️  You are being connected to a human agent    ×
```
Yellow background (`bg-yellow-50`), amber border, dismissible.

---

## App

**File:** `src/App.jsx`

Root component — provides branding wrapper and renders `ChatWidget`.

- Dark gradient background (`from-slate-900 via-blue-950 to-slate-900`)
- Bot emoji logo + "Customer Care Bot" label
- `ChatWidget` constrained to `max-w-2xl h-[80vh]`
- Footer: "Powered by Gemini Flash · RAG · ChromaDB"

---

## api.js

**File:** `src/services/api.js`

### `sendMessageStream(sessionId, message, onToken, companySlug?)`

Streams tokens from `POST /api/chat/stream` via SSE.

```javascript
// onToken signature:
// (token: string, reset?: boolean) => void
// reset=true means model switched mid-stream — clear accumulated text

const metadata = await sendMessageStream(sessionId, text, (token, reset) => {
  if (reset) accumulated = ''
  else accumulated += token
  updateUI(accumulated)
})
// metadata: { done, session_id, confidence, sources, turn_count, error? }
```

### `sendMessage(sessionId, message, companySlug?)`

Non-streaming. Returns full JSON response from `POST /api/chat`.

```javascript
const data = await sendMessage(sessionId, 'Hello')
// data: { session_id, response, confidence, is_escalated, ... }
```

### `createSession()`
```javascript
const { session_id } = await createSession()
```

### `getHistory(sessionId)`
```javascript
const { messages, count } = await getHistory(sessionId)
```

### Default `companySlug`
Both `sendMessage` and `sendMessageStream` default to `'demo-corp'`.  
To target a different company, pass the slug as the last argument.
