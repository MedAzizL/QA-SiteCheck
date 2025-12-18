import React, { useMemo, useState } from "react";
import { Eye, Shield, Zap, Code, Search, CheckCircle2, AlertCircle, XCircle } from "lucide-react";
import { analyzeUrl } from "./lib/api";
import { isProbablyUrl, normalizeUrl } from "./lib/urls";
import type { Report } from "./types";
import { CircleScore } from "./components/CircleScore";
import { Badge, PriorityBadge } from "./components/Badge";

function getMetricIcon(name: string) {
  const iconMap: Record<string, any> = {
    Performance: Zap,
    Security: Shield,
    Accessibility: Eye,
    "Code Quality": Code,
    SEO: Search,
  };
  return iconMap[name] || CheckCircle2;
}

function getStatusIcon(status: string) {
  switch (status) {
    case "excellent":
    case "good":
      return <CheckCircle2 className="w-4 h-4 text-emerald-600" />;
    case "warning":
      return <AlertCircle className="w-4 h-4 text-orange-600" />;
    case "critical":
      return <XCircle className="w-4 h-4 text-red-600" />;
    default:
      return <CheckCircle2 className="w-4 h-4 text-gray-600" />;
  }
}

export default function App() {
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [report, setReport] = useState<Report | null>(null);

  const canSubmit = useMemo(() => isProbablyUrl(input), [input]);

  const handleSubmit = async () => {
    setErr(null);
    setReport(null);

    let url: string;
    try {
      url = normalizeUrl(input);
    } catch {
      setErr("Please enter a valid URL (e.g., https://example.com)");
      return;
    }

    setLoading(true);
    try {
      const res = await analyzeUrl(url);
      setReport(res.report);
    } catch (e: any) {
      setErr(e?.message || "Analysis failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && canSubmit && !loading) {
      handleSubmit();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex flex-col">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl blur-lg opacity-30"></div>
              <div className="relative bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl p-2.5">
                <Zap className="w-5 h-5 text-white" />
              </div>
            </div>
            <div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
                QA Site Check
              </h1>
              <p className="text-xs text-gray-600">Website quality insights you can trust</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1">
        {/* Hero Section */}
        <section className="max-w-7xl mx-auto px-4 sm:px-6 pt-12 sm:pt-16 pb-8 sm:pb-12">
          <div className="text-center max-w-3xl mx-auto mb-8 sm:mb-12">
            <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-gray-900 mb-4 sm:mb-6 leading-tight">
              Instantly audit your website quality
            </h2>
            <p className="text-lg sm:text-xl text-gray-600 leading-relaxed">
              Get a clear, actionable analysis of performance, accessibility, SEO, security, and best practices — all in one simple report.
            </p>
          </div>

          {/* Input Section */}
          <div className="max-w-2xl mx-auto mb-12 sm:mb-16">
            <div className="bg-white rounded-2xl shadow-xl border border-gray-200 p-6 sm:p-8">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Website URL
                  </label>
                  <div className="flex flex-col sm:flex-row gap-3">
                    <input
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder="example.com or https://example.com"
                      className="flex-1 px-4 py-3.5 rounded-xl border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition text-gray-900 placeholder:text-gray-400"
                    />
                    <button
                      onClick={handleSubmit}
                      disabled={!canSubmit || loading}
                      className="px-8 py-3.5 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-xl hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition shadow-lg hover:shadow-xl whitespace-nowrap"
                    >
                      {loading ? (
                        <span className="flex items-center justify-center gap-2">
                          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                          Analyzing
                        </span>
                      ) : (
                        "Run analysis"
                      )}
                    </button>
                  </div>
                </div>

                {err && (
                  <div className="flex items-start gap-3 p-4 bg-red-50 border border-red-200 rounded-xl">
                    <XCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                    <div className="text-sm text-red-800">{err}</div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Results Section */}
          {!report ? (
            <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-12 sm:p-16">
              <div className="text-center max-w-md mx-auto">
                <div className="w-20 h-20 bg-gradient-to-br from-blue-100 to-purple-100 rounded-full flex items-center justify-center mx-auto mb-6">
                  <Search className="w-10 h-10 text-blue-600" />
                </div>
                <h3 className="text-xl sm:text-2xl font-bold text-gray-900 mb-3">
                  Your website report will appear here
                </h3>
                <p className="text-gray-600">
                  Enter a website URL to instantly uncover issues, risks, and opportunities to improve quality.
                </p>
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Overall Score Card */}
              <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6 sm:p-8">
                <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6 sm:gap-8">
                  <div className="flex-1">
                    <div className="flex flex-wrap items-center gap-2 mb-4">
                      <Badge variant={report.status === "critical" ? "error" : report.status === "warning" ? "warning" : "success"}>
                        Grade {report.grade}
                      </Badge>
                      <Badge>Status: {report.status}</Badge>
                      {report.details?.ai_powered && <Badge>AI-Powered</Badge>}
                    </div>
                    <h3 className="text-xl sm:text-2xl font-bold text-gray-900 mb-2">
                      {report.summary}
                    </h3>
                    {report.details?.load_time && (
                      <p className="text-gray-600">Load time: {report.details.load_time}</p>
                    )}
                  </div>

                  <div className="mx-auto lg:mx-0">
                    <CircleScore
                      value={report.overall_score}
                      size={140}
                      stroke={12}
                      ringColor={report.metrics?.[0]?.color || "#3b82f6"}
                    />
                  </div>
                </div>
              </div>

              {/* Metrics Grid */}
              <div className="grid gap-4 sm:gap-6 sm:grid-cols-2 lg:grid-cols-3">
                {report.metrics.map((m) => {
                  const IconComponent = getMetricIcon(m.name);
                  return (
                    <div key={m.name} className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center gap-3 flex-1 min-w-0">
                          <div className="w-12 h-12 bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl flex items-center justify-center flex-shrink-0">
                            <IconComponent className="w-6 h-6 text-blue-600" />
                          </div>
                          <div className="min-w-0">
                            <h4 className="font-semibold text-gray-900 truncate">{m.name}</h4>
                            <div className="flex items-center gap-1 mt-1">
                              {getStatusIcon(m.status)}
                              <span className="text-xs text-gray-600">{m.status}</span>
                            </div>
                          </div>
                        </div>
                        <div className="text-right flex-shrink-0 ml-2">
                          <div className="text-2xl font-bold text-gray-900">{m.score}</div>
                          <div className="text-xs text-gray-500">/100</div>
                        </div>
                      </div>

                      <div className="space-y-3">
                        <div className="h-2.5 w-full rounded-full bg-gray-100">
                          <div
                            className="h-2.5 rounded-full transition-all"
                            style={{ 
                              width: `${Math.max(0, Math.min(100, m.score))}%`, 
                              backgroundColor: m.color 
                            }}
                          />
                        </div>
                        <p className="text-sm text-gray-600 leading-relaxed">{m.description}</p>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Highlights & Details */}
              <div className="grid gap-4 sm:gap-6 lg:grid-cols-2">
                <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
                  <h4 className="text-lg font-bold text-gray-900 mb-4">Key Highlights</h4>
                  <ul className="space-y-3">
                    {report.highlights?.map((h, i) => (
                      <li key={i} className="flex gap-3">
                        <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0 mt-0.5" />
                        <span className="text-gray-700">{h}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
                  <h4 className="text-lg font-bold text-gray-900 mb-4">Performance Details</h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-gray-50 rounded-xl p-4">
                      <div className="text-xs text-gray-600 mb-1">Total Issues</div>
                      <div className="text-2xl font-bold text-gray-900">{report.details?.total_issues ?? "—"}</div>
                    </div>
                    <div className="bg-gray-50 rounded-xl p-4">
                      <div className="text-xs text-gray-600 mb-1">Critical</div>
                      <div className="text-2xl font-bold text-red-600">{report.details?.critical_issues ?? "—"}</div>
                    </div>
                    <div className="bg-gray-50 rounded-xl p-4">
                      <div className="text-xs text-gray-600 mb-1">Warnings</div>
                      <div className="text-2xl font-bold text-orange-600">{report.details?.warnings ?? "—"}</div>
                    </div>
                    <div className="bg-gray-50 rounded-xl p-4">
                      <div className="text-xs text-gray-600 mb-1">Load Time</div>
                      <div className="text-xl font-bold text-gray-900 truncate">{report.details?.load_time ?? "—"}</div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Recommendations */}
              {report.recommendations && report.recommendations.length > 0 && (
                <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6 sm:p-8">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6 gap-3">
                    <h4 className="text-xl font-bold text-gray-900">Action Items</h4>
                    <span className="text-sm text-gray-500">Sorted by priority</span>
                  </div>

                  <div className="space-y-4">
                    {report.recommendations
                      .sort((a, b) => {
                        const order = { critical: 0, high: 1, medium: 2, low: 3 };
                        return order[a.priority] - order[b.priority];
                      })
                      .map((r, idx) => (
                        <div key={idx} className="bg-gray-50 rounded-xl p-4 sm:p-6 border border-gray-200">
                          <div className="flex flex-wrap items-center justify-between gap-3 mb-3">
                            <div className="flex items-center gap-2">
                              <PriorityBadge p={r.priority} />
                              <Badge>{r.category}</Badge>
                            </div>
                            <span className="text-xs text-gray-500">#{idx + 1}</span>
                          </div>

                          <h5 className="font-semibold text-gray-900 mb-2">{r.title}</h5>
                          <p className="text-gray-700 mb-3 leading-relaxed">{r.description}</p>
                          <div className="text-sm text-gray-600">
                            <span className="font-medium">Impact:</span> {r.impact}
                          </div>
                        </div>
                      ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-12 sm:mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
          <div className="text-center text-sm text-gray-600">
            © 2025 QA Site Check — Website quality insights you can trust
          </div>
        </div>
      </footer>
    </div>
  );
}