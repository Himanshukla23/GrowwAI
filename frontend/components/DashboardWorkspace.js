"use client";

import { useState } from "react";

// ── Google Finance-inspired Line/Area chart ──────────────────────────────────
function LineChart({ data, color = "#006c4f" }) {
  if (!data || data.length === 0) return null;

  const max = Math.max(...data.map((d) => d.value)) * 1.05;
  const min = Math.min(...data.map((d) => d.value)) * 0.95;
  const range = max - min || 1;

  const width = 600;
  const height = 150;
  const paddingLeft = 45;
  const paddingRight = 15;
  const paddingTop = 20;
  const paddingBottom = 25;

  const usableWidth = width - paddingLeft - paddingRight;
  const usableHeight = height - paddingTop - paddingBottom;

  const points = data.map((d, i) => {
    const x = paddingLeft + (i / (data.length - 1)) * usableWidth;
    const y = height - paddingBottom - ((d.value - min) / range) * usableHeight;
    return { x, y, label: d.label, value: d.value };
  });

  const pathD =
    points.length > 0
      ? `M ${points[0].x} ${points[0].y} ` +
        points
          .slice(1)
          .map((p) => `L ${p.x} ${p.y}`)
          .join(" ")
      : "";

  const areaD =
    points.length > 0
      ? `${pathD} L ${points[points.length - 1].x} ${
          height - paddingBottom
        } L ${points[0].x} ${height - paddingBottom} Z`
      : "";

  return (
    <div className="w-full select-none">
      <svg
        viewBox={`0 0 ${width} ${height}`}
        width="100%"
        height={height}
        className="overflow-visible"
      >
        <defs>
          <linearGradient id="googleAreaGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity="0.22" />
            <stop offset="100%" stopColor={color} stopOpacity="0.0" />
          </linearGradient>
        </defs>

        {/* Horizontal gridlines */}
        {[0, 0.5, 1].map((ratio) => {
          const y = height - paddingBottom - ratio * usableHeight;
          const val = min + ratio * range;
          return (
            <g key={ratio}>
              <line
                x1={paddingLeft}
                y1={y}
                x2={width - paddingRight}
                y2={y}
                stroke="#edf0f2"
                strokeWidth="1"
                strokeDasharray="3 3"
              />
              <text
                x={paddingLeft - 8}
                y={y + 3}
                textAnchor="end"
                fontSize="9"
                fill="#80868b"
                fontFamily="monospace"
                fontWeight="500"
              >
                ₹{Math.round(val)}
              </text>
            </g>
          );
        })}

        {/* X Axis labels */}
        {points
          .filter((_, i) => data.length < 8 || i % Math.ceil(data.length / 5) === 0)
          .map((p, i) => (
            <text
              key={i}
              x={p.x}
              y={height - 6}
              textAnchor="middle"
              fontSize="9"
              fill="#80868b"
              fontWeight="500"
            >
              {p.label}
            </text>
          ))}

        {/* Area Fill */}
        <path d={areaD} fill="url(#googleAreaGradient)" className="transition-all duration-300" />

        {/* Main Line */}
        <path
          d={pathD}
          fill="none"
          stroke={color}
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          className="transition-all duration-300"
        />

        {/* Last Point Indicator */}
        {points.length > 0 && (
          <circle
            cx={points[points.length - 1].x}
            cy={points[points.length - 1].y}
            r="4"
            fill={color}
            stroke="#ffffff"
            strokeWidth="2"
          />
        )}
      </svg>
    </div>
  );
}

