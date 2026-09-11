"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Boxes,
  Layers,
  FileClock,
  ShieldCheck,
  CheckCircle2,
} from "lucide-react";
import { Logo } from "@/components/branding/Logo";
import { cn } from "@/lib/utils";

interface AdminSidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

export function AdminSidebar({ isOpen, onClose }: AdminSidebarProps) {
  const pathname = usePathname();

  const navigation = [
    {
      name: "Dashboard",
      href: "/dashboard",
      icon: LayoutDashboard,
      current: pathname === "/dashboard" || pathname === "/admin/dashboard",
    },
    {
      name: "Create Batch",
      href: "/batches",
      icon: Boxes,
      current: pathname.startsWith("/batches"),
    },
    {
      name: "Layout Generation",
      href: "/layout-generation",
      icon: Layers,
      current: pathname.startsWith("/layout-generation"),
    },
    {
      name: "Logs / History",
      href: "/logs",
      icon: FileClock,
      current: pathname.startsWith("/logs"),
    },
  ];

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm md:hidden transition-opacity"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-50 flex w-64 flex-col border-r border-border bg-card transition-transform duration-200 ease-in-out md:static md:translate-x-0",
          isOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        {/* Brand Header */}
        <div className="flex h-16 items-center justify-between border-b border-border px-6">
          <Logo size="sm" subtitle="Admin Console" />
        </div>

        {/* Navigation items */}
        <nav className="flex-1 space-y-1.5 px-4 py-6">
          <div className="px-3 pb-2 text-[11px] font-bold uppercase tracking-wider text-muted-foreground/80">
            Manufacturing Workflow
          </div>

          {navigation.map((item) => {
            const Icon = item.icon;
            return (
              <Link
                key={item.name}
                href={item.href}
                onClick={() => onClose && onClose()}
                className={cn(
                  "group flex items-center gap-3 rounded-xl px-3.5 py-3 text-sm font-semibold transition-all",
                  item.current
                    ? "bg-[#6D5CE7] text-white shadow-sm shadow-[#6D5CE7]/30 font-bold"
                    : "text-muted-foreground hover:bg-secondary hover:text-foreground"
                )}
                aria-current={item.current ? "page" : undefined}
              >
                <Icon
                  className={cn(
                    "h-5 w-5 shrink-0 transition-colors",
                    item.current
                      ? "text-white"
                      : "text-muted-foreground group-hover:text-foreground"
                  )}
                />
                <span>{item.name}</span>
              </Link>
            );
          })}
        </nav>

        {/* Regulatory & Security Compliance Box */}
        <div className="p-4 m-4 rounded-2xl bg-secondary/60 border border-border/80">
          <div className="flex items-center gap-2 text-xs font-bold text-foreground">
            <ShieldCheck className="h-4 w-4 text-[#6D5CE7]" />
            <span>Pharma Serialization</span>
          </div>
          <p className="mt-1 text-[11px] text-muted-foreground leading-snug">
            GS1 DataMatrix & CDSCO 2024 compliance active.
          </p>
          <div className="mt-2 flex items-center gap-1.5 text-[10px] font-bold text-emerald-600 dark:text-emerald-400">
            <CheckCircle2 className="h-3 w-3" />
            <span>Cryptographic Ledger Synced</span>
          </div>
        </div>

        {/* Footer info */}
        <div className="border-t border-border px-6 py-3 text-[10px] text-muted-foreground flex justify-between items-center">
          <span>Zero Latency Platform</span>
          <span>v1.0.0</span>
        </div>
      </aside>
    </>
  );
}
