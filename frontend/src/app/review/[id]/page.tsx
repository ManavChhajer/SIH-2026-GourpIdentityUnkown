"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import Link from "next/link";
import {
  approveDocument,
  getDocument,
  saveBoundary,
  type AnalyzeResult,
} from "@/lib/api";

const CANVAS_W = 600;
const CANVAS_H = 420;

export default function ReviewDocument() {
  const router = useRouter();
  const params = useParams<{ id: string }>();
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const [employee, setEmployee] = useState<string | null>(null);
  const [doc, setDoc] = useState<AnalyzeResult | null>(null);
  const [points, setPoints] = useState<number[][]>([]);
  const [mode, setMode] = useState<"view" | "draw">("view");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const bgImageRef = useRef<HTMLImageElement | null>(null);
  const [bgLoaded, setBgLoaded] = useState(false);

  useEffect(() => {
    const img = new Image();
    img.src = "/dummy-land.svg";
    img.onload = () => {
      bgImageRef.current = img;
      setBgLoaded(true);
    };
  }, []);

  useEffect(() => {
    const emp = sessionStorage.getItem("gov_employee");
    if (!emp) {
      router.push("/review/login");
      return;
    }
    setEmployee(emp);
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [params.id]);

  async function load() {
    const d = await getDocument(params.id);
    setDoc(d);
    if (d.boundary) setPoints(d.boundary);
  }

  useEffect(() => {
    draw();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [points, bgLoaded]);

  function draw() {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.clearRect(0, 0, CANVAS_W, CANVAS_H);

    if (bgImageRef.current) {
      // real dummy land/parcel image as the sketch surface
      ctx.drawImage(bgImageRef.current, 0, 0, CANVAS_W, CANVAS_H);
    } else {
      // fallback while the image is still loading
      ctx.fillStyle = "#f4f1e8";
      ctx.fillRect(0, 0, CANVAS_W, CANVAS_H);
      ctx.fillStyle = "#a89f87";
      ctx.font = "12px sans-serif";
      ctx.fillText("Loading land image…", 16, 20);
    }

    if (points.length === 0) return;

    // lines
    ctx.strokeStyle = "#4338ca";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(points[0][0], points[0][1]);
    for (let i = 1; i < points.length; i++) {
      ctx.lineTo(points[i][0], points[i][1]);
    }
    if (points.length > 2) ctx.closePath();
    ctx.stroke();

    // fill if closed polygon
    if (points.length > 2) {
      ctx.fillStyle = "rgba(67, 56, 202, 0.12)";
      ctx.fill();
    }

    // dots
    points.forEach(([x, y], i) => {
      ctx.fillStyle = "#4338ca";
      ctx.beginPath();
      ctx.arc(x, y, 5, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = "#1e1b4b";
      ctx.font = "10px sans-serif";
      ctx.fillText(String(i + 1), x + 7, y - 7);
    });
  }

  function handleCanvasClick(e: React.MouseEvent<HTMLCanvasElement>) {
    if (mode !== "draw") return;
    const rect = canvasRef.current!.getBoundingClientRect();
    const x = Math.round(e.clientX - rect.left);
    const y = Math.round(e.clientY - rect.top);
    setPoints((prev) => [...prev, [x, y]]);
  }

  function undoPoint() {
    setPoints((prev) => prev.slice(0, -1));
  }

  function clearPoints() {
    setPoints([]);
  }

  async function handleApprove() {
    setBusy(true);
    setMessage(null);
    try {
      const updated = await approveDocument(params.id);
      setDoc(updated);
      setMessage("Approved as-is.");
    } finally {
      setBusy(false);
    }
  }

  async function handleSaveBoundary() {
    if (points.length < 3) {
      setMessage("Draw at least 3 points to close a boundary.");
      return;
    }
    setBusy(true);
    setMessage(null);
    try {
      const updated = await saveBoundary(params.id, points);
      setDoc(updated);
      setMode("view");
      setMessage("Boundary saved.");
    } finally {
      setBusy(false);
    }
  }

  if (!employee || !doc) return null;

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="bg-slate-900 text-white px-8 py-4 flex items-center justify-between">
        <div>
          <h1 className="font-bold text-lg">{doc.filename}</h1>
          <p className="text-xs text-slate-400">{doc.document_id} &middot; reviewer: {employee}</p>
        </div>
        <Link href="/review" className="text-sm text-slate-300 hover:text-white">
          ← Back to queue
        </Link>
      </header>

      <main className="max-w-5xl mx-auto p-8 grid grid-cols-5 gap-6">
        <div className="col-span-3 bg-white rounded-2xl border border-slate-200 p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-sm">Dummy land image — mark boundary</h2>
            <div className="flex gap-2">
              <button
                onClick={() => setMode(mode === "draw" ? "view" : "draw")}
                className={`text-xs font-semibold px-3 py-1.5 rounded-lg border ${
                  mode === "draw"
                    ? "bg-indigo-600 text-white border-indigo-600"
                    : "border-slate-300 text-slate-700 hover:bg-slate-50"
                }`}
              >
                {mode === "draw" ? "✎ Drawing…" : "✎ Draw boundary"}
              </button>
              <button
                onClick={undoPoint}
                disabled={points.length === 0}
                className="text-xs font-semibold px-3 py-1.5 rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-50 disabled:opacity-40"
              >
                Undo point
              </button>
              <button
                onClick={clearPoints}
                disabled={points.length === 0}
                className="text-xs font-semibold px-3 py-1.5 rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-50 disabled:opacity-40"
              >
                Clear
              </button>
            </div>
          </div>
          <canvas
            ref={canvasRef}
            width={CANVAS_W}
            height={CANVAS_H}
            onClick={handleCanvasClick}
            className={`rounded-lg border border-slate-300 ${mode === "draw" ? "cursor-crosshair" : "cursor-default"}`}
          />
          <p className="text-xs text-slate-500 mt-3">
            {mode === "draw"
              ? `Click directly on the land image to drop boundary points (dots), connected in order (lines). ${points.length} point(s) placed — need 3+ to save.`
              : "Click \"Draw boundary\" to sketch the parcel outline by hand on the dummy satellite image below."}
          </p>
          <div className="mt-4 flex gap-2">
            <button
              onClick={handleSaveBoundary}
              disabled={busy || points.length < 3}
              className="flex-1 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold rounded-lg py-2.5 disabled:opacity-40"
            >
              Save hand-drawn boundary
            </button>
          </div>
        </div>

        <div className="col-span-2 space-y-4">
          <div className="bg-white rounded-2xl border border-slate-200 p-5">
            <h2 className="font-semibold text-sm mb-3">Extracted fields</h2>
            <table className="w-full text-sm">
              <tbody>
                {doc.fields.map((f) => (
                  <tr key={f.name} className="border-t border-slate-100">
                    <td className="py-2 text-slate-500 text-xs">{f.label}</td>
                    <td className="py-2 font-medium text-xs">{f.value}</td>
                    <td className="py-2 text-right text-xs font-bold">
                      {Math.round(f.confidence * 100)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="bg-white rounded-2xl border border-slate-200 p-5">
            <h2 className="font-semibold text-sm mb-1">Executive decision</h2>
            <p className="text-xs text-slate-500 mb-4">
              Current status:{" "}
              <span className="font-semibold text-slate-700">{doc.status}</span>
            </p>
            <button
              onClick={handleApprove}
              disabled={busy}
              className="w-full bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-semibold rounded-lg py-2.5 mb-2 disabled:opacity-40"
            >
              ✓ Approve as-is
            </button>
            <p className="text-[11px] text-slate-400">
              Or use the boundary tool on the left to hand-correct the parcel
              outline instead of approving the auto-extracted result.
            </p>
            {message && (
              <p className="text-xs font-semibold text-indigo-600 mt-3">{message}</p>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