// ── Google Material Design 3 Speedometer ─────────────────────────────────────
function RiskMeter({ risk = "Moderately High" }) {
  const rLower = (risk || "").toLowerCase();
  const isVeryHigh = rLower.includes("very high");
  const isHigh = rLower.includes("high") && !isVeryHigh;
  const isMod = rLower.includes("moderate") || rLower.includes("medium");

  const activeColor = isVeryHigh
    ? "#c5221f"
    : isHigh
    ? "#ea8600"
    : isMod
    ? "#137333"
    : "#1a73e8";

  const segments = [
    { label: "Low", color: "#1a73e8", active: !isMod && !isHigh && !isVeryHigh },
    { label: "Moderate", color: "#137333", active: isMod },
    { label: "High", color: "#ea8600", active: isHigh },
    { label: "Very High", color: "#c5221f", active: isVeryHigh },
  ];

  return (
    <div className="flex flex-col items-center w-full">
      <div className="grid grid-cols-4 gap-1.5 w-full max-w-[240px] my-3">
        {segments.map((s, i) => (
          <div key={i} className="flex flex-col items-center gap-1">
            <div
              className={`h-2 w-full rounded-full transition-all ${
                s.active ? "shadow-xs scale-y-125" : "opacity-25"
              }`}
              style={{ backgroundColor: s.color }}
            />
            <span
              className={`text-[9px] font-bold uppercase tracking-wider text-center ${
                s.active ? "text-on-surface font-extrabold" : "text-on-surface-variant/50"
              }`}
            >
              {s.label}
            </span>
          </div>
        ))}
      </div>
      <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-surface-container-low border border-outline-variant/15">
        <span
          className="w-2 h-2 rounded-full"
          style={{ backgroundColor: activeColor }}
        />
        <span className="text-xs font-bold text-on-surface">
          Riskometer: {risk}
        </span>
      </div>
    </div>
  );
}

// ── Google-style Clean Stat Tile ─────────────────────────────────────────────
function StatTile({ label, value, sub, mono = false }) {
  return (
    <div className="p-3.5 bg-surface-container-low/60 rounded-xl border border-outline-variant/10 flex flex-col justify-between">
      <span className="text-[10px] font-bold uppercase tracking-wider text-on-surface-variant/70 mb-1">
        {label}
      </span>
      <span className={`text-base font-extrabold text-on-surface ${mono ? "font-mono" : ""}`}>
        {value}
      </span>
      {sub && <span className="text-[10px] text-on-surface-variant/70 mt-0.5">{sub}</span>}
    </div>
  );
}

