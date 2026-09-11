"use client";

import { useEffect, useState } from "react";

export function useAuth() {
  const [username, setUsername] = useState<string | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    setUsername(window.localStorage.getItem("auth_username"));
    setReady(true);
  }, []);

  function setSession(u: string, token: string) {
    window.localStorage.setItem("auth_username", u);
    window.localStorage.setItem("auth_token", token);
    setUsername(u);
  }

  function clearSession() {
    window.localStorage.removeItem("auth_username");
    window.localStorage.removeItem("auth_token");
    setUsername(null);
  }

  return { username, ready, setSession, clearSession };
}
