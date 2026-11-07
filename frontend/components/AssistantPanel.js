"use client";

import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

// ── "See more / See less" expandable text block ───────────────────────────────
const COLLAPSE_THRESHOLD = 260; // chars before truncating

function ExpandableBlock({ children, className, animStyle }) {
  const [expanded, setExpanded] = useState(false);
  const text = typeof children === "string" ? children : "";
  const isLong = text.length > COLLAPSE_THRESHOLD;
  const display = !isLong || expanded ? text : text.slice(0, COLLAPSE_THRESHOLD) + "…";

  return (
    <div className={className} style={animStyle}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          strong: ({ node, ...props }) => (
            <span
              className="inline-flex items-center px-1.5 py-0.5 rounded-md bg-primary/10 text-primary font-bold text-[11px] mx-0.5"
              {...props}
            />
          ),
          p: ({ children }) => <p className="mb-1.5 last:mb-0 leading-relaxed">{children}</p>,
          ul: ({ children }) => (
            <ul className="list-disc list-inside space-y-1 mt-1 text-xs">{children}</ul>
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
          className="mt-2 inline-flex items-center gap-1 text-[11px] font-bold text-primary hover:underline focus:outline-none cursor-pointer"
        >
          <span className="material-symbols-outlined text-[14px]">
            {expanded ? "expand_less" : "expand_more"}
          </span>
          {expanded ? "Show less" : "Read full analysis"}
        </button>
      )}
    </div>
  );
}

