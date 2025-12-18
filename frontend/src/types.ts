export type MetricStatus = "excellent" | "good" | "warning" | "critical";

export type Metric = {
  name: string;
  score: number;
  status: MetricStatus;
  icon: string;
  description: string;
  color: string; // hex
};

export type Recommendation = {
  priority: "critical" | "high" | "medium" | "low";
  category: string;
  title: string;
  description: string;
  impact: string;
};

export type Report = {
  overall_score: number;
  grade: "A" | "B" | "C" | "D" | "F";
  status: MetricStatus;
  summary: string;
  metrics: Metric[];
  highlights: string[];
  recommendations: Recommendation[];
  details?: {
    load_time?: string;
    total_issues?: number;
    critical_issues?: number;
    warnings?: number;
    ai_powered?: boolean;
    [k: string]: any;
  };
};

export type AnalyzeResponse = {
  url?: string;
  final_url?: string;
  status?: number;
  error?: boolean;
  error_type?: string;
  error_message?: string;
  timestamp?: string;
  analysis_duration?: number;
  report?: Report;
  raw_data?: any;

  // OR sometimes backend may return the report directly
  overall_score?: number;
  grade?: "A" | "B" | "C" | "D" | "F";
  statusText?: string;
};