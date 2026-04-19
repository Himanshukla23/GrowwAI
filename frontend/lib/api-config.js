// Central API Configuration
// This allows easy switching between local and production environments

export const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
export const STREAMLIT_URL = process.env.NEXT_PUBLIC_STREAMLIT_APP_URL || "http://localhost:8501";

export const ENDPOINTS = {
  HEALTH: `${API_BASE}/health`,
  METRICS: `${API_BASE}/metrics`,
  CREATE_THREAD: `${API_BASE}/threads`,
  QUERY: (threadId) => `${API_BASE}/chat/${threadId}/query`,
  HISTORY: (threadId) => `${API_BASE}/threads/${threadId}/history`,
};
