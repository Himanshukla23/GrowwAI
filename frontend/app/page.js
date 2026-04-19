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

  // Initialize Thread & Health
  useEffect(() => {
    let retryCount = 0;
    const maxRetries = 5;

    async function init() {
      try {
        const res = await fetch(ENDPOINTS.CREATE_THREAD, { method: "POST" });
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
        const data = await res.json();
        setThreadId(data.thread_id);
        setIsInitializing(false);
        
        // Also fetch health for sidebar
        fetch(ENDPOINTS.HEALTH).then(r => r.ok && r.json().then(setHealthData));
      } catch (err) {
        if (retryCount < maxRetries) {
          retryCount++;
          setTimeout(init, 2000);
        } else {
          setIsInitializing(false);
        }
      }
    }
    init();
  }, []);

  const handleSend = async (e, textOverride = null) => {
    e?.preventDefault();
    const finalQuery = textOverride || query;
    if (!finalQuery.trim() || !threadId || isLoading) return;

    const userMessage = { role: "user", content: finalQuery, timestamp: new Date().toISOString() };
    setMessages(prev => [...prev, userMessage]);
    setQuery("");
    setIsLoading(true);

    const maxQueryRetries = 2;
    let queryAttempt = 0;

    const executeQuery = async () => {
      try {
        const res = await fetch(ENDPOINTS.QUERY(threadId), {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query: finalQuery })
        });
        
        if (!res.ok) throw new Error("Server error");
        
        const data = await res.json();

        const assistantMessage = {
          role: "assistant",
          content: data.answer,
          intent: data.intent,
          timestamp: data.timestamp,
          violations: data.guardrail_violations || [],
          citation_url: data.citation_url
        };
        setMessages(prev => [...prev, assistantMessage]);

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
          setMessages(prev => [...prev, {
            role: "assistant",
            content: "Encountered a connection error. Please ensure the backend engine is operational.",
            error: true
          }]);
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
    <div className="bg-background text-on-surface font-body antialiased min-h-screen flex">
      <Sidebar onNewAnalysis={handleNewAnalysis} healthData={healthData} messageCount={messages.length} />

      <main className="flex-1 md:ml-[280px] xl:mr-[384px] flex flex-col min-h-screen overflow-hidden">
        <Navbar title={viewMode === "dashboard" ? "Market Overview" : "Comparisons"} />
        
        <div className="flex-1 overflow-y-auto no-scrollbar">
          {viewMode === "dashboard" ? (
            <DashboardWorkspace
              fundData={activeFundData}
              onCompareClick={() => setViewMode("comparison")}
            />
          ) : (
            <ComparisonWorkspace comparisonData={comparisonData} />
          )}
        </div>
      </main>

      <div className="hidden xl:block">
        <AssistantPanel
          messages={messages}
          isLoading={isLoading}
          query={query}
          setQuery={setQuery}
          handleSend={handleSend}
          isInitializing={isInitializing}
        />
      </div>

      <style jsx global>{`
        .no-scrollbar::-webkit-scrollbar {
          display: none;
        }
        .no-scrollbar {
          -ms-overflow-style: none;  /* IE and Edge */
          scrollbar-width: none;  /* Firefox */
        }
        .custom-scrollbar::-webkit-scrollbar {
          width: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: #bacac1;
          border-radius: 10px;
        }
      `}</style>
    </div>
  );
}

