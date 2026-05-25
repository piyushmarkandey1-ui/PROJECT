import { BrowserRouter as Router, Routes, Route, Link, useSearchParams } from 'react-router-dom'
import ChatWidget from './components/ChatWidget'
import CreateCompany from './components/CreateCompany'
import CompanyDashboard from './components/CompanyDashboard'

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
          <Link to="/create" className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
            Create Company
          </Link>
        </div>
      </div>
    </nav>
  )
}

function HomePage() {
  const [searchParams] = useSearchParams()
  const companySlug = searchParams.get('company') || 'demo-corp'

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 flex flex-col">
      <Header />
      <div className="flex-1 flex flex-col items-center justify-center p-4">
        <div className="mb-6 flex flex-col items-center gap-2 text-center">
          <h1 className="text-white text-3xl font-bold">
            {companySlug === 'demo-corp' ? 'Demo Chat Bot' : `${companySlug.replace(/-/g, ' ')} Assistant`}
          </h1>
          <p className="text-white/60 text-sm">
            {companySlug === 'demo-corp' 
              ? 'Try our customer care assistant with demo content' 
              : `White-labeled AI assistant for ${companySlug}`}
          </p>
        </div>
        <div className="w-full max-w-2xl h-[70vh] min-h-[500px]">
          <ChatWidget companySlug={companySlug} />
        </div>
        <p className="mt-4 text-white/30 text-xs">
          Powered by Gemini Flash · RAG · ChromaDB
        </p>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/create" element={<CreateCompany />} />
        <Route path="/dashboard/:slug" element={<CompanyDashboard />} />
      </Routes>
    </Router>
  )
}
