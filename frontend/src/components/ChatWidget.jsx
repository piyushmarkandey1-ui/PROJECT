import { useState, useEffect, useRef, useCallback } from 'react'
import { v4 as uuidv4 } from 'uuid'
import MessageBubble from './MessageBubble'
import TypingIndicator from './TypingIndicator'
import EscalationAlert from './EscalationAlert'
import { sendMessage } from '../services/api'

const SESSION_KEY = 'care_bot_session_id'

function getOrCreateSessionId() {
  let id = localStorage.getItem(SESSION_KEY)
  if (!id) {
    id = uuidv4()
    localStorage.setItem(SESSION_KEY, id)
  }
  return id
}

export default function ChatWidget() {
  const [sessionId, setSessionId] = useState(getOrCreateSessionId)
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: "Hi! 👋 I'm your customer care assistant. How can I help you today?",
      timestamp: new Date().toISOString(),
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [isEscalated, setIsEscalated] = useState(false)

  const bottomRef = useRef(null)
  const inputRef = useRef(null)

  // Auto-scroll whenever messages change or typing indicator appears
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const handleSend = useCallback(async () => {
    const text = input.trim()
    if (!text || loading) return

    const userMsg = {
      role: 'user',
      content: text,
      timestamp: new Date().toISOString(),
    }

    setMessages((prev) => [...prev, userMsg])
    setInput('')
    setLoading(true)
    setError(null)

    try {
      const data = await sendMessage(sessionId, text)

      // Sync session id if backend assigned a new one
      if (data.session_id && data.session_id !== sessionId) {
        setSessionId(data.session_id)
        localStorage.setItem(SESSION_KEY, data.session_id)
      }

      const botMsg = {
        role: 'assistant',
        content: data.response,
        timestamp: data.timestamp || new Date().toISOString(),
      }
      setMessages((prev) => [...prev, botMsg])

      if (data.is_escalated) setIsEscalated(true)
    } catch (err) {
      console.error('Chat error:', err)
      setError(`Could not reach the server: ${err.message}`)
    } finally {
      setLoading(false)
      // Small delay so the DOM updates before we focus
      setTimeout(() => inputRef.current?.focus(), 50)
    }
  }, [input, loading, sessionId])

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleNewSession = () => {
    const newId = uuidv4()
    localStorage.setItem(SESSION_KEY, newId)
    setSessionId(newId)
    setMessages([
      {
        role: 'assistant',
        content: "Hi! 👋 I'm your customer care assistant. How can I help you today?",
        timestamp: new Date().toISOString(),
      },
    ])
    setIsEscalated(false)
    setError(null)
    setTimeout(() => inputRef.current?.focus(), 50)
  }

  return (
    <div className="flex flex-col h-full w-full max-w-2xl mx-auto bg-gray-50 rounded-2xl shadow-2xl overflow-hidden">

      {/* ── Header ── */}
      <div className="flex items-center gap-3 px-5 py-4 bg-blue-600 text-white shadow-md flex-shrink-0">
        <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center text-xl select-none">
          🤖
        </div>
        <div className="flex-1 min-w-0">
          <h1 className="font-semibold text-base leading-tight truncate">
            Customer Care Assistant
          </h1>
          <div className="flex items-center gap-1.5 mt-0.5">
            <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse flex-shrink-0" />
            <span className="text-xs text-blue-100">Online</span>
          </div>
        </div>
        <button
          onClick={handleNewSession}
          title="Start new conversation"
          className="text-xs text-blue-200 hover:text-white border border-blue-400 hover:border-white
                     rounded-lg px-2 py-1 transition-colors flex-shrink-0"
        >
          New chat
        </button>
      </div>

      {/* ── Escalation alert ── */}
      <EscalationAlert visible={isEscalated} onDismiss={() => setIsEscalated(false)} />

      {/* ── Messages ── */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4 bg-gray-50">
        {messages.map((msg, i) => (
          <MessageBubble key={i} message={msg} />
        ))}
        <TypingIndicator visible={loading} />
        <div ref={bottomRef} />
      </div>

      {/* ── Error banner ── */}
      {error && (
        <div className="mx-4 mb-2 flex items-center justify-between text-sm text-red-700
                        bg-red-50 border border-red-200 rounded-xl px-3 py-2 flex-shrink-0">
          <span>{error}</span>
          <button
            onClick={() => setError(null)}
            className="ml-3 text-red-400 hover:text-red-600 text-lg leading-none"
          >
            ×
          </button>
        </div>
      )}

      {/* ── Input area ── */}
      <div className="px-4 py-3 bg-white border-t border-gray-200 flex items-end gap-2 flex-shrink-0">
        <textarea
          ref={inputRef}
          rows={1}
          value={input}
          onChange={(e) => {
            setInput(e.target.value)
            // Auto-grow up to ~5 lines
            e.target.style.height = 'auto'
            e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px'
          }}
          onKeyDown={handleKeyDown}
          placeholder="Type your message… (Enter to send)"
          disabled={loading}
          className="flex-1 resize-none rounded-xl border border-gray-300 px-4 py-2.5 text-sm
                     focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
                     disabled:opacity-50 leading-relaxed overflow-hidden"
          style={{ minHeight: '42px', maxHeight: '120px' }}
        />
        <button
          onClick={handleSend}
          disabled={loading || !input.trim()}
          className="flex-shrink-0 w-10 h-10 rounded-xl bg-blue-600 text-white flex items-center
                     justify-center hover:bg-blue-700 active:scale-95 transition-all
                     disabled:opacity-40 disabled:cursor-not-allowed"
          aria-label="Send message"
        >
          {loading ? (
            <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
            </svg>
          ) : (
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
              <path d="M3.478 2.405a.75.75 0 00-.926.94l2.432 7.905H13.5a.75.75 0 010 1.5H4.984l-2.432 7.905a.75.75 0 00.926.94 60.519 60.519 0 0018.445-8.986.75.75 0 000-1.218A60.517 60.517 0 003.478 2.405z" />
            </svg>
          )}
        </button>
      </div>
    </div>
  )
}
