const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

/**
 * Company management
 */
export async function createCompany(data) {
  const res = await fetch(`${API_URL}/api/companies`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || `HTTP ${res.status}`)
  }
  return res.json()
}

export async function getCompany(slug) {
  const res = await fetch(`${API_URL}/api/companies/${slug}`)
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || `HTTP ${res.status}`)
  }
  return res.json()
}

export async function listCompanies() {
  const res = await fetch(`${API_URL}/api/companies`)
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

/**
 * Knowledge base
 */
export async function uploadKnowledgeBase(file, apiKey) {
  const formData = new FormData()
  formData.append('file', file)
  
  const res = await fetch(`${API_URL}/api/knowledge/upload-csv`, {
    method: 'POST',
    headers: { 'X-API-Key': apiKey },
    body: formData,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || `HTTP ${res.status}`)
  }
  return res.json()
}

export async function getKnowledgeStats(companySlug, apiKey) {
  const headers = apiKey ? { 'X-API-Key': apiKey } : {}
  const res = await fetch(`${API_URL}/api/knowledge/stats?company_slug=${companySlug}`, {
    headers,
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

/**
 * Non-streaming chat — returns full response JSON.
 */
export async function sendMessage(sessionId, message, companySlug = 'demo-corp') {
  const res = await fetch(`${API_URL}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: sessionId,
      message,
      company_slug: companySlug,
    }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || `HTTP ${res.status}`)
  }
  return res.json()
}

/**
 * Streaming chat — calls onToken(text) for each chunk, returns final metadata.
 * Uses Server-Sent Events from /api/chat/stream.
 */
export async function sendMessageStream(sessionId, message, onToken, companySlug = 'demo-corp') {
  const res = await fetch(`${API_URL}/api/chat/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: sessionId,
      message,
      company_slug: companySlug,
    }),
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || `HTTP ${res.status}`)
  }

  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let metadata = null
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n\n')
    buffer = lines.pop() // keep incomplete chunk

    for (const line of lines) {
      if (!line.startsWith('data: ')) continue
      try {
        const data = JSON.parse(line.slice(6))
        if (data.reset) {
          // Model switched mid-stream — clear accumulated tokens
          onToken('', true /* reset */)
        } else if (data.token) {
          onToken(data.token)
        }
        if (data.done) metadata = data
      } catch {
        // ignore malformed SSE lines
      }
    }
  }

  return metadata
}

export async function createSession(companySlug) {
  const res = await fetch(`${API_URL}/api/session/new?company_slug=${companySlug}`, { method: 'POST' })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

export async function getHistory(companySlug, sessionId) {
  const res = await fetch(`${API_URL}/api/session/${companySlug}/${sessionId}/history`)
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}
