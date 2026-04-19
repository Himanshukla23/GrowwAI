"use client";

import { createContext, useContext, useState, useEffect } from "react";

const SavedContext = createContext();

/**
 * SavedProvider — Manages user's saved/bookmarked analyses.
 * Persists to localStorage under the "lucid_ledger_saved_analyses" key.
 */
export function SavedProvider({ children }) {
  const [saved, setSaved] = useState([]);

  // Load from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem("lucid_ledger_saved_analyses");
    if (stored) {
      try {
        setSaved(JSON.parse(stored));
      } catch (e) {
        console.error("Failed to parse saved analyses", e);
      }
    }
  }, []);

  // Save to localStorage whenever state changes
  useEffect(() => {
    localStorage.setItem("lucid_ledger_saved_analyses", JSON.stringify(saved));
  }, [saved]);

  const toggleSave = (analysis) => {
    setSaved((prev) => {
      const exists = prev.some((a) => a.id === analysis.id);
      if (exists) {
        return prev.filter((a) => a.id !== analysis.id);
      } else {
        return [...prev, analysis];
      }
    });
  };

  const isSaved = (analysis) => {
    return saved.some((a) => a.id === analysis.id);
  };

  return (
    <SavedContext.Provider value={{ saved, toggleSave, isSaved }}>
      {children}
    </SavedContext.Provider>
  );
}

export function useSaved() {
  const context = useContext(SavedContext);
  if (!context) {
    throw new Error("useSaved must be used within a SavedProvider");
  }
  return context;
}
