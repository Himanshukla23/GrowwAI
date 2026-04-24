"use client";

import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

// ── "See more / See less" expandable text block ───────────────────────────────
const COLLAPSE_THRESHOLD = 220; // chars before truncating

function ExpandableBlock({ children, className, animStyle }) {
  const [expanded, setExpanded] = useState(false);
  const text = typeof children === "string" ? children : "";
  const isLong = text.length > COLLAPSE_THRESHOLD;
  const display = !isLong || expanded ? text : text.slice(0, COLLAPSE_THRESHOLD) + "…";

  return (
    <div
      className={className}
      style={animStyle}
    >
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          strong: ({ node, ...props }) => (
            <span
              className="inline-flex items-center px-1 py-0.5 rounded bg-primary/10 text-primary font-bold text-[11px]"
              {...props}
            />
          ),
          p: ({ children }) => <p className="mb-1 last:mb-0">{children}</p>,
          ul: ({ children }) => (
            <ul className="list-disc list-inside space-y-0.5 mt-1">{children}</ul>
          ),
          li: ({ children }) => (
            <li className="text-xs text-on-surface leading-snug">{children}</li>
          ),
        }}
      >
        {display}
      </ReactMarkdown>

      {isLong && (
        <button
          onClick={() => setExpanded((v) => !v)}
          className="mt-2 flex items-center gap-1 text-[11px] font-bold text-primary hover:underline focus:outline-none"
        >
          <span className="material-symbols-outlined text-[14px]">
            {expanded ? "expand_less" : "expand_more"}
          </span>
          {expanded ? "See less" : "See more"}
        </button>
      )}
    </div>
  );
}

// ── Financial figure highlighter ──────────────────────────────────────────────
function HighlightedText({ children }) {
  if (typeof children !== "string") return children;
  const parts = children.split(
    /(\d+(?:\.\d+)?%|₹\s*\d+(?:\.\d+)?(?:,\d+)*|Rs\.\s*\d+(?:\.\d+)?(?:,\d+)*)/g
  );
  return (
    <>
      {parts.map((part, i) => {
        const isMatch =
          /(\d+(?:\.\d+)?%|₹\s*\d+(?:\.\d+)?|Rs\.\s*\d+)/.test(part);
        return isMatch ? (
          <span
            key={i}
            className="font-extrabold text-primary px-1 py-0.5 bg-primary/5 rounded border border-primary/10 mx-0.5 text-[11px]"
          >
            {part}
          </span>
        ) : (
          part
        );
      })}
    </>
  );
}