export default function AssistantPanel({
  messages = [],
  isLoading = false,
  query = "",
  setQuery,
  handleSend,
  isInitializing = false,
  onClose,
}) {
  const bottomRef = useRef(null);
  const [copiedIndex, setCopiedIndex] = useState(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const onKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend(e);
    }
  };

  const handleCopy = (text, idx) => {
    if (navigator?.clipboard) {
      navigator.clipboard.writeText(text);
      setCopiedIndex(idx);
      setTimeout(() => setCopiedIndex(null), 2000);
    }
  };

  const PROMPT_SUGGESTIONS = [
    {
      text: "Compare SBI Contra Fund and Nippon India Large Cap",
      icon: "compare_arrows",
      tag: "Comparison",
    },
    {
      text: "Compare HDFC Mid Cap Fund and SBI Small Cap Fund",
      icon: "show_chart",
      tag: "Growth",
    },
    {
      text: "What is the expense ratio and NAV of SBI Contra Fund?",
      icon: "percent",
      tag: "Fact Check",
    },
    {
      text: "What is the NAV of ICICI Prudential Large Cap Fund?",
      icon: "account_balance",
      tag: "NAV",
    },
  ];

  return (
    <section className="h-full w-full bg-surface-container-lowest border-l border-outline-variant/15 flex flex-col shadow-xl">
      {/* ── Google Gemini-style Header ── */}
      <header className="px-5 py-4 border-b border-outline-variant/15 flex items-center justify-between bg-surface-container-lowest/80 backdrop-blur-md shrink-0">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-primary to-primary-container flex items-center justify-center text-white shadow-xs">
            <span
              className="material-symbols-outlined text-[18px]"
              style={{ fontVariationSettings: "'FILL' 1" }}
            >
              auto_awesome
            </span>
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <h2 className="text-on-surface font-headline font-bold text-sm leading-none tracking-tight">
                Groww Assist AI
              </h2>
              <span className="w-2 h-2 rounded-full bg-primary" />
            </div>
            <p className="text-[11px] text-on-surface-variant font-medium mt-0.5">
              Grounded Gemini Engine
            </p>
          </div>
        </div>

        {onClose && (
          <button
            onClick={onClose}
            aria-label="Close assistant"
            className="p-1.5 rounded-full text-on-surface-variant hover:bg-surface-container-high transition-colors"
          >
            <span className="material-symbols-outlined text-lg">close</span>
          </button>
        )}
      </header>

      {/* ── Message Area ── */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4 custom-scrollbar bg-surface-container-low/30">
        {/* Empty state: Google Gemini style prompt cards */}
        {messages.length === 0 && !isLoading && (
          <div className="h-full flex flex-col items-center justify-center text-center px-2 py-6 space-y-4">
            <div className="w-12 h-12 rounded-2xl bg-primary/10 text-primary flex items-center justify-center shadow-xs">
              <span
                className="material-symbols-outlined text-2xl"
                style={{ fontVariationSettings: "'FILL' 1" }}
              >
                psychology
              </span>
            </div>
            <div>
              <h3 className="font-headline font-bold text-sm text-on-surface">
                What would you like to analyze today?
              </h3>
              <p className="text-xs text-on-surface-variant/80 max-w-[260px] mx-auto mt-1 leading-relaxed">
                Compare mutual funds side-by-side, verify live NAVs, or audit expense ratios.
              </p>
            </div>

            <div className="flex flex-col gap-2 w-full pt-2">
              {PROMPT_SUGGESTIONS.map((item, idx) => (
                <button
                  key={idx}
                  disabled={isInitializing}
                  onClick={(e) => handleSend(e, item.text)}
                  className={`group p-3 text-left bg-surface-container-lowest rounded-xl border border-outline-variant/15 hover:border-primary/40 hover:shadow-xs transition-all flex items-start gap-2.5 ${
                    isInitializing
                      ? "opacity-50 cursor-not-allowed"
                      : "cursor-pointer"
                  }`}
                >
                  <div className="w-6 h-6 rounded-lg bg-surface-container text-on-surface-variant group-hover:bg-primary/10 group-hover:text-primary flex items-center justify-center shrink-0 transition-colors mt-0.5">
                    <span className="material-symbols-outlined text-[14px]">
                      {item.icon}
                    </span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-semibold text-on-surface group-hover:text-primary transition-colors leading-snug">
                      {item.text}
                    </p>
                    <span className="text-[10px] text-on-surface-variant/70 font-medium">
                      {item.tag}
                    </span>
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Message list */}
        {messages.map((msg, index) => {
          if (msg.role === "user") {
            return (
              <div key={index} className="flex flex-col items-end animate-slide-up">
                <div className="bg-gradient-to-r from-primary to-primary-container text-white font-medium px-4 py-2.5 rounded-2xl rounded-tr-xs max-w-[88%] text-xs shadow-xs leading-relaxed">
                  {msg.content}
                </div>
                <span className="text-[10px] text-on-surface-variant/60 mt-1 font-medium pr-1">
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

          const isError =
            msg.error ||
            msg.violations?.length > 0 ||
            (typeof msg.content === "string" &&
              (msg.content.includes("internal generation error") ||
                msg.content.includes("error occurred")));

          const rawBlocks = msg.content
            ? msg.content
                .split(/\n{2,}/)
                .map((b) => b.trim())
                .filter(Boolean)
            : [msg.content || ""];

          return (
            <div key={index} className="flex flex-col items-start animate-fade-in group/msg">
              <div className="flex items-center gap-1.5 mb-1 ml-0.5">
                <div className="w-4 h-4 rounded-full bg-primary/10 text-primary flex items-center justify-center">
                  <span className="material-symbols-outlined text-[11px]" style={{ fontVariationSettings: "'FILL' 1" }}>
                    auto_awesome
                  </span>
                </div>
                <span className="text-[11px] font-bold text-on-surface">Groww AI</span>
                <span className="text-[10px] text-on-surface-variant/60">
                  {msg.timestamp
                    ? new Date(msg.timestamp).toLocaleTimeString([], {
                        hour: "2-digit",
                        minute: "2-digit",
                      })
                    : ""}
                </span>
              </div>

              {isError ? (
                <div className="bg-error-container text-on-error-container px-4 py-3 rounded-2xl rounded-tl-xs text-xs leading-relaxed shadow-xs max-w-[92%] border border-error/20">
                  {msg.content}
                </div>
              ) : (
                <div className="flex flex-col gap-2 w-full max-w-[94%]">
                  {rawBlocks.map((block, i) => (
                    <ExpandableBlock
                      key={i}
                      className={`bg-surface-container-lowest text-on-surface px-4 py-3 border border-outline-variant/15 ${
                        i === 0 ? "rounded-2xl rounded-tl-xs" : "rounded-2xl"
                      } text-xs leading-relaxed shadow-xs`}
                      animStyle={{
                        animationDelay: `${i * 80}ms`,
                        animationFillMode: "both",
                      }}
                    >
                      {block}
                    </ExpandableBlock>
                  ))}
                </div>
              )}

              {/* Action Buttons: Citation + Copy */}
              <div className="flex items-center gap-2 mt-2 ml-1">
                {msg.citation_url && !isError && (
                  <button
                    onClick={() => window.open(msg.citation_url, "_blank")}
                    className="flex items-center gap-1.5 px-3 py-1 bg-surface-container hover:bg-primary/10 text-primary border border-outline-variant/20 rounded-full text-[11px] font-semibold transition-all shadow-2xs cursor-pointer"
                  >
                    <span className="material-symbols-outlined text-[13px]">open_in_new</span>
                    <span>Source on Groww</span>
                  </button>
                )}

                {!isError && (
                  <button
                    onClick={() => handleCopy(msg.content, index)}
                    className="flex items-center gap-1 px-2.5 py-1 text-on-surface-variant/70 hover:text-on-surface text-[11px] font-medium rounded-full hover:bg-surface-container transition-colors cursor-pointer"
                    title="Copy answer"
                  >
                    <span className="material-symbols-outlined text-[13px]">
                      {copiedIndex === index ? "check" : "content_copy"}
                    </span>
                    <span>{copiedIndex === index ? "Copied" : "Copy"}</span>
                  </button>
                )}
              </div>
            </div>
          );
        })}

        {/* Google-style pulsing dots loading state */}
        {isLoading && (
          <div className="flex items-center gap-2.5 p-3 bg-surface-container-lowest rounded-2xl border border-outline-variant/15 max-w-[200px] shadow-xs">
            <span className="material-symbols-outlined text-primary text-sm animate-spin">
              autorenew
            </span>
            <div className="flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-primary animate-bounce" style={{ animationDelay: "0ms" }} />
              <span className="w-1.5 h-1.5 rounded-full bg-primary animate-bounce" style={{ animationDelay: "150ms" }} />
              <span className="w-1.5 h-1.5 rounded-full bg-primary animate-bounce" style={{ animationDelay: "300ms" }} />
              <span className="text-xs font-semibold text-on-surface-variant ml-1.5">Analyzing...</span>
            </div>
          </div>
        )}

        <div ref={bottomRef} className="h-1" />
      </div>

      {/* ── Floating Pill Input Footer (Google Style) ── */}
      <footer className="p-3.5 bg-surface-container-lowest border-t border-outline-variant/15 shrink-0">
        <form onSubmit={handleSend} className="relative flex items-center">
          <div className="absolute left-3.5 flex items-center pointer-events-none text-on-surface-variant/70">
            <span className="material-symbols-outlined text-[18px]">search</span>
          </div>
          <input
            autoFocus
            disabled={isInitializing || isLoading}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={onKeyDown}
            className={`w-full bg-surface-container-low focus:bg-surface-container-lowest border border-outline-variant/20 focus:border-primary/40 rounded-full py-2.5 pl-10 pr-11 text-xs text-on-surface placeholder:text-on-surface-variant/60 focus:ring-2 focus:ring-primary/15 transition-all outline-none ${
              isInitializing ? "animate-pulse" : ""
            }`}
            placeholder={
              isInitializing
                ? "Connecting to RAG engine..."
                : "Ask about any mutual fund or compare…"
            }
            type="text"
          />
          <button
            type="submit"
            disabled={!query.trim() || isInitializing || isLoading}
            className="absolute right-1.5 w-7 h-7 rounded-full bg-primary text-white flex items-center justify-center hover:scale-105 active:scale-95 transition-all disabled:opacity-30 disabled:hover:scale-100 cursor-pointer shadow-xs"
            aria-label="Send query"
          >
            {isInitializing ? (
              <span className="material-symbols-outlined text-sm animate-spin">sync</span>
            ) : (
              <span
                className="material-symbols-outlined text-[15px]"
                style={{ fontVariationSettings: "'FILL' 1" }}
              >
                arrow_upward
              </span>
            )}
          </button>
        </form>
        <div className="flex items-center justify-between px-2 mt-2 text-[10px] text-on-surface-variant/60">
          <span>Grounded RAG Compliant</span>
          <span>Source: Official Groww Data</span>
        </div>
      </footer>
    </section>
  );
}
