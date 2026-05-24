export default function TypingIndicator({ visible }) {
  if (!visible) return null
  return (
    <div className="flex items-center gap-2 px-4 py-2">
      <span className="text-lg">🤖</span>
      <div className="flex items-center gap-1 bg-white rounded-2xl px-4 py-2 shadow-sm">
        {[0, 1, 2].map((i) => (
          <span
            key={i}
            className="w-2 h-2 bg-gray-400 rounded-full dot-bounce"
            style={{ animationDelay: `${i * 0.2}s` }}
          />
        ))}
        <span className="ml-2 text-xs text-gray-400">Assistant is typing...</span>
      </div>
    </div>
  )
}
