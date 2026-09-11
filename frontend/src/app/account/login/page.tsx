"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { login, signup } from "@/lib/api";
import { useAuth } from "@/lib/useAuth";

export default function AccountLogin() {
  const router = useRouter();
  const { setSession } = useAuth();
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (!username.trim() || !password.trim()) {
      setError("Enter both a username and password.");
      return;
    }
    setBusy(true);
    try {
      const result =
        mode === "login"
          ? await login(username.trim(), password)
          : await signup(username.trim(), password);
      setSession(result.username, result.token);
      router.push("/account");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center px-4">
      <div className="w-full max-w-sm bg-white rounded-2xl border border-slate-200 shadow-sm p-8">
        <div className="text-center mb-6">
          <div className="mx-auto mb-3 w-12 h-12 rounded-full bg-slate-900 text-white flex items-center justify-center font-bold text-lg">
            📄
          </div>
          <h1 className="text-lg font-bold text-slate-900">
            {mode === "login" ? "Sign in" : "Create an account"}
          </h1>
          <p className="text-sm text-slate-500">
            Track the status of documents you upload.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-500 mb-1">Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="e.g. r_venkataiah"
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-900"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-500 mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-900"
            />
          </div>
          {error && <p className="text-xs text-rose-600">{error}</p>}
          <button
            type="submit"
            disabled={busy}
            className="w-full rounded-lg bg-slate-900 hover:bg-slate-700 text-white font-semibold text-sm py-2.5 disabled:opacity-50"
          >
            {mode === "login" ? "Sign in" : "Create account"}
          </button>
        </form>

        <button
          onClick={() => {
            setMode(mode === "login" ? "signup" : "login");
            setError(null);
          }}
          className="w-full text-center text-xs text-slate-500 hover:text-slate-800 mt-4"
        >
          {mode === "login"
            ? "New here? Create an account instead"
            : "Already have an account? Sign in instead"}
        </button>

        <Link
          href="/"
          className="block text-center text-xs text-slate-400 hover:text-slate-600 mt-3"
        >
          ← Back to upload (continue without an account)
        </Link>
      </div>
    </div>
  );
}
