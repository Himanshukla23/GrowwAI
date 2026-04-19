"use client";

import { useState } from "react";

// ── Material Design 3-inspired Line/Area chart ──────────────────────────────────
function LineChart({ data, color = "#00a86b" }) {
  const max = Math.max(...data.map((d) => d.value)) * 1.1; // 10% padding on top
  const min = Math.min(...data.map((d) => d.value)) * 0.9;
  const range = max - min;
  
  const width = 500;
  const height = 140;
  const paddingLeft = 40;
  const paddingRight = 10;
  const paddingTop = 20;
  const paddingBottom = 30;
  
  const usableWidth = width - paddingLeft - paddingRight;
  const usableHeight = height - paddingTop - paddingBottom;

  // Calculate coordinates
  const points = data.map((d, i) => {
    const x = paddingLeft + (i / (data.length - 1)) * usableWidth;
    const y = height - paddingBottom - ((d.value - min) / range) * usableHeight;
    return { x, y, label: d.label, value: d.value };
  });

  // Construct path string
  const pathD = points.length > 0 
    ? `M ${points[0].x} ${points[0].y} ` + points.slice(1).map(p => `L ${p.x} ${p.y}`).join(" ")
    : "";
    
  const areaD = points.length > 0
    ? `${pathD} L ${points[points.length-1].x} ${height - paddingBottom} L ${points[0].x} ${height - paddingBottom} Z`
    : "";

  return (
    <div className="w-full select-none" style={{ fontFamily: "inherit" }}>
      <svg
        viewBox={`0 0 ${width} ${height}`}
        width="100%"
        height={height}
        className="overflow-visible"
      >
        <defs>
          <linearGradient id="areaGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity="0.25" />
            <stop offset="100%" stopColor={color} stopOpacity="0" />
          </linearGradient>
        </defs>

        {/* Y Axis Grid & Labels */}
        {[0, 0.5, 1].map((ratio) => {
          const y = height - paddingBottom - ratio * usableHeight;
          const val = min + ratio * range;
          return (
            <g key={ratio}>
              <line 
                x1={paddingLeft} y1={y} x2={width - paddingRight} y2={y} 
                stroke="#e0e0e0" strokeWidth="0.5" strokeDasharray="4 4" 
              />
              <text x={paddingLeft - 8} y={y + 3} textAnchor="end" fontSize="8" fill="#90a4ae" fontWeight="600">
                {Math.round(val/1000)}k
              </text>
            </g>
          );
        })}

        {/* X Axis labels */}
        {points.filter((_, i) => data.length < 15 || i % Math.floor(data.length/6) === 0).map((p, i) => (
          <text key={i} x={p.x} y={height - 10} textAnchor="middle" fontSize="8" fill="#90a4ae" fontWeight="600">
            {p.label}
          </text>
        ))}

        {/* Area Fill */}
        <path d={areaD} fill="url(#areaGradient)" style={{ transition: 'all 0.5s ease' }} />

        {/* Main Line */}
        <path d={pathD} fill="none" stroke={color} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" style={{ transition: 'all 0.5s ease' }} />

        {/* Data Points (Dots) */}
        {points.map((p, i) => (
          <circle 
            key={i} 
            cx={p.x} 
            cy={p.y} 
            r="3" 
            fill="white" 
            stroke={color} 
            strokeWidth="2"
            className="hover:r-4 transition-all cursor-pointer"
          />
        ))}
        
        {/* X Axis Baseline */}
        <line x1={paddingLeft} y1={height - paddingBottom} x2={width - paddingRight} y2={height - paddingBottom} stroke="#cfd8dc" strokeWidth="1" />
      </svg>
    </div>
  );
}

