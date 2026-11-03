const KEY = "jarvis-session";

export function newSessionId(): string {
  return crypto.randomUUID().replace(/-/g, "").slice(0, 32); // matches ^[A-Za-z0-9_-]{1,64}$
}

export function loadSessionId(): string {
  try {
    const saved = sessionStorage.getItem(KEY);
    if (saved && /^[A-Za-z0-9_-]{1,64}$/.test(saved)) return saved;
  } catch {
    /* storage can throw (private mode, blocked): the page works without it */
  }
  return saveSessionId(newSessionId());
}

export function saveSessionId(id: string): string {
  try {
    sessionStorage.setItem(KEY, id);
  } catch {
    /* ignore */
  }
  return id;
}