// ── Main Dashboard Workspace ──────────────────────────────────────────────────
export default function DashboardWorkspace({ fundData, onCompareClick, onSelectFund }) {
  const [chartRange, setChartRange] = useState("1Y");

  // Verified Groww funds showcase
  const TOP_GROWW_FUNDS = [
    {
      name: "SBI Contra Direct Plan Growth",
      category: "Equity • Value Oriented",
      nav: "₹414.54",
      cagr3Y: "11.80%",
      er: "0.86%",
      aum: "₹45,067 Cr",
      risk: "Moderately High",
      query: "What is the expense ratio and NAV of SBI Contra Fund?",
    },
    {
      name: "Nippon India Large Cap Direct Growth",
      category: "Equity • Large Cap",
      nav: "₹101.36",
      cagr3Y: "12.56%",
      er: "0.85%",
      aum: "₹51,296 Cr",
      risk: "Moderately High",
      query: "What is the expense ratio and NAV of Nippon India Large Cap Fund?",
    },
    {
      name: "HDFC Mid Cap Fund Direct Growth",
      category: "Equity • Mid Cap",
      nav: "₹196.20",
      cagr3Y: "24.10%",
      er: "0.78%",
      aum: "₹68,140 Cr",
      risk: "Very High",
      query: "What are the details of HDFC Mid Cap Fund?",
    },
    {
      name: "ICICI Prudential Large Cap Direct Growth",
      category: "Equity • Large Cap",
      nav: "₹96.15",
      cagr3Y: "13.40%",
      er: "0.70%",
      aum: "₹48,920 Cr",
      risk: "Very High",
      query: "What is the NAV of ICICI Prudential Large Cap Fund?",
    },
  ];

  const chartDataMap = {
    "1M": [
      { label: "05 Oct", value: 405 },
      { label: "12 Oct", value: 409 },
      { label: "19 Oct", value: 407 },
      { label: "26 Oct", value: 412 },
      { label: "05 Nov", value: 414.54 },
    ],
    "6M": [
      { label: "May", value: 375 },
      { label: "Jun", value: 388 },
      { label: "Jul", value: 395 },
      { label: "Aug", value: 402 },
      { label: "Sep", value: 408 },
      { label: "Nov", value: 414.54 },
    ],
    "1Y": [
      { label: "Nov '25", value: 340 },
      { label: "Jan '26", value: 355 },
      { label: "Mar '26", value: 370 },
      { label: "May '26", value: 382 },
      { label: "Jul '26", value: 398 },
      { label: "Sep '26", value: 409 },
      { label: "Nov '26", value: 414.54 },
    ],
    "3Y": [
      { label: "2023", value: 295 },
      { label: "2024", value: 345 },
      { label: "2025", value: 380 },
      { label: "2026", value: 414.54 },
    ],
    "5Y": [
      { label: "2021", value: 215 },
      { label: "2022", value: 260 },
      { label: "2023", value: 295 },
      { label: "2024", value: 345 },
      { label: "2025", value: 380 },
      { label: "2026", value: 414.54 },
    ],
  };

  // ── Welcome Screen (Google Finance Aesthetic) ────────────────────────────────
  if (!fundData) {
    return (
      <div className="p-4 md:p-8 max-w-6xl mx-auto space-y-6 animate-fade-in">
        {/* Header Section */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <div className="flex items-center gap-1.5 text-xs font-semibold text-primary mb-1">
              <span className="material-symbols-outlined text-[15px]" style={{ fontVariationSettings: "'FILL' 1" }}>
                insights
              </span>
              <span>Groww Market Intelligence</span>
            </div>
            <h2 className="font-headline text-2xl md:text-3xl font-extrabold text-on-surface tracking-tight">
              Mutual Fund Analytics & Research
            </h2>
            <p className="text-xs md:text-sm text-on-surface-variant/80 mt-1 max-w-2xl leading-relaxed">
              Explore official scheme facts, compare portfolio performance, and query the grounded Groww AI engine.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={onCompareClick}
              className="px-4 py-2 bg-gradient-to-r from-primary to-primary-container text-white font-semibold rounded-full text-xs shadow-xs hover:scale-[1.02] active:scale-95 transition-all flex items-center gap-1.5 cursor-pointer"
            >
              <span className="material-symbols-outlined text-[16px]">compare_arrows</span>
              <span>Compare Funds</span>
            </button>
          </div>
        </div>

        {/* Featured Market Funds Table (Google Finance Style) */}
        <div className="bg-surface-container-lowest rounded-2xl border border-outline-variant/15 shadow-xs overflow-hidden">
          <div className="px-5 py-3.5 border-b border-outline-variant/15 flex items-center justify-between bg-surface-container-low/40">
            <div>
              <h4 className="font-headline text-xs font-bold uppercase tracking-wider text-on-surface">
                Verified Funds in Focus (Live Nov 2026)
              </h4>
            </div>
            <span className="text-[10px] font-bold text-primary bg-primary/10 px-2.5 py-0.5 rounded-full">
              Chroma RAG Synced
            </span>
          </div>

          <div className="divide-y divide-outline-variant/10 text-xs">
            {TOP_GROWW_FUNDS.map((fund, idx) => (
              <div
                key={idx}
                className="grid grid-cols-12 py-3.5 px-5 items-center hover:bg-surface-container-low/40 transition-colors"
              >
                <div className="col-span-12 sm:col-span-5 mb-2 sm:mb-0">
                  <span className="font-bold text-on-surface text-xs block leading-snug">
                    {fund.name}
                  </span>
                  <span className="text-[10px] text-on-surface-variant/70 font-medium">
                    {fund.category} • {fund.aum}
                  </span>
                </div>

                <div className="col-span-4 sm:col-span-2">
                  <span className="text-[10px] text-on-surface-variant/70 block uppercase font-semibold">
                    NAV
                  </span>
                  <span className="font-mono font-bold text-on-surface text-xs">
                    {fund.nav}
                  </span>
                </div>

                <div className="col-span-4 sm:col-span-2">
                  <span className="text-[10px] text-on-surface-variant/70 block uppercase font-semibold">
                    Expense Ratio
                  </span>
                  <span className="font-mono font-bold text-primary text-xs">
                    {fund.er}
                  </span>
                </div>

                <div className="col-span-4 sm:col-span-3 flex items-center justify-end gap-2">
                  <span className="hidden md:inline px-2 py-0.5 rounded-full text-[10px] font-bold bg-surface-container text-on-surface-variant">
                    {fund.risk}
                  </span>
                  <button
                    onClick={() => onSelectFund && onSelectFund(fund.query)}
                    className="px-3 py-1 rounded-full bg-primary/10 hover:bg-primary text-primary hover:text-white font-semibold text-[11px] transition-all cursor-pointer"
                  >
                    Analyze
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Launchpad to Comparisons */}
        <div className="bg-gradient-to-r from-surface-container-lowest to-surface-container-low rounded-2xl p-5 border border-primary/20 shadow-xs flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-primary/10 text-primary flex items-center justify-center shrink-0">
              <span className="material-symbols-outlined text-2xl">compare_arrows</span>
            </div>
            <div>
              <h5 className="font-headline font-bold text-sm text-on-surface">
                Ready to Compare Schemes?
              </h5>
              <p className="text-xs text-on-surface-variant/80">
                Run side-by-side performance audits between SBI Contra, Nippon Large Cap, and HDFC Mid Cap.
              </p>
            </div>
          </div>
          <button
            onClick={onCompareClick}
            className="px-5 py-2 bg-primary text-white font-semibold rounded-full text-xs shadow-xs hover:brightness-105 active:scale-95 transition-all shrink-0 cursor-pointer"
          >
            Launch Comparison Engine
          </button>
        </div>
      </div>
    );
  }

  // ── Fund Detail View (Google Finance Single Stock/Fund View) ─────────────────
  const isNeg = fundData.change?.includes("-");
  const chartColor = isNeg ? "#c5221f" : "#006c4f";
  const chartData = chartDataMap[chartRange] || chartDataMap["1Y"];

  return (
    <div className="p-4 md:p-8 max-w-6xl mx-auto space-y-6 animate-fade-in pb-28">
      {/* Header Section */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-primary/10 text-primary uppercase tracking-wider">
              {fundData.type || "Equity Mutual Fund"}
            </span>
            <span className="text-outline-variant">•</span>
            <span className="text-xs text-on-surface-variant font-medium">
              {fundData.plan || "Direct Plan • Growth"}
            </span>
          </div>
          <h2 className="font-headline text-2xl md:text-3xl font-extrabold text-on-surface tracking-tight leading-tight">
            {fundData.name || "SBI Contra Direct Plan Growth"}
          </h2>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={onCompareClick}
            className="px-4 py-1.5 rounded-full border border-outline-variant/30 text-on-surface font-semibold hover:bg-surface-container transition-all flex items-center gap-1.5 text-xs shadow-2xs cursor-pointer"
          >
            <span className="material-symbols-outlined text-[15px]">compare_arrows</span>
            <span>Compare Scheme</span>
          </button>
        </div>
      </div>

      {/* Main NAV & Google Finance Interactive Chart Card */}
      <div className="bg-surface-container-lowest rounded-2xl p-5 md:p-6 border border-outline-variant/15 shadow-xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-baseline justify-between gap-3">
          <div>
            <span className="text-[10px] font-bold text-on-surface-variant/70 uppercase tracking-wider block">
              Net Asset Value (NAV) • {fundData.navDate || "05 Nov 2026"}
            </span>
            <div className="flex items-baseline gap-2.5 mt-0.5">
              <span className="text-3xl md:text-4xl font-extrabold font-mono text-on-surface tracking-tight">
                ₹{fundData.nav || "414.54"}
              </span>
              <span
                className={`flex items-center gap-0.5 font-bold text-xs px-2 py-0.5 rounded-full ${
                  isNeg
                    ? "text-error bg-error/10"
                    : "text-primary bg-primary/10"
                }`}
              >
                <span className="material-symbols-outlined text-[13px]">
                  {isNeg ? "arrow_downward" : "arrow_upward"}
                </span>
                {fundData.change || "+0.82%"}
              </span>
            </div>
          </div>

          {/* Timeframe Selector (Google Finance Style) */}
          <div className="flex bg-surface-container-low p-1 rounded-full gap-0.5 border border-outline-variant/15">
            {["1M", "6M", "1Y", "3Y", "5Y"].map((tf) => (
              <button
                key={tf}
                onClick={() => setChartRange(tf)}
                className={`px-3 py-1 rounded-full text-[11px] font-bold transition-all cursor-pointer ${
                  tf === chartRange
                    ? "bg-surface-container-lowest text-primary shadow-xs border border-outline-variant/20"
                    : "text-on-surface-variant/70 hover:text-on-surface"
                }`}
              >
                {tf}
              </button>
            ))}
          </div>
        </div>

        {/* SVG Chart */}
        <div className="pt-2">
          <LineChart data={chartData} color={chartColor} />
        </div>
      </div>

      {/* Key Fund Statistics Grid (Google Finance Layout) */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <StatTile
          label="Expense Ratio"
          value={fundData.expenseRatio || "0.86%"}
          sub="Direct Plan"
          mono
        />
        <StatTile
          label="Fund Size (AUM)"
          value={fundData.aum || "₹45,067 Cr"}
          sub="Total Assets"
          mono
        />
        <StatTile
          label="Minimum SIP"
          value={fundData.minInvestment || "₹500"}
          sub="Monthly Investment"
          mono
        />
        <StatTile
          label="Exit Load"
          value={fundData.exitLoad || "0.25% in 30d"}
          sub="Redemption Terms"
        />
      </div>

      {/* Risk Assessment & Objective Section */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-4">
        {/* Riskometer */}
        <div className="md:col-span-5 bg-surface-container-lowest p-5 rounded-2xl border border-outline-variant/15 shadow-xs flex flex-col justify-between">
          <span className="text-[10px] font-bold text-on-surface-variant/70 uppercase tracking-wider block mb-2">
            SEBI Riskometer
          </span>
          <RiskMeter risk={fundData.risk || "Moderately High"} />
          <p className="text-[11px] text-on-surface-variant/70 text-center mt-3">
            Principal investment will be at Moderately High risk according to SEBI mutual fund guidelines.
          </p>
        </div>

        {/* Investment Objective */}
        <div className="md:col-span-7 bg-surface-container-lowest p-5 rounded-2xl border border-outline-variant/15 shadow-xs flex flex-col justify-between">
          <div>
            <span className="text-[10px] font-bold text-on-surface-variant/70 uppercase tracking-wider block mb-2">
              Investment Objective & Strategy
            </span>
            <p className="text-xs text-on-surface-variant/90 leading-relaxed">
              {fundData.desc ||
                "The scheme seeks to provide the investor with long-term capital appreciation by investing in a diversified portfolio of equity and equity-related securities following a contrarian investment strategy across recognized sectors."}
            </p>
          </div>

          <div className="mt-4 pt-3 border-t border-outline-variant/10 flex items-center justify-between text-xs font-semibold">
            <span className="text-on-surface-variant/70">Benchmark Index</span>
            <span className="font-bold text-on-surface">BSE 500 Total Return Index</span>
          </div>
        </div>
      </div>
    </div>
  );
}
