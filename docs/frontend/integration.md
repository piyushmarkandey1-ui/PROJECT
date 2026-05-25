# Frontend Integration Guide

## Getting Started

### Installation
```bash
cd frontend
npm install
```

### Development Server
```bash
npm run dev
```
Visit http://localhost:5173

### Production Build
```bash
npm run build
npm run preview   # preview locally before deploying
```

---

## Environment Configuration

Create `.env` in the `frontend/` directory:
```env
VITE_API_URL=http://localhost:8000
```

**Production (Vercel):** Set `VITE_API_URL` to your Railway backend URL in Vercel's environment variables dashboard.

---

## Connecting to a Company

The chat widget defaults to `demo-corp`. To use a different company, update the `companySlug` in `api.js`:

```javascript
// src/services/api.js
export async function sendMessageStream(sessionId, message, onToken, companySlug = 'your-company-slug') {
```

Or pass it dynamically from `ChatWidget.jsx`:
```jsx
const data = await sendMessageStream(sessionId, text, onToken, 'acme-corp')
```

---

## Streaming Integration

The frontend uses Server-Sent Events (SSE) for streaming. The `sendMessageStream` function handles the full SSE lifecycle:

```javascript
import { sendMessageStream } from './services/api'

let accumulated = ''

const metadata = await sendMessageStream(
  sessionId,
  userMessage,
  (token, reset = false) => {
    if (reset) accumulated = ''   // model switched mid-stream
    else accumulated += token
    updateUI(accumulated)
  },
  'demo-corp'
)

// After streaming completes:
console.log(metadata.session_id)   // sync session
console.log(metadata.confidence)   // 0.85 = KB hit, 0.55 = no KB match
console.log(metadata.is_escalated) // true if escalated
```

### SSE Event Types

| Event | Meaning |
|-------|---------|
| `{ token: "..." }` | Next token to append |
| `{ reset: true }` | Model switched — clear accumulated text |
| `{ done: true, session_id, confidence, sources, turn_count }` | Stream complete |
| `{ token: "...", error: true }` | All models rate-limited |

---

## Deployment (Vercel)

### 1. Install Vercel CLI
```bash
npm install -g vercel
```

### 2. Build and deploy
```bash
cd frontend
npm run build
vercel --prod
```

### 3. Set environment variable
In Vercel dashboard → Settings → Environment Variables:
```
VITE_API_URL = https://your-backend.railway.app
```

---

## Customisation

### Change Company
Update the default `companySlug` in `api.js` or pass it as a prop.

### Change Colours
Edit Tailwind classes in `ChatWidget.jsx`:
- Header: `bg-blue-600` → any Tailwind colour
- User bubbles: `bg-blue-600` → any colour
- Background: `bg-gray-50` → any colour

### Change Initial Message
In `ChatWidget.jsx`:
```jsx
const [messages, setMessages] = useState([
  {
    role: 'assistant',
    content: "Hi! 👋 Welcome to Acme Corp. How can I help you today?",
    timestamp: new Date().toISOString(),
  },
])
```

### Embed in Existing App
```jsx
import ChatWidget from './components/ChatWidget'

export default function SupportPage() {
  return (
    <div className="h-screen">
      <ChatWidget />
    </div>
  )
}
```

---

## Troubleshooting

### "Could not reach the server: Failed to fetch"
- Backend is not running — start it: `uvicorn main:app --port 8000`
- `VITE_API_URL` is wrong — check `.env`
- CORS issue — verify backend `allow_origins` includes your frontend URL

### Messages send but no response appears
- Check browser DevTools → Network → the `/api/chat/stream` request
- If status is 404: company slug doesn't exist — create it first
- If status is 500: check backend logs for the error

### Streaming stops mid-message
- Model quota hit — backend sends `{ reset: true }` and switches to fallback model
- The frontend clears accumulated text and continues from the new model
- If all models are exhausted, a rate-limit message is shown

### Session resets on page refresh
- Expected behaviour — session ID is in `localStorage` but session data is in-memory on the backend
- Sessions expire after 30 minutes of inactivity
- After a server restart, all sessions are lost (in-memory storage)
