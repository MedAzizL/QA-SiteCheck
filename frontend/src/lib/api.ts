import type { AnalyzeResponse, Report } from "../types";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

function coerceToReport(data: any): { report: Report; meta?: Partial<AnalyzeResponse> } {
  // Case A: backend returns { report: {...}, url, ... }
  if (data?.report?.overall_score !== undefined) {
    return { report: data.report as Report, meta: data as AnalyzeResponse };
  }

  // Case B: backend returns the report directly (your Orchestrator currently does)
  if (data?.overall_score !== undefined && Array.isArray(data?.metrics)) {
    return { report: data as Report, meta: {} };
  }

  // Otherwise: throw
  throw new Error("Unexpected API response shape");
}

export async function analyzeUrl(url: string): Promise<{ report: Report; meta?: Partial<AnalyzeResponse> }> {
  const res = await fetch(`${API_BASE}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });

  let data: any = null;
  try {
    data = await res.json();
  } catch {
    // ignore
  }

  if (!res.ok) {
    const msg = data?.detail || data?.message || `Request failed (${res.status})`;
    throw new Error(msg);
  }

  return coerceToReport(data);
}