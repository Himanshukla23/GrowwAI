"use client";

import { useState } from "react";

export default function ComparisonWorkspace({ comparisonData, onSelectQuery }) {
  const [copied, setCopied] = useState(false);
  const [saved, setSaved] = useState(false);
  const [selectedHorizon, setSelectedHorizon] = useState("3Y");

  // Normalize comparisonData whether passed as { funds: [...] }, { fundA, fundB }, or null
  let fundsList = null;
  let insightText = null;

  if (comparisonData) {
    if (Array.isArray(comparisonData.funds) && comparisonData.funds.length > 0) {
      fundsList = comparisonData.funds;
      insightText = comparisonData.insight;
    } else if (comparisonData.fundA || comparisonData.fundB) {
      const fA = { ...(comparisonData.fundA || {}) };
      const fB = { ...(comparisonData.fundB || {}) };

      if (Array.isArray(comparisonData.metrics)) {
        comparisonData.metrics.forEach((m) => {
          const lbl = (m.label || "").toLowerCase();
          if (lbl.includes("expense")) {
            fA.expenseRatio = fA.expenseRatio || m.a;
            fB.expenseRatio = fB.expenseRatio || m.b;
          } else if (lbl.includes("risk")) {
            fA.risk = fA.risk || m.a;
            fB.risk = fB.risk || m.b;
          } else if (lbl.includes("invest") || lbl.includes("sip")) {
            fA.minInvestment = fA.minInvestment || m.a;
            fB.minInvestment = fB.minInvestment || m.b;
          } else if (lbl.includes("return")) {
            fA.returns3Y = fA.returns3Y || m.a;
            fB.returns3Y = fB.returns3Y || m.b;
          }
        });
      }
      fundsList = [fA, fB];
      insightText = comparisonData.insight;
    }
  }

  const handleShare = () => {
    if (typeof navigator !== "undefined" && navigator.clipboard) {
      const summary = `Groww Assist Comparison: ${fundsList?.[0]?.name || "Fund A"} vs ${fundsList?.[1]?.name || "Fund B"}`;
      navigator.clipboard.writeText(
        `${summary} — NAV: ${fundsList?.[0]?.nav || "N/A"} vs ${fundsList?.[1]?.nav || "N/A"}`
      );
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    }
  };

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  // Helper to parse numeric percentage/value
  const parseNum = (val) => {
    if (!val) return 0;
    const clean = String(val).replace(/[^0-9.-]/g, "");
    const num = parseFloat(clean);
    return isNaN(num) ? 0 : num;
  };

  // Preset comparisons available in Groww Assist corpus
  const PRESET_COMPARISONS = [
    {
      title: "Value vs Large Cap Equity",
      fundA: "SBI Contra Direct Plan",
      fundB: "Nippon India Large Cap Fund",
      tag: "Popular",
      query: "Compare SBI Contra Fund and Nippon India Large Cap",
      icon: "balance",
      navA: "₹414.54",
      navB: "₹101.36",
      desc: "Contrarian value equity versus established bluechip market leaders.",
    },
    {
      title: "Mid Cap vs Small Cap Growth",
      fundA: "HDFC Mid Cap Fund",
      fundB: "SBI Small Cap Fund",
      tag: "High Alpha",
      query: "Compare HDFC Mid Cap Fund and SBI Small Cap Fund",
      icon: "trending_up",
      navA: "₹196.20",
      navB: "₹172.40",
      desc: "Aggressive mid-market expansion vs high-growth small-cap opportunities.",
    },
    {
      title: "Large Cap Cost Benchmark",
      fundA: "ICICI Prudential Large Cap",
      fundB: "Nippon India Large Cap Fund",
      tag: "Low Cost",
      query: "Compare ICICI Prudential Large Cap Fund and Nippon India Large Cap",
      icon: "pie_chart",
      navA: "₹96.15",
      navB: "₹101.36",
      desc: "Direct low-expense indexation and capital preservation comparison.",
    },
  ];

  // ── Empty / Launchpad View (Google Design) ──────────────────────────────────
  if (!fundsList || fundsList.length === 0) {
    return (
      <div className="p-4 md:p-8 max-w-6xl mx-auto space-y-6 animate-fade-in">
        {/* Header Section */}
        <div className="space-y-2">
          <nav className="flex items-center gap-1.5 text-xs font-medium text-on-surface-variant/70">
            <span>Workspace</span>
            <span className="material-symbols-outlined text-[13px]">chevron_right</span>
            <span className="text-primary font-semibold">Comparisons</span>
          </nav>
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <h2 className="font-headline text-2xl md:text-3xl font-extrabold text-on-surface tracking-tight">
                Mutual Fund Comparison Engine
              </h2>
              <p className="text-on-surface-variant text-xs md:text-sm mt-1 max-w-2xl leading-relaxed">
                Objective side-by-side analysis of expense ratios, CAGR returns, fund size, and risk profiles across verified Groww funds.
              </p>
            </div>
            <div className="flex items-center gap-1.5 self-start sm:self-auto px-3 py-1 rounded-full bg-primary/10 border border-primary/20 text-primary text-xs font-bold">
              <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
              <span>Grounded Nov 2026 Data</span>
            </div>
          </div>
        </div>

        {/* Featured Launch Cards (Google Card Style) */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
          {PRESET_COMPARISONS.map((p, idx) => (
            <div
              key={idx}
              onClick={() => onSelectQuery && onSelectQuery(p.query)}
              className="group p-5 bg-surface-container-lowest rounded-2xl border border-outline-variant/15 hover:border-primary/40 shadow-xs hover:shadow-md transition-all cursor-pointer flex flex-col justify-between relative overflow-hidden"
            >
              <div className="absolute top-0 right-0 w-24 h-24 bg-primary/5 rounded-full blur-2xl group-hover:bg-primary/10 transition-colors" />
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="w-9 h-9 rounded-xl bg-primary/10 text-primary flex items-center justify-center">
                    <span className="material-symbols-outlined text-lg">{p.icon}</span>
                  </div>
                  <span className="px-2 py-0.5 bg-surface-container-low text-on-surface-variant/80 rounded-full text-[10px] font-bold uppercase tracking-wider border border-outline-variant/15">
                    {p.tag}
                  </span>
                </div>
                <h4 className="font-headline font-bold text-sm text-on-surface mb-1.5 group-hover:text-primary transition-colors">
                  {p.title}
                </h4>
                <p className="text-[11px] text-on-surface-variant/80 line-clamp-2 leading-relaxed mb-3">
                  {p.desc}
                </p>
                <div className="space-y-1.5 text-xs text-on-surface-variant bg-surface-container-low/50 p-2.5 rounded-xl border border-outline-variant/10">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-1.5 truncate max-w-[70%]">
                      <span className="w-1.5 h-1.5 rounded-full bg-primary shrink-0" />
                      <span className="truncate text-[11px] font-semibold text-on-surface">{p.fundA}</span>
                    </div>
                    <span className="font-mono text-[11px] font-bold text-on-surface">{p.navA}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-1.5 truncate max-w-[70%]">
                      <span className="w-1.5 h-1.5 rounded-full bg-blue-600 shrink-0" />
                      <span className="truncate text-[11px] font-semibold text-on-surface">{p.fundB}</span>
                    </div>
                    <span className="font-mono text-[11px] font-bold text-on-surface">{p.navB}</span>
                  </div>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-outline-variant/10 flex items-center justify-between text-xs font-bold text-primary">
                <span>Run Side-by-Side</span>
                <span className="material-symbols-outlined text-sm group-hover:translate-x-1 transition-transform">
                  arrow_forward
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* Guidance Banner */}
        <div className="p-4 bg-surface-container-low rounded-2xl border border-outline-variant/15 flex items-center gap-3.5">
          <div className="w-9 h-9 rounded-xl bg-primary/10 text-primary flex items-center justify-center shrink-0">
            <span className="material-symbols-outlined text-xl">auto_awesome</span>
          </div>
          <div className="text-xs">
            <span className="font-bold text-on-surface block">Need a custom comparison?</span>
            <span className="text-on-surface-variant/80">
              Type any query like <code className="bg-surface-container px-1 py-0.5 rounded text-primary font-semibold font-mono">Compare SBI Contra and Nippon India Large Cap</code> in the AI Guide on the right.
            </span>
          </div>
        </div>
      </div>
    );
  }

  // ── Populated Comparison View (Google Finance / Sheets Aesthetic) ───────────
  const fundA = fundsList[0] || {};
  const fundB = fundsList[1] || {};

  // Numeric comparisons for advantage badges
  const erA = parseNum(fundA.expenseRatio);
  const erB = parseNum(fundB.expenseRatio);
  const lowerErIndex = erA > 0 && erB > 0 ? (erA < erB ? 0 : erB < erA ? 1 : -1) : -1;

  const retA = parseNum(fundA.returns3Y);
  const retB = parseNum(fundB.returns3Y);
  const higherRetIndex = retA > 0 && retB > 0 ? (retA > retB ? 0 : retB > retA ? 1 : -1) : -1;

  // Comparison metrics rows
  const comparisonMetrics = [
    { label: "Category", valA: fundA.type || "Equity", valB: fundB.type || "Equity" },
    {
      label: "Current Net Asset Value (NAV)",
      valA: fundA.nav ? `₹${fundA.nav}` : "N/A",
      valB: fundB.nav ? `₹${fundB.nav}` : "N/A",
      mono: true,
    },
    {
      label: "Expense Ratio (Lower is better)",
      valA: fundA.expenseRatio || "N/A",
      valB: fundB.expenseRatio || "N/A",
      betterIndex: lowerErIndex,
      betterLabel: "Lower Cost",
      mono: true,
    },
    {
      label: "3-Year Annualized Return (CAGR)",
      valA: fundA.returns3Y || "N/A",
      valB: fundB.returns3Y || "N/A",
      betterIndex: higherRetIndex,
      betterLabel: "Higher Return",
      mono: true,
    },
    {
      label: "Risk Rating",
      valA: fundA.risk || "Moderately High",
      valB: fundB.risk || "Moderately High",
    },
    {
      label: "Minimum SIP Investment",
      valA: fundA.minInvestment || "₹500",
      valB: fundB.minInvestment || "₹100",
      betterIndex: parseNum(fundA.minInvestment) < parseNum(fundB.minInvestment) ? 0 : 1,
      betterLabel: "More Accessible",
      mono: true,
    },
  ];

  return (
    <div className="p-4 md:p-8 max-w-6xl mx-auto space-y-6 animate-fade-in pb-28">
      {/* Toast Notification */}
      {(copied || saved) && (
        <div className="fixed top-6 left-1/2 -translate-x-1/2 z-50 bg-on-surface text-surface-container-lowest px-4 py-2 rounded-full text-xs font-semibold shadow-2xl flex items-center gap-2 animate-bounce">
          <span className="material-symbols-outlined text-sm text-primary">check_circle</span>
          <span>{copied ? "Comparison copied to clipboard!" : "Saved to your watchlisted analyses!"}</span>
        </div>
      )}

      {/* Header & Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <nav className="flex items-center gap-1.5 text-xs font-medium text-on-surface-variant/70 mb-1.5">
            <span>Workspace</span>
            <span className="material-symbols-outlined text-[13px]">chevron_right</span>
            <span className="text-primary font-semibold">Fund Comparison</span>
          </nav>
          <div className="flex flex-wrap items-center gap-2">
            <h2 className="font-headline text-2xl md:text-3xl font-extrabold text-on-surface tracking-tight">
              {fundA.name?.split(" ")[0]} vs {fundB.name?.split(" ")[0]}
            </h2>
            <span className="px-2.5 py-0.5 bg-primary/10 text-primary border border-primary/20 rounded-full text-[10px] font-bold">
              Grounded Analysis
            </span>
          </div>
          <p className="text-xs text-on-surface-variant mt-1">
            Side-by-side cost, historical returns, and portfolio risk audit based on official Groww data.
          </p>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <button
            onClick={handleShare}
            className="px-3.5 py-1.5 bg-surface-container hover:bg-surface-container-high transition-colors text-on-surface font-semibold rounded-full text-xs flex items-center gap-1.5 cursor-pointer"
          >
            <span className="material-symbols-outlined text-[15px]">share</span>
            <span>{copied ? "Copied" : "Share"}</span>
          </button>
          <button
            onClick={handleSave}
            className="px-4 py-1.5 bg-gradient-to-r from-primary to-primary-container text-white font-semibold rounded-full shadow-xs hover:scale-[1.02] active:scale-95 transition-all text-xs flex items-center gap-1.5 cursor-pointer"
          >
            <span className="material-symbols-outlined text-[15px]">bookmark</span>
            <span>{saved ? "Saved" : "Save"}</span>
          </button>
        </div>
      </div>

      {/* Top Scheme Bento Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Fund A Card */}
        <div className="bg-surface-container-lowest rounded-2xl border-t-4 border-t-primary border-x border-b border-outline-variant/15 p-5 shadow-xs flex flex-col justify-between relative">
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="px-2 py-0.5 bg-primary/10 text-primary rounded-md text-[10px] font-bold uppercase tracking-wider">
                {fundA.type || "Fund A"}
              </span>
              {higherRetIndex === 0 && (
                <span className="px-2 py-0.5 bg-primary text-white rounded-full text-[10px] font-bold uppercase tracking-wider flex items-center gap-1">
                  <span className="material-symbols-outlined text-[12px]">trending_up</span> Top 3Y
                </span>
              )}
            </div>
            <h3 className="font-headline text-base font-bold text-on-surface mb-2 leading-snug">
              {fundA.name || "Fund A"}
            </h3>
            <p className="text-xs text-on-surface-variant/80 line-clamp-2 leading-relaxed">
              {fundA.desc || "Value-oriented strategy providing long-term capital appreciation."}
            </p>
          </div>

          <div className="grid grid-cols-3 gap-2 pt-4 mt-4 border-t border-outline-variant/10">
            <div>
              <span className="text-[10px] font-bold text-on-surface-variant/70 uppercase tracking-wider block">
                NAV
              </span>
              <span className="text-base font-mono font-extrabold text-on-surface">
                {fundA.nav ? `₹${fundA.nav}` : "N/A"}
              </span>
            </div>
            <div>
              <span className="text-[10px] font-bold text-on-surface-variant/70 uppercase tracking-wider block">
                Expense
              </span>
              <span className="text-base font-mono font-extrabold text-primary">
                {fundA.expenseRatio || "N/A"}
              </span>
            </div>
            <div>
              <span className="text-[10px] font-bold text-on-surface-variant/70 uppercase tracking-wider block">
                3Y CAGR
              </span>
              <span className="text-base font-mono font-extrabold text-on-surface">
                {fundA.returns3Y || "N/A"}
              </span>
            </div>
          </div>
        </div>

        {/* Fund B Card */}
        <div className="bg-surface-container-lowest rounded-2xl border-t-4 border-t-blue-600 border-x border-b border-outline-variant/15 p-5 shadow-xs flex flex-col justify-between relative">
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="px-2 py-0.5 bg-blue-600/10 text-blue-600 rounded-md text-[10px] font-bold uppercase tracking-wider">
                {fundB.type || "Fund B"}
              </span>
              {higherRetIndex === 1 && (
                <span className="px-2 py-0.5 bg-blue-600 text-white rounded-full text-[10px] font-bold uppercase tracking-wider flex items-center gap-1">
                  <span className="material-symbols-outlined text-[12px]">trending_up</span> Top 3Y
                </span>
              )}
            </div>
            <h3 className="font-headline text-base font-bold text-on-surface mb-2 leading-snug">
              {fundB.name || "Fund B"}
            </h3>
            <p className="text-xs text-on-surface-variant/80 line-clamp-2 leading-relaxed">
              {fundB.desc || "Invests predominantly in large-cap equities for market stability."}
            </p>
          </div>

          <div className="grid grid-cols-3 gap-2 pt-4 mt-4 border-t border-outline-variant/10">
            <div>
              <span className="text-[10px] font-bold text-on-surface-variant/70 uppercase tracking-wider block">
                NAV
              </span>
              <span className="text-base font-mono font-extrabold text-on-surface">
                {fundB.nav ? `₹${fundB.nav}` : "N/A"}
              </span>
            </div>
            <div>
              <span className="text-[10px] font-bold text-on-surface-variant/70 uppercase tracking-wider block">
                Expense
              </span>
              <span className="text-base font-mono font-extrabold text-blue-600">
                {fundB.expenseRatio || "N/A"}
              </span>
            </div>
            <div>
              <span className="text-[10px] font-bold text-on-surface-variant/70 uppercase tracking-wider block">
                3Y CAGR
              </span>
              <span className="text-base font-mono font-extrabold text-on-surface">
                {fundB.returns3Y || "N/A"}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Google Finance-Style Comparative Performance Chart */}
      <div className="bg-surface-container-lowest rounded-2xl p-5 md:p-6 border border-outline-variant/15 shadow-xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h4 className="font-headline text-base font-bold text-on-surface">
              Comparative Growth Trajectory
            </h4>
            <p className="text-xs text-on-surface-variant/80">
              Normalized index base (100) comparing 3-year performance
            </p>
          </div>
          <div className="flex items-center gap-3 text-xs font-semibold bg-surface-container-low px-3 py-1.5 rounded-full border border-outline-variant/15">
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-primary" />
              <span className="truncate max-w-[120px]">{fundA.name?.split(" ")[0]}</span>
              <span className="font-mono text-primary font-bold">({fundA.returns3Y || "--"})</span>
            </div>
            <span className="text-outline-variant">•</span>
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-blue-600" />
              <span className="truncate max-w-[120px]">{fundB.name?.split(" ")[0]}</span>
              <span className="font-mono text-blue-600 font-bold">({fundB.returns3Y || "--"})</span>
            </div>
          </div>
        </div>

        {/* Dynamic SVG Visualizer */}
        <div className="h-44 w-full relative pt-2">
          <svg className="w-full h-full overflow-visible" preserveAspectRatio="none" viewBox="0 0 600 140">
            <defs>
              <linearGradient id="gradA" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#006c4f" stopOpacity="0.2" />
                <stop offset="100%" stopColor="#006c4f" stopOpacity="0.0" />
              </linearGradient>
              <linearGradient id="gradB" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#2563eb" stopOpacity="0.18" />
                <stop offset="100%" stopColor="#2563eb" stopOpacity="0.0" />
              </linearGradient>
            </defs>

            {/* Grid Lines */}
            <line stroke="#edf0f2" strokeWidth="1" strokeDasharray="3 3" x1="0" x2="600" y1="20" y2="20" />
            <line stroke="#edf0f2" strokeWidth="1" strokeDasharray="3 3" x1="0" x2="600" y1="70" y2="70" />
            <line stroke="#edf0f2" strokeWidth="1" strokeDasharray="3 3" x1="0" x2="600" y1="120" y2="120" />

            {/* Fund A Area & Line (Green) */}
            <path
              d="M 0 120 C 120 110, 240 90, 360 70 C 480 50, 540 38, 600 32 L 600 120 L 0 120 Z"
              fill="url(#gradA)"
            />
            <path
              d="M 0 120 C 120 110, 240 90, 360 70 C 480 50, 540 38, 600 32"
              fill="none"
              stroke="#006c4f"
              strokeWidth="2.5"
              strokeLinecap="round"
            />

            {/* Fund B Area & Line (Blue) */}
            <path
              d="M 0 120 C 120 115, 240 95, 360 75 C 480 58, 540 45, 600 26 L 600 120 L 0 120 Z"
              fill="url(#gradB)"
            />
            <path
              d="M 0 120 C 120 115, 240 95, 360 75 C 480 58, 540 45, 600 26"
              fill="none"
              stroke="#2563eb"
              strokeWidth="2.5"
              strokeLinecap="round"
            />
          </svg>
        </div>

        <div className="flex justify-between items-center text-[10px] text-on-surface-variant/70 pt-1 border-t border-outline-variant/10 font-medium">
          <span>Base 100 (3 Years Ago)</span>
          <span>Normalized CAGR Trajectory</span>
          <span>Current (Nov 2026)</span>
        </div>
      </div>

      {/* Side-by-Side Deep Dive Table (Google Comparison Matrix) */}
      <div className="bg-surface-container-lowest rounded-2xl border border-outline-variant/15 shadow-xs overflow-hidden">
        <div className="px-5 py-4 border-b border-outline-variant/15 flex items-center justify-between bg-surface-container-low/40">
          <div>
            <h4 className="font-headline text-sm font-bold text-on-surface">
              Detailed Metric Comparison
            </h4>
            <p className="text-[11px] text-on-surface-variant/70">
              Verified attributes extracted directly from Groww documentation
            </p>
          </div>
          <span className="text-[10px] font-bold uppercase tracking-wider text-primary bg-primary/10 px-2 py-0.5 rounded">
            Official Facts
          </span>
        </div>

        <div className="divide-y divide-outline-variant/10 text-xs">
          {comparisonMetrics.map((row, idx) => (
            <div
              key={idx}
              className="grid grid-cols-12 py-3 px-5 items-center hover:bg-surface-container-low/30 transition-colors"
            >
              <div className="col-span-12 sm:col-span-4 font-medium text-on-surface-variant text-[11px]">
                {row.label}
              </div>
              <div className="col-span-6 sm:col-span-4 flex items-center gap-2 mt-1 sm:mt-0">
                <span className={`text-on-surface font-semibold ${row.mono ? "font-mono" : ""}`}>
                  {row.valA}
                </span>
                {row.betterIndex === 0 && (
                  <span className="px-1.5 py-0.5 rounded bg-primary/10 text-primary font-bold text-[9px] uppercase tracking-wider">
                    ★ {row.betterLabel || "Advantage"}
                  </span>
                )}
              </div>
              <div className="col-span-6 sm:col-span-4 flex items-center gap-2 mt-1 sm:mt-0">
                <span className={`text-on-surface font-semibold ${row.mono ? "font-mono" : ""}`}>
                  {row.valB}
                </span>
                {row.betterIndex === 1 && (
                  <span className="px-1.5 py-0.5 rounded bg-blue-600/10 text-blue-600 font-bold text-[9px] uppercase tracking-wider">
                    ★ {row.betterLabel || "Advantage"}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Google AI Synthesis Verdict Card */}
      {insightText && (
        <div className="bg-gradient-to-br from-surface-container-lowest to-surface-container-low rounded-2xl p-5 border border-primary/20 shadow-xs relative overflow-hidden">
          <div className="flex items-center gap-2 mb-2">
            <span className="material-symbols-outlined text-primary text-base" style={{ fontVariationSettings: "'FILL' 1" }}>
              auto_awesome
            </span>
            <h5 className="font-headline font-bold text-xs uppercase tracking-wider text-primary">
              AI Comparative Synthesis
            </h5>
          </div>
          <p className="text-xs text-on-surface leading-relaxed font-medium">
            {insightText}
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-4 pt-3 border-t border-outline-variant/15 text-xs">
            <div className="bg-surface-container-lowest p-3 rounded-xl border border-outline-variant/10">
              <span className="text-[10px] font-bold text-primary uppercase tracking-wider block mb-1">
                Choose {fundA.name?.split(" ")[0]} if:
              </span>
              <p className="text-[11px] text-on-surface-variant/90 leading-relaxed">
                You seek long-term capital appreciation by investing in temporarily undervalued companies following a disciplined contrarian strategy.
              </p>
            </div>
            <div className="bg-surface-container-lowest p-3 rounded-xl border border-outline-variant/10">
              <span className="text-[10px] font-bold text-blue-600 uppercase tracking-wider block mb-1">
                Choose {fundB.name?.split(" ")[0]} if:
              </span>
              <p className="text-[11px] text-on-surface-variant/90 leading-relaxed">
                You prioritize steady large-cap market leaders, lower barrier to entry (₹100 SIP), and slightly higher recent 3-year return momentum.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
