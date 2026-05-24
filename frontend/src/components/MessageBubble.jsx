export default function MessageBubble({ message }) {
  const isUser = message.role === 'user'

  const time = new Date(message.timestamp).toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
  })

  return (
    <div className={`flex items-end gap-2 fade-in ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
      {/* Avatar */}
      <div className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm
                      bg-gray-200 select-none">
        {isUser ? '👤' : '🤖'}
      </div>

      <div className={`flex flex-col max-w-[75%] ${isUser ? 'items-end' : 'items-start'}`}>
        {/* Label */}
        <span className="text-xs text-gray-400 mb-1 px-1">
          {isUser ? 'You' : 'Assistant'}
        </span>

        {/* Bubble */}
        <div
          className={`px-4 py-2.5 rounded-2xl text-sm leading-relaxed shadow-sm
            ${isUser
              ? 'bg-blue-600 text-white rounded-br-sm'
              : 'bg-white text-gray-800 rounded-bl-sm border border-gray-100'
            }`}
        >
          {message.content}
        </div>

        {/* Timestamp */}
        <span className="text-xs text-gray-400 mt-1 px-1">{time}</span>
      </div>
    </div>
  )
}
