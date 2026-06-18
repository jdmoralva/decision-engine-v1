export type SessionMe = {
  id: string;
  username: string;
  displayName: string | null;
  roles: string[];
};

export type StoredSession = {
  accessToken: string;
  me: SessionMe;
};


const SESSION_STORAGE_KEY = "decision-engine.session";

export function getStoredSessionKey(): string {
  return SESSION_STORAGE_KEY;
}


function isSessionMe(value: unknown): value is SessionMe {
  if (typeof value !== "object" || value === null) {
    return false;
  }

  const candidate = value as Record<string, unknown>;
  return (
    typeof candidate.id === "string" &&
    typeof candidate.username === "string" &&
    (typeof candidate.displayName === "string" || candidate.displayName === null) &&
    Array.isArray(candidate.roles) &&
    candidate.roles.every((role) => typeof role === "string")
  );
}


function isStoredSession(value: unknown): value is StoredSession {
  if (typeof value !== "object" || value === null) {
    return false;
  }

  const candidate = value as Record<string, unknown>;
  return typeof candidate.accessToken === "string" && isSessionMe(candidate.me);
}


export function saveStoredSession(session: StoredSession): void {
  localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(session));
}


export function loadStoredSession(): StoredSession | null {
  const rawValue = localStorage.getItem(SESSION_STORAGE_KEY);
  if (rawValue === null) {
    return null;
  }

  try {
    const parsed = JSON.parse(rawValue) as unknown;
    if (!isStoredSession(parsed)) {
      clearStoredSession();
      return null;
    }
    return parsed;
  } catch {
    clearStoredSession();
    return null;
  }
}


export function clearStoredSession(): void {
  localStorage.removeItem(SESSION_STORAGE_KEY);
}