// ── Speedometer / gauge for risk ──────────────────────────────────────────────
function RiskGauge({ risk }) {
  const isHigh = risk?.toLowerCase().includes("high");
  const isMod = risk?.toLowerCase().includes("moderate");
  const color = isHigh ? "#d32f2f" : isMod ? "#f57c00" : "#00897b";
  const bgColor = isHigh ? "#ffebee" : isMod ? "#fff3e0" : "#e0f2f1";
  // needle angle: low=−60°, mod=0°, high=+60°
  const angle = isHigh ? 60 : isMod ? 0 : -60;
  const rad = ((angle - 90) * Math.PI) / 180;
  const cx = 60, cy = 60, r = 44;
  const nx = cx + r * Math.cos(rad);
  const ny = cy + r * Math.sin(rad);

  return (
    <svg viewBox="0 0 120 70" width="120" height="70">
      {/* Gauge arc segments */}
      {[
        { start: 180, end: 240, c: "#64b5f6" },
        { start: 240, end: 300, c: "#ffb74d" },
        { start: 300, end: 360, c: "#e57373" },
      ].map(({ start, end, c }, idx) => {
        const s = ((start - 90) * Math.PI) / 180;
        const e = ((end - 90) * Math.PI) / 180;
        const x1 = cx + r * Math.cos(s),
          y1 = cy + r * Math.sin(s);
        const x2 = cx + r * Math.cos(e),
          y2 = cy + r * Math.sin(e);
        return (
          <path
            key={idx}
            d={`M ${x1} ${y1} A ${r} ${r} 0 0 1 ${x2} ${y2}`}
            fill="none"
            stroke={c}
            strokeWidth="10"
            strokeLinecap="round"
          />
        );
      })}
      {/* Needle */}
      <line
        x1={cx}
        y1={cy}
        x2={nx}
        y2={ny}
        stroke={color}
        strokeWidth="2.5"
        strokeLinecap="round"
      />
      <circle cx={cx} cy={cy} r="4" fill={color} />
    </svg>
  );
}

// ── Stat tile ──────────────────────────────────────────────────────────────────
function StatTile({ label, value, sub }) {
  return (
    <div className="flex flex-col gap-0.5 p-3 bg-surface-container-low rounded-xl">
      <p className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider leading-none">
        {label}
      </p>
      <p className="text-lg font-extrabold font-headline text-on-surface leading-tight">
        {value}
      </p>
      {sub && <p className="text-[10px] text-on-surface-variant">{sub}</p>}
    </div>
  );
}

// ── Section card wrapper ──────────────────────────────────────────────────────
function Card({ title, children, className = "" }) {
  return (
    <div
      className={`bg-surface-container-lowest rounded-2xl border border-outline-variant/10 shadow-sm overflow-hidden ${className}`}
    >
      {title && (
        <div className="px-5 pt-4 pb-2">
          <p className="text-[10px] font-bold text-on-surface-variant uppercase tracking-widest">
            {title}
          </p>
        </div>
      )}
      <div className="px-5 pb-5">{children}</div>
    </div>
  );
}

// ── Holdings percentage bar ───────────────────────────────────────────────────
function HoldingBar({ name, value }) {
  const pct = parseFloat(value) || 50;
  return (
    <div className="flex flex-col gap-1">
      <div className="flex justify-between items-center">
        <span className="text-xs font-semibold text-on-surface truncate max-w-[70%]">{name}</span>
        <span className="text-xs font-bold text-primary">{value}</span>
      </div>
      <div className="w-full bg-surface-container h-1.5 rounded-full overflow-hidden">
        <div
          className="bg-gradient-to-r from-primary to-primary-container h-full rounded-full"
          style={{ width: `${Math.min(pct, 100)}%` }}
        />
      </div>
    </div>
  );
}

