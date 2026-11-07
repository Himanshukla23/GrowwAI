"use client";

import Image from "next/image";
import { useState } from "react";

export default function Navbar({
  title = "Market Overview",
  onSearch,
  isAssistantOpen,
  onToggleAssistant,
  onMobileMenuToggle,
}) {
  const [searchInput, setSearchInput] = useState("");

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (searchInput.trim() && onSearch) {
      onSearch(searchInput.trim());
    }
  };

  return (
    <header className="sticky top-0 z-40 h-16 w-full bg-surface-container-lowest/90 backdrop-blur-md border-b border-outline-variant/15 px-4 md:px-8 flex items-center justify-between transition-all">
      {/* Left: Mobile Menu + Title */}
      <div className="flex items-center gap-3 md:gap-6 flex-1 min-w-0">
        <button
          onClick={onMobileMenuToggle}
          aria-label="Open navigation menu"
          className="md:hidden p-2 rounded-full text-on-surface-variant hover:bg-surface-container-high transition-colors"
        >
          <span className="material-symbols-outlined text-xl">menu</span>
        </button>

        <div className="flex items-center gap-2 min-w-0">
          <div className="w-2 h-2 rounded-full bg-primary animate-pulse hidden sm:block shrink-0" />
          <h2 className="text-base md:text-lg font-headline font-bold text-on-surface tracking-tight truncate">
            {title}
          </h2>
        </div>

        {/* Center Google-style Pill Search Bar */}
        <form
          onSubmit={handleSearchSubmit}
          className="relative w-full max-w-md hidden md:block group"
        >
          <span className="material-symbols-outlined absolute left-3.5 top-1/2 -translate-y-1/2 text-on-surface-variant/70 text-[18px] group-focus-within:text-primary transition-colors">
            search
          </span>
          <input
            type="text"
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder="Search funds, compare schemes, or ask anything…"
            className="w-full pl-10 pr-16 py-2 bg-surface-container-low hover:bg-surface-container focus:bg-surface-container-lowest rounded-full border border-outline-variant/20 focus:border-primary/40 focus:ring-2 focus:ring-primary/15 text-xs text-on-surface placeholder:text-on-surface-variant/60 transition-all outline-none"
          />
          <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-1 pointer-events-none">
            <kbd className="hidden lg:inline-block px-1.5 py-0.5 text-[9px] font-mono font-semibold text-on-surface-variant/60 bg-surface-container rounded border border-outline-variant/30">
              ↵ Enter
            </kbd>
          </div>
        </form>
      </div>

      {/* Right: Actions & User Avatar */}
      <div className="flex items-center gap-2 md:gap-3 shrink-0">
        {/* AI Assistant Toggle Button (Google Gemini Style) */}
        <button
          onClick={onToggleAssistant}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold transition-all ${
            isAssistantOpen
              ? "bg-primary/10 text-primary border border-primary/25 shadow-sm"
              : "bg-surface-container-low text-on-surface-variant hover:bg-surface-container hover:text-on-surface border border-outline-variant/15"
          }`}
          title="Toggle AI Guide panel"
        >
          <span
            className="material-symbols-outlined text-[16px] text-primary"
            style={{ fontVariationSettings: "'FILL' 1" }}
          >
            auto_awesome
          </span>
          <span className="hidden sm:inline">AI Guide</span>
        </button>

        {/* Notifications */}
        <button
          aria-label="Notifications"
          className="p-2 rounded-full text-on-surface-variant hover:bg-surface-container-high transition-colors relative"
        >
          <span className="material-symbols-outlined text-[20px]">notifications</span>
          <span className="absolute top-2 right-2 w-2 h-2 rounded-full bg-primary border-2 border-surface-container-lowest" />
        </button>

        {/* User Account Avatar (Google Style) */}
        <div className="flex items-center gap-2 pl-1 border-l border-outline-variant/20 ml-1">
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-primary to-primary-container p-0.5 shadow-sm cursor-pointer hover:scale-105 transition-transform">
            <div className="w-full h-full rounded-full bg-surface-container-lowest flex items-center justify-center font-headline font-bold text-xs text-primary">
              G
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
