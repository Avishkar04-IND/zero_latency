"use client";

import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { useRouter, usePathname } from "next/navigation";
import { authService } from "@/services/api/auth";
import { AuthenticatedUser, LoginRequest } from "@/types/auth";

interface AuthContextType {
  user: AuthenticatedUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (credentials: LoginRequest) => Promise<void>;
  logout: () => Promise<void>;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();

  const [user, setUser] = useState<AuthenticatedUser | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const initAuth = useCallback(async () => {
    try {
      setIsLoading(true);
      if (authService.hasToken()) {
        // First set cached user for instant UI rendering
        const cached = authService.getCachedUser();
        if (cached) setUser(cached);

        // Then verify with backend
        const verifiedUser = await authService.getMe();
        if (verifiedUser) {
          setUser(verifiedUser);
        } else if (!cached) {
          setUser(null);
        }
      } else {
        setUser(null);
      }
    } catch {
      // Offline or expired
      const cached = authService.getCachedUser();
      if (cached) setUser(cached);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    initAuth();

    const handleSessionExpired = () => {
      setUser(null);
      setError("Your session has expired. Please sign in again.");
      router.push("/login");
    };

    window.addEventListener("auth:session-expired", handleSessionExpired);
    return () => {
      window.removeEventListener("auth:session-expired", handleSessionExpired);
    };
  }, [initAuth, router]);

  const login = async (credentials: LoginRequest) => {
    setError(null);
    setIsLoading(true);
    try {
      const authenticatedUser = await authService.login(credentials);
      setUser(authenticatedUser);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "Invalid credentials provided");
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    setIsLoading(true);
    try {
      await authService.logout();
      setUser(null);
      router.push("/login");
    } finally {
      setIsLoading(false);
    }
  };

  const clearError = () => setError(null);

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        error,
        login,
        logout,
        clearError,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