// ── Main component ────────────────────────────────────────────────────────────
export default function DashboardWorkspace({ fundData, onCompareClick }) {
  const [chartRange, setChartRange] = useState("1Y");

  const chartDataMap = {
    "1M": [
      { label: "W1", value: 48200 }, { label: "W2", value: 50100 },
      { label: "W3", value: 49800 }, { label: "W4", value: 54200 },
    ],
    "6M": [
      { label: "Nov", value: 44000 }, { label: "Dec", value: 46500 },
      { label: "Jan", value: 45800 }, { label: "Feb", value: 48900 },
      { label: "Mar", value: 51000 }, { label: "Apr", value: 54200 },
    ],
    "1Y": [
      { label: "May", value: 38000 }, { label: "Jun", value: 40500 },
      { label: "Jul", value: 42000 }, { label: "Aug", value: 41000 },
      { label: "Sep", value: 44500 }, { label: "Oct", value: 47000 },
      { label: "Nov", value: 45500 }, { label: "Dec", value: 48000 },
      { label: "Jan", value: 49500 }, { label: "Feb", value: 51000 },
      { label: "Mar", value: 52800 }, { label: "Apr", value: 54200 },
    ],
    "3Y": [
      { label: "2022", value: 28000 }, { label: "2023", value: 38000 },
      { label: "2024", value: 48000 }, { label: "2025", value: 54200 },
    ],
    "5Y": [
      { label: "2021", value: 20000 }, { label: "2022", value: 28000 },
      { label: "2023", value: 38000 }, { label: "2024", value: 48000 },
      { label: "2025", value: 54200 },
    ],
  };

  // ── Welcome state (no fund selected) ──────────────────────────────────────
  if (!fundData) {
    return (
      <div className="flex-1 p-6 bg-surface-container-low min-h-full">
        {/* Header */}
        <div className="mb-6 flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-headline font-bold text-on-surface tracking-tight">
              Welcome Back, Investor
            </h2>
            <p className="text-sm text-on-surface-variant mt-0.5">
              Real-time portfolio intelligence and fund analysis.
            </p>
          </div>
          <div className="flex items-center gap-2 bg-surface-container-lowest border border-outline-variant/20 px-3 py-1.5 rounded-full shadow-sm">
            <div className="w-2 h-2 rounded-full bg-primary animate-pulse" />
            <span className="text-xs font-bold uppercase tracking-widest text-on-surface-variant">
              Live Data
            </span>
          </div>
        </div>

        {/* Bento grid */}
        <div className="grid grid-cols-12 gap-4">
          {/* Portfolio overview + chart */}
          <div className="col-span-12 lg:col-span-8 bg-surface-container-lowest rounded-2xl p-5 shadow-sm border border-outline-variant/10">
            <div className="flex justify-between items-start mb-4">
              <div>
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full bg-secondary-container text-on-secondary-container text-[10px] font-bold tracking-widest uppercase mb-2">
                  Portfolio Overview
                </span>
                <p className="text-xs text-on-surface-variant font-medium">Total Market Growth</p>
                <h3 className="text-3xl font-headline font-extrabold text-on-surface mt-0.5">
                  ₹12,84,500
                </h3>
                <div className="flex items-center gap-2 mt-2">
                  <span className="bg-primary/10 text-primary px-2.5 py-0.5 rounded-full text-xs font-bold flex items-center gap-1">
                    <span className="material-symbols-outlined text-[12px]" style={{ fontVariationSettings: "'FILL' 1" }}>trending_up</span>
                    +14.2%
                  </span>
                  <span className="text-on-surface-variant text-xs">Past 30 days</span>
                </div>
              </div>
            </div>

            {/* Labeled line chart */}
            <LineChart
              data={chartDataMap["1Y"]}
              color="#00a86b"
            />
          </div>

          {/* Invest Now card */}
          <div className="col-span-12 lg:col-span-4 bg-gradient-to-br from-primary to-[#00D09C] p-5 rounded-2xl shadow-lg flex flex-col justify-between text-white relative overflow-hidden">
            <div className="absolute top-0 right-0 w-24 h-24 bg-white/10 blur-2xl rounded-full -mr-8 -mt-8" />
            <div className="relative z-10">
              <span className="material-symbols-outlined text-3xl mb-3 text-white/90">
                account_balance_wallet
              </span>
              <h4 className="text-xl font-headline font-bold">Invest Now</h4>
              <p className="text-white/80 text-xs mt-2 leading-relaxed">
                Maximize returns with curated AI recommendations based on your risk profile.
              </p>
            </div>
            <button className="bg-white text-primary font-bold py-2.5 rounded-xl mt-6 hover:brightness-105 transition-all shadow-md text-sm">
              Explore Top Funds
            </button>
          </div>

          {/* Watchlist */}
          <div className="col-span-12 lg:col-span-6 bg-surface-container-lowest p-4 rounded-2xl shadow-sm border border-outline-variant/10">
            <div className="flex justify-between items-center mb-3">
              <h4 className="font-bold text-sm text-on-surface">Watchlist Highlights</h4>
              <span className="text-primary font-bold text-xs cursor-pointer hover:underline">View All</span>
            </div>
            <div className="space-y-1">
              {[
                { n: "SBI Gold Fund", c: "Commodities", p: "21.45", change: "+1.2%", color: "bg-orange-100 text-orange-600", initial: "S" },
                { n: "HDFC Mid Cap", c: "Equity · Mid Cap", p: "142.18", change: "-0.4%", color: "bg-blue-100 text-blue-600", initial: "H", neg: true },
                { n: "ICICI Large Cap", c: "Equity · Large Cap", p: "84.12", change: "+0.8%", color: "bg-emerald-100 text-emerald-600", initial: "I" },
              ].map((item, i) => (
                <div key={i} className="flex items-center justify-between p-2.5 rounded-xl hover:bg-surface-container-low transition-colors cursor-pointer">
                  <div className="flex items-center gap-3">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${item.color}`}>{item.initial}</div>
                    <div>
                      <p className="font-semibold text-xs text-on-surface">{item.n}</p>
                      <p className="text-[10px] text-on-surface-variant font-medium">{item.c}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-bold text-xs text-on-surface">₹{item.p}</p>
                    <p className={`text-[11px] font-bold ${item.neg ? "text-error" : "text-primary"}`}>{item.change}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Market sentiment placeholder */}
          <div className="col-span-12 lg:col-span-6 bg-surface-container-lowest p-4 rounded-2xl shadow-sm border border-outline-variant/10 flex items-center justify-center min-h-[160px]">
            <div className="text-center">
              <span className="material-symbols-outlined text-3xl text-primary mb-2">insights</span>
              <p className="font-bold text-sm text-on-surface">Live Market Sentiment</p>
              <p className="text-xs text-on-surface-variant mt-1">Ask AI to analyze specific sectors</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // ── Fund detail view ───────────────────────────────────────────────────────
  const isNeg = fundData.change?.includes("-");
  const chartColor = isNeg ? "#d32f2f" : "#00a86b";
  const chartData = chartDataMap[chartRange];

  return (
    <div className="flex-1 p-6 pb-24 bg-surface min-h-full">

      {/* Fund Header */}
      <section className="mb-5">
        <div className="flex items-center gap-2 mb-2">
          <span className="px-2 py-0.5 bg-surface-container-high text-on-surface-variant text-[10px] font-bold tracking-widest rounded-full uppercase">
            Mutual Fund
          </span>
          <span className="text-outline-variant text-xs">•</span>
          <span className="text-on-surface-variant font-semibold text-xs">{fundData.type || "Equity"}</span>
        </div>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div>
            <h2 className="text-2xl md:text-3xl font-extrabold font-headline text-on-surface tracking-tight leading-tight">
              {fundData.name || "SBI Gold Fund"}
            </h2>
            <div className="flex items-center gap-1.5 mt-1.5">
              <span className="material-symbols-outlined text-primary text-sm" style={{ fontVariationSettings: "'FILL' 1" }}>verified</span>
              <span className="text-on-surface-variant font-medium text-xs">{fundData.plan || "Direct Plan · Growth"}</span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={onCompareClick}
              className="px-4 py-2 rounded-full border border-outline-variant/50 text-on-surface font-semibold hover:bg-surface-container transition-all flex items-center gap-1.5 shadow-sm text-xs"
            >
              <span className="material-symbols-outlined text-[15px]">compare_arrows</span>
              Compare
            </button>
            <button className="px-5 py-2 rounded-full bg-gradient-to-r from-primary to-primary-container text-white font-semibold shadow-md hover:scale-[1.02] active:scale-[0.98] transition-all flex items-center gap-1.5 text-xs">
              <span className="material-symbols-outlined text-[15px]">analytics</span>
              Save Analysis
            </button>
          </div>
        </div>
      </section>

      {/* NAV + Chart */}
      <section className="bg-surface-container-lowest rounded-2xl p-5 border border-outline-variant/10 shadow-sm mb-5">
        <div className="flex justify-between items-start mb-4">
          <div>
            <p className="text-[10px] text-on-surface-variant font-bold uppercase tracking-widest mb-1">Net Asset Value (NAV)</p>
            <div className="flex items-baseline gap-2">
              <h3 className="text-3xl font-extrabold font-headline text-on-surface">₹{fundData.nav || "54.20"}</h3>
              <span className={`flex items-center gap-0.5 font-bold text-xs px-2 py-0.5 rounded-full ${isNeg ? "text-error bg-error/10" : "text-primary bg-primary/10"}`}>
                <span className="material-symbols-outlined text-[12px]">{isNeg ? "arrow_downward" : "arrow_upward"}</span>
                {fundData.change || "+1.2%"}
              </span>
            </div>
          </div>
          {/* Range selector */}
          <div className="flex bg-surface-container-low p-1 rounded-full gap-0.5 border border-outline-variant/10">
            {["1M", "6M", "1Y", "3Y", "5Y"].map((tf) => (
              <button
                key={tf}
                onClick={() => setChartRange(tf)}
                className={`px-3 py-1.5 rounded-full text-[10px] font-bold transition-all ${
                  tf === chartRange
                    ? "bg-white text-primary shadow-sm border border-outline-variant/20"
                    : "text-on-surface-variant hover:text-on-surface"
                }`}
              >
                {tf}
              </button>
            ))}
          </div>
        </div>

        {/* Labeled line chart */}
        <LineChart data={chartData} color={chartColor} />

        <div className="flex justify-between items-center mt-1 px-1">
          <span className="text-[10px] text-on-surface-variant font-medium">
            {chartRange === "1Y" ? "Apr 2024 – Apr 2025" : chartRange === "5Y" ? "2021 – 2025" : ""}
          </span>
          <span className="text-[10px] text-primary font-bold">
            {isNeg ? "↓ Declining" : "↑ Growing"} trend
          </span>
        </div>
      </section>

      {/* Stats grid */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-4">

        {/* Risk Assessment */}
        <div className="bg-surface-container-lowest p-6 rounded-2xl shadow-sm border border-outline-variant/10 flex flex-col items-center justify-center text-center relative overflow-hidden h-full">
          <h4 className="absolute top-5 left-5 text-[10px] font-bold text-on-surface-variant uppercase tracking-widest z-10 w-full text-left">Risk Assessment</h4>

          {/* Final Polished upward SVG Gauge */}
          {(() => {
            const risk = (fundData.risk || "high risk").toLowerCase();
            const isVeryHigh = risk.includes("very high");
            const isHigh     = risk.includes("high") && !isVeryHigh;
            const isMod      = risk.includes("moderate") || risk.includes("medium");

            // Progress: 0.1 to 0.9 range
            const progress = isVeryHigh ? 0.92 : isHigh ? 0.68 : isMod ? 0.32 : 0.08;
            const riskColor = isVeryHigh ? "#b71c1c" : isHigh ? "#e65100" : isMod ? "#f9a825" : "#1b5e20";

            // Geometry: Center (100, 105), Track Radius 65, Label Radius 86
            const CX = 100, CY = 105, R = 65, LR = 86;

            const arc = (startPct, endPct, radius = R) => {
              const sRad = (startPct * 180 * Math.PI) / 180;
              const eRad = (endPct * 180 * Math.PI) / 180;
              const x1 = CX - radius * Math.cos(sRad);
              const y1 = CY - radius * Math.sin(sRad);
              const x2 = CX - radius * Math.cos(eRad);
              const y2 = CY - radius * Math.sin(eRad);
              return `M ${x1} ${y1} A ${radius} ${radius} 0 0 1 ${x2} ${y2}`;
            };

            const getPoint = (pct, radius) => {
              const rad = (pct * 180 * Math.PI) / 180;
              return {
                x: CX - radius * Math.cos(rad),
                y: CY - radius * Math.sin(rad)
              };
            };

            const nx = getPoint(progress, 60).x;
            const ny = getPoint(progress, 60).y;

            return (
              <div className="relative mt-12 mb-4 w-full flex justify-center">
                <svg viewBox="0 10 200 110" width="240" height="120" className="overflow-visible">
                  <defs>
                    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                      <feGaussianBlur stdDeviation="2" result="blur" />
                      <feComposite in="SourceGraphic" in2="blur" operator="over" />
                    </filter>
                  </defs>

                  {/* Faded Background Track */}
                  <path d={arc(0, 1)} fill="none" stroke="#f0f0f0" strokeWidth="12" strokeLinecap="round" />

                  {/* Segmented zones */}
                  <g fill="none" strokeWidth="12" strokeLinecap="round">
                    <path d={arc(0, 0.25)} stroke="#d1e7dd" />
                    <path d={arc(0.25, 0.5)} stroke="#fff3cd" />
                    <path d={arc(0.5, 0.75)} stroke="#ffe5d0" />
                    <path d={arc(0.75, 1)} stroke="#f8d7da" />
                  </g>

                  {/* Active segment with glow */}
                  <path d={arc(0, progress)} fill="none" stroke={riskColor} strokeWidth="12" strokeLinecap="round" filter="url(#glow)" style={{ transition: 'all 1.2s' }} />

                  {/* Outer Labels (Avoiding arc overlap) */}
                  <g fontSize="8" fontWeight="800" fill="#adb5bd">
                    <text x={getPoint(0.04, LR).x} y={getPoint(0.04, LR).y} textAnchor="middle">Low</text>
                    <text x={getPoint(0.35, LR).x} y={getPoint(0.35, LR).y} textAnchor="middle">Mod</text>
                    <text x={getPoint(0.65, LR).x} y={getPoint(0.65, LR).y} textAnchor="middle">High</text>
                    <text x={getPoint(0.96, LR).x} y={getPoint(0.96, LR).y} textAnchor="middle">V.High</text>
                  </g>

                  {/* Needle */}
                  <g style={{ transition: 'all 0.8s ease-out' }}>
                    <line x1={CX} y1={CY} x2={nx} y2={ny} stroke={riskColor} strokeWidth="6" strokeLinecap="round" />
                    <circle cx={CX} cy={CY} r="10" fill="white" stroke={riskColor} strokeWidth="3" />
                    <circle cx={CX} cy={CY} r="4" fill={riskColor} />
                  </g>
                </svg>
              </div>
            );
          })()}

          <div className="mt-4">
            <h3 className={`font-headline font-black text-2xl tracking-tight leading-none ${
               (fundData.risk || "").toLowerCase().includes("very high") ? "text-red-800" :
               (fundData.risk || "").toLowerCase().includes("high")      ? "text-orange-700" :
               (fundData.risk || "").toLowerCase().includes("moderate")  ? "text-amber-600" : "text-green-800"
            }`}>
              {fundData.risk || "High Risk"}
            </h3>
            <p className="text-[10px] text-on-surface-variant/80 mt-2 font-bold uppercase tracking-widest max-w-[200px]">
              Risk Category
            </p>
          </div>
        </div>

        {/* Holdings */}
        <div className="bg-surface-container-lowest p-6 rounded-2xl shadow-sm border border-outline-variant/10 flex flex-col">
          <h4 className="text-[10px] font-bold text-on-surface-variant uppercase tracking-widest mb-4">Top Holdings Breakdown</h4>
          <div className="flex-1 flex flex-col gap-3">
            {fundData.holdings && fundData.holdings.length > 0 ? (
              // Cap at 5 items, strip % for bar width
              fundData.holdings.slice(0, 5).map((h, i) => {
                const pct = parseFloat(String(h.value).replace("%", "")) || 30;
                const barColors = ["bg-primary", "bg-primary/80", "bg-primary/60", "bg-primary/45", "bg-primary/30"];
                return (
                  <div key={i} className="flex flex-col gap-1">
                    <div className="flex justify-between items-center">
                      <span className="text-xs font-semibold text-on-surface truncate max-w-[65%]">{h.name}</span>
                      <span className="text-xs font-bold text-primary">{h.value}</span>
                    </div>
                    <div className="w-full bg-surface-container h-1.5 rounded-full overflow-hidden">
                      <div
                        className={`${barColors[i]} h-full rounded-full transition-all`}
                        style={{ width: `${Math.min(pct, 100)}%` }}
                      />
                    </div>
                  </div>
                );
              })
            ) : (
              // Fallback: build synthetic bars from available fund data
              (() => {
                const syntheticItems = [
                  { name: "Equity / Primary Asset", value: "70%", pct: 70 },
                  { name: fundData.category || "Core Sector", value: "20%", pct: 20 },
                  { name: "Cash & Equivalents", value: "10%", pct: 10 },
                ];
                return (
                  <div className="flex flex-col gap-3">
                    {syntheticItems.map((h, i) => (
                      <div key={i} className="flex flex-col gap-1">
                        <div className="flex justify-between items-center">
                          <span className="text-xs font-semibold text-on-surface">{h.name}</span>
                          <span className="text-xs font-bold text-on-surface-variant">{h.value}</span>
                        </div>
                        <div className="w-full bg-surface-container h-1.5 rounded-full overflow-hidden">
                          <div
                            className="bg-primary/40 h-full rounded-full"
                            style={{ width: `${h.pct}%` }}
                          />
                        </div>
                      </div>
                    ))}
                    <p className="text-[10px] text-on-surface-variant/60 italic mt-1">
                      Estimated allocation · Detailed breakdown unavailable
                    </p>
                  </div>
                );
              })()
            )}
          </div>
          {fundData.holdings && fundData.holdings.length > 0 && (
            <button className="text-primary text-xs font-bold hover:underline mt-4 flex items-center gap-1 group w-fit">
              View detailed allocation
              <span className="material-symbols-outlined text-sm group-hover:translate-x-1 transition-transform">arrow_forward</span>
            </button>
          )}
        </div>

        {/* Key Metrics */}
        <div className="bg-surface-container-lowest p-6 rounded-2xl shadow-sm border border-outline-variant/10 flex flex-col justify-between">
          <h4 className="text-[10px] font-bold text-on-surface-variant uppercase tracking-widest mb-4 border-b border-outline-variant/10 pb-3">Key Metrics</h4>
          <div className="grid grid-cols-2 gap-y-5 flex-1">
            <div>
              <p className="text-[10px] text-on-surface-variant font-bold uppercase tracking-wider mb-1">Expense Ratio</p>
              <p className="font-headline font-extrabold text-xl text-on-surface">{fundData.expenseRatio || "0.64%"}</p>
            </div>
            <div>
              <p className="text-[10px] text-on-surface-variant font-bold uppercase tracking-wider mb-1">Exit Load</p>
              <p className="font-headline font-extrabold text-xl text-on-surface">{fundData.exitLoad || "1%"}</p>
            </div>
            <div className="col-span-2">
              <p className="text-[10px] text-on-surface-variant font-bold uppercase tracking-wider mb-1">Alpha Rating (Proprietary)</p>
              <div className="flex items-baseline gap-2">
                <p className="font-headline font-black text-4xl text-primary">{fundData.alphaScore || "8.4"}</p>
                <p className="text-sm font-bold text-on-surface-variant">/ 10</p>
              </div>
              <div className="w-full bg-surface-container h-2 rounded-full mt-3 overflow-hidden">
                <div
                  className="bg-gradient-to-r from-primary to-primary-container h-full rounded-full"
                  style={{ width: `${(parseFloat(fundData.alphaScore || "8.4") / 10) * 100}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Disclaimer */}
      <footer className="fixed bottom-0 left-0 md:left-[280px] right-0 xl:right-[384px] bg-surface/90 backdrop-blur-md border-t border-outline-variant/20 px-6 py-3 z-40 hidden md:flex items-start gap-2 justify-center text-center">
        <span className="material-symbols-outlined text-on-surface-variant/60 text-sm mt-0.5">info</span>
        <p className="text-[10px] text-on-surface-variant/70 leading-relaxed max-w-2xl">
          Groww Assist integrates RAG APIs for analytics. Mutual Fund investments are subject to market risks. Past performance does not guarantee future returns.
        </p>
      </footer>
    </div>
  );
}
