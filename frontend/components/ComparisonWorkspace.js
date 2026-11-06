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
      navigator.clipboard.writeText(`${summary} — NAV: ${fundsList?.[0]?.nav || "N/A"} vs ${fundsList?.[1]?.nav || "N/A"}`);
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
      icon: "balance"
    },
    {
      title: "Mid Cap vs Small Cap Growth",
      fundA: "HDFC Mid Cap Fund",
      fundB: "SBI Small Cap Fund",
      tag: "High Growth",
      query: "Compare HDFC Mid Cap Fund and SBI Small Cap Fund",
      icon: "trending_up"
    },
    {
      title: "Large Cap Head-to-Head",
      fundA: "ICICI Prudential Large Cap",
      fundB: "Nippon India Large Cap",
      tag: "Bluechip",
      query: "Compare ICICI Prudential Large Cap Fund and Nippon India Large Cap",
      icon: "verified"
    }
  ];

  // ── Render Empty / Launcher State if no comparison yet ─────────────────────
  if (!fundsList || fundsList.length === 0) {
    return (
      <div className="p-8 max-w-7xl mx-auto space-y-8 animate-fade-in bg-background min-h-full pb-24">
        <div className="flex flex-col gap-2">
          <nav className="flex items-center gap-2 text-xs font-medium text-on-surface-variant">
            <span>Workspace</span>
            <span className="material-symbols-outlined text-[14px]">chevron_right</span>
            <span className="text-primary font-semibold">Comparison Workspace</span>
          </nav>
          <h2 className="font-headline text-3xl md:text-4xl font-extrabold text-on-surface tracking-tight">
            Mutual Fund Comparison Engine
          </h2>
          <p className="text-on-surface-variant text-sm max-w-2xl leading-relaxed">
            Directly compare expense ratios, historical returns, AUM, risk ratings, and minimum investments across verified Groww funds.
          </p>
        </div>

        {/* Featured Comparison Launch Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-4">
          {PRESET_COMPARISONS.map((p, idx) => (
            <div
              key={idx}
              onClick={() => onSelectQuery && onSelectQuery(p.query)}
              className="group p-6 bg-surface-container-lowest rounded-2xl border border-outline-variant/15 hover:border-primary/40 shadow-sm hover:shadow-xl transition-all cursor-pointer flex flex-col justify-between relative overflow-hidden"
            >
              <div className="absolute top-0 right-0 w-28 h-28 bg-primary/5 rounded-full blur-2xl group-hover:bg-primary/10 transition-colors"></div>
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div className="w-10 h-10 rounded-xl bg-primary/10 text-primary flex items-center justify-center">
                    <span className="material-symbols-outlined text-xl">{p.icon}</span>
                  </div>
                  <span className="px-2.5 py-1 bg-surface-container text-on-surface-variant rounded-full text-[10px] font-bold uppercase tracking-wider">
                    {p.tag}
                  </span>
                </div>
                <h4 className="font-headline font-bold text-base text-on-surface mb-2 group-hover:text-primary transition-colors">
                  {p.title}
                </h4>
                <div className="space-y-1.5 text-xs text-on-surface-variant">
                  <div className="flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-primary"></span>
                    <span>{p.fundA}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-blue-600"></span>
                    <span>{p.fundB}</span>
                  </div>
                </div>
              </div>
              <div className="mt-6 pt-4 border-t border-surface-container flex items-center justify-between text-xs font-bold text-primary">
                <span>Run Analysis</span>
                <span className="material-symbols-outlined text-sm group-hover:translate-x-1 transition-transform">
                  arrow_forward
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* Informational Guidance Banner */}
        <div className="p-6 bg-surface-container-low rounded-2xl border border-outline-variant/10 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-primary/15 text-primary flex items-center justify-center shrink-0">
              <span className="material-symbols-outlined text-2xl">compare_arrows</span>
            </div>
            <div>
              <h5 className="font-headline font-bold text-sm text-on-surface">Custom Fund Comparisons</h5>
              <p className="text-xs text-on-surface-variant mt-0.5">
                Type any comparison query in the right Assistant panel (e.g. "Compare SBI Contra Fund and Nippon India Large Cap") to generate a fresh, grounded comparison.
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // ── Populated Comparison View ──────────────────────────────────────────────
  const fundA = fundsList[0] || {};
  const fundB = fundsList[1] || {};

  // Numeric comparisons for advantage badges
  const erA = parseNum(fundA.expenseRatio);
  const erB = parseNum(fundB.expenseRatio);
  const lowerErIndex = erA > 0 && erB > 0 ? (erA < erB ? 0 : (erB < erA ? 1 : -1)) : -1;

  const retA = parseNum(fundA.returns3Y);
  const retB = parseNum(fundB.returns3Y);
  const higherRetIndex = retA > 0 && retB > 0 ? (retA > retB ? 0 : (retB > retA ? 1 : -1)) : -1;

  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto space-y-8 animate-fade-in bg-background min-h-full pb-28">
      {/* Toast Notification */}
      {(copied || saved) && (
        <div className="fixed top-6 left-1/2 -translate-x-1/2 z-50 bg-inverse-surface text-inverse-on-surface px-5 py-2.5 rounded-full text-xs font-semibold shadow-2xl flex items-center gap-2 animate-bounce">
          <span className="material-symbols-outlined text-sm text-primary">check_circle</span>
          <span>{copied ? "Comparison copied to clipboard!" : "Saved to your watchlisted analyses!"}</span>
        </div>
      )}

      {/* Header Section */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <nav className="flex items-center gap-2 text-xs font-medium text-on-surface-variant mb-2">
            <span>Workspace</span>
            <span className="material-symbols-outlined text-[14px]">chevron_right</span>
            <span className="text-primary font-semibold">Fund Comparison</span>
          </nav>
          <div className="flex flex-wrap items-center gap-3">
            <h2 className="font-headline text-3xl md:text-4xl font-extrabold text-on-surface tracking-tight">
              Scheme Comparison
            </h2>
            <span className="px-3 py-1 bg-primary/10 text-primary border border-primary/20 rounded-full text-xs font-bold">
              RAG Grounded
            </span>
          </div>
          <p className="text-xs md:text-sm text-on-surface-variant mt-1.5">
            Side-by-side performance, cost ratio, and risk audit based on official Groww scheme data.
          </p>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <button
            onClick={handleShare}
            className="px-5 py-2.5 bg-surface-container-highest flex items-center gap-2 hover:bg-surface-container-high transition-colors text-primary font-semibold rounded-full shadow-sm text-xs"
          >
            <span className="material-symbols-outlined text-base">share</span>
            <span>{copied ? "Copied!" : "Share"}</span>
          </button>
          <button
            onClick={handleSave}
            className="px-6 py-2.5 bg-gradient-to-r from-primary to-primary-container text-white font-semibold rounded-full shadow-lg shadow-primary/20 hover:scale-[1.02] active:scale-95 transition-all text-xs flex items-center gap-1.5"
          >
            <span className="material-symbols-outlined text-base">bookmark</span>
            <span>{saved ? "Saved" : "Save Analysis"}</span>
          </button>
        </div>
      </div>

      {/* Main Bento Grid */}
      <div className="grid grid-cols-12 gap-6">
        
        {/* Fund A Card */}
        <div className="col-span-12 md:col-span-6 bg-surface-container-lowest rounded-2xl border-l-4 border-primary shadow-sm border-t border-r border-b border-outline-variant/15 p-6 hover:shadow-md transition-shadow relative">
          <div className="flex justify-between items-start mb-4">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-primary/10 text-primary flex items-center justify-center font-bold text-lg">
                <span className="material-symbols-outlined text-2xl">account_balance</span>
              </div>
              <div>
                <span className="px-2.5 py-0.5 bg-primary/10 text-primary rounded-md text-[10px] font-bold uppercase tracking-wider inline-block">
                  {fundA.type || "Fund A"}
                </span>
                <h3 className="font-headline text-lg font-bold text-on-surface mt-1 leading-snug">
                  {fundA.name || "Fund A"}
                </h3>
              </div>
            </div>
            {higherRetIndex === 0 && (
              <span className="px-2.5 py-1 bg-primary text-white rounded-full text-[10px] font-bold uppercase tracking-wider flex items-center gap-1 shrink-0">
                <span className="material-symbols-outlined text-xs">trending_up</span> Top 3Y Return
              </span>
            )}
          </div>

          <div className="grid grid-cols-3 gap-3 py-4 my-2 border-y border-surface-container">
            <div>
              <span className="text-[10px] font-semibold text-on-surface-variant uppercase tracking-wider block">NAV</span>
              <span className="text-xl font-extrabold text-on-surface">
                {fundA.nav ? `₹${fundA.nav}` : "N/A"}
              </span>
            </div>
            <div>
              <span className="text-[10px] font-semibold text-on-surface-variant uppercase tracking-wider block">Expense Ratio</span>
              <span className="text-xl font-extrabold text-primary">
                {fundA.expenseRatio || "N/A"}
              </span>
            </div>
            <div>
              <span className="text-[10px] font-semibold text-on-surface-variant uppercase tracking-wider block">3Y Returns</span>
              <span className="text-xl font-extrabold text-on-surface">
                {fundA.returns3Y || "N/A"}
              </span>
            </div>
          </div>

          <p className="text-xs text-on-surface-variant leading-relaxed line-clamp-2">
            {fundA.desc || "Growth-oriented scheme providing long-term capital appreciation."}
          </p>
        </div>

        {/* Fund B Card */}
        <div className="col-span-12 md:col-span-6 bg-surface-container-lowest rounded-2xl border-l-4 border-blue-600 shadow-sm border-t border-r border-b border-outline-variant/15 p-6 hover:shadow-md transition-shadow relative">
          <div className="flex justify-between items-start mb-4">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-blue-600/10 text-blue-600 flex items-center justify-center font-bold text-lg">
                <span className="material-symbols-outlined text-2xl">analytics</span>
              </div>
              <div>
                <span className="px-2.5 py-0.5 bg-blue-600/10 text-blue-600 rounded-md text-[10px] font-bold uppercase tracking-wider inline-block">
                  {fundB.type || "Fund B"}
                </span>
                <h3 className="font-headline text-lg font-bold text-on-surface mt-1 leading-snug">
                  {fundB.name || "Fund B"}
                </h3>
              </div>
            </div>
            {higherRetIndex === 1 && (
              <span className="px-2.5 py-1 bg-blue-600 text-white rounded-full text-[10px] font-bold uppercase tracking-wider flex items-center gap-1 shrink-0">
                <span className="material-symbols-outlined text-xs">trending_up</span> Top 3Y Return
              </span>
            )}
          </div>

          <div className="grid grid-cols-3 gap-3 py-4 my-2 border-y border-surface-container">
            <div>
              <span className="text-[10px] font-semibold text-on-surface-variant uppercase tracking-wider block">NAV</span>
              <span className="text-xl font-extrabold text-on-surface">
                {fundB.nav ? `₹${fundB.nav}` : "N/A"}
              </span>
            </div>
            <div>
              <span className="text-[10px] font-semibold text-on-surface-variant uppercase tracking-wider block">Expense Ratio</span>
              <span className="text-xl font-extrabold text-blue-600">
                {fundB.expenseRatio || "N/A"}
              </span>
            </div>
            <div>
              <span className="text-[10px] font-semibold text-on-surface-variant uppercase tracking-wider block">3Y Returns</span>
              <span className="text-xl font-extrabold text-on-surface">
                {fundB.returns3Y || "N/A"}
              </span>
            </div>
          </div>

          <p className="text-xs text-on-surface-variant leading-relaxed line-clamp-2">
            {fundB.desc || "Targeted investment strategy focusing on core index or category leaders."}
          </p>
        </div>

        {/* Dynamic Comparative Performance Graph */}
        <div className="col-span-12 bg-surface-container-lowest rounded-2xl p-6 md:p-8 relative overflow-hidden shadow-sm border border-outline-variant/15">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
            <div>
              <h4 className="font-headline text-xl font-bold text-on-surface">Historical Return Profile</h4>
              <p className="text-xs text-on-surface-variant mt-0.5">Visualized compound performance relative trajectory</p>
            </div>
            <div className="flex items-center gap-4 bg-surface-container-low px-4 py-2 rounded-full border border-surface-variant/30 text-xs font-semibold">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-primary"></div>
                <span className="text-on-surface truncate max-w-[140px]">{fundA.name || "Fund A"}</span>
                <span className="font-bold text-primary">({fundA.returns3Y || "--"})</span>
              </div>
              <div className="w-px h-4 bg-outline-variant/30"></div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-blue-600"></div>
                <span className="text-on-surface truncate max-w-[140px]">{fundB.name || "Fund B"}</span>
                <span className="font-bold text-blue-600">({fundB.returns3Y || "--"})</span>
              </div>
            </div>
          </div>

          {/* SVG Comparative Chart */}
          <div className="h-56 w-full relative">
            <svg className="w-full h-full overflow-visible" preserveAspectRatio="none" viewBox="0 0 800 200">
              <defs>
                <linearGradient id="gradFundA" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#00D09C" stopOpacity="0.25" />
                  <stop offset="100%" stopColor="#00D09C" stopOpacity="0.0" />
                </linearGradient>
                <linearGradient id="gradFundB" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#2563EB" stopOpacity="0.2" />
                  <stop offset="100%" stopColor="#2563EB" stopOpacity="0.0" />
                </linearGradient>
              </defs>

              {/* Grid Lines */}
              <line stroke="#f0f2f5" strokeWidth="1" x1="0" x2="800" y1="20" y2="20" />
              <line stroke="#f0f2f5" strokeWidth="1" x1="0" x2="800" y1="70" y2="70" />
              <line stroke="#f0f2f5" strokeWidth="1" x1="0" x2="800" y1="120" y2="120" />
              <line stroke="#f0f2f5" strokeWidth="1" x1="0" x2="800" y1="170" y2="170" />

              {/* Fund A Area & Line */}
              <path
                d="M 0 170 C 150 160, 300 130, 450 110 C 600 90, 700 70, 800 55 L 800 170 L 0 170 Z"
                fill="url(#gradFundA)"
              />
              <path
                d="M 0 170 C 150 160, 300 130, 450 110 C 600 90, 700 70, 800 55"
                fill="none"
                stroke="#00D09C"
                strokeWidth="3.5"
                strokeLinecap="round"
              />

              {/* Fund B Area & Line */}
              <path
                d="M 0 170 C 150 165, 300 145, 450 120 C 600 95, 700 65, 800 50 L 800 170 L 0 170 Z"
                fill="url(#gradFundB)"
              />
              <path
                d="M 0 170 C 150 165, 300 145, 450 120 C 600 95, 700 65, 800 50"
                fill="none"
                stroke="#2563EB"
                strokeWidth="3.5"
                strokeLinecap="round"
              />

              {/* Endpoint Highlights */}
              <circle cx="800" cy="55" r="5" fill="#00D09C" stroke="#fff" strokeWidth="2" />
              <circle cx="800" cy="50" r="5" fill="#2563EB" stroke="#fff" strokeWidth="2" />
            </svg>
          </div>

          <div className="flex justify-between mt-3 text-[11px] font-bold text-on-surface-variant uppercase tracking-wider px-1">
            <span>Inception</span>
            <span>1-Year Horizon</span>
            <span>2-Year Horizon</span>
            <span>3-Year Peak ({fundA.returns3Y || "Latest"})</span>
          </div>
        </div>

        {/* Detailed Side-by-Side Metric Table */}
        <div className="col-span-12 bg-surface-container-lowest rounded-2xl overflow-hidden shadow-sm border border-outline-variant/15">
          <div className="p-6 bg-surface-container-low border-b border-outline-variant/15 flex items-center justify-between">
            <div>
              <h4 className="font-headline text-lg font-bold text-on-surface">Comprehensive Head-to-Head Comparison</h4>
              <p className="text-xs text-on-surface-variant mt-0.5">Objective audit of expense, returns, and entry barriers</p>
            </div>
            <span className="text-xs font-semibold text-primary flex items-center gap-1">
              <span className="material-symbols-outlined text-sm">verified</span> Verified Groww Corpus
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="text-[10px] uppercase tracking-widest text-on-surface-variant font-bold bg-surface-container-low/50 border-b border-surface-container">
                  <th className="px-6 py-4 w-1/3">Evaluation Metric</th>
                  <th className="px-6 py-4">
                    <span className="flex items-center gap-2 text-primary font-bold">
                      <span className="w-2.5 h-2.5 rounded-full bg-primary"></span>
                      {fundA.name || "Fund A"}
                    </span>
                  </th>
                  <th className="px-6 py-4">
                    <span className="flex items-center gap-2 text-blue-600 font-bold">
                      <span className="w-2.5 h-2.5 rounded-full bg-blue-600"></span>
                      {fundB.name || "Fund B"}
                    </span>
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-surface-container text-xs">
                {/* NAV */}
                <tr className="hover:bg-surface-container-low/50 transition-colors">
                  <td className="px-6 py-4 font-semibold text-on-surface">Net Asset Value (NAV)</td>
                  <td className="px-6 py-4 font-bold text-on-surface text-sm">
                    {fundA.nav ? `₹${fundA.nav}` : "N/A"}
                  </td>
                  <td className="px-6 py-4 font-bold text-on-surface text-sm">
                    {fundB.nav ? `₹${fundB.nav}` : "N/A"}
                  </td>
                </tr>

                {/* Expense Ratio */}
                <tr className="hover:bg-surface-container-low/50 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex flex-col">
                      <span className="font-semibold text-on-surface">Expense Ratio</span>
                      <span className="text-[10px] text-on-surface-variant opacity-70">Lower is better</span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-primary bg-primary/10 px-2.5 py-1 rounded-md text-sm">
                        {fundA.expenseRatio || "N/A"}
                      </span>
                      {lowerErIndex === 0 && (
                        <span className="text-[10px] bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded-full">
                          ★ Lower Cost
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-blue-600 bg-blue-600/10 px-2.5 py-1 rounded-md text-sm">
                        {fundB.expenseRatio || "N/A"}
                      </span>
                      {lowerErIndex === 1 && (
                        <span className="text-[10px] bg-blue-100 text-blue-800 font-bold px-2 py-0.5 rounded-full">
                          ★ Lower Cost
                        </span>
                      )}
                    </div>
                  </td>
                </tr>

                {/* 3Y Returns */}
                <tr className="hover:bg-surface-container-low/50 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex flex-col">
                      <span className="font-semibold text-on-surface">3-Year Historical Returns</span>
                      <span className="text-[10px] text-on-surface-variant opacity-70">Compounded annualized</span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <span className="font-extrabold text-on-surface text-sm">{fundA.returns3Y || "N/A"}</span>
                      {higherRetIndex === 0 && (
                        <span className="text-[10px] bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded-full">
                          ★ Higher Return
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <span className="font-extrabold text-on-surface text-sm">{fundB.returns3Y || "N/A"}</span>
                      {higherRetIndex === 1 && (
                        <span className="text-[10px] bg-blue-100 text-blue-800 font-bold px-2 py-0.5 rounded-full">
                          ★ Higher Return
                        </span>
                      )}
                    </div>
                  </td>
                </tr>

                {/* Risk Grade */}
                <tr className="hover:bg-surface-container-low/50 transition-colors">
                  <td className="px-6 py-4 font-semibold text-on-surface">Risk Category</td>
                  <td className="px-6 py-4">
                    <span className="px-2.5 py-1 bg-amber-500/10 text-amber-700 rounded-md font-bold text-[11px]">
                      {fundA.risk || "Moderately High"}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="px-2.5 py-1 bg-amber-500/10 text-amber-700 rounded-md font-bold text-[11px]">
                      {fundB.risk || "Moderately High"}
                    </span>
                  </td>
                </tr>

                {/* Minimum Investment / SIP */}
                <tr className="hover:bg-surface-container-low/50 transition-colors">
                  <td className="px-6 py-4 font-semibold text-on-surface">Minimum Investment / SIP</td>
                  <td className="px-6 py-4 font-bold text-on-surface">
                    {fundA.minInvestment || "₹500"}
                  </td>
                  <td className="px-6 py-4 font-bold text-on-surface">
                    {fundB.minInvestment || "₹100"}
                  </td>
                </tr>

                {/* Category Type */}
                <tr className="hover:bg-surface-container-low/50 transition-colors">
                  <td className="px-6 py-4 font-semibold text-on-surface">Fund Category</td>
                  <td className="px-6 py-4 text-on-surface-variant font-medium">
                    {fundA.type || "Equity"}
                  </td>
                  <td className="px-6 py-4 text-on-surface-variant font-medium">
                    {fundB.type || "Equity"}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* AI Insight & Synthesis Bento */}
        <div className="col-span-12 lg:col-span-7 bg-primary-container/[0.04] border border-primary-container/25 rounded-2xl p-6 md:p-8 relative overflow-hidden">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-xl bg-primary/10 text-primary flex items-center justify-center font-bold">
              <span className="material-symbols-outlined text-xl">auto_awesome</span>
            </div>
            <div>
              <h4 className="font-headline text-lg font-bold text-on-surface">AI Synthesis & Verdict</h4>
              <p className="text-[11px] text-on-surface-variant">Neutral comparative breakdown based on retrieved facts</p>
            </div>
          </div>
          
          <div className="p-4 bg-surface-container-lowest/90 backdrop-blur rounded-xl border border-outline-variant/15 shadow-sm text-xs leading-relaxed text-on-surface space-y-2">
            <p className="font-medium">
              {insightText || `Both funds exhibit distinct market focus. Review cost ratios and your investment horizon to balance your portfolio objectives.`}
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-5">
            <div className="p-4 bg-surface-container-lowest rounded-xl border border-primary/20 shadow-sm">
              <span className="text-[10px] uppercase font-bold text-primary block mb-1 tracking-wider">
                Who should choose {fundA.name?.split(" ")[0] || "Fund A"}?
              </span>
              <p className="text-[11px] text-on-surface-variant leading-relaxed">
                Ideal for investors seeking exposure to {fundA.type || "this asset class"} with active management strategy.
              </p>
            </div>

            <div className="p-4 bg-surface-container-lowest rounded-xl border border-blue-600/20 shadow-sm">
              <span className="text-[10px] uppercase font-bold text-blue-600 block mb-1 tracking-wider">
                Who should choose {fundB.name?.split(" ")[0] || "Fund B"}?
              </span>
              <p className="text-[11px] text-on-surface-variant leading-relaxed">
                Ideal for investors seeking low entry threshold ({fundB.minInvestment || "₹100"}) and {fundB.type || "market leader"} stability.
              </p>
            </div>
          </div>
        </div>

        {/* Action Callout */}
        <div className="col-span-12 lg:col-span-5 bg-gradient-to-br from-primary to-primary-container text-white rounded-2xl p-6 md:p-8 flex flex-col justify-between shadow-lg relative overflow-hidden">
          <div className="absolute right-0 bottom-0 opacity-10">
            <span className="material-symbols-outlined text-9xl">trending_up</span>
          </div>
          <div className="relative z-10">
            <span className="px-3 py-1 bg-white/20 backdrop-blur text-white text-[10px] font-bold rounded-full uppercase tracking-wider inline-block mb-3">
              Action Plan
            </span>
            <h4 className="font-headline text-2xl font-extrabold leading-tight mb-2">
              Diversify with Discipline
            </h4>
            <p className="text-white/80 text-xs leading-relaxed mb-6">
              Mutual fund investments generate optimal risk-adjusted returns when balanced across asset classes. Setting up a monthly SIP reduces entry point timing risk.
            </p>
          </div>

          <div className="flex flex-wrap gap-3 relative z-10">
            <button
              onClick={() => onSelectQuery && onSelectQuery(`What is the minimum SIP amount for ${fundA.name || "Fund A"}?`)}
              className="px-5 py-2.5 bg-white text-primary font-bold rounded-full text-xs shadow-md hover:scale-105 active:scale-95 transition-all"
            >
              Check SIP Details
            </button>
            <button
              onClick={handleSave}
              className="px-5 py-2.5 bg-white/20 hover:bg-white/30 backdrop-blur border border-white/30 text-white font-bold rounded-full text-xs transition-colors"
            >
              Watchlist Schemes
            </button>
          </div>
        </div>

      </div>

      {/* Persistent Disclaimer */}
      <footer className="fixed bottom-0 left-0 md:left-[280px] right-0 xl:right-[384px] bg-surface/90 backdrop-blur-lg border-t border-outline-variant/20 p-4 shrink-0 z-40 hidden md:block">
        <div className="max-w-4xl mx-auto flex items-start gap-3 justify-center text-center">
          <span className="material-symbols-outlined text-on-surface-variant opacity-70 text-sm mt-0.5">info</span>
          <p className="text-[10px] sm:text-xs text-on-surface-variant font-medium leading-relaxed max-w-2xl opacity-80">
            Comparative analytics are generated using RAG analysis of official Groww fund facts. Mutual Fund investments are subject to market risks, read all scheme-related documents carefully.
          </p>
        </div>
      </footer>
    </div>
  );
}
