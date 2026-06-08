import { beforeEach, describe, expect, it, vi } from "vitest";

import {
  clearStoredSession,
  loadStoredSession,
  saveStoredSession,
} from "../src/session-storage";


describe("session storage", () => {
  beforeEach(() => {
    const store = new Map<string, string>();

    vi.stubGlobal("localStorage", {
      getItem: (key: string) => store.get(key) ?? null,
      setItem: (key: string, value: string) => store.set(key, value),
      removeItem: (key: string) => store.delete(key),
    });
  });

  it("persists and reloads a session", () => {
    saveStoredSession({
      accessToken: "token-123",
      me: {
        id: "user-1",
        username: "admin",
        displayName: "Administrador",
        roles: ["admin"],
      },
    });

    expect(loadStoredSession()).toEqual({
      accessToken: "token-123",
      me: {
        id: "user-1",
        username: "admin",
        displayName: "Administrador",
        roles: ["admin"],
      },
    });
  });

  it("clears an existing session", () => {
    saveStoredSession({
      accessToken: "token-123",
      me: {
        id: "user-1",
        username: "admin",
        displayName: "Administrador",
        roles: ["admin"],
      },
    });

    clearStoredSession();

    expect(loadStoredSession()).toBeNull();
  });

  it("drops corrupted session payloads", () => {
    localStorage.setItem("decision-engine.session", "not-json");

    expect(loadStoredSession()).toBeNull();
  });
});
