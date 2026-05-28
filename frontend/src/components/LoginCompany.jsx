import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getMyCompany, loginWithEmailPassword } from '../services/api'

export default function LoginCompany() {
  const navigate = useNavigate()
  const [loginMethod, setLoginMethod] = useState('apikey') // 'apikey' or 'password'
  const [apiKey, setApiKey] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    setError(null)
  }, [])

  const handleApiKeySubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const company = await getMyCompany(apiKey.trim())
      localStorage.setItem(`care_bot_api_key_${company.slug}`, apiKey.trim())
      localStorage.setItem(`care_bot_company_${company.slug}`, JSON.stringify(company))
      navigate(`/dashboard/${company.slug}`, { state: { company } })
    } catch (err) {
      setError(err.message || 'Invalid API key')
    } finally {
      setLoading(false)
    }
  }

  const handlePasswordSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const response = await loginWithEmailPassword(email.trim(), password)
      const company = response.company
      localStorage.setItem(`care_bot_token_${company.slug}`, response.access_token)
      localStorage.setItem(`care_bot_company_${company.slug}`, JSON.stringify(company))
      navigate(`/dashboard/${company.slug}`, { state: { company } })
    } catch (err) {
      setError(err.message || 'Invalid email or password')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 flex flex-col">
      <nav className="w-full bg-slate-800/80 backdrop-blur-sm border-b border-slate-700 px-6 py-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-2xl shadow-lg shadow-blue-900/40">
              💬
            </div>
            <span className="text-white font-semibold text-lg">Customer Care Bot Platform</span>
          </div>
        </div>
      </nav>

      <div className="flex-1 flex items-center justify-center p-6">
        <div className="w-full max-w-xl bg-slate-800/90 backdrop-blur-sm rounded-2xl shadow-2xl border border-slate-700 p-8">
          <h1 className="text-3xl font-bold text-white mb-2">Company Login</h1>
          <p className="text-slate-400 mb-6 text-sm">
            Manage your knowledge base and dashboard.
          </p>

          {/* Login Method Toggle */}
          <div className="flex gap-2 mb-6">
            <button
              type="button"
              onClick={() => setLoginMethod('apikey')}
              className={`flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-colors ${
                loginMethod === 'apikey'
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-700/50 text-slate-300 hover:bg-slate-700'
              }`}
            >
              API Key
            </button>
            <button
              type="button"
              onClick={() => setLoginMethod('password')}
              className={`flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-colors ${
                loginMethod === 'password'
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-700/50 text-slate-300 hover:bg-slate-700'
              }`}
            >
              Email & Password
            </button>
          </div>

          {loginMethod === 'apikey' ? (
            <form onSubmit={handleApiKeySubmit} className="space-y-5">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">API Key</label>
                <input
                  type="password"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder="Paste your API key"
                  required
                  className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono"
                />
              </div>

              {error && (
                <div className="p-4 bg-red-500/20 border border-red-500/50 rounded-xl text-red-300 text-sm">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-3 px-6 rounded-xl transition-colors"
              >
                {loading ? 'Logging in…' : 'Login with API Key'}
              </button>
            </form>
          ) : (
            <form onSubmit={handlePasswordSubmit} className="space-y-5">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Email</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="company@example.com"
                  required
                  className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Password</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  required
                  className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {error && (
                <div className="p-4 bg-red-500/20 border border-red-500/50 rounded-xl text-red-300 text-sm">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-3 px-6 rounded-xl transition-colors"
              >
                {loading ? 'Logging in…' : 'Login with Email & Password'}
              </button>
            </form>
          )}

          <div className="mt-6 text-center text-slate-400 text-xs">
            Don&apos;t have an account? <a href="/signup" className="text-blue-400 hover:text-blue-300">Sign up</a>
          </div>
        </div>
      </div>
    </div>
  )
}

