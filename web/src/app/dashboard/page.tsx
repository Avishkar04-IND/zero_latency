"use client";

import React from "react";
import Link from "next/link";
import { useAuth } from "@/context/AuthContext";
import { AdminShell } from "@/components/layout/AdminShell";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import {
  Boxes,
  Layers,
  FileClock,
  ArrowRight,
  ShieldCheck,
  Building2,
  CheckCircle2,
  QrCode,
  Printer,
  ChevronRight,
  FileCheck2,
} from "lucide-react";

export default function DashboardPage() {
  const { user } = useAuth();

  return (
    <AdminShell>
      <div className="space-y-8">
        {/* Welcome & Organization Overview Banner */}
        <div className="rounded-3xl bg-gradient-to-r from-[#25233A] via-[#322F4C] to-[#1A1829] text-white p-6 sm:p-8 shadow-elevated relative overflow-hidden">
          <div className="absolute right-0 top-0 bottom-0 w-1/3 bg-gradient-to-l from-[#6D5CE7]/20 to-transparent pointer-events-none" />

          <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div className="space-y-2">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold tracking-wider uppercase bg-[#6D5CE7]/40 text-[#C4B5FD] border border-[#6D5CE7]/50">
                  Serialization Console
                </span>
                <span className="flex items-center gap-1.5 text-xs text-emerald-400 font-medium">
                  <span className="h-2 w-2 rounded-full bg-emerald-400 animate-ping" />
                  Live Operational Mode
                </span>
              </div>

              <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
                Welcome, {user?.name || "Administrator"}
              </h1>

              <div className="flex items-center gap-3 text-xs text-slate-300 flex-wrap">
                <span className="flex items-center gap-1 font-semibold text-white">
                  <Building2 className="h-3.5 w-3.5 text-[#A78BFA]" />
                  {user?.organization_name || "Sun Pharmaceutical Industries Ltd."}
                </span>
                <span>•</span>
                <span>{user?.branch_name || "Plant Unit 01 — Serialization Facility"}</span>
                <span>•</span>
                <span className="text-[#C4B5FD] font-medium">Role: {user?.role || "Company Admin"}</span>
              </div>
            </div>

            <div className="flex items-center gap-3 shrink-0">
              <div className="rounded-2xl bg-white/10 backdrop-blur border border-white/10 p-3.5 text-center min-w-[140px]">
                <span className="text-[10px] uppercase tracking-wider text-slate-300 font-semibold block">
                  Regulatory Target
                </span>
                <span className="text-sm font-extrabold text-white mt-0.5 block">
                  CDSCO Rule 96
                </span>
                <span className="text-[10px] text-emerald-300 font-medium mt-0.5 block">
                  GS1 DataMatrix Verified
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Primary Pharmaceutical Manufacturing Workflow Stepper */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
              <span>Manufacturer Execution Workflow</span>
            </h2>
            <span className="text-xs text-muted-foreground">Standard Serialization Pipeline</span>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            {[
              { step: "01", name: "Create Batch", sub: "Medicine & lot registration", icon: Boxes },
              { step: "02", name: "Generate Code", sub: "Unique 2D DataMatrix keys", icon: QrCode },
              { step: "03", name: "Generate Layout", sub: "Packaging constraint fit", icon: Layers },
              { step: "04", name: "Print", sub: "SVG / PDF packaging export", icon: Printer },
              { step: "05", name: "View Logs", sub: "Telemetry & audit history", icon: FileClock },
            ].map((item, idx) => {
              const Icon = item.icon;
              return (
                <div
                  key={item.step}
                  className="p-4 rounded-2xl bg-card border border-border/80 relative flex flex-col justify-between group hover:border-[#6D5CE7]/60 transition-all shadow-subtle hover:shadow-card"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-mono font-extrabold text-[#6D5CE7] bg-[#6D5CE7]/10 px-2 py-0.5 rounded-md">
                      {item.step}
                    </span>
                    <Icon className="h-4 w-4 text-muted-foreground group-hover:text-[#6D5CE7] transition-colors" />
                  </div>
                  <div className="mt-4">
                    <p className="font-bold text-sm text-foreground">{item.name}</p>
                    <p className="text-[11px] text-muted-foreground mt-0.5 leading-snug">{item.sub}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* The Three Primary Action Cards */}
        <div className="space-y-3">
          <h2 className="text-sm font-bold uppercase tracking-wider text-muted-foreground">
            Primary Administration Actions
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Action Card 1: CREATE BATCH / GENERATE CODE */}
            <Card className="flex flex-col justify-between border-border hover:border-[#6D5CE7] shadow-card hover:shadow-elevated transition-all group">
              <CardHeader className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="h-12 w-12 rounded-2xl bg-[#6D5CE7]/10 text-[#6D5CE7] flex items-center justify-center group-hover:bg-[#6D5CE7] group-hover:text-white transition-all shadow-sm">
                    <Boxes className="h-6 w-6" />
                  </div>
                  <Badge variant="secondary" className="font-bold text-[10px]">
                    STAGE 1 & 2
                  </Badge>
                </div>
                <div>
                  <CardTitle className="text-lg group-hover:text-[#6D5CE7] transition-colors">
                    CREATE BATCH / GENERATE CODE
                  </CardTitle>
                  <CardDescription className="text-xs mt-1.5 leading-relaxed">
                    Register new pharmaceutical manufacturing lots, specify dosage strength, batch numbers, and generate cryptographically signed GS1 DataMatrix serialization codes.
                  </CardDescription>
                </div>
              </CardHeader>

              <CardContent className="space-y-2 pt-0 text-xs text-muted-foreground">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600 dark:text-emerald-400 shrink-0" />
                  <span>Medicine formulation association</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600 dark:text-emerald-400 shrink-0" />
                  <span>Unique alphanumeric serial numbers</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600 dark:text-emerald-400 shrink-0" />
                  <span>Server-authoritative database registration</span>
                </div>
              </CardContent>

              <CardFooter className="pt-2 border-t border-border/40">
                <Link href="/batches" className="w-full">
                  <Button variant="primary" className="w-full gap-2 justify-center text-xs font-bold">
                    <span>Launch Batch Creation</span>
                    <ArrowRight className="h-3.5 w-3.5" />
                  </Button>
                </Link>
              </CardFooter>
            </Card>

            {/* Action Card 2: GENERATE LAYOUT */}
            <Card className="flex flex-col justify-between border-border hover:border-[#6D5CE7] shadow-card hover:shadow-elevated transition-all group">
              <CardHeader className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="h-12 w-12 rounded-2xl bg-indigo-500/10 text-indigo-600 flex items-center justify-center group-hover:bg-indigo-600 group-hover:text-white transition-all shadow-sm">
                    <Layers className="h-6 w-6" />
                  </div>
                  <Badge variant="secondary" className="font-bold text-[10px]">
                    STAGE 3 & 4
                  </Badge>
                </div>
                <div>
                  <CardTitle className="text-lg group-hover:text-indigo-600 transition-colors">
                    GENERATE LAYOUT
                  </CardTitle>
                  <CardDescription className="text-xs mt-1.5 leading-relaxed">
                    Compute packaging printable boundaries, calculate 2D code placement constraints, avoid cutting lines on blister packs, and preview print-ready SVG/PDF layouts.
                  </CardDescription>
                </div>
              </CardHeader>

              <CardContent className="space-y-2 pt-0 text-xs text-muted-foreground">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600 dark:text-emerald-400 shrink-0" />
                  <span>Package dimension constraint solver</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600 dark:text-emerald-400 shrink-0" />
                  <span>Micro-font & DataMatrix coordinate placement</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600 dark:text-emerald-400 shrink-0" />
                  <span>Vector print preview & export</span>
                </div>
              </CardContent>

              <CardFooter className="pt-2 border-t border-border/40">
                <Link href="/layout-generation" className="w-full">
                  <Button variant="outline" className="w-full gap-2 justify-center text-xs font-bold hover:bg-indigo-50 hover:text-indigo-600 hover:border-indigo-300">
                    <span>Open Layout Optimizer</span>
                    <ArrowRight className="h-3.5 w-3.5" />
                  </Button>
                </Link>
              </CardFooter>
            </Card>

            {/* Action Card 3: LOGS / HISTORY */}
            <Card className="flex flex-col justify-between border-border hover:border-[#6D5CE7] shadow-card hover:shadow-elevated transition-all group">
              <CardHeader className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="h-12 w-12 rounded-2xl bg-amber-500/10 text-amber-600 flex items-center justify-center group-hover:bg-amber-600 group-hover:text-white transition-all shadow-sm">
                    <FileClock className="h-6 w-6" />
                  </div>
                  <Badge variant="secondary" className="font-bold text-[10px]">
                    STAGE 5
                  </Badge>
                </div>
                <div>
                  <CardTitle className="text-lg group-hover:text-amber-600 transition-colors">
                    LOGS / HISTORY
                  </CardTitle>
                  <CardDescription className="text-xs mt-1.5 leading-relaxed">
                    Review live scan telemetry from consumer and clinical verification events, detect suspicious multi-location scans, and examine immutable audit logs.
                  </CardDescription>
                </div>
              </CardHeader>

              <CardContent className="space-y-2 pt-0 text-xs text-muted-foreground">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600 dark:text-emerald-400 shrink-0" />
                  <span>Real-time verification telemetry</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600 dark:text-emerald-400 shrink-0" />
                  <span>Suspicious scan & counterfeit alerts</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600 dark:text-emerald-400 shrink-0" />
                  <span>Tamper-proof audit logs</span>
                </div>
              </CardContent>

              <CardFooter className="pt-2 border-t border-border/40">
                <Link href="/logs" className="w-full">
                  <Button variant="outline" className="w-full gap-2 justify-center text-xs font-bold hover:bg-amber-50 hover:text-amber-700 hover:border-amber-300">
                    <span>Inspect Audit Logs</span>
                    <ArrowRight className="h-3.5 w-3.5" />
                  </Button>
                </Link>
              </CardFooter>
            </Card>
          </div>
        </div>

        {/* Regulatory & System Architecture Status */}
        <div className="rounded-2xl border border-border/80 bg-card p-4 sm:p-6 shadow-subtle">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-xl bg-emerald-500/10 text-emerald-600 flex items-center justify-center shrink-0">
                <ShieldCheck className="h-5 w-5" />
              </div>
              <div>
                <p className="text-sm font-bold text-foreground">
                  System Architecture: Active Production Foundation
                </p>
                <p className="text-xs text-muted-foreground">
                  FastAPI backend authoritative verification engine attached. All session records authenticated.
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2 text-xs font-mono text-muted-foreground bg-secondary/80 px-3 py-1.5 rounded-xl border border-border/60">
              <span className="h-2 w-2 rounded-full bg-emerald-500" />
              <span>API: /api/v1/auth & /api/v1/verification</span>
            </div>
          </div>
        </div>
      </div>
    </AdminShell>
  );
}
