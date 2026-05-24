import ChatWidget from './components/ChatWidget'

export default function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900
                    flex flex-col items-center justify-center p-4">
      {/* Logo / branding */}
      <div className="mb-4 flex flex-col items-center gap-1 select-none">
        <div className="w-14 h-14 rounded-2xl bg-blue-600 flex items-center justify-center
                        text-3xl shadow-lg shadow-blue-900/40">
          💬
        </div>
        <span className="text-white/70 text-sm font-medium tracking-wide mt-1">
          Customer Care Bot
        </span>
      </div>

      {/* Chat widget — full height on mobile, fixed height on desktop */}
      <div className="w-full max-w-2xl h-[80vh] min-h-[500px]">
        <ChatWidget />
      </div>

      <p className="mt-4 text-white/30 text-xs">
        Powered by Gemini Flash · RAG · ChromaDB
      </p>
    </div>
  )
}
