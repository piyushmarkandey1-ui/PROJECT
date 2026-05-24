# Frontend Component Specification

## ChatWidget

**File:** `src/components/ChatWidget.jsx`

### Description
Main chat interface component that orchestrates the entire chat experience.

### Props
| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `companySlug` | string | Yes | - | Company identifier |
| `companyName` | string | No | "Our Company" | Display name of the company |
| `initialMessage` | string | No | - | Initial bot message |

### State
```javascript
const [messages, setMessages] = useState([]);
const [inputText, setInputText] = useState("");
const [isTyping, setIsTyping] = useState(false);
const [sessionId, setSessionId] = useState(null);
const [showEscalation, setShowEscalation] = useState(false);
```

### Methods
- `handleSendMessage()` - Sends user message to backend
- `handleKeyPress()` - Handles Enter key for sending
- `scrollToBottom()` - Auto-scrolls chat to latest message

### Usage
```jsx
<ChatWidget
  companySlug="acme-corp"
  companyName="Acme Corporation"
  initialMessage="Hi! How can I help you today?"
/>
```

---

## MessageBubble

**File:** `src/components/MessageBubble.jsx`

### Description
Displays individual chat messages with styling based on sender.

### Props
| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `message` | string | Yes | - | Message text |
| `sender` | string | Yes | - | "user" or "assistant" |
| `timestamp` | Date | No | - | Message timestamp |

### Styling
- **User messages**: Right-aligned, blue background
- **Bot messages**: Left-aligned, gray background
- Supports markdown rendering

### Usage
```jsx
<MessageBubble
  message="Hello, how can I help?"
  sender="assistant"
  timestamp={new Date()}
/>
```

---

## TypingIndicator

**File:** `src/components/TypingIndicator.jsx`

### Description
Animated indicator showing the bot is "typing".

### Props
| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `visible` | boolean | No | true | Controls visibility |

### Animation
Three bouncing dots animation with 0.5s delay between each dot.

### Usage
```jsx
<TypingIndicator visible={isTyping} />
```

---

## EscalationAlert

**File:** `src/components/EscalationAlert.jsx`

### Description
Alert component shown when conversation is escalated to human agent.

### Props
| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `visible` | boolean | No | false | Controls visibility |
| `reason` | string | No | - | Escalation reason |
| `onClose` | function | No | - | Callback when closed |

### Usage
```jsx
<EscalationAlert
  visible={showEscalation}
  reason="Low confidence"
  onClose={() => setShowEscalation(false)}
/>
```

---

## App

**File:** `src/App.jsx`

### Description
Root application component.

### State
```javascript
const [companySlug, setCompanySlug] = useState("acme-corp");
```

### Usage
```jsx
<App />
```

---

## api.js

**File:** `src/services/api.js`

### Description
API client for backend communication.

### Functions

#### sendMessage(sessionId, message, companyName)
Sends a chat message to the backend.

**Parameters:**
- `sessionId` (string, optional) - Existing session ID
- `message` (string) - User message
- `companyName` (string, optional) - Company name

**Returns:** Promise resolving to chat response

#### createSession()
Creates a new chat session.

**Returns:** Promise resolving to session object

#### getHistory(sessionId)
Retrieves conversation history.

**Parameters:**
- `sessionId` (string) - Session ID

**Returns:** Promise resolving to history array

### Usage
```javascript
import { sendMessage, createSession, getHistory } from './services/api';

const response = await sendMessage(null, "Hello", "Acme Corp");
const session = await createSession();
const history = await getHistory(session.session_id);
```
