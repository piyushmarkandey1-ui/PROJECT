# Frontend Architecture

## Directory Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ChatWidget.jsx       # Main chat UI — streaming, session, escalation
│   │   ├── MessageBubble.jsx    # Message display with streaming cursor
│   │   ├── TypingIndicator.jsx  # Animated dots (shown before first token)
│   │   └── EscalationAlert.jsx  # Yellow banner on escalation
│   ├── services/
│   │   └── api.js               # sendMessageStream() + sendMessage() + helpers
│   ├── App.jsx                  # Root — branding wrapper
│   ├── main.jsx                 # Entry point
│   └── index.css                # Global styles + animations
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
└── postcss.config.js
```

---

## Component Hierarchy

```
App
└── ChatWidget
    ├── Header (blue bar — title, online dot, New chat button)
    ├── EscalationAlert (yellow banner — conditionally rendered)
    ├── Messages list
    │   ├── MessageBubble × N  (user + assistant messages)
    │   └── TypingIndicator    (visible while loading + no content yet)
    ├── Error banner (red — conditionally rendered)
    └── Input area (textarea + send button)
```

---

## State Management

All state is local to `ChatWidget` using React hooks:

```javascript
const [sessionId, setSessionId]     // persisted in localStorage
const [messages, setMessages]       // array of { role, content, timestamp, _id, _streaming }
const [input, setInput]             // current textarea value
const [loading, setLoading]         // true while waiting for response
const [error, setError]             // error string or null
const [isEscalated, setIsEscalated] // shows EscalationAlert when true
```

### Streaming Message State
Each bot message has extra fields during streaming:
```javascript
{
  role: 'assistant',
  content: '',           // fills in token by token
  timestamp: '...',
  _id: 1748123456789,    // Date.now() — used as React key
  _streaming: true       // shows blinking cursor, hides timestamp
}
```

---

## Streaming Flow

```
User sends message
      │
      ▼
POST /api/chat/stream  (SSE)
      │
      ├── Empty bot message added to state (_streaming: true)
      │
      ├── SSE chunk: { token: "Hello" }  → append to message content
      ├── SSE chunk: { token: " there" } → append to message content
      ├── SSE chunk: { reset: true }     → clear content (model switched)
      ├── SSE chunk: { token: "Hi!" }    → append again
      │
      └── SSE chunk: { done: true, session_id, confidence, ... }
                → mark _streaming: false, sync session_id
```

---

## API Client (`src/services/api.js`)

### `sendMessageStream(sessionId, message, onToken, companySlug)`
Streams tokens via SSE. Calls `onToken(text, reset?)` for each chunk.

```javascript
const metadata = await sendMessageStream(
  sessionId,
  'Hello',
  (token, reset) => {
    if (reset) accumulated = ''
    else accumulated += token
    // update UI
  }
)
// metadata = { done, session_id, confidence, sources, turn_count }
```

### `sendMessage(sessionId, message, companySlug)`
Non-streaming fallback — returns full JSON response.

### `createSession()` / `getHistory(sessionId)`
Session management helpers.

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API base URL | `http://localhost:8000` |

Set in `.env` (development) or Vercel dashboard (production).

---

## Build

```bash
# Development (HMR, source maps)
npm run dev        # → http://localhost:5173

# Production
npm run build      # → dist/
npm run preview    # preview production build locally
```

Vite automatically:
- Tree-shakes unused code
- Code-splits by route
- Minifies JS and CSS
- Optimises assets
