"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import { AdminHeader } from "./AdminHeader";
import { AdminSidebar } from "./AdminSidebar";
import { ShieldCheck, Loader2 } from "lucide-react";

interface AdminShellProps {
  children: React.ReactNode;
}

export function AdminShell({ children }: AdminShellProps) {
  const router = useRouter();
  const { user, isAuthenticated, isLoading } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [isLoading, isAuthenticated, router]);

  // Loading state while verifying credentials or restoring session
  if (isLoading) {
    return (
      <div className="flex min-h-screen w-full flex-col items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-4 p-8 rounded-2xl bg-card border border-border shadow-sm max-w-sm text-center">
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-tr from-[#5B48D9] to-[#8B7CF6] text-white shadow-md shadow-[#6D5CE7]/30 animate-pulse">
            <ShieldCheck className="h-6 w-6" />
          </div>
          <div>
            <h2 className="text-base font-bold text-foreground">
              Authenticating Admin Session
            </h2>
            <p className="mt-1 text-xs text-muted-foreground">
              Verifying credentials with pharmaceutical ledger...
            </p>
          </div>
          <div className="flex items-center gap-2 text-xs font-semibold text-[#6D5CE7]">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span>Establishing secure session</span>
          </div>
        </div>
      </div>
    );
  }

  // Not authenticated: wait for redirect
  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="flex min-h-screen bg-background">
      {/* Sidebar */}
      <AdminSidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      {/* Main Content Area */}
      <div className="flex flex-1 flex-col overflow-x-hidden">
        <AdminHeader onMenuClick={() => setSidebarOpen(true)} />

        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
