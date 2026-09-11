"use client";

import { useRef, useState } from "react";
import { analyzeDocument, type AnalyzeResult } from "@/lib/api";
import Link from "next/link";

type Status = "idle" | "loading" | "done" | "error";

function ConfidenceBadge({ value }: { value: number }) {
  const pct = Math.round(value * 100);
  const color =
    value >= 0.85
      ? "bg-emerald-100 text-emerald-800 border-emerald-300"
      : value >= 0.7
        ? "bg-amber-100 text-amber-800 border-amber-300"
        : "bg-rose-100 text-rose-800 border-rose-300";
  return (
    <span className={`inline-block rounded-full border px-2.5 py-0.5 text-xs font-semibold ${color}`}>
      {pct}%
    </span>
  );
}

function StatusPill({ status }: { status: AnalyzeResult["status"] }) {
  const map: Record<AnalyzeResult["status"], { label: string; cls: string }> = {
    auto_approved: { label: "✓ Auto-approved", cls: "bg-emerald-100 text-emerald-800" },
    pending_review: { label: "⏳ Pending review", cls: "bg-amber-100 text-amber-800" },
    approved: { label: "✓ Approved by reviewer", cls: "bg-emerald-100 text-emerald-800" },
    boundary_drawn: { label: "✎ Boundary drawn", cls: "bg-indigo-100 text-indigo-800" },
  };
  const s = map[status];
  return <span className={`inline-block rounded-full px-3 py-1 text-xs font-semibold ${s.cls}`}>{s.label}</span>;
}

export default function Home() {
  const [status, setStatus] = useState<Status>("idle");
  const [result, setResult] = useState<AnalyzeResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  async function handleFile(file: File) {
    setStatus("loading");
    setError(null);
    try {
      const res = await analyzeDocument(file);
      setResult(res);
      setStatus("done");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unknown error");
      setStatus("error");
    }
  }

  function reset() {
    setResult(null);
    setStatus("idle");
    setError(null);
    if (inputRef.current) inputRef.current.value = "";
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto max-w-3xl px-6 py-5 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold tracking-tight text-slate-900">
              Intelligent Land Record Digitization
            </h1>
            <p className="text-sm text-slate-500">
              Upload a Khata/Khasra page scan to extract structured fields with confidence scoring.
            </p>
          </div>
          <Link
            href="/review/login"
            className="shrink-0 rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50"
          >
            Gov Employee Portal →
          </Link>
        </div>
      </header>

      <main className="mx-auto max-w-3xl px-6 py-10">
        {status !== "done" && (
          <div className="rounded-xl border-2 border-dashed border-slate-300 bg-white p-10 text-center">
            <input
              ref={inputRef}
              type="file"
              accept="image/*"
              className="hidden"
              id="file-upload"
              disabled={status === "loading"}
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) handleFile(file);
              }}
            />
            {status === "idle" && (
              <label
                htmlFor="file-upload"
                className="cursor-pointer rounded-lg bg-slate-900 px-5 py-2.5 text-sm font-semibold text-white hover:bg-slate-700"
              >
                Choose a scanned document
              </label>
            )}
            {status === "loading" && (
              <div className="flex flex-col items-center gap-3">
                <div className="h-8 w-8 animate-spin rounded-full border-4 border-slate-200 border-t-slate-900" />
                <p className="text-sm text-slate-600">Processing scan — extracting fields…</p>
              </div>
            )}
            {status === "error" && (
              <div className="flex flex-col items-center gap-3">
                <p className="text-sm text-rose-600">{error}</p>
                <button
                  onClick={reset}
                  className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-semibold text-white"
                >
                  Try again
                </button>
              </div>
            )}
          </div>
        )}

        {status === "done" && result && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <StatusPill status={result.status} />
              {result.status === "pending_review" && (
                <p className="text-xs text-slate-500">
                  A government employee will review this record in the{" "}
                  <Link href="/review/login" className="font-semibold text-indigo-600 hover:underline">
                    Gov Employee Portal
                  </Link>
                  .
                </p>
              )}
            </div>

            {result.review_required && (
              <div className="rounded-lg border border-amber-300 bg-amber-50 px-4 py-3 text-sm font-medium text-amber-800">
                ⚠ Needs review — one or more fields have low confidence.
              </div>
            )}

            <div className="rounded-xl border border-slate-200 bg-white p-6">
              <div className="mb-4 flex items-center justify-between">
                <div>
                  <p className="text-xs uppercase tracking-wide text-slate-400">Document</p>
                  <p className="font-semibold">{result.filename}</p>
                  <p className="text-xs text-slate-400 mt-0.5">{result.document_id}</p>
                </div>
                <div className="text-right">
                  <p className="text-xs uppercase tracking-wide text-slate-400">Overall confidence</p>
                  <p className="font-semibold">{Math.round(result.overall_confidence * 100)}%</p>
                </div>
              </div>

              <table className="w-full text-sm">
                <tbody>
                  {result.fields.map((f) => (
                    <tr key={f.name} className="border-t border-slate-100">
                      <td className="py-3 text-slate-500">{f.label}</td>
                      <td className="py-3 font-medium">{f.value}</td>
                      <td className="py-3 text-right">
                        <ConfidenceBadge value={f.confidence} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <button
              onClick={reset}
              className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50"
            >
              Upload another document
            </button>
          </div>
        )}
      </main>
    </div>
  );
}
