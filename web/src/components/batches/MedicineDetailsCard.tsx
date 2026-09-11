"use client";

import React from "react";
import {
  Pill,
  Building2,
  AlertTriangle,
  FileText,
  ShieldCheck,
  RotateCcw,
  Sparkles,
  ThermometerSnowflake,
  Activity,
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import { MedicineResponse } from "@/types/medicine";

interface MedicineDetailsCardProps {
  medicine: MedicineResponse;
  onChangeMedicine?: () => void;
  compact?: boolean;
}

export function MedicineDetailsCard({
  medicine,
  onChangeMedicine,
  compact = false,
}: MedicineDetailsCardProps) {
  return (
    <Card className="border-[#6D5CE7]/30 bg-card shadow-subtle overflow-hidden">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-[#6D5CE7]/15 via-[#6D5CE7]/10 to-transparent p-4 sm:p-5 border-b border-[#6D5CE7]/20 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="h-11 w-11 rounded-2xl bg-[#6D5CE7] text-white flex items-center justify-center shrink-0 shadow-md shadow-[#6D5CE7]/30">
            <Pill className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <h3 className="font-extrabold text-base sm:text-lg text-foreground">
                {medicine.brand_name}
              </h3>
              <Badge variant="default" className="font-mono font-bold text-xs bg-[#6D5CE7] text-white">
                {medicine.strength}
              </Badge>
              {medicine.schedule_type && (
                <Badge variant="secondary" className="text-[10px] font-bold">
                  {medicine.schedule_type}
                </Badge>
              )}
            </div>
            <p className="text-xs text-muted-foreground mt-0.5 font-medium">
              Generic: {medicine.generic_name}
            </p>
          </div>
        </div>

        {onChangeMedicine && (
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={onChangeMedicine}
            className="gap-1.5 text-xs self-start sm:self-auto border-border/80 hover:border-[#6D5CE7]"
          >
            <RotateCcw className="h-3.5 w-3.5" />
            <span>Change Medicine</span>
          </Button>
        )}
      </div>

      <CardContent className="p-4 sm:p-6 space-y-5">
        {/* Core Registered Specifications Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
          <div className="p-3 rounded-xl bg-secondary/50 border border-border/50 space-y-1">
            <span className="text-[10px] uppercase font-bold text-muted-foreground tracking-wider block">
              Dosage Form
            </span>
            <span className="font-bold text-foreground block">{medicine.dosage_form}</span>
            {medicine.coating_type && (
              <span className="text-[11px] text-muted-foreground block">{medicine.coating_type}</span>
            )}
          </div>

          <div className="p-3 rounded-xl bg-secondary/50 border border-border/50 space-y-1">
            <span className="text-[10px] uppercase font-bold text-muted-foreground tracking-wider block">
              Therapeutic Class
            </span>
            <span className="font-bold text-foreground block truncate">{medicine.category}</span>
            <span className="text-[11px] text-muted-foreground block">CDSCO Approved</span>
          </div>

          <div className="p-3 rounded-xl bg-secondary/50 border border-border/50 space-y-1">
            <span className="text-[10px] uppercase font-bold text-muted-foreground tracking-wider block">
              Manufacturer
            </span>
            <span className="font-bold text-foreground block truncate">{medicine.manufacturer}</span>
            <span className="text-[11px] text-muted-foreground block">Org ID: #{medicine.organization_id}</span>
          </div>

          <div className="p-3 rounded-xl bg-secondary/50 border border-border/50 space-y-1">
            <span className="text-[10px] uppercase font-bold text-muted-foreground tracking-wider block">
              Physical Form
            </span>
            <span className="font-bold text-foreground block">
              {medicine.tablet_shape || "Standard"} ({medicine.tablet_color || "White"})
            </span>
            <span className="text-[11px] text-muted-foreground block">
              Score: {medicine.score_line || "None"}
            </span>
          </div>
        </div>

        {/* Active Pharmaceutical Ingredients (APIs) */}
        {medicine.active_ingredients && medicine.active_ingredients.length > 0 && (
          <div className="space-y-2">
            <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
              <Activity className="h-3.5 w-3.5 text-[#6D5CE7]" />
              <span>Active Pharmaceutical Ingredients (API)</span>
            </span>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {medicine.active_ingredients.map((ing, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-2.5 rounded-xl border border-border bg-card/60 text-xs"
                >
                  <span className="font-semibold text-foreground">{ing.name}</span>
                  <span className="font-mono font-bold text-[#6D5CE7] bg-[#6D5CE7]/10 px-2 py-0.5 rounded-md">
                    {ing.strength} {ing.unit}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Clinical Indications & Warnings */}
        {!compact && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            {medicine.indications && (
              <div className="p-3.5 rounded-xl bg-card border border-border space-y-1.5">
                <span className="font-bold text-foreground flex items-center gap-1.5">
                  <FileText className="h-3.5 w-3.5 text-[#6D5CE7]" />
                  <span>Approved Indications</span>
                </span>
                <p className="text-muted-foreground leading-relaxed text-[11px]">
                  {medicine.indications}
                </p>
              </div>
            )}

            {medicine.warnings_and_precautions && (
              <div className="p-3.5 rounded-xl bg-amber-500/5 border border-amber-500/20 space-y-1.5">
                <span className="font-bold text-amber-700 dark:text-amber-400 flex items-center gap-1.5">
                  <AlertTriangle className="h-3.5 w-3.5 text-amber-600 dark:text-amber-400" />
                  <span>Warnings &amp; Precautions</span>
                </span>
                <p className="text-amber-900/80 dark:text-amber-200/80 leading-relaxed text-[11px]">
                  {medicine.warnings_and_precautions}
                </p>
              </div>
            )}
          </div>
        )}

        {/* Storage Conditions */}
        {medicine.storage_conditions && (
          <div className="flex items-center gap-2 p-2.5 rounded-xl bg-secondary/40 border border-border/40 text-[11px] text-muted-foreground">
            <ThermometerSnowflake className="h-4 w-4 text-[#6D5CE7] shrink-0" />
            <span>
              <strong className="text-foreground font-semibold">Storage: </strong>
              {medicine.storage_conditions}
            </span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
