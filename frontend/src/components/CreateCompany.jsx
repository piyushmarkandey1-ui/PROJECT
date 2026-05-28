import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { createCompany } from '../services/api'

function Header() {
  return (
    <nav className="w-full bg-slate-800/80 backdrop-blur-sm border-b border-slate-700 px-6 py-4">
      <div className="max-w-6xl mx-auto flex items-center justify-between">
        <Link to="/" className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-2xl shadow-lg shadow-blue-900/40">
            💬
          </div>
          <span className="text-white font-semibold text-lg">Customer Care Bot Platform</span>
        </Link>
        <div className="flex items-center gap-4">
          <Link to="/" className="text-white/70 hover:text-white transition-colors text-sm font-medium">
            Demo Chat
          </Link>
        </div>
      </div>
    </nav>
  )
}

export default function CreateCompany() {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    contact_phone: '',
    password: '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [createdCompany, setCreatedCompany] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const company = await createCompany(formData)
      setCreatedCompany(company)
      // Store for subsequent dashboard actions (KB upload, stats).
      localStorage.setItem(`care_bot_api_key_${company.slug}`, company.api_key)
      localStorage.setItem(`care_bot_company_${company.slug}`, JSON.stringify(company))
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value,
    }))
  }

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
    alert('API Key copied to clipboard!')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 flex flex-col">
      <Header />
      <div className="flex-1 flex items-center justify-center p-6">
        <div className="w-full max-w-xl bg-slate-800/90 backdrop-blur-sm rounded-2xl shadow-2xl border border-slate-700 p-8">
          {!createdCompany ? (
            <>
              <div className="text-center mb-8">
                <h1 className="text-3xl font-bold text-white mb-2">Create Your Company</h1>
                <p className="text-slate-400">Build a customized, white-labeled chat bot for your business</p>
              </div>
              <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">Company Name</label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    required
                    placeholder="Acme Corporation"
                    className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">Email Address</label>
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    required
                    placeholder="support@acme.com"
                    className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">Contact Phone (optional)</label>
                  <input
                    type="tel"
                    name="contact_phone"
                    value={formData.contact_phone}
                    onChange={handleChange}
                    placeholder="555-123-4567"
                    className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">Password (optional, min 8 chars)</label>
                  <input
                    type="password"
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    placeholder="Create a password for email login"
                    minLength={8}
                    className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <p className="text-slate-500 text-xs mt-1">Optional: If provided, enables email/password login</p>
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
                  {loading ? 'Creating...' : 'Create Company'}
                </button>
              </form>
            </>
          ) : (
            <div className="text-center space-y-6">
              <div className="w-20 h-20 bg-green-500/20 rounded-full flex items-center justify-center mx-auto">
                <span className="text-4xl">✅</span>
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white mb-2">Company Created!</h2>
                <p className="text-slate-400 mb-6">Your chat bot is ready. Save your API key securely.</p>
              </div>
              
              <div className="bg-slate-700/50 rounded-xl p-6 text-left space-y-4">
                <div>
                  <span className="text-slate-400 text-sm">Company Name</span>
                  <p className="text-white font-medium">{createdCompany.name}</p>
                </div>
                <div>
                  <span className="text-slate-400 text-sm">Company Slug</span>
                  <p className="text-white font-mono">{createdCompany.slug}</p>
                </div>
                <div>
                  <span className="text-slate-400 text-sm">API Key (save this!)</span>
                  <div className="flex items-center gap-2 mt-1">
                    <code className="flex-1 bg-slate-800 px-3 py-2 rounded-lg text-green-400 text-sm break-all">
                      {createdCompany.api_key}
                    </code>
                    <button
                      onClick={() => copyToClipboard(createdCompany.api_key)}
                      className="px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-lg transition-colors"
                    >
                      Copy
                    </button>
                  </div>
                </div>
              </div>

              <div className="flex gap-3">
                <Link
                  to={`/dashboard/${createdCompany.slug}`}
                  state={{ company: createdCompany }}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-xl transition-colors"
                >
                  Go to Dashboard
                </Link>
                <Link
                  to="/"
                  className="px-6 py-3 bg-slate-700 hover:bg-slate-600 text-white font-medium rounded-xl transition-colors"
                >
                  Home
                </Link>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
