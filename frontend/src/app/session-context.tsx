import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";

import { clearAllWorkspaceDrafts } from "../features/decision-workspace/workspace-session";
import { AuthApiClient } from "../features/auth/auth-service";
import { canManageEngine } from "../features/platform/service-visibility";
import {
  clearStoredSession,
  loadStoredSession,
  saveStoredSession,
  type SessionMe,
  type StoredSession,
} from "../session-storage";

type SessionStatus = "restoring" | "anonymous" | "authenticated";

type SessionContextValue = {
  status: SessionStatus;
  token: string | null;
  me: SessionMe | null;
  isSubmitting: boolean;
  error: string | null;
  canManageCurrentSession: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  clearError: () => void;
};

const SessionContext = createContext<SessionContextValue | null>(null);

function clearSensitiveSessionState(): void {
  clearStoredSession();
  clearAllWorkspaceDrafts();
}

export function SessionProvider({ children }: { children: ReactNode }) {
  const [status, setStatus] = useState<SessionStatus>("restoring");
  const [session, setSession] = useState<StoredSession | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    async function restoreSession() {
      const storedSession = loadStoredSession();
      if (storedSession === null) {
        if (isMounted) {
          setSession(null);
          setStatus("anonymous");
        }
        return;
      }

      try {
        const me = await new AuthApiClient().restore(storedSession.accessToken);
        if (isMounted) {
          const restoredSession = { accessToken: storedSession.accessToken, me };
          setSession(restoredSession);
          saveStoredSession(restoredSession);
          setStatus("authenticated");
        }
      } catch {
        clearSensitiveSessionState();
        if (isMounted) {
          setSession(null);
          setStatus("anonymous");
        }
      }
    }

    void restoreSession();

    return () => {
      isMounted = false;
    };
  }, []);

  async function login(username: string, password: string): Promise<void> {
    setError(null);
    setIsSubmitting(true);

    try {
      const nextSession = await new AuthApiClient().login(username, password);
      setSession(nextSession);
      setStatus("authenticated");
    } catch (caughtError) {
      clearSensitiveSessionState();
      setSession(null);
      setStatus("anonymous");
      setError(
        caughtError instanceof Error ? caughtError.message : "Ocurrio un error inesperado.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  function logout() {
    clearSensitiveSessionState();
    setSession(null);
    setStatus("anonymous");
    setError(null);
  }

  const me = session?.me ?? null;

  return (
    <SessionContext.Provider
      value={{
        status,
        token: session?.accessToken ?? null,
        me,
        isSubmitting,
        error,
        canManageCurrentSession: me !== null ? canManageEngine(me.roles) : false,
        login,
        logout,
        clearError: () => setError(null),
      }}
    >
      {children}
    </SessionContext.Provider>
  );
}

export function useSessionContext(): SessionContextValue {
  const context = useContext(SessionContext);
  if (context === null) {
    throw new Error("useSessionContext must be used within SessionProvider.");
  }

  return context;
}
