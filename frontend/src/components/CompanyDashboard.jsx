import { useState, useEffect } from 'react'
import { Link, useParams, useLocation } from 'react-router-dom'
import { getCompany, uploadKnowledgeBase, getKnowledgeStats } from '../services/api'
import ChatWidget from './ChatWidget'

function Header({ company }) {
  return (
    <nav className="w-full bg-slate-800/80 backdrop-blur-sm border-b border-slate-700 px-6 py-4">
      <div className="max-w-6xl mx-auto flex items-center justify-between">
        <Link to="/" className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-2xl shadow-lg shadow-blue-900/40">
            💬
          </div>
          <span className="text-white font-semibold text-lg">{company?.name || 'Dashboard'}</span>
        </Link>
        <div className="flex items-center gap-4">
          <Link to="/" className="text-white/70 hover:text-white transition-colors text-sm font-medium">
            Home
          </Link>
        </div>
      </div>
    </nav>
  )
}

export default function CompanyDashboard() {
  const { slug } = useParams()
  const location = useLocation()
  const [company, setCompany] = useState(location.state?.company || null)
  const [apiKey, setApiKey] = useState(() => (slug ? localStorage.getItem(`care_bot_api_key_${slug}`) : null))
  const [knowledgeStats, setKnowledgeStats] = useState(null)
  const [selectedFile, setSelectedFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [uploadError, setUploadError] = useState(null)
  const [uploadSuccess, setUploadSuccess] = useState(null)

  useEffect(() => {
    if (!slug) return

    // Prefer route state (after signup) but fall back to localStorage or public lookup.
    const storedApiKey = localStorage.getItem(`care_bot_api_key_${slug}`)
    setApiKey(storedApiKey)

    if (!company) {
      loadCompany()
    }

    if (storedApiKey) {
      loadKnowledgeStats(storedApiKey)
    }
  }, [slug])

  const loadCompany = async () => {
    try {
      const data = await getCompany(slug)
      setCompany(data)
    } catch (err) {
      console.error('Failed to load company:', err)
    }
  }

  const loadKnowledgeStats = async (key) => {
    try {
      const data = await getKnowledgeStats(slug, key)
      setKnowledgeStats(data)
    } catch (err) {
      console.error('Failed to load knowledge stats:', err)
    }
  }

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0])
    setUploadError(null)
    setUploadSuccess(null)
  }

  const handleUpload = async () => {
    if (!selectedFile || !apiKey) return
    setUploading(true)
    setUploadError(null)
    setUploadSuccess(null)
    try {
      const result = await uploadKnowledgeBase(selectedFile, apiKey)
      setUploadSuccess(result.message)
      setSelectedFile(null)
      loadKnowledgeStats(apiKey)
    } catch (err) {
      setUploadError(err.message)
    } finally {
      setUploading(false)
    }
  }

  const chatBotUrl = `${window.location.origin}/?company=${slug}`

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 flex flex-col">
      <Header company={company} />
      <div className="flex-1 p-6 max-w-6xl mx-auto w-full">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left column: Company Info & Knowledge Base */}
          <div className="space-y-6">
            <div className="bg-slate-800/90 backdrop-blur-sm rounded-2xl shadow-xl border border-slate-700 p-6">
              <h2 className="text-xl font-bold text-white mb-4">Company Details</h2>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">Name</span>
                  <span className="text-white font-medium">{company?.name}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">Slug</span>
                  <span className="text-white font-mono">{company?.slug}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">Email</span>
                  <span className="text-white">{company?.email}</span>
                </div>
              </div>
            </div>

            <div className="bg-slate-800/90 backdrop-blur-sm rounded-2xl shadow-xl border border-slate-700 p-6">
              <h2 className="text-xl font-bold text-white mb-4">Knowledge Base</h2>
              <div className="mb-4 p-4 bg-slate-700/50 rounded-xl">
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">Documents</span>
                  <span className={`font-bold ${knowledgeStats?.total_documents > 0 ? 'text-green-400' : 'text-yellow-400'}`}>
                    {knowledgeStats?.total_documents || 0}
                  </span>
                </div>
                <div className="flex justify-between items-center mt-2">
                  <span className="text-slate-400">Status</span>
                  <span className={`font-medium ${knowledgeStats?.status === 'ready' ? 'text-green-400' : 'text-yellow-400'}`}>
                    {knowledgeStats?.status || 'empty'}
                  </span>
                </div>
              </div>

              {!apiKey && (
                <div className="mb-4 p-4 bg-blue-500/15 border border-blue-500/30 rounded-xl text-blue-100 text-sm">
                  To upload or refresh knowledge base stats, log in with your company API key.
                </div>
              )}
              
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">Upload CSV File</label>
                  <input
                    type="file"
                    accept=".csv"
                    onChange={handleFileChange}
                    className="w-full text-slate-300 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-sm file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-700"
                  />
                </div>
                {selectedFile && (
                  <p className="text-slate-400 text-sm">Selected: {selectedFile.name}</p>
                )}
                {uploadError && (
                  <div className="p-3 bg-red-500/20 border border-red-500/50 rounded-xl text-red-300 text-sm">
                    {uploadError}
                  </div>
                )}
                {uploadSuccess && (
                  <div className="p-3 bg-green-500/20 border border-green-500/50 rounded-xl text-green-300 text-sm">
                    {uploadSuccess}
                  </div>
                )}
                <button
                  onClick={handleUpload}
                  disabled={!selectedFile || uploading || !apiKey}
                  className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-3 px-6 rounded-xl transition-colors"
                >
                  {uploading ? 'Uploading...' : 'Upload Knowledge Base'}
                </button>
              </div>
            </div>

            <div className="bg-slate-800/90 backdrop-blur-sm rounded-2xl shadow-xl border border-slate-700 p-6">
              <h2 className="text-xl font-bold text-white mb-4">Chat Bot URL</h2>
              <div className="flex items-center gap-2">
                <code className="flex-1 bg-slate-700/50 px-4 py-3 rounded-xl text-slate-300 text-sm break-all">
                  {chatBotUrl}
                </code>
                <button
                  onClick={() => navigator.clipboard.writeText(chatBotUrl)}
                  className="px-4 py-3 bg-slate-700 hover:bg-slate-600 text-white font-medium rounded-xl transition-colors"
                >
                  Copy
                </button>
              </div>
            </div>
          </div>

          {/* Right column: Live Chat Preview */}
          <div className="space-y-6">
            <div className="bg-slate-800/90 backdrop-blur-sm rounded-2xl shadow-xl border border-slate-700 p-6">
              <h2 className="text-xl font-bold text-white mb-4">Live Chat Preview</h2>
              <div className="h-[600px]">
                <ChatWidget companySlug={slug} />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
