"use client";

export default function ComparisonWorkspace({ comparisonData }) {
  // Demo mock data if none is provided via backend
  const data = comparisonData && comparisonData.funds ? comparisonData : {
    funds: [
      {
        name: "SBI Gold Fund",
        nav: "18.42",
        change: "+0.82%",
        expenseRatio: "0.12%",
        risk: "Moderate",
        minInvestment: "₹5,000",
        returns3Y: "11.4%",
        color: "primary",
        hex: "#006C4F",
        type: "Gold Fund",
        desc: "Stable asset-backed investment focusing on physical gold and gold ETFs."
      },
      {
        name: "HDFC Mid Cap Opportunities",
        nav: "142.18",
        change: "-1.24%",
        expenseRatio: "0.76%",
        risk: "Very High",
        minInvestment: "₹100",
        returns3Y: "34.2%",
        color: "orange-600",
        hex: "#8B4513",
        type: "Mid Cap",
        desc: "High-growth strategy targeting medium-sized companies with strong fundamentals."
      }
    ],
    insight: "While HDFC Mid Cap shows significantly higher returns, it comes with a Very High risk profile. For a balanced portfolio, SBI Gold acts as a crucial hedge against market volatility, despite lower absolute returns."
  };

  const fundA = data.funds[0] || {};
  const fundB = data.funds[1] || {};

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 animate-fade-in bg-background min-h-full pb-24">
      {/* Header Section */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <nav className="flex items-center gap-2 text-xs font-medium text-on-surface-variant mb-2">
            <span>Workspace</span>
            <span className="material-symbols-outlined text-[14px]">chevron_right</span>
            <span>Comparison Workspace</span>
          </nav>
          <h3 className="font-headline text-display-lg font-bold text-on-surface tracking-tight leading-none text-4xl">Comparison Result</h3>
        </div>
        <div className="flex items-center gap-3">
          <button className="px-6 py-3 bg-surface-container-highest flex items-center gap-2 hover:bg-surface-container-high transition-colors text-primary font-semibold rounded-full shadow-sm">
             <span className="material-symbols-outlined text-sm">share</span>
             Share
          </button>
          <button className="px-8 py-3 bg-gradient-to-r from-primary to-primary-container text-white font-semibold rounded-full shadow-lg shadow-primary/20 hover:scale-[1.02] active:scale-95 transition-all">
             Save Comparison
          </button>
        </div>
      </div>

      {/* Main Comparison Bento Grid */}
      <div className="grid grid-cols-12 gap-6">
        
        {/* Fund Cards (1st Column) */}
        <div className="col-span-12 lg:col-span-4 flex flex-col gap-6">
          {/* Fund A Card */}
          <div className={`p-6 bg-surface-container-lowest rounded-2xl border-l-4 border-primary shadow-sm border-t border-r border-b border-outline-variant/10 hover:shadow-md transition-shadow`}>
            <div className="flex justify-between items-start mb-4">
              <div className="w-12 h-12 rounded-xl bg-surface-container flex items-center justify-center">
                <span className={`material-symbols-outlined text-primary`} style={{fontVariationSettings: "'FILL' 1"}}>payments</span>
              </div>
              <span className={`px-3 py-1 bg-primary/10 text-primary rounded-full text-[10px] font-bold uppercase tracking-wider`}>
                {fundA.type || "Fund"}
              </span>
            </div>
            <h4 className="font-headline text-xl font-bold mb-1">{fundA.name}</h4>
            <div className="flex items-baseline gap-2 mb-4">
              <span className="text-2xl font-bold">₹{fundA.nav}</span>
              <span className={`${fundA.change?.includes('-') ? 'text-error' : 'text-primary'} font-semibold text-sm flex items-center`}>
                <span className="material-symbols-outlined text-sm">{fundA.change?.includes('-') ? 'arrow_drop_down' : 'arrow_drop_up'}</span>
                {fundA.change}
              </span>
            </div>
            <div className="pt-4 border-t border-surface-container">
              <p className="text-xs text-on-surface-variant leading-relaxed">{fundA.desc || "Analysis target for your portfolio."}</p>
            </div>
          </div>

          {/* Fund B Card */}
          <div className="p-6 bg-surface-container-lowest rounded-2xl border-l-4 border-[#8B4513] shadow-sm border-t border-r border-b border-outline-variant/10 hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start mb-4">
              <div className="w-12 h-12 rounded-xl bg-surface-container flex items-center justify-center">
                <span className="material-symbols-outlined text-[#8B4513]" style={{fontVariationSettings: "'FILL' 1"}}>analytics</span>
              </div>
              <span className="px-3 py-1 bg-[#8B4513]/10 text-[#8B4513] rounded-full text-[10px] font-bold uppercase tracking-wider">
                {fundB.type || "Fund"}
              </span>
            </div>
            <h4 className="font-headline text-xl font-bold mb-1">{fundB.name}</h4>
            <div className="flex items-baseline gap-2 mb-4">
              <span className="text-2xl font-bold">₹{fundB.nav}</span>
              <span className={`${fundB.change?.includes('-') ? 'text-error' : 'text-primary'} font-semibold text-sm flex items-center`}>
                <span className="material-symbols-outlined text-sm">{fundB.change?.includes('-') ? 'arrow_drop_down' : 'arrow_drop_up'}</span>
                {fundB.change}
              </span>
            </div>
            <div className="pt-4 border-t border-surface-container">
              <p className="text-xs text-on-surface-variant leading-relaxed">{fundB.desc || "Analysis target for your portfolio."}</p>
            </div>
          </div>
        </div>

        {/* Performance Chart Card */}
        <div className="col-span-12 lg:col-span-8 bg-surface-container-lowest rounded-2xl p-8 relative overflow-hidden group shadow-[0px_8px_24px_rgba(24,27,38,0.04)] border border-outline-variant/10">
          <div className="flex justify-between items-center mb-8">
            <div>
              <h4 className="font-headline text-xl font-bold text-on-surface">Performance Over Time</h4>
              <p className="text-sm text-on-surface-variant mt-1">Relative growth normalized to base 100</p>
            </div>
            <div className="flex gap-4 bg-surface-container-low px-4 py-2 rounded-full border border-surface-variant/30">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-primary mb-[1px]"></div>
                <span className="text-xs font-semibold text-on-surface">{fundA.name?.substring(0, 10)}...</span>
              </div>
              <div className="w-px h-4 bg-outline-variant/30 mt-[2px]"></div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-[#8B4513] mb-[1px]"></div>
                <span className="text-xs font-semibold text-on-surface">{fundB.name?.substring(0, 10)}...</span>
              </div>
            </div>
          </div>

          {/* SVG Chart */}
          <div className="h-64 w-full relative">
            <svg className="w-full h-full overflow-visible" preserveAspectRatio="none" viewBox="0 0 800 200">
              {/* Grid Lines */}
              <line stroke="#ecedfd" strokeWidth="1" x1="0" x2="800" y1="0" y2="0"></line>
              <line stroke="#ecedfd" strokeWidth="1" x1="0" x2="800" y1="50" y2="50"></line>
              <line stroke="#ecedfd" strokeWidth="1" x1="0" x2="800" y1="100" y2="100"></line>
              <line stroke="#ecedfd" strokeWidth="1" x1="0" x2="800" y1="150" y2="150"></line>
              <line stroke="#ecedfd" strokeWidth="1" x1="0" x2="800" y1="200" y2="200"></line>
              <line stroke="#ecedfd" strokeWidth="1" strokeDasharray="4 4" x1="500" x2="500" y1="0" y2="200" className="opacity-0 group-hover:opacity-100 transition-opacity"></line>
              
              {/* Fund A Path */}
              <path d="M0 160 Q 100 140, 200 155 T 400 145 T 600 130 T 800 110" fill="none" stroke="#00D09C" strokeWidth="4"></path>
              {/* Fund B Path */}
              <path d="M0 160 Q 150 180, 300 120 T 500 80 T 700 100 T 800 60" fill="none" stroke="#8B4513" strokeWidth="4"></path>
              
              {/* Data Point (Hover Effect Concept) */}
              <circle className="shadow-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300" cx="500" cy="80" fill="#8B4513" r="6" stroke="#fff" strokeWidth="2"></circle>
              <circle className="shadow-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300" cx="500" cy="138" fill="#00D09C" r="6" stroke="#fff" strokeWidth="2"></circle>
            </svg>
            
            {/* Tooltip Overlay */}
            <div className="absolute top-4 left-[50%] -translate-x-1/2 p-4 bg-inverse-surface text-inverse-on-surface rounded-xl shadow-2xl scale-0 group-hover:scale-100 transition-transform duration-300 origin-bottom z-10 pointer-events-none">
              <p className="text-[10px] uppercase font-bold text-surface-container-high tracking-widest mb-2 border-b border-white/10 pb-1">Aug 2024 Performance</p>
              <div className="space-y-2.5 mt-1">
                <div className="flex justify-between gap-10 items-center">
                  <span className="text-xs font-medium flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-[#8B4513]"></span> 
                    {fundB.name?.substring(0, 10)}...
                  </span>
                  <span className="text-xs font-bold text-[#8df3c9]">+24.5%</span>
                </div>
                <div className="flex justify-between gap-10 items-center">
                  <span className="text-xs font-medium flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-primary-container"></span> 
                    {fundA.name?.substring(0, 10)}...
                  </span>
                  <span className="text-xs font-bold text-surface-container-high">+11.2%</span>
                </div>
              </div>
              <div className="absolute -bottom-1.5 left-1/2 -translate-x-1/2 w-3 h-3 bg-inverse-surface rotate-45"></div>
            </div>
          </div>
          
          {/* Time Scale Labels */}
          <div className="flex justify-between mt-4 text-[10px] font-bold text-on-surface-variant uppercase tracking-widest px-2">
            <span>Jan</span>
            <span>Mar</span>
            <span>May</span>
            <span>Jul</span>
            <span>Sep</span>
            <span>Nov</span>
          </div>
        </div>

        {/* Metrics Table Card (Full Width) */}
        <div className="col-span-12 bg-surface-container-lowest rounded-2xl overflow-hidden shadow-sm border border-outline-variant/10">
          <div className="p-6 bg-surface-container-low border-b border-outline-variant/20">
            <h4 className="font-headline text-lg font-bold text-on-surface">Key Performance Metrics</h4>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="text-[10px] uppercase tracking-widest text-on-surface-variant font-bold bg-surface-container-lowest border-b border-surface-container shadow-[0px_4px_12px_rgba(0,0,0,0.01)]">
                  <th className="px-8 py-5 w-1/3">Key Metric</th>
                  <th className="px-8 py-5">
                    <span className="flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-primary"></span>
                      {fundA.name}
                    </span>
                  </th>
                  <th className="px-8 py-5">
                     <span className="flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-[#8B4513]"></span>
                      {fundB.name}
                    </span>
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-surface-container">
                <tr className="hover:bg-surface-container-low transition-colors group">
                  <td className="px-8 py-5">
                    <div className="flex flex-col">
                      <span className="font-bold text-sm text-on-surface group-hover:text-primary transition-colors">Expense Ratio</span>
                      <span className="text-[11px] text-on-surface-variant/70 mt-1">Annual management cost</span>
                    </div>
                  </td>
                  <td className="px-8 py-5">
                    <span className="font-bold text-primary bg-primary/10 px-2 py-1 rounded text-sm">{fundA.expenseRatio}</span>
                  </td>
                  <td className="px-8 py-5">
                    <span className="font-bold text-on-surface text-sm">{fundB.expenseRatio}</span>
                  </td>
                </tr>
                <tr className="hover:bg-surface-container-low transition-colors group">
                  <td className="px-8 py-5">
                    <div className="flex flex-col">
                      <span className="font-bold text-sm text-on-surface group-hover:text-primary transition-colors">Risk Grade</span>
                      <span className="text-[11px] text-on-surface-variant/70 mt-1">Standard volatility rating</span>
                    </div>
                  </td>
                  <td className="px-8 py-5">
                    <span className={`px-3 py-1 ${fundA.risk?.toLowerCase().includes("high") ? "bg-error/10 text-error" : "bg-primary-container/20 text-on-primary-container"} rounded-full text-[10px] font-bold uppercase tracking-wider`}>
                      {fundA.risk}
                    </span>
                  </td>
                  <td className="px-8 py-5">
                    <span className={`px-3 py-1 ${fundB.risk?.toLowerCase().includes("high") ? "bg-error/10 text-error" : "bg-primary-container/20 text-on-primary-container"} rounded-full text-[10px] font-bold uppercase tracking-wider`}>
                      {fundB.risk}
                    </span>
                  </td>
                </tr>
                <tr className="hover:bg-surface-container-low transition-colors group">
                  <td className="px-8 py-5">
                    <div className="flex flex-col">
                      <span className="font-bold text-sm text-on-surface group-hover:text-primary transition-colors">Min Investment</span>
                      <span className="text-[11px] text-on-surface-variant/70 mt-1">Initial lump-sum amount</span>
                    </div>
                  </td>
                  <td className="px-8 py-5">
                    <span className="font-bold text-on-surface text-sm">{fundA.minInvestment}</span>
                  </td>
                  <td className="px-8 py-5">
                    <span className="font-bold text-on-surface text-sm">{fundB.minInvestment}</span>
                  </td>
                </tr>
                <tr className="hover:bg-surface-container-low transition-colors group">
                  <td className="px-8 py-5">
                    <div className="flex flex-col">
                      <span className="font-bold text-sm text-on-surface group-hover:text-primary transition-colors">3Y Returns</span>
                      <span className="text-[11px] text-on-surface-variant/70 mt-1">Compound annual growth</span>
                    </div>
                  </td>
                  <td className="px-8 py-5">
                    <span className="font-bold text-lg text-on-surface">{fundA.returns3Y}</span>
                  </td>
                  <td className="px-8 py-5">
                    <span className="font-bold text-lg text-[#8B4513]">{fundB.returns3Y}</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* AI Insight Card */}
        <div className="col-span-12 lg:col-span-6 bg-primary-container/[0.03] border border-primary-container/20 rounded-2xl p-8 relative overflow-hidden">
          <div className="absolute top-0 right-0 p-8 opacity-5">
             <span className="material-symbols-outlined text-9xl text-primary">auto_awesome</span>
          </div>
          <div className="flex items-center gap-3 mb-6 relative z-10">
            <div className="w-10 h-10 rounded-full bg-primary-container/30 flex items-center justify-center">
              <span className="material-symbols-outlined text-primary" style={{fontVariationSettings: "'FILL' 1"}}>auto_awesome</span>
            </div>
            <h4 className="font-headline text-xl font-bold text-on-surface">AI Insight</h4>
          </div>
          <p className="text-on-surface-variant leading-relaxed text-sm mb-6 relative z-10">
            {data.insight}
          </p>
          <div className="flex gap-4 relative z-10">
            <div className="flex-1 p-4 bg-white/60 backdrop-blur-md rounded-xl border border-white/50 shadow-sm">
              <span className="text-[10px] uppercase font-bold text-primary block mb-1 tracking-widest">Efficiency King</span>
              <span className="text-sm font-bold text-on-surface">{fundA.name}</span>
            </div>
            <div className="flex-1 p-4 bg-white/60 backdrop-blur-md rounded-xl border border-white/50 shadow-sm">
              <span className="text-[10px] uppercase font-bold text-[#8B4513] block mb-1 tracking-widest">Growth Leader</span>
              <span className="text-sm font-bold text-on-surface">{fundB.name}</span>
            </div>
          </div>
        </div>

        {/* CTA Card */}
        <div className="col-span-12 lg:col-span-6 rounded-2xl overflow-hidden relative group border border-outline-variant/10 shadow-sm">
          <div className="absolute inset-0 bg-gradient-to-br from-primary to-primary-container mix-blend-multiply opacity-90 group-hover:opacity-100 transition-opacity"></div>
          
          <div className="absolute -left-10 -bottom-10 w-40 h-40 bg-white/20 rounded-full blur-2xl"></div>
          <div className="absolute right-10 top-10 w-20 h-20 bg-black/10 rounded-full blur-xl"></div>
          
          <div className="relative h-full p-8 flex flex-col justify-center text-white text-on-primary">
            <h4 className="font-headline text-3xl font-extrabold mb-3">Ready to invest?</h4>
            <p className="text-white/80 text-sm mb-8 max-w-sm leading-relaxed">Consider balancing your risk profile. Start a SIP in both funds to optimize long-term growth vs volatility.</p>
            <div className="flex gap-4 mt-auto">
              <button className="px-6 py-2.5 bg-white text-primary font-bold rounded-full text-sm shadow-lg shadow-black/10 hover:scale-105 active:scale-95 transition-all">Start SIP Now</button>
              <button className="px-6 py-2.5 bg-white/20 backdrop-blur-md border border-white/30 text-white font-bold rounded-full text-sm hover:bg-white/30 transition-colors">Add to Watchlist</button>
            </div>
          </div>
        </div>
      </div>
      
       {/* Persistent Bottom Disclaimer */}
       <footer className="fixed bottom-0 left-0 md:left-[280px] right-0 xl:right-[384px] bg-surface/90 backdrop-blur-lg border-t border-outline-variant/20 p-4 shrink-0 z-40 hidden md:block">
         <div className="max-w-4xl mx-auto flex items-start gap-3 justify-center text-center">
            <span className="material-symbols-outlined text-on-surface-variant opacity-70 text-sm mt-0.5">info</span>
            <p className="text-[10px] sm:text-xs text-on-surface-variant font-medium leading-relaxed max-w-2xl opacity-80">
              Comparative analytics are generated using RAG analysis. Mutual Fund investments are subject to market risks, read all scheme related documents carefully. Past performance does not guarantee future returns.
            </p>
         </div>
      </footer>
    </div>
  );
}