export default function AssistantPanel({
  messages,
  isLoading,
  query,
  setQuery,
  handleSend,
  isInitializing,
}) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const onKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend(e);
    }
  };

  return (
    <section className="fixed right-0 top-0 bottom-0 w-[384px] bg-white shadow-2xl flex flex-col z-50">
      {/* ── Header ── */}
      <header className="px-5 py-4 border-b border-surface-container-low flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
          <span
            className="material-symbols-outlined text-primary text-2xl"
            style={{ fontVariationSettings: "'FILL' 1" }}
          >
            smart_toy
          </span>
        </div>
        <div>
          <h2 className="text-on-surface font-headline font-bold text-base leading-tight">
            Groww Assist
          </h2>
          <p className="text-on-surface-variant text-xs font-medium">AI Financial Guide</p>
        </div>
      </header>

      {/* ── Messages ── */}
      <div className="flex-1 overflow-y-auto px-4 py-5 space-y-4 custom-scrollbar bg-surface/30">
        {/* Empty state */}
        {messages.length === 0 && !isLoading && (
          <div className="h-full flex flex-col items-center justify-center text-center px-4 space-y-3">
            <div className="w-14 h-14 rounded-full bg-surface-container flex items-center justify-center">
              <span
                className="material-symbols-outlined text-2xl text-primary"
                style={{ fontVariationSettings: "'FILL' 1" }}
              >
                psychology
              </span>
            </div>
            <h3 className="font-headline font-semibold text-base text-on-surface">
              How can I help you?
            </h3>
            <p className="text-xs text-on-surface-variant max-w-[220px] leading-relaxed">
              Ask me about market trends, compare mutual funds, or check fund details.
            </p>
            <div className="flex flex-col gap-2 mt-3 w-full">
              {[
                "What is the expense ratio of Nippon India Small Cap?",
                "How has Quant Small Cap performed recently?",
                "What are the top holdings of SBI Bluechip Fund?",
              ].map((suggestion, idx) => (
                <button
                  key={idx}
                  disabled={isInitializing}
                  onClick={(e) => handleSend(e, suggestion)}
                  className={`px-4 py-2.5 text-xs text-left bg-surface-container-high/40 rounded-xl text-on-surface font-medium transition-colors border border-outline-variant/10 ${
                    isInitializing ? "opacity-50 cursor-not-allowed" : "hover:bg-surface-container-high/80"
                  }`}
                >
                  "{suggestion}"
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Message list */}
        {messages.map((msg, index) => {
          // ── User bubble ──────────────────────────────────────────────────
          if (msg.role === "user") {
            return (
              <div key={index} className="flex flex-col items-end">
                <div className="bg-primary-container text-on-primary-container font-medium px-4 py-3 rounded-2xl rounded-tr-sm max-w-[88%] text-xs shadow-sm whitespace-pre-wrap leading-relaxed">
                  {msg.content}
                </div>
                <span className="text-[10px] text-on-surface-variant mt-1 font-medium">
                  {msg.timestamp
                    ? new Date(msg.timestamp).toLocaleTimeString([], {
                        hour: "2-digit",
                        minute: "2-digit",
                      })
                    : ""}
                </span>
              </div>
            );
          }

          // ── Assistant bubble ─────────────────────────────────────────────
          const isError = msg.error || msg.violations?.length > 0;

          // Split into logical blocks by paragraph / double-newline
          const rawBlocks = msg.content
            ? msg.content
                .split(/\n{2,}/)
                .map((b) => b.trim())
                .filter(Boolean)
            : [msg.content || ""];

          return (
            <div key={index} className="flex flex-col items-start">
              {isError ? (
                <div className="bg-error-container text-on-error-container px-4 py-3 rounded-2xl rounded-tl-sm text-xs leading-relaxed shadow-sm max-w-[90%]">
                  {msg.content}
                </div>
              ) : (
                <div className="flex flex-col gap-2 w-full max-w-[92%]">
                  {rawBlocks.map((block, i) => (
                    <ExpandableBlock
                      key={i}
                      className={`bg-surface-variant text-on-surface px-4 py-3 ${
                        i === 0 ? "rounded-2xl rounded-tl-sm" : "rounded-2xl"
                      } text-xs leading-relaxed shadow-sm animate-slide-up`}
                      animStyle={{
                        animationDelay: `${i * 100}ms`,
                        animationFillMode: "both",
                      }}
                    >
                      {block}
                    </ExpandableBlock>
                  ))}
                </div>
              )}

              {/* Citation button */}
              {msg.citation_url && !isError && (
                <div className="mt-1.5 animate-fade-in">
                  <button
                    onClick={() => window.open(msg.citation_url, "_blank")}
                    className="flex items-center gap-1.5 px-3 py-1.5 bg-primary/10 text-primary border border-primary/20 rounded-full text-[11px] font-bold hover:bg-primary hover:text-white transition-all shadow-sm"
                  >
                    <span className="material-symbols-outlined text-[13px]">description</span>
                    View Source Document
                  </button>
                </div>
              )}

              <span className="text-[10px] text-on-surface-variant mt-1 ml-0.5 font-medium">
                Groww AI •{" "}
                {msg.timestamp
                  ? new Date(msg.timestamp).toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    })
                  : ""}
              </span>
            </div>
          );
        })}

        {/* Typing indicator */}
        {isLoading && (
          <div className="flex items-center gap-2 text-on-surface-variant/60 ml-1">
            <span className="material-symbols-outlined animate-spin text-primary text-base">sync</span>
            <span className="text-xs font-medium animate-pulse">Analyzing...</span>
          </div>
        )}

        <div ref={bottomRef} className="h-2" />
      </div>

      {/* ── RAG compliance badge ── */}
      {messages.length > 0 && !isLoading && (
        <div className="px-5 py-2 flex justify-center bg-surface-container-low border-t border-surface-container">
          <span className="text-[10px] text-on-surface-variant font-bold uppercase tracking-[2px]">
            RAG Compliant · Source: Groww Direct
          </span>
        </div>
      )}

      {/* ── Input area ── */}
      <footer className="p-4 bg-white/80 backdrop-blur-xl border-t border-surface-container-low pb-6">
        <form onSubmit={handleSend} className="relative">
          <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
            <span className="material-symbols-outlined text-on-surface-variant text-lg">search</span>
          </div>
          <input
            autoFocus
            disabled={isInitializing || isLoading}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={onKeyDown}
            className={`w-full bg-surface-container-low border-none rounded-xl py-3 pl-10 pr-12 text-xs focus:ring-2 focus:ring-primary/30 transition-all placeholder:text-on-surface-variant/50 outline-none ${
              isInitializing ? "animate-pulse" : ""
            }`}
            placeholder={isInitializing ? "AI engine waking up..." : "Ask about any fund…"}
            type="text"
          />
          <button
            type="submit"
            disabled={!query.trim() || isInitializing || isLoading}
            className="absolute inset-y-1.5 right-1.5 px-3 bg-primary text-white rounded-lg flex items-center justify-center hover:scale-[1.02] active:scale-[0.98] transition-transform disabled:opacity-40 disabled:hover:scale-100"
          >
            {isInitializing ? (
               <span className="material-symbols-outlined text-base animate-spin">sync</span>
            ) : (
              <span className="material-symbols-outlined text-base" style={{ fontVariationSettings: "'FILL' 1" }}>
                send
              </span>
            )}
          </button>
        </form>
        <p className="mt-2 text-center text-[10px] text-on-surface-variant/60 italic">
          AI responses may occasionally be inaccurate.
        </p>
      </footer>
    </section>
  );
}
