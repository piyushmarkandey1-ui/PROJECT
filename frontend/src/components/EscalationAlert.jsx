export default function EscalationAlert({ visible, onDismiss }) {
  if (!visible) return null

  return (
    <div className="mx-4 mt-2 flex items-center justify-between bg-yellow-50 border border-yellow-300
                    rounded-xl px-4 py-3 shadow-sm fade-in flex-shrink-0">
      <div className="flex items-center gap-2">
        <span className="text-yellow-500 text-lg flex-shrink-0">⚠️</span>
        <span className="text-sm text-yellow-800 font-medium">
          You are being connected to a human agent
        </span>
      </div>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="text-yellow-500 hover:text-yellow-700 text-xl leading-none ml-4 flex-shrink-0"
          aria-label="Dismiss"
        >
          ×
        </button>
      )}
    </div>
  )
}
