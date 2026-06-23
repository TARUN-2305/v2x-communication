import React, { useState } from 'react';
import { useSimulation } from './hooks/useSimulation';
import { MapView } from './components/MapView';
import { EconomicsPanel } from './components/EconomicsPanel';
import { SummaryCard } from './components/SummaryCard';
import { Controls } from './components/Controls';
import { AgentFeed } from './components/AgentFeed';

const TABS = [
  { id: 'dashboard', label: '🗺️ Live Map', desc: 'Real-time bus positions on Bengaluru ORR' },
  { id: 'ai',        label: '🧠 AI Reasoning', desc: 'LLM-powered dispatch explanations' },
  { id: 'analytics', label: '📈 Economics', desc: 'Cost-benefit analysis charts' },
];

function StatusPill({ mode }) {
  const isAgentic = mode === 'agentic';
  return (
    <div className={`flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-bold border uppercase tracking-wider
      ${isAgentic
        ? 'bg-emerald-500/10 border-emerald-500/40 text-emerald-400'
        : 'bg-blue-500/10 border-blue-500/40 text-blue-400'}`}>
      <span className={`relative flex h-2 w-2`}>
        <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75
          ${isAgentic ? 'bg-emerald-400' : 'bg-blue-400'}`}></span>
        <span className={`relative inline-flex rounded-full h-2 w-2
          ${isAgentic ? 'bg-emerald-500' : 'bg-blue-500'}`}></span>
      </span>
      {isAgentic ? 'Agentic AI Active' : 'Static Timetable'}
    </div>
  );
}

function TabBar({ active, setActive }) {
  return (
    <div className="flex gap-1 bg-slate-900/80 border border-slate-700/60 rounded-xl p-1">
      {TABS.map(tab => (
        <button
          key={tab.id}
          onClick={() => setActive(tab.id)}
          className={`flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-semibold transition-all duration-200
            ${active === tab.id
              ? 'bg-gradient-to-r from-blue-600 to-emerald-600 text-white shadow-lg shadow-blue-900/40'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'}`}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}

function StatBadge({ label, value, accent }) {
  return (
    <div className={`flex flex-col px-4 py-2 rounded-xl border bg-slate-900/70 backdrop-blur ${accent}`}>
      <span className="text-xs text-slate-500 uppercase tracking-wider font-medium">{label}</span>
      <span className="text-base font-bold text-slate-100 mt-0.5">{value}</span>
    </div>
  );
}

const STOP_NAMES = [
  'Hebbal','Esteem Mall','Nagawara','Hennur','KR Puram',
  'Tin Factory','Marathahalli','Bellandur','Sarjapur Rd','HSR Layout',
  'Silk Board','BTM Layout','JP Nagar','Bannerghatta Rd','Gottigere',
  'Uttarahalli','Kengeri','Mysore Rd','Peenya','Jalahalli',
  'Yeshwanthpur','Tumkur Rd','Mathikere','HBR Layout','Banaswadi',
  'Horamavu','Ramamurthy Nagar','Varthur','Whitefield','Hebbal Loop'
];

function TelemetrySidebar({ buses, loads, busActions, logs }) {
  return (
    <div className="flex flex-col h-full bg-slate-900 border-l border-slate-800/60 overflow-hidden w-80 shrink-0">
      <div className="p-4 border-b border-slate-800 shrink-0 bg-slate-950/20">
        <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider flex items-center gap-2">
          📡 Live Telemetry
        </h3>
        <p className="text-xs text-slate-500 mt-1">Real-time stats per active vehicle</p>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {buses.length === 0 ? (
          <div className="h-full flex items-center justify-center text-center p-4">
            <div className="text-slate-500 text-xs">Waiting for live simulation stream...</div>
          </div>
        ) : (
          buses.map(bus => {
            const loadObj = loads.find(l => l.id === bus.id);
            const load = loadObj ? loadObj.load : 0;
            const action = busActions[bus.id] ?? 0;
            const stopName = STOP_NAMES[bus.stop % STOP_NAMES.length] ?? `Stop ${bus.stop}`;
            
            // Get latest action log details
            const latestLog = [...logs].reverse().find(l => l.bus_id === bus.id);
            const reward = latestLog ? latestLog.reward : null;
            const explanation = latestLog ? latestLog.explanation : "Waiting for first decision explanation...";
            
            const loadPercent = Math.min((load / 80) * 100, 100);
            const loadColor = load >= 60 ? 'bg-rose-500' : load >= 30 ? 'bg-amber-500' : 'bg-emerald-500';
            const actionLabel = action === 1 ? 'HOLD' : action === 2 ? 'SKIP' : 'PROCEED';
            const actionBadgeColor = action === 1 
              ? 'bg-blue-500/10 border-blue-500/30 text-blue-400' 
              : action === 2 
                ? 'bg-orange-500/10 border-orange-500/30 text-orange-400' 
                : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400';
            
            return (
              <div key={bus.id} className="bg-slate-950/40 border border-slate-800/80 rounded-xl p-3.5 space-y-3 shadow-md hover:border-slate-700/60 transition-all">
                {/* Header */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-6 h-6 rounded-lg bg-slate-800 flex items-center justify-center font-bold text-xs text-slate-300">
                      #{bus.id}
                    </div>
                    <span className="text-sm font-semibold text-slate-200">Vehicle {bus.id}</span>
                  </div>
                  <span className={`px-2 py-0.5 rounded-full text-[10px] font-extrabold uppercase border tracking-wider ${actionBadgeColor}`}>
                    {actionLabel}
                  </span>
                </div>

                {/* Location */}
                <div className="text-xs text-slate-400 flex justify-between items-center bg-slate-900/40 p-2 rounded-lg border border-slate-900">
                  <span>📍 {stopName}</span>
                  <span className="text-slate-500">Stop {bus.stop}</span>
                </div>

                {/* Onboard load progress */}
                <div className="space-y-1">
                  <div className="flex justify-between text-[11px] text-slate-400">
                    <span>👥 Onboard Load</span>
                    <span className="font-semibold">{load}/80 pax</span>
                  </div>
                  <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                    <div className={`h-full ${loadColor} transition-all duration-500`} style={{ width: `${loadPercent}%` }} />
                  </div>
                </div>

                {/* Economy impact & explanation */}
                <div className="border-t border-slate-800 pt-2 text-[11px] text-slate-400 space-y-1">
                  <div className="flex justify-between items-center text-[10px]">
                    <span className="text-slate-500">ECONOMY NET</span>
                    {reward !== null ? (
                      <span className={`font-bold ${reward >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                        {reward >= 0 ? '+' : ''}₹{reward.toFixed(1)}
                      </span>
                    ) : (
                      <span className="text-slate-600">—</span>
                    )}
                  </div>
                  <p className="italic text-slate-300 leading-snug line-clamp-2">{explanation}</p>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}

function App() {
  const { staticMetrics, simulationState, mode, setMode, resetSimulation } = useSimulation();
  const [activeTab, setActiveTab] = useState('dashboard');

  const step = simulationState?.step ?? 0;
  const logCount = simulationState?.logs?.length ?? 0;
  const buses = simulationState?.buses ?? [];

  return (
    <div className="h-screen bg-slate-950 text-slate-50 flex flex-col font-sans overflow-hidden">

      {/* ── HERO HEADER ── */}
      <header className="shrink-0 px-6 pt-5 pb-4 border-b border-slate-800/60 bg-slate-950/80 backdrop-blur">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">

          {/* Branding */}
          <div>
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-500 to-emerald-500 flex items-center justify-center text-xl shadow-lg">
                🚌
              </div>
              <div>
                <h1 className="text-2xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-cyan-300 to-emerald-400">
                  ECO-SYNC Transit AI
                </h1>
                <p className="text-xs text-slate-500 font-medium -mt-0.5">
                  Agentic Bus Dispatch · Bengaluru ORR · PPO + LLaMA-3
                </p>
              </div>
            </div>
          </div>

          {/* Live status + metrics strip */}
          <div className="flex flex-wrap items-center gap-2">
            <StatusPill mode={mode} />
            <StatBadge label="Sim Step" value={`#${step}`} accent="border-slate-700/60" />
            <StatBadge label="Buses" value={`${buses.length} active`} accent="border-slate-700/60" />
            <StatBadge label="AI Logs" value={logCount} accent="border-slate-700/60" />
            {staticMetrics?.summary && (
              <StatBadge
                label="Efficiency Gain"
                value={`+${staticMetrics.summary.efficiency_gain_percent.toFixed(1)}%`}
                accent="border-emerald-700/40 text-emerald-400"
              />
            )}
          </div>
        </div>

        {/* Tab Bar */}
        <div className="mt-4">
          <TabBar active={activeTab} setActive={setActiveTab} />
          <p className="text-xs text-slate-500 mt-1.5 ml-1">
            {TABS.find(t => t.id === activeTab)?.desc}
          </p>
        </div>
      </header>

      {/* ── MAIN CONTENT ── */}
      <main className="flex-1 min-h-0 overflow-hidden">

        {/* ─── TAB 1: LIVE MAP ─── */}
        {activeTab === 'dashboard' && (
          <div className="h-full flex gap-0 overflow-hidden">

            {/* Left Sidebar: Controls */}
            <aside className="w-56 shrink-0 bg-slate-900 border-r border-slate-800 overflow-y-auto">
              <div className="p-4">
                <Controls mode={mode} setMode={setMode} resetSimulation={resetSimulation} />
              </div>
            </aside>

            {/* Map (fills everything) */}
            <div className="flex-1 relative min-w-0">
              <MapView
                buses={simulationState.buses}
                loads={simulationState.loads}
                stopQueues={simulationState.stopQueues}
                busActions={simulationState.busActions}
              />

              {/* Floating info bar at bottom of map */}
              <div className="absolute bottom-0 left-0 right-0 z-[1000] pointer-events-none">
                <div className="m-3 p-3 rounded-xl bg-slate-900/90 border border-slate-700/60 backdrop-blur flex items-center justify-between gap-4">
                  <div className="text-xs text-slate-400 flex items-center gap-2">
                    <span className="text-slate-500">Route:</span>
                    <span className="text-slate-200 font-semibold">Bengaluru Outer Ring Road (ORR) — 30 Stops</span>
                  </div>
                  <div className="text-xs text-slate-500 flex items-center gap-3">
                    <span>🚏 30 stops mapped</span>
                    <span>🚌 {buses.length} buses live</span>
                    <span className="text-emerald-400 font-semibold">● Simulation running</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Right Sidebar: Telemetry */}
            <TelemetrySidebar
              buses={simulationState.buses}
              loads={simulationState.loads}
              busActions={simulationState.busActions}
              logs={simulationState.logs}
            />
          </div>
        )}

        {/* ─── TAB 2: AI REASONING ─── */}
        {activeTab === 'ai' && (
          <div className="h-full flex gap-0 overflow-hidden">
            <aside className="w-56 shrink-0 bg-slate-900 border-r border-slate-800 overflow-y-auto">
              <div className="p-4">
                <Controls mode={mode} setMode={setMode} resetSimulation={resetSimulation} />
              </div>
            </aside>
            <div className="flex-1 flex flex-col min-w-0 overflow-hidden p-6 gap-4">
              <div className="shrink-0">
                <h2 className="text-lg font-bold text-slate-100">🧠 Agent Decision Feed</h2>
                <p className="text-sm text-slate-500 mt-1">
                  Every second, the PPO agent dispatches a bus. Groq's LLaMA-3 model explains each
                  decision in plain English — this is what makes ECO-SYNC "agentic" rather than a
                  black-box controller.
                </p>
              </div>
              <div className="grid grid-cols-3 gap-3 shrink-0">
                <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-xl p-3 text-center">
                  <div className="text-2xl font-black text-emerald-400">PROCEED</div>
                  <div className="text-xs text-slate-400 mt-1">Bus moves to next stop — revenue-positive</div>
                </div>
                <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-3 text-center">
                  <div className="text-2xl font-black text-blue-400">HOLD</div>
                  <div className="text-xs text-slate-400 mt-1">Bus waits to prevent bunching with bus ahead</div>
                </div>
                <div className="bg-orange-500/10 border border-orange-500/30 rounded-xl p-3 text-center">
                  <div className="text-2xl font-black text-orange-400">SKIP</div>
                  <div className="text-xs text-slate-400 mt-1">Bus skips a stop to rebalance the route</div>
                </div>
              </div>
              <div className="flex-1 min-h-0">
                <AgentFeed logs={simulationState.logs} />
              </div>
            </div>
          </div>
        )}

        {/* ─── TAB 3: ECONOMICS ─── */}
        {activeTab === 'analytics' && (
          <div className="h-full flex gap-0 overflow-hidden">
            <aside className="w-56 shrink-0 bg-slate-900 border-r border-slate-800 overflow-y-auto">
              <div className="p-4">
                <Controls mode={mode} setMode={setMode} resetSimulation={resetSimulation} />
              </div>
            </aside>
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              <div>
                <h2 className="text-lg font-bold text-slate-100">📈 Economic Analytics</h2>
                <p className="text-sm text-slate-500 mt-1">
                  Every dispatch decision has a direct cost. Revenue from tickets offsets wait-time
                  costs (₹1.67/min) and fuel costs (₹0.83/min). The Agentic AI minimises net cost
                  by reducing bunching events.
                </p>
              </div>

              {/* CBA summary card - full width */}
              <SummaryCard metrics={staticMetrics} equityGini={simulationState.equityGini} />

              {/* Economics chart - full width, tall */}
              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
                <h3 className="text-sm font-semibold text-slate-300 mb-4 uppercase tracking-wider">
                  Live Economic Metrics (₹ per step)
                </h3>
                <div className="h-72">
                  <EconomicsPanel data={simulationState.history} staticMetrics={staticMetrics} />
                </div>
              </div>

              {/* Explainer cards */}
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
                  <div className="text-2xl mb-2">⏱️</div>
                  <div className="font-semibold text-slate-200">Wait Cost</div>
                  <div className="text-xs text-slate-500 mt-1">₹1.67 per passenger-minute. Bunched buses leave long gaps → high wait cost.</div>
                </div>
                <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
                  <div className="text-2xl mb-2">⛽</div>
                  <div className="font-semibold text-slate-200">Fuel Cost</div>
                  <div className="text-xs text-slate-500 mt-1">₹0.83 per bus-minute. HOLD decisions reduce fuel burn by stopping idle cruising.</div>
                </div>
                <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
                  <div className="text-2xl mb-2">🎟️</div>
                  <div className="font-semibold text-slate-200">Revenue</div>
                  <div className="text-xs text-slate-500 mt-1">₹15 per passenger boarding. Agentic dispatch reduces overcrowding → more boardings.</div>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
