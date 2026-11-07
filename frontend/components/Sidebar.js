"use client";

import { useState, useEffect } from "react";
import { ENDPOINTS } from "@/lib/api-config";

export default function Sidebar({
  onNewAnalysis,
  healthData,
  messageCount = 0,
  viewMode = "dashboard",
  setViewMode,
  isOpen = false,
  onClose,
}) {
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

  const navItems = [
    {
      id: "dashboard",
      label: "Workspace",
      icon: "dashboard",
      onClick: () => {
        setViewMode && setViewMode("dashboard");
        onClose && onClose();
      },
    },
    {
      id: "funds",
      label: "Top Funds",
      icon: "trending_up",
      onClick: () => {
        setViewMode && setViewMode("dashboard");
        onClose && onClose();
      },
    },
    {
      id: "comparison",
      label: "Compare Funds",
      icon: "compare_arrows",
      badge: "Live",
      onClick: () => {
        setViewMode && setViewMode("comparison");
        onClose && onClose();
      },
    },
  ];

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          onClick={onClose}
          className="fixed inset-0 z-40 bg-black/30 backdrop-blur-sm md:hidden transition-opacity"
        />
      )}

      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 w-[260px] bg-surface-container-lowest border-r border-outline-variant/15 flex flex-col py-5 px-4 transition-transform duration-300 ease-out md:translate-x-0 ${
          isOpen ? "translate-x-0 shadow-2xl" : "-translate-x-full"
        }`}
      >
        {/* Header: Logo & Product Title */}
        <div className="flex items-center justify-between px-2 mb-6">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-primary to-primary-container flex items-center justify-center text-white shadow-sm shadow-primary/20">
              <span
                className="material-symbols-outlined text-[20px]"
                style={{ fontVariationSettings: "'FILL' 1" }}
              >
                bolt
              </span>
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-headline font-bold text-base text-on-surface tracking-tight leading-none">
                  Groww Assist
                </span>
                <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-primary/10 text-primary uppercase tracking-wider">
                  AI
                </span>
              </div>
              <p className="text-[11px] text-on-surface-variant font-medium mt-0.5">
                Financial Analyst
              </p>
            </div>
          </div>

          {/* Close button for mobile */}
          <button
            onClick={onClose}
            className="md:hidden p-1.5 rounded-full text-on-surface-variant hover:bg-surface-container-high"
          >
            <span className="material-symbols-outlined text-lg">close</span>
          </button>
        </div>

        {/* Primary Action Button: Google FAB style */}
        <button
          onClick={() => {
            onNewAnalysis && onNewAnalysis();
            onClose && onClose();
          }}
          className="group w-full bg-gradient-to-r from-primary to-primary-container text-white font-headline font-semibold py-3 px-4 rounded-full flex items-center justify-center gap-2 mb-6 shadow-md shadow-primary/20 hover:shadow-lg hover:shadow-primary/30 hover:scale-[1.01] active:scale-[0.98] transition-all text-xs"
        >
          <span className="material-symbols-outlined text-[18px] transition-transform group-hover:rotate-90">
            add
          </span>
          <span>New Analysis</span>
        </button>

        {/* Navigation Items (M3 Style Pills) */}
        <nav className="flex-1 space-y-1">
          {navItems.map((item) => {
            const isActive = viewMode === item.id;
            return (
              <button
                key={item.id}
                onClick={item.onClick}
                className={`w-full flex items-center justify-between px-4 py-2.5 rounded-full text-xs font-semibold transition-all text-left ${
                  isActive
                    ? "bg-primary/10 text-primary font-bold shadow-xs"
                    : "text-on-surface-variant hover:bg-surface-container-low hover:text-on-surface"
                }`}
              >
                <div className="flex items-center gap-3">
                  <span
                    className={`material-symbols-outlined text-[18px] ${
                      isActive ? "text-primary" : "text-on-surface-variant/80"
                    }`}
                    style={isActive ? { fontVariationSettings: "'FILL' 1" } : {}}
                  >
                    {item.icon}
                  </span>
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span className="px-2 py-0.5 rounded-full text-[9px] font-bold bg-primary/15 text-primary uppercase tracking-wider">
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}

          <div className="flex items-center justify-between px-4 py-2.5 rounded-full text-xs font-medium text-on-surface-variant">
            <div className="flex items-center gap-3">
              <span className="material-symbols-outlined text-[18px] text-on-surface-variant/80">
                forum
              </span>
              <span>AI Chat History</span>
            </div>
            {messageCount > 0 && (
              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-surface-container-high text-on-surface">
                {messageCount}
              </span>
            )}
          </div>
        </nav>

        {/* Google Cloud-style System Status Card */}
        <div className="mt-auto space-y-3 pt-4 border-t border-outline-variant/15">
          <div className="bg-surface-container-low/70 rounded-2xl p-3.5 border border-outline-variant/10 text-xs">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] font-bold uppercase tracking-wider text-on-surface-variant/70">
                System Health
              </span>
              <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-primary/10">
                <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
                <span className="text-[10px] font-bold text-primary">
                  {healthData?.status === "healthy" ? "Operational" : "Connected"}
                </span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2 text-[11px] pt-1">
              <div>
                <span className="text-on-surface-variant/70 block text-[9px] uppercase font-semibold">
                  Chunks
                </span>
                <span className="font-mono font-bold text-on-surface">
                  {healthData?.indexed_chunks || "197"}
                </span>
              </div>
              <div>
                <span className="text-on-surface-variant/70 block text-[9px] uppercase font-semibold">
                  Engine
                </span>
                <span className="font-mono font-bold text-primary truncate block" title={healthData?.chroma_collection || "groww_mf_chunks_v5"}>
                  RAG v5
                </span>
              </div>
            </div>

            {metrics && (
              <div className="mt-2.5 pt-2 border-t border-outline-variant/10 grid grid-cols-2 gap-2 text-[11px]">
                <div>
                  <span className="text-on-surface-variant/70 block text-[9px] uppercase font-semibold">
                    Accuracy
                  </span>
                  <span className="font-bold text-primary">
                    {(metrics.factual_answer_rate * 100).toFixed(0)}%
                  </span>
                </div>
                <div>
                  <span className="text-on-surface-variant/70 block text-[9px] uppercase font-semibold">
                    Latency
                  </span>
                  <span className="font-bold text-on-surface">
                    {(metrics.avg_latency_ms / 1000).toFixed(1)}s
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* Quick links */}
          <div className="flex items-center justify-between px-2 text-[11px] text-on-surface-variant/60 font-medium">
            <span>Groww Direct Data</span>
            <span className="text-[10px]">Nov 2026</span>
          </div>
        </div>
      </aside>
    </>
  );
}
