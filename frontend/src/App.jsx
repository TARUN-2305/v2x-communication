import { useEffect, useState, useRef, useCallback } from 'react'
import {
  AlertTriangle, Bus, LoaderCircle, MapPinned, Radio,
  Play, Square, ToggleLeft, ToggleRight, Activity,
  Zap, Users, TrendingUp, Wifi, WifiOff, Database
} from 'lucide-react'
import MapLayer from './components/MapLayer.jsx'
import DynamicStops from './components/DynamicStops.jsx'
import V2XFeed from './components/V2XFeed.jsx'
import MetricsPanel from './components/MetricsPanel.jsx'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'
const WS_BASE  = import.meta.env.VITE_WS_BASE  || API_BASE.replace(/^http/, 'ws')

export default function App() {
  const [mapData,        setMapData]        = useState(null)
  const [liveState,      setLiveState]      = useState({ buses:[], stops:{}, traffic:[], debate_history:[], metrics:{}, mode:'agentic', tick:0 })
  const [connState,      setConnState]      = useState('Connecting')
  const [error,          setError]          = useState('')
  const [running,        setRunning]        = useState(false)
  const [numBuses,       setNumBuses]       = useState(6)
  const [metricsHistory, setMetricsHistory] = useState([])   // rolling 60-pt chart data
  const wsRef = useRef(null)

  // ── Load static map data ─────────────────────────────────────────────────
  useEffect(() => {
    let alive = true, retryT
    const load = async () => {
      try {
        const r = await fetch(`${API_BASE}/api/map`)
        if (!r.ok) throw new Error(`Map fetch failed ${r.status}`)
        const d = await r.json()
        if (alive) { setMapData(d); setError('') }
      } catch (e) {
        if (alive) { setError(e.message); retryT = setTimeout(load, 2000) }
      }
    }
    load()
    return () => { alive=false; clearTimeout(retryT) }
  }, [])

  // ── WebSocket live stream ────────────────────────────────────────────────
  const connectWS = useCallback(() => {
    const ws = new WebSocket(`${WS_BASE}/ws/live`)
    wsRef.current = ws

    ws.onopen  = () => { setConnState('Live'); setError('') }
    ws.onerror = () => setConnState('Interrupted')
    ws.onclose = () => {
      setConnState('Reconnecting')
      setTimeout(connectWS, 2000)
    }
    ws.onmessage = (ev) => {
      try {
        const payload = JSON.parse(ev.data)
        if (payload.type === 'heartbeat') return
        setLiveState(payload)
        setRunning(true)
        // Accumulate rolling metrics history (1 point per 5 ticks)
        if (payload.metrics && payload.tick % 5 === 0) {
          setMetricsHistory(prev => [...prev, {
            t:        payload.tick,
            headway:  Math.round(payload.metrics.avg_headway_s ?? 180),
            variance: Math.round(payload.metrics.variance ?? 0),
            bunching: payload.metrics.bunching ?? 0,
            decisions:payload.metrics.decisions ?? 0,
          }].slice(-60))
        }
      } catch {}
    }
  }, [])

  useEffect(() => { connectWS() }, [connectWS])

  // ── Control handlers ─────────────────────────────────────────────────────
  const startSim = async () => {
    const mode = liveState.mode || 'agentic'
    await fetch(`${API_BASE}/api/simulation/start?num_buses=${numBuses}&mode=${mode}`, { method:'POST' })
    setRunning(true)
  }
  const stopSim = async () => {
    await fetch(`${API_BASE}/api/simulation/stop`, { method:'POST' })
    setRunning(false)
  }
  const toggleMode = async () => {
    const r = await fetch(`${API_BASE}/api/simulation/mode`, { method:'POST' })
    const d = await r.json()
    setLiveState(prev => ({ ...prev, mode: d.mode }))
  }

  // ── Derived display data ─────────────────────────────────────────────────
  const stopEntries = mapData
    ? Object.entries(mapData.stops).map(([name, stop]) => ({
        name, ...stop,
        waiting: liveState.stops?.[name]?.waiting ?? 0,
      }))
    : []

  const activeTraffic = liveState.traffic?.length > 0
    ? liveState.traffic
    : [{ location: 'Corridor', severity: 'Normal flow' }]

  const m = liveState.metrics || {}
  const mode = liveState.mode || 'agentic'

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top,#143546_0%,#08131a_45%,#05080b_100%)] text-slate-100">

      {/* ── Top bar ──────────────────────────────────────────────────────── */}
      <header className="flex flex-wrap items-center justify-between gap-3 border-b border-white/10 bg-slate-950/80 px-5 py-3 backdrop-blur">
        <div>
          <p className="text-xs uppercase tracking-[.35em] text-cyan-300">ECO-SYNC V2X v2.0</p>
          <h1 className="text-xl font-bold text-white">BMTC Route 378 · Live V2X Corridor</h1>
          <p className="text-xs text-slate-400">Kengeri TTMC → Electronic City · {liveState.buses?.length ?? 0} Buses · {numBuses}-bus fleet</p>
        </div>

        {/* KPI strip */}
        <div className="flex flex-wrap items-center gap-3">
          {[
            { icon: <Activity  className="h-3.5 w-3.5"/>, label:'AVG HEADWAY',  val: `${m.avg_headway_s?.toFixed(0) ?? '—'}s`,   col:'text-cyan-300' },
            { icon: <Zap       className="h-3.5 w-3.5"/>, label:'DECISIONS',    val: m.decisions ?? 0,                           col:'text-yellow-300' },
            { icon: <AlertTriangle className="h-3.5 w-3.5"/>,label:'BUNCHING',  val: m.bunching ?? 0,                            col: (m.bunching??0)>0?'text-red-400':'text-emerald-400' },
            { icon: <Users     className="h-3.5 w-3.5"/>, label:'PAX SERVED',   val: m.passengers_served ?? 0,                   col:'text-violet-300' },
          ].map(k => (
            <div key={k.label} className="rounded-xl border border-white/10 bg-slate-900/70 px-3 py-2 text-center">
              <div className={`flex items-center gap-1 text-[10px] uppercase tracking-widest ${k.col}`}>{k.icon}{k.label}</div>
              <div className={`text-lg font-bold leading-tight ${k.col}`}>{k.val}</div>
            </div>
          ))}

          {/* Connection pill */}
          <div className="flex items-center gap-2 rounded-full border border-cyan-400/30 bg-cyan-400/10 px-3 py-1.5 text-xs">
            {connState==='Live' ? <Wifi className="h-3.5 w-3.5 text-emerald-400"/> : <WifiOff className="h-3.5 w-3.5 text-red-400"/>}
            <span>{connState}</span>
          </div>
        </div>
      </header>

      {/* ── Control bar ──────────────────────────────────────────────────── */}
      <div className="flex flex-wrap items-center gap-3 border-b border-white/10 bg-slate-950/60 px-5 py-2">
        {/* Bus count */}
        <div className="flex items-center gap-1.5 text-xs text-slate-400">
          <Bus className="h-3.5 w-3.5"/>
          <span>Fleet:</span>
          {[2,4,6,8].map(n => (
            <button key={n} onClick={() => setNumBuses(n)}
              className={`rounded px-2 py-0.5 text-xs border transition-colors ${numBuses===n ? 'bg-cyan-600 border-cyan-500 text-white' : 'border-white/10 text-slate-400 hover:border-cyan-600'}`}>
              {n}
            </button>
          ))}
        </div>

        <div className="h-5 w-px bg-white/10"/>

        {/* Start / Stop */}
        <button onClick={startSim} disabled={running}
          className="flex items-center gap-1.5 rounded-lg border border-emerald-600/50 bg-emerald-700/30 px-3 py-1.5 text-xs text-emerald-300 disabled:opacity-40 transition-opacity hover:bg-emerald-700/50">
          <Play className="h-3 w-3"/> Start
        </button>
        <button onClick={stopSim} disabled={!running}
          className="flex items-center gap-1.5 rounded-lg border border-red-600/50 bg-red-700/30 px-3 py-1.5 text-xs text-red-300 disabled:opacity-40 transition-opacity hover:bg-red-700/50">
          <Square className="h-3 w-3"/> Stop
        </button>

        <div className="h-5 w-px bg-white/10"/>

        {/* Agentic / Static toggle */}
        <button onClick={toggleMode}
          className={`flex items-center gap-2 rounded-lg border px-3 py-1.5 text-xs transition-colors ${
            mode==='agentic'
              ? 'border-cyan-500/50 bg-cyan-900/40 text-cyan-300'
              : 'border-slate-500/50 bg-slate-800/40 text-slate-400'
          }`}>
          {mode==='agentic' ? <ToggleRight className="h-4 w-4"/> : <ToggleLeft className="h-4 w-4"/>}
          {mode==='agentic' ? 'Agentic V2X' : 'Static Timetable'}
        </button>

        <div className="ml-auto flex items-center gap-2 text-[10px] text-slate-500">
          <Database className="h-3 w-3"/>
          <span>Tick {liveState.tick ?? 0} · Session {liveState.session_id?.slice(0,8) ?? '—'}</span>
        </div>
      </div>

      {/* ── Main grid ────────────────────────────────────────────────────── */}
      <div className="mx-auto grid min-h-[calc(100vh-120px)] max-w-[1800px] gap-4 p-4
                      lg:grid-cols-[minmax(0,1.6fr)_380px]">

        {/* LEFT: map + metrics */}
        <section className="flex flex-col gap-4">

          {/* Map card */}
          <div className="flex-1 overflow-hidden rounded-2xl border border-white/10 bg-white/5 shadow-2xl shadow-cyan-950/30 backdrop-blur">
            <div className="border-b border-white/10 px-4 py-2.5">
              <p className="flex items-center gap-2 text-xs uppercase tracking-[.25em] text-cyan-200">
                <MapPinned className="h-3.5 w-3.5"/> Live Route Map · OSRM Road Geometry
              </p>
            </div>
            {mapData
              ? <MapLayer routePolyline={mapData.route_polyline} buses={liveState.buses} stops={stopEntries}/>
              : <div className="flex h-[520px] items-center justify-center gap-2 text-slate-400 text-sm">
                  <LoaderCircle className="h-4 w-4 animate-spin"/> Loading route geometry…
                </div>
            }
          </div>

          {/* Metrics charts row */}
          <MetricsPanel history={metricsHistory} metrics={m} mode={mode}/>
        </section>

        {/* RIGHT: sidebar panels */}
        <aside className="flex flex-col gap-4">

          {/* Stop pressure */}
          <div className="rounded-2xl border border-white/10 bg-slate-950/70 p-4">
            <div className="mb-3 flex items-center gap-2 text-cyan-200">
              <MapPinned className="h-4 w-4"/>
              <h2 className="text-xs uppercase tracking-[.2em]">Stop Pressure</h2>
            </div>
            <div className="space-y-2">
              {stopEntries.map(s => <DynamicStops key={s.name} stop={s}/>)}
            </div>
          </div>

          {/* Traffic events */}
          <div className="rounded-2xl border border-white/10 bg-slate-950/70 p-4">
            <div className="mb-3 flex items-center gap-2 text-amber-200">
              <AlertTriangle className="h-4 w-4"/>
              <h2 className="text-xs uppercase tracking-[.2em]">TMC Traffic Events (V2I)</h2>
            </div>
            <div className="space-y-2">
              {activeTraffic.map((ev, i) => (
                <div key={i} className={`rounded-xl border px-3 py-2 text-xs ${
                  ev.severity==='High'   ? 'border-red-500/40 bg-red-500/10 text-red-100' :
                  ev.severity==='Medium' ? 'border-amber-500/40 bg-amber-500/10 text-amber-100' :
                                           'border-slate-500/30 bg-slate-800/30 text-slate-300'
                }`}>
                  <p className="font-semibold">{ev.location}</p>
                  <p className="text-white/60">{ev.severity} · {ev.desc || ev.severity}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Fleet snapshot */}
          <div className="rounded-2xl border border-white/10 bg-slate-950/70 p-4">
            <div className="mb-3 flex items-center gap-2 text-emerald-200">
              <Bus className="h-4 w-4"/>
              <h2 className="text-xs uppercase tracking-[.2em]">Fleet Snapshot</h2>
            </div>
            <div className="space-y-2">
              {liveState.buses?.map(bus => (
                <div key={bus.id} className="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold" style={{color: bus.color || '#00D4FF'}}>{bus.id}</span>
                    <span className={`rounded px-1.5 py-0.5 text-[10px] font-bold ${
                      bus.action==='HOLD'      ? 'bg-yellow-500/20 text-yellow-300' :
                      bus.action==='SKIP_STOP' ? 'bg-orange-500/20 text-orange-300' :
                                                 'bg-emerald-500/20 text-emerald-300'
                    }`}>{bus.action}</span>
                  </div>
                  <p className="text-slate-400">{bus.passengers} pax · idx {bus.path_index}</p>
                  <p className="text-slate-500">↕ {bus.headway_ahead_s}s ahead / {bus.headway_behind_s}s behind</p>
                </div>
              ))}
            </div>
          </div>

          {/* V2X Debate Feed */}
          <div className="flex-1">
            <V2XFeed feed={liveState.debate_history || []}/>
          </div>
        </aside>
      </div>

      {error && (
        <div className="fixed bottom-4 right-4 rounded-xl border border-rose-500/40 bg-rose-500/10 px-4 py-2 text-xs text-rose-200">
          {error}
        </div>
      )}
    </main>
  )
}
