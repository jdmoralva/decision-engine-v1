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


export function saveStoredSession(session: StoredSession): void {
  localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(session));
}


export function loadStoredSession(): StoredSession | null {
  const rawValue = localStorage.getItem(SESSION_STORAGE_KEY);
  if (rawValue === null) {
    return null;
  }

  try {
    return JSON.parse(rawValue) as StoredSession;
  } catch {
    clearStoredSession();
    return null;
  }
}


export function clearStoredSession(): void {
  localStorage.removeItem(SESSION_STORAGE_KEY);
}
