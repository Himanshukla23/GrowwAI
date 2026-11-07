"use client";

import { useState, useEffect } from "react";
import Navbar from "@/components/Navbar";
import AssistantPanel from "@/components/AssistantPanel";
import DashboardWorkspace from "@/components/DashboardWorkspace";
import ComparisonWorkspace from "@/components/ComparisonWorkspace";
import Sidebar from "@/components/Sidebar";
import { ENDPOINTS } from "@/lib/api-config";

export default function Home() {
  const [query, setQuery] = useState("");
  const [threadId, setThreadId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isInitializing, setIsInitializing] = useState(true);
  const [viewMode, setViewMode] = useState("dashboard"); // 'dashboard' or 'comparison'
  const [activeFundData, setActiveFundData] = useState(null);
  const [comparisonData, setComparisonData] = useState(null);
  const [healthData, setHealthData] = useState(null);

  // Responsive / Google Gemini style drawer states
  const [isAssistantOpen, setIsAssistantOpen] = useState(true);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  // Initialize Thread & Health
  useEffect(() => {
    let retryCount = 0;
    const maxRetries = 20;

    async function init() {
      try {
        console.log(`[Init] Connecting to Groww Assist engine (Attempt ${retryCount + 1})...`);
        const res = await fetch(ENDPOINTS.CREATE_THREAD, { method: "POST" });
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
        const data = await res.json();
        setThreadId(data.thread_id);
        setIsInitializing(false);
        console.log("[Init] Backend connected.");

        fetch(ENDPOINTS.HEALTH).then((r) => r.ok && r.json().then(setHealthData));
      } catch (err) {
        console.warn(`[Init] Backend connection attempt: ${err.message}`);
        if (retryCount < maxRetries) {
          retryCount++;
          setTimeout(init, 3000);
        } else {
          setThreadId("thread-" + Date.now());
          setIsInitializing(false);
        }
      }
    }
    init();
  }, []);

  // Keep-alive ping (for Render free tier)
  useEffect(() => {
    if (isInitializing || !threadId) return;

    const interval = setInterval(() => {
      fetch(ENDPOINTS.HEALTH).catch(() => {});
    }, 600000); // 10 minutes

    return () => clearInterval(interval);
  }, [isInitializing, threadId]);

  const handleSend = async (e, textOverride = null) => {
    e?.preventDefault();
    const finalQuery = textOverride || query;
    if (!finalQuery.trim() || isLoading) return;

    let activeThread = threadId || "thread-" + Date.now();
    if (!threadId) {
      setThreadId(activeThread);
    }

    // Auto open assistant if closed
    setIsAssistantOpen(true);

    const userMessage = {
      role: "user",
      content: finalQuery,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setQuery("");
    setIsLoading(true);

    const maxQueryRetries = 2;
    let queryAttempt = 0;

    const executeQuery = async () => {
      try {
        const res = await fetch(ENDPOINTS.QUERY(activeThread), {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query: finalQuery }),
        });

        if (!res.ok) throw new Error("Server error");

        const data = await res.json();

        const assistantMessage = {
          role: "assistant",
          content: data.answer,
          intent: data.intent,
          timestamp: data.timestamp,
          violations: data.guardrail_violations || [],
          citation_url: data.citation_url,
        };
        setMessages((prev) => [...prev, assistantMessage]);

        if (data.intent === "comparison") {
          setViewMode("comparison");
          if (data.structured_data) setComparisonData(data.structured_data);
        } else if (data.intent === "factual") {
          setViewMode("dashboard");
          if (data.structured_data) setActiveFundData(data.structured_data);
        }
        setIsLoading(false);
      } catch (err) {
        if (queryAttempt < maxQueryRetries) {
          queryAttempt++;
          setTimeout(executeQuery, 1500);
        } else {
          setMessages((prev) => [
            ...prev,
            {
              role: "assistant",
              content:
                "Encountered a connection error. Please ensure the backend engine is operational.",
              error: true,
            },
          ]);
          setIsLoading(false);
        }
      }
    };

    executeQuery();
  };

  const handleNewAnalysis = () => {
    setMessages([]);
    setQuery("");
    setViewMode("dashboard");
    setActiveFundData(null);
    setComparisonData(null);
  };

  return (
    <div className="bg-background text-on-surface font-body antialiased min-h-screen flex selection:bg-primary/15 selection:text-on-surface">
      {/* Google Navigation Drawer Sidebar */}
      <Sidebar
        onNewAnalysis={handleNewAnalysis}
        healthData={healthData}
        messageCount={messages.length}
        viewMode={viewMode}
        setViewMode={setViewMode}
        isOpen={isMobileMenuOpen}
        onClose={() => setIsMobileMenuOpen(false)}
      />

      {/* Main Content Area */}
      <div
        className={`flex-1 flex flex-col min-h-screen transition-all duration-300 md:ml-[260px] ${
          isAssistantOpen ? "xl:mr-[380px]" : "xl:mr-0"
        }`}
      >
        <Navbar
          title={viewMode === "dashboard" ? "Market Intelligence" : "Fund Comparisons"}
          onSearch={(q) => handleSend(null, q)}
          isAssistantOpen={isAssistantOpen}
          onToggleAssistant={() => setIsAssistantOpen((v) => !v)}
          onMobileMenuToggle={() => setIsMobileMenuOpen(true)}
        />

        <main className="flex-1 overflow-y-auto no-scrollbar">
          {viewMode === "dashboard" ? (
            <DashboardWorkspace
              fundData={activeFundData}
              onCompareClick={() => setViewMode("comparison")}
              onSelectFund={(q) => handleSend(null, q)}
            />
          ) : (
            <ComparisonWorkspace
              comparisonData={comparisonData}
              onSelectQuery={(q) => handleSend(null, q)}
            />
          )}
        </main>
      </div>

      {/* Google Gemini-Style AI Assistant Drawer */}
      <div
        className={`fixed top-0 bottom-0 right-0 z-40 w-[380px] transition-transform duration-300 ease-out ${
          isAssistantOpen ? "translate-x-0" : "translate-x-full"
        }`}
      >
        <AssistantPanel
          messages={messages}
          isLoading={isLoading}
          query={query}
          setQuery={setQuery}
          handleSend={handleSend}
          isInitializing={isInitializing}
          onClose={() => setIsAssistantOpen(false)}
        />
      </div>

      {/* Floating Action Button on Mobile when Assistant is closed */}
      {!isAssistantOpen && (
        <button
          onClick={() => setIsAssistantOpen(true)}
          className="fixed bottom-6 right-6 z-40 bg-gradient-to-r from-primary to-primary-container text-white p-3.5 rounded-full shadow-lg shadow-primary/30 hover:scale-105 active:scale-95 transition-all flex items-center gap-2 cursor-pointer"
          title="Open AI Guide"
        >
          <span
            className="material-symbols-outlined text-xl"
            style={{ fontVariationSettings: "'FILL' 1" }}
          >
            auto_awesome
          </span>
          <span className="text-xs font-headline font-bold pr-1">Ask AI</span>
        </button>
      )}
    </div>
  );
}
