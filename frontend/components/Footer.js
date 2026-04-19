"use client";

export default function Footer() {
  return (
    <footer className="bg-surface-container-low border-t border-outline-variant/8 py-2.5 px-8 flex justify-between items-center z-50">
      <div className="flex items-center gap-3">
        <div className="w-5 h-5 rounded-md primary-gradient flex items-center justify-center">
          <span className="material-symbols-outlined text-white text-[10px]" style={{fontVariationSettings: "'FILL' 1"}}>auto_awesome</span>
        </div>
        <p className="text-[10px] font-black uppercase tracking-[0.15em] text-on-surface-variant/40">
          © 2026 Groww Assist AI
        </p>
      </div>
      <div className="flex gap-6 uppercase text-[9px] font-black tracking-widest text-on-surface-variant/40">
        <a href="#" className="hover:text-primary transition-colors">Compliance</a>
        <a href="#" className="hover:text-primary transition-colors">Data Policy</a>
        <a href="#" className="hover:text-primary transition-colors">Security</a>
      </div>
    </footer>
  );
}
