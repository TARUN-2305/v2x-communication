import React from 'react';
import { Activity, TrendingUp, Scale, Clock, ShieldAlert, Award } from 'lucide-react';

export function SummaryCard({ metrics, equityGini }) {
  if (!metrics?.summary?.static || !metrics?.summary?.agentic) {
    return (
      <div className="bg-slate-900/80 rounded-2xl p-6 border border-slate-800 h-full flex items-center justify-center text-center backdrop-blur-md">
        <div>
          <div className="text-4xl mb-3">📊</div>
          <div className="text-slate-300 text-sm font-semibold">CBA data not available.</div>
          <div className="text-slate-500 text-xs mt-1.5">Run <code className="bg-slate-950 px-2 py-0.5 rounded border border-slate-800">analyze_economics.py</code> first.</div>
        </div>
      </div>
    );
  }

  const { static: s, agentic: a, efficiency_gain_percent, total_savings_rupees } = metrics.summary;
  const gainIsPositive = efficiency_gain_percent >= 0;

  // Calculate percentage improvements
  const waitCostDiff = s.wait_cost - a.wait_cost;
  const waitPct = (waitCostDiff / s.wait_cost) * 100;
  
  const fuelCostDiff = s.fuel_cost - a.fuel_cost;
  const fuelPct = (fuelCostDiff / s.fuel_cost) * 100;
  
  const revDiff = a.revenue - s.revenue;
  const revPct = (revDiff / s.revenue) * 100;

  return (
    <div className="bg-gradient-to-br from-slate-900 to-slate-950 rounded-2xl p-6 border border-slate-800/80 h-full flex flex-col justify-between shadow-xl space-y-6">
      
      {/* Header */}
      <div className="flex items-center justify-between shrink-0">
        <h3 className="text-sm font-black text-slate-100 flex items-center gap-2 uppercase tracking-widest">
          <Activity className="text-blue-500 w-4 h-4 animate-pulse" /> Economic Dispatch Performance
        </h3>
        <span className="bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-wider">
          Live Audit
        </span>
      </div>

      {/* Main Stats Grid */}
      <div className="grid grid-cols-3 gap-4">
        
        {/* Efficiency Gain */}
        <div className="bg-slate-950/80 p-4 rounded-xl border border-slate-800/60 relative overflow-hidden group">
          <div className="absolute top-0 left-0 h-1 bg-gradient-to-r from-blue-500 to-emerald-500 w-full" />
          <div className="text-xs text-slate-500 font-bold uppercase tracking-wider mb-1 flex items-center gap-1.5">
            <TrendingUp className="w-3.5 h-3.5 text-emerald-400" /> Net Efficiency
          </div>
          <div className={`text-2xl font-black ${gainIsPositive ? 'text-emerald-400' : 'text-rose-400'}`}>
            {gainIsPositive ? '+' : ''}{efficiency_gain_percent.toFixed(1)}%
          </div>
          <p className="text-[10px] text-slate-500 mt-1">Overall economic utility gain</p>
        </div>

        {/* Total Savings */}
        <div className="bg-slate-950/80 p-4 rounded-xl border border-slate-800/60 relative overflow-hidden">
          <div className="absolute top-0 left-0 h-1 bg-gradient-to-r from-emerald-500 to-purple-500 w-full" />
          <div className="text-xs text-slate-500 font-bold uppercase tracking-wider mb-1 flex items-center gap-1.5">
            <Award className="w-3.5 h-3.5 text-purple-400" /> Operational Savings
          </div>
          <div className="text-2xl font-black text-slate-100">
            ₹{total_savings_rupees?.toFixed(0) ?? '—'}
          </div>
          <p className="text-[10px] text-slate-500 mt-1">Reduced wait + fuel cost</p>
        </div>

        {/* Stop Queue Gini */}
        <div className="bg-slate-950/80 p-4 rounded-xl border border-slate-800/60 relative overflow-hidden">
          <div className="absolute top-0 left-0 h-1 bg-gradient-to-r from-purple-500 to-blue-500 w-full" />
          <div className="text-xs text-slate-500 font-bold uppercase tracking-wider mb-1 flex items-center gap-1.5">
            <Scale className="w-3.5 h-3.5 text-blue-400" /> Equity (Gini)
          </div>
          <div className={`text-2xl font-black ${(equityGini ?? 0) < 0.35 ? 'text-emerald-400' : (equityGini ?? 0) < 0.6 ? 'text-amber-400' : 'text-rose-400'}`}>
            {(equityGini ?? 0).toFixed(2)}
          </div>
          <p className="text-[10px] text-slate-500 mt-1">0 = Perfect Equity, 1 = Inequality</p>
        </div>

      </div>

      {/* Comparative Breakdown Bar Charts */}
      <div className="space-y-4 border-t border-slate-850 pt-4 flex-1">
        <div className="text-xs text-slate-400 font-bold uppercase tracking-wider">CBA Category Impact</div>
        
        {/* Wait Cost Impact */}
        <div className="space-y-1.5">
          <div className="flex justify-between items-center text-xs">
            <span className="text-slate-400 flex items-center gap-1.5"><Clock className="w-3.5 h-3.5 text-rose-400" /> Passenger Wait Cost</span>
            <span className="font-bold text-emerald-400">
              {waitCostDiff >= 0 ? `Saved ₹${waitCostDiff.toFixed(0)} (${waitPct.toFixed(0)}%)` : `Increased ₹${Math.abs(waitCostDiff).toFixed(0)}`}
            </span>
          </div>
          <div className="flex items-center gap-2 bg-slate-950/40 p-2.5 rounded-lg border border-slate-900 text-[11px]">
            <div className="w-1/2 flex justify-between pr-2 border-r border-slate-800">
              <span className="text-slate-500">Static:</span>
              <span className="text-slate-300">₹{s.wait_cost.toFixed(0)}</span>
            </div>
            <div className="w-1/2 flex justify-between pl-2">
              <span className="text-slate-500">Agentic:</span>
              <span className="text-emerald-400 font-semibold">₹{a.wait_cost.toFixed(0)}</span>
            </div>
          </div>
        </div>

        {/* Fuel Cost Impact */}
        <div className="space-y-1.5">
          <div className="flex justify-between items-center text-xs">
            <span className="text-slate-400 flex items-center gap-1.5"><ShieldAlert className="w-3.5 h-3.5 text-blue-400" /> Fleet Fuel Cost</span>
            <span className="font-bold text-emerald-400">
              {fuelCostDiff >= 0 ? `Saved ₹${fuelCostDiff.toFixed(0)} (${fuelPct.toFixed(0)}%)` : `Increased ₹${Math.abs(fuelCostDiff).toFixed(0)}`}
            </span>
          </div>
          <div className="flex items-center gap-2 bg-slate-950/40 p-2.5 rounded-lg border border-slate-900 text-[11px]">
            <div className="w-1/2 flex justify-between pr-2 border-r border-slate-800">
              <span className="text-slate-500">Static:</span>
              <span className="text-slate-300">₹{s.fuel_cost.toFixed(0)}</span>
            </div>
            <div className="w-1/2 flex justify-between pl-2">
              <span className="text-slate-500">Agentic:</span>
              <span className="text-emerald-400 font-semibold">₹{a.fuel_cost.toFixed(0)}</span>
            </div>
          </div>
        </div>

        {/* Ticket Revenue */}
        <div className="space-y-1.5">
          <div className="flex justify-between items-center text-xs">
            <span className="text-slate-400 flex items-center gap-1.5">🎟️ Ticket Revenue</span>
            <span className="font-bold text-emerald-400">
              {revDiff >= 0 ? `Increased ₹${revDiff.toFixed(0)} (+${revPct.toFixed(0)}%)` : `Reduced ₹${Math.abs(revDiff).toFixed(0)}`}
            </span>
          </div>
          <div className="flex items-center gap-2 bg-slate-950/40 p-2.5 rounded-lg border border-slate-900 text-[11px]">
            <div className="w-1/2 flex justify-between pr-2 border-r border-slate-800">
              <span className="text-slate-500">Static:</span>
              <span className="text-slate-300">₹{s.revenue.toFixed(0)}</span>
            </div>
            <div className="w-1/2 flex justify-between pl-2">
              <span className="text-slate-500">Agentic:</span>
              <span className="text-emerald-400 font-semibold">₹{a.revenue.toFixed(0)}</span>
            </div>
          </div>
        </div>

      </div>

    </div>
  );
}
