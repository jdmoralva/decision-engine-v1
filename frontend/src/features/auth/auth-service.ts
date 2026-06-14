import {
  clearStoredSession,
  saveStoredSession,
  type SessionMe,
  type StoredSession,
} from "../../session-storage";

type Fetcher = typeof fetch;


function resolveFetcher(fetcher?: Fetcher): Fetcher {
  return fetcher ?? globalThis.fetch.bind(globalThis);
}

export type LoginResult = {
  access_token: string;
  token_type: string;
};

export type MeResult = {
  id: string;
  username: string;
  display_name: string | null;
  roles: string[];
};

export function toSessionMe(me: MeResult): SessionMe {
  return {
    id: me.id,
    username: me.username,
    displayName: me.display_name,
    roles: me.roles,
  };
}

export class AuthApiClient {
  private readonly fetcher: Fetcher;

  constructor(fetcher?: Fetcher) {
    this.fetcher = resolveFetcher(fetcher);
  }

  async login(username: string, password: string): Promise<StoredSession> {
    const loginResponse = await this.fetcher("/api/v1/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    if (!loginResponse.ok) {
      throw new Error("Credenciales invalidas. Verifica usuario y password.");
    }

    const loginPayload = (await loginResponse.json()) as LoginResult;
    const me = await this.restore(loginPayload.access_token);
    const session = { accessToken: loginPayload.access_token, me };
    saveStoredSession(session);
    return session;
  }

  async restore(accessToken: string): Promise<SessionMe> {
    const meResponse = await this.fetcher("/api/v1/me", {
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    if (!meResponse.ok) {
      clearStoredSession();
      throw new Error("La sesion guardada ya no es valida.");
    }

    return toSessionMe((await meResponse.json()) as MeResult);
  }
}
