const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export async function sendMessage(sessionId, message, companyName = 'Our Company') {
  const res = await fetch(`${API_URL}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: sessionId,
      message,
      company_name: companyName,
    }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || `HTTP ${res.status}`)
  }
  return res.json()
}

export async function createSession() {
  const res = await fetch(`${API_URL}/api/session/new`, { method: 'POST' })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

export async function getHistory(sessionId) {
  const res = await fetch(`${API_URL}/api/session/${sessionId}/history`)
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}
