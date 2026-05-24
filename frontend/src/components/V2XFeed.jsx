import { MessagesSquare, Cpu, Clock } from 'lucide-react'

const actionStyle = (a) => ({
  HOLD:      'bg-yellow-500/20 text-yellow-300 border-yellow-500/30',
  SKIP_STOP: 'bg-orange-500/20 text-orange-300 border-orange-500/30',
  PROCEED:   'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
}[a] || 'bg-slate-500/20 text-slate-300 border-slate-500/30')

export default function V2XFeed({ feed }) {
  const items = [...feed].reverse()
  return (
    <div className="flex h-full flex-col overflow-hidden rounded-2xl border border-white/10 bg-[linear-gradient(180deg,rgba(8,17,24,.95),rgba(3,7,12,.95))]">
      <div className="flex items-center gap-3 border-b border-white/10 px-4 py-3">
        <MessagesSquare className="h-4 w-4 text-cyan-300"/>
        <div>
          <h2 className="font-bold text-base text-white">V2X Debate Feed</h2>
          <p className="text-[10px] text-slate-500 uppercase tracking-widest">Live corridor brain · V2V + V2I</p>
        </div>
        <span className="ml-auto rounded-full border border-cyan-400/20 bg-cyan-400/10 px-2 py-0.5 text-[10px] text-cyan-300">
          {items.length} events
        </span>
      </div>

      <div className="flex-1 space-y-2.5 overflow-y-auto px-3 py-3">
        {items.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-white/15 bg-white/[.03] px-4 py-6 text-center text-xs text-slate-500">
            Waiting for first V2V negotiation near a major stop…
          </div>
        ) : (
          items.map((entry, i) => (
            <article key={`${entry.stop}-${i}`} className="rounded-2xl border border-cyan-400/15 bg-cyan-400/[.04] p-3">
              <div className="mb-1.5 flex items-start justify-between gap-2">
                <span className="text-[10px] uppercase tracking-[.25em] text-cyan-300">{entry.stop}</span>
                <div className="flex items-center gap-1 text-[10px] text-slate-500">
                  <Clock className="h-2.5 w-2.5"/>
                  {entry.latency_ms ? `${entry.latency_ms}ms` : ''}
                </div>
              </div>

              {/* Actions */}
              <div className="mb-2 flex gap-1.5 flex-wrap">
                {[
                  {id: entry.bus_1_id, action: entry.decision?.bus_1_action},
                  {id: entry.bus_2_id, action: entry.decision?.bus_2_action},
                ].map(b => (
                  <span key={b.id} className={`rounded border px-1.5 py-0.5 text-[10px] font-bold ${actionStyle(b.action)}`}>
                    {b.id}: {b.action}
                  </span>
                ))}
                {entry.model && (
                  <span className="ml-auto flex items-center gap-1 rounded border border-slate-700 px-1.5 py-0.5 text-[10px] text-slate-500">
                    <Cpu className="h-2.5 w-2.5"/>{entry.model}
                  </span>
                )}
              </div>

              {/* Reasoning (ATIS signboard text) */}
              <p className="text-xs leading-relaxed text-slate-200">
                {entry.decision?.reasoning_for_signboard}
              </p>
            </article>
          ))
        )}
      </div>
    </div>
  )
}
