"use client";

import React from "react";
import Link from "next/link";
import { AdminShell } from "@/components/layout/AdminShell";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { FileClock, ArrowLeft, Clock } from "lucide-react";

export default function LogsPlaceholderPage() {
  return (
    <AdminShell>
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="flex items-center gap-3">
          <Link href="/dashboard">
            <Button variant="outline" size="sm" className="gap-1.5 text-xs">
              <ArrowLeft className="h-3.5 w-3.5" />
              <span>Back to Dashboard</span>
            </Button>
          </Link>
        </div>

        <Card className="border-dashed border-2 border-border p-8 text-center space-y-4">
          <div className="h-16 w-16 mx-auto rounded-3xl bg-amber-500/10 text-amber-600 flex items-center justify-center">
            <FileClock className="h-8 w-8" />
          </div>
          <div className="space-y-1">
            <CardTitle className="text-xl font-extrabold">
              Stage 5: Verification Telemetry & Audit Logs
            </CardTitle>
            <CardDescription className="text-xs max-w-md mx-auto">
              This module displays real-time telemetry from consumer & hospital verification scans, suspicious duplicate code alerts, and immutable compliance logs for regulatory review.
            </CardDescription>
          </div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-secondary text-xs font-semibold text-muted-foreground">
            <Clock className="h-3.5 w-3.5 text-amber-600" />
            <span>Workflow Navigation Active — Ready for Telemetry Integration</span>
          </div>
        </Card>
      </div>
    </AdminShell>
  );
}
