import React, { createContext, useContext, useEffect, useState, useCallback } from "react";
import { authApi, type AuthUser } from "@/lib/api";

interface AuthContextType {
  user: AuthUser | null;
  isLoading: boolean;
  requestMagicLink: (email: string) => Promise<void>;
  consumeToken: (token: string) => Promise<AuthUser>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

/**
 * Real magic-link authentication. No passwords and no credentials are stored in
 * localStorage; the session lives in Secure HttpOnly cookies managed by the API.
 * Any legacy prototype keys from the old localStorage auth are cleared on load.
 */
function clearLegacyKeys() {
  const legacy = ["users", "currentUser"];
  Object.keys(localStorage).forEach((k) => {
    if (legacy.includes(k) || k.startsWith("progress_") || k.startsWith("quizResults_")) {
      localStorage.removeItem(k);
    }
  });
}

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const refreshUser = useCallback(async () => {
    try {
      const me = await authApi.me();
      setUser(me);
    } catch {
      setUser(null);
    }
  }, []);

  useEffect(() => {
    clearLegacyKeys();
    (async () => {
      await refreshUser();
      setIsLoading(false);
    })();
  }, [refreshUser]);

  const requestMagicLink = useCallback(async (email: string) => {
    await authApi.requestMagicLink(email);
  }, []);

  const consumeToken = useCallback(async (token: string) => {
    const result = await authApi.consume(token);
    setUser(result.user);
    return result.user;
  }, []);

  const logout = useCallback(async () => {
    try {
      await authApi.logout();
    } finally {
      setUser(null);
    }
  }, []);

  return (
    <AuthContext.Provider value={{ user, isLoading, requestMagicLink, consumeToken, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
};
