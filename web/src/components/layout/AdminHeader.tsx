"use client";

import React from "react";
import { useAuth } from "@/context/AuthContext";
import { Building2, MapPin, User, LogOut, Shield } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";

interface AdminHeaderProps {
  onMenuClick?: () => void;
}

export function AdminHeader({ onMenuClick }: AdminHeaderProps) {
  const { user, logout, isLoading } = useAuth();

  return (
    <header className="sticky top-0 z-30 flex h-16 w-full items-center justify-between border-b border-border bg-card/95 px-4 sm:px-6 backdrop-blur supports-[backdrop-filter]:bg-card/75">
      {/* Mobile Menu trigger & context info */}
      <div className="flex items-center gap-4">
        {onMenuClick && (
          <button
            onClick={onMenuClick}
            className="md:hidden rounded-lg p-2 hover:bg-accent text-foreground"
            aria-label="Toggle navigation menu"
          >
            <svg
              className="h-5 w-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 6h16M4 12h16M4 18h16"
              />
            </svg>
          </button>
        )}

        {/* Company & Branch Context (from authenticated session) */}
        <div className="hidden sm:flex items-center gap-4 text-xs">
          {user?.organization_name && (
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-secondary/80 text-foreground font-medium border border-border/50">
              <Building2 className="h-3.5 w-3.5 text-[#6D5CE7]" />
              <span className="truncate max-w-[200px] sm:max-w-[260px]">
                {user.organization_name}
              </span>
            </div>
          )}

          {user?.branch_name && (
            <div className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-secondary/80 text-muted-foreground font-medium border border-border/50">
              <MapPin className="h-3.5 w-3.5 text-muted-foreground" />
              <span className="truncate max-w-[220px]">
                {user.branch_name}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Admin Identity & Actions */}
      <div className="flex items-center gap-3">
        {/* Admin profile pill */}
        <div className="flex items-center gap-3 pl-3 pr-1 py-1 rounded-xl bg-secondary/50 border border-border/60">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[#6D5CE7]/10 text-[#6D5CE7] font-bold text-xs">
            <User className="h-4 w-4" />
          </div>

          <div className="flex flex-col text-left pr-2">
            <span className="text-xs font-bold text-foreground leading-tight truncate max-w-[160px]">
              {user?.name || "Admin Officer"}
            </span>
            <span className="text-[10px] font-semibold text-[#6D5CE7] uppercase tracking-wider flex items-center gap-1">
              <Shield className="h-2.5 w-2.5" />
              {user?.role === "company_admin"
                ? "Company Admin"
                : user?.role || "Administrator"}
            </span>
          </div>
        </div>

        {/* Logout Button */}
        <Button
          variant="outline"
          size="sm"
          onClick={() => logout()}
          disabled={isLoading}
          className="gap-1.5 text-xs text-muted-foreground hover:text-destructive hover:border-destructive/40"
          aria-label="Logout from administration portal"
        >
          <LogOut className="h-3.5 w-3.5" />
          <span className="hidden sm:inline">Sign Out</span>
        </Button>
      </div>
    </header>
  );
}
