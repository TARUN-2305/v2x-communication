import {
  AreaChart, Area, LineChart, Line, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine
} from 'recharts'

const CT = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div className="rounded-lg border border-white/10 bg-slate-900 px-2 py-1.5 text-xs text-slate-200 shadow-xl">
      <p className="text-slate-400 mb-1">tick {label}</p>
      {payload.map((p, i) => (
        <p key={i} style={{color: p.color}}>{p.name}: {p.value}</p>
      ))}
    </div>
  )
}

export default function MetricsPanel({ history, metrics, mode }) {
  const modeColor = mode === 'agentic' ? '#22d3ee' : '#94a3b8'
  return (
    <div className="grid grid-cols-3 gap-3">

      {/* Headway chart */}
      <div className="rounded-2xl border border-white/10 bg-slate-950/70 p-3">
        <p className="mb-2 text-[10px] uppercase tracking-widest text-cyan-300/70">
          Avg Headway (s) · target 180s
        </p>
        <ResponsiveContainer width="100%" height={110}>
          <AreaChart data={history} margin={{top:4,right:4,left:-20,bottom:0}}>
            <CartesianGrid strokeDasharray="2 4" stroke="#1e293b"/>
            <XAxis dataKey="t" tick={{fontSize:8, fill:'#475569'}} interval="preserveStartEnd"/>
            <YAxis tick={{fontSize:8, fill:'#475569'}} domain={[0,360]}/>
            <Tooltip content={<CT/>}/>
            <ReferenceLine y={180} stroke="#fbbf24" strokeDasharray="3 3" strokeWidth={1}/>
            <Area type="monotone" dataKey="headway" name="headway"
              stroke={modeColor} fill={`${modeColor}22`} strokeWidth={1.5} dot={false}/>
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Bunching events */}
      <div className="rounded-2xl border border-white/10 bg-slate-950/70 p-3">
        <p className="mb-2 text-[10px] uppercase tracking-widest text-red-400/70">
          Bunching Events (cumulative)
        </p>
        <ResponsiveContainer width="100%" height={110}>
          <AreaChart data={history} margin={{top:4,right:4,left:-20,bottom:0}}>
            <CartesianGrid strokeDasharray="2 4" stroke="#1e293b"/>
            <XAxis dataKey="t" tick={{fontSize:8, fill:'#475569'}} interval="preserveStartEnd"/>
            <YAxis tick={{fontSize:8, fill:'#475569'}}/>
            <Tooltip content={<CT/>}/>
            <Area type="monotone" dataKey="bunching" name="bunching"
              stroke="#f87171" fill="#f8717122" strokeWidth={1.5} dot={false}/>
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Decisions */}
      <div className="rounded-2xl border border-white/10 bg-slate-950/70 p-3">
        <p className="mb-2 text-[10px] uppercase tracking-widest text-violet-300/70">
          V2X Decisions (cumulative)
        </p>
        <ResponsiveContainer width="100%" height={110}>
          <LineChart data={history} margin={{top:4,right:4,left:-20,bottom:0}}>
            <CartesianGrid strokeDasharray="2 4" stroke="#1e293b"/>
            <XAxis dataKey="t" tick={{fontSize:8, fill:'#475569'}} interval="preserveStartEnd"/>
            <YAxis tick={{fontSize:8, fill:'#475569'}}/>
            <Tooltip content={<CT/>}/>
            <Line type="monotone" dataKey="decisions" name="decisions"
              stroke="#a78bfa" strokeWidth={1.5} dot={false}/>
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
