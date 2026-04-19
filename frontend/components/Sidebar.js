"use client";

import { useState, useEffect } from "react";
import { ENDPOINTS } from "@/lib/api-config";

export default function Sidebar({ onNewAnalysis, healthData, messageCount }) {
  const [metrics, setMetrics] = useState(null);

  useEffect(() => {
    async function fetchMetrics() {
      try {
        const res = await fetch(ENDPOINTS.METRICS);
        if (res.ok) {
          const data = await res.json();
          setMetrics(data);
        }
      } catch (err) {
        // Silently fail
      }
    }
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <aside className="flex flex-col h-screen py-8 px-4 fixed left-0 top-0 bg-surface-container-lowest border-r border-on-surface/[0.08] z-50 w-64 md:w-[280px] hidden md:flex">
      <div className="flex items-center gap-3 px-2 mb-8">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-primary-container flex items-center justify-center text-on-primary shadow-sm">
          <span className="material-symbols-outlined" style={{fontVariationSettings: "'FILL' 1"}}>bolt</span>
        </div>
        <div>
          <h1 className="font-headline font-bold text-lg text-on-surface leading-tight tracking-tight">Groww Assist</h1>
          <p className="text-xs text-on-surface-variant font-medium opacity-70">Premium Assistant</p>
        </div>
      </div>

      <button onClick={onNewAnalysis} className="bg-gradient-to-br from-primary to-primary-container text-on-primary font-headline font-bold py-4 px-6 rounded-lg flex items-center justify-center gap-2 mb-8 transition-transform hover:scale-[0.98] active:scale-95 shadow-[0px_12px_32px_rgba(24,27,38,0.06)]">
        <span className="material-symbols-outlined">add</span>
        <span>New Analysis</span>
      </button>

      <nav className="flex-1 space-y-1">
        <a className="flex items-center gap-3 px-4 py-3 bg-secondary-container/30 text-on-secondary-container rounded-xl font-headline font-semibold transition-all relative overflow-hidden" href="#">
          <div className="absolute left-0 top-0 bottom-0 w-1 bg-secondary"></div>
          <span className="material-symbols-outlined" style={{fontVariationSettings: "'FILL' 1"}}>dashboard</span>
          <span>Workspace</span>
        </a>
        <a className="flex items-center gap-3 px-4 py-3 text-on-surface-variant hover:bg-surface-container-low rounded-xl font-headline font-semibold transition-all group" href="#">
          <span className="material-symbols-outlined group-hover:text-primary">trending_up</span>
          <span>Funds</span>
        </a>
        <a className="flex items-center gap-3 px-4 py-3 text-on-surface-variant hover:bg-surface-container-low rounded-xl font-headline font-semibold transition-all group" href="#">
          <span className="material-symbols-outlined group-hover:text-primary">compare_arrows</span>
          <span>Comparisons</span>
        </a>
        <a className="flex items-center gap-3 px-4 py-3 text-on-surface-variant hover:bg-surface-container-low rounded-xl font-headline font-semibold transition-all group justify-between" href="#">
          <div className="flex gap-3">
            <span className="material-symbols-outlined group-hover:text-primary">forum</span>
            <span>AI History</span>
          </div>
          {messageCount > 0 && <span className="bg-primary/10 text-primary text-[10px] font-black px-2 py-0.5 rounded-md">{messageCount}</span>}
        </a>
      </nav>

      <div className="mt-auto space-y-4 pt-6">
        <div className="bg-surface-container-low rounded-xl p-4 border border-on-surface/[0.04]">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold uppercase tracking-wider text-on-surface-variant opacity-60">System Status</span>
            <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-primary-container/20">
              <div className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse"></div>
              <span className="text-[10px] font-bold text-on-primary-container">{healthData ? "Operational" : "Connecting"}</span>
            </div>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span className="text-on-surface-variant">Chunks Processed</span>
              <span className="font-mono font-bold text-on-surface">{healthData?.indexed_chunks || "-"}</span>
            </div>
            <div className="flex justify-between text-xs">
              <span class="text-on-surface-variant">Version</span>
              <span className="font-mono font-bold text-on-surface">{healthData?.version || "-"}</span>
            </div>
          </div>
        </div>

        {metrics && (
          <div className="bg-surface-container-low rounded-xl p-4 border border-on-surface/[0.04]">
            <span className="text-xs font-bold uppercase tracking-wider text-on-surface-variant opacity-60 block mb-3">Performance</span>
            <div className="grid grid-cols-2 gap-3">
              <div className="flex flex-col">
                <span className="text-[10px] text-on-surface-variant">Accuracy</span>
                <span className="text-sm font-bold text-primary">{(metrics.factual_answer_rate * 100).toFixed(0)}%</span>
              </div>
              <div className="flex flex-col">
                <span className="text-[10px] text-on-surface-variant">Citations</span>
                <span className="text-sm font-bold text-primary">{(metrics.citation_coverage * 100).toFixed(0)}%</span>
              </div>
              <div className="flex flex-col">
                <span className="text-[10px] text-on-surface-variant">Latency</span>
                <span className="text-sm font-bold text-on-surface">{(metrics.avg_latency_ms / 1000).toFixed(1)}s</span>
              </div>
              <div className="flex flex-col">
                <span className="text-[10px] text-on-surface-variant">Queries</span>
                <span className="text-sm font-bold text-on-surface">{metrics.total_queries}</span>
              </div>
            </div>
          </div>
        )}

        <div className="flex flex-col gap-1 border-t border-on-surface/[0.04] pt-4">
          <a className="flex items-center gap-3 px-4 py-2 text-on-surface-variant hover:text-primary text-sm font-medium transition-colors" href="#">
            <span className="material-symbols-outlined text-[20px]">help_outline</span>
            <span>Help</span>
          </a>
          <a className="flex items-center gap-3 px-4 py-2 text-on-surface-variant hover:text-primary text-sm font-medium transition-colors" href="#">
            <span className="material-symbols-outlined text-[20px]">settings</span>
            <span>Settings</span>
          </a>
        </div>
      </div>
    </aside>
  );
}
