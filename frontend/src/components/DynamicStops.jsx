function tone(waiting) {
  if (waiting >= 20) {
    return 'border-orange-400/40 bg-orange-500/10 text-orange-100'
  }
  if (waiting >= 10) {
    return 'border-yellow-300/30 bg-yellow-400/10 text-yellow-50'
  }
  return 'border-emerald-400/30 bg-emerald-500/10 text-emerald-50'
}

function DynamicStops({ stop }) {
  return (
    <div className={`rounded-2xl border px-3 py-3 ${tone(stop.waiting)}`}>
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="font-medium">{stop.name}</p>
          <p className="text-xs uppercase tracking-[0.2em] text-white/60">Crowd load</p>
        </div>
        <div className="text-right">
          <p className="text-2xl font-semibold">{stop.waiting}</p>
          <p className="text-xs text-white/60">waiting</p>
        </div>
      </div>
    </div>
  )
}

export default DynamicStops
