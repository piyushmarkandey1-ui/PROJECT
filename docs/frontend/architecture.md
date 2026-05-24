# Frontend Architecture

## Directory Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ChatWidget.jsx          # Main chat interface
│   │   ├── MessageBubble.jsx        # Individual message display
│   │   ├── TypingIndicator.jsx     # Typing animation
│   │   └── EscalationAlert.jsx     # Escalation notification
│   ├── services/
│   │   └── api.js                   # API client
│   ├── App.jsx                      # Root component
│   ├── main.jsx                     # Entry point
│   └── index.css                    # Global styles
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
└── postcss.config.js
```

## Component Architecture

### Component Hierarchy
```
App
└── ChatWidget
    ├── MessageBubble (user messages)
    ├── MessageBubble (bot messages)
    ├── TypingIndicator
    └── EscalationAlert
```

## State Management

### Local State
Each component manages its own local state using React hooks:
- `useState` for component state
- `useEffect` for side effects
- `useCallback` for memoized callbacks

### Session State
Session state is stored in memory and managed via the backend API.

## API Integration

### API Client (`src/services/api.js`)
The API client provides a clean interface for backend communication:
- `sendMessage()` - Send chat messages
- `createSession()` - Create new chat session
- `getHistory()` - Retrieve conversation history

## Styling

### Tailwind CSS
The project uses Tailwind CSS for utility-first styling:
- Responsive design
- Dark/light mode support
- Consistent color palette

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `http://localhost:8000` |

## Build Process

### Development
```bash
npm run dev
```
- Hot Module Replacement (HMR)
- Fast refresh
- Source maps

### Production
```bash
npm run build
```
- Tree-shaking
- Code splitting
- Minification
- Asset optimization
