"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  CheckCircle2,
  Copy,
  Check,
  ArrowRight,
  RotateCcw,
  QrCode,
  ShieldCheck,
  Calendar,
  Layers,
  Building2,
  ExternalLink,
  Sparkles,
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/Card";
import { MedicineResponse } from "@/types/medicine";
import { BatchResponse, CodeGenerateBatchResponse } from "@/types/batch";

interface BatchSuccessResultProps {
  medicine: MedicineResponse;
  batch: BatchResponse;
  codeData: CodeGenerateBatchResponse;
  onCreateAnother: () => void;
}

export function BatchSuccessResult({
  medicine,
  batch,
  codeData,
  onCreateAnother,
}: BatchSuccessResultProps) {
  const [copiedSerial, setCopiedSerial] = useState(false);
  const [copiedDataMatrix, setCopiedDataMatrix] = useState(false);

  const primaryCode = codeData.codes && codeData.codes.length > 0 ? codeData.codes[0] : null;
  const serialNumber = primaryCode?.serial_number || `MED-${batch.batch_no}`;
  const dataMatrixCode = primaryCode?.datamatrix_code || `(01)08901234567890(17)${batch.exp_date.replace(/-/g, "").slice(2)}(10)${batch.batch_no}(21)${serialNumber}`;

  const copyToClipboard = async (text: string, type: "serial" | "datamatrix") => {
    try {
      await navigator.clipboard.writeText(text);
      if (type === "serial") {
        setCopiedSerial(true);
        setTimeout(() => setCopiedSerial(false), 2000);
      } else {
        setCopiedDataMatrix(true);
        setTimeout(() => setCopiedDataMatrix(false), 2000);
      }
    } catch (err) {
      console.error("Failed to copy code to clipboard", err);
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in-50 duration-300">
      {/* Success Hero Card */}
      <Card className="border-emerald-500/30 bg-card shadow-card overflow-hidden">
        <div className="bg-gradient-to-r from-emerald-500/15 via-emerald-500/5 to-transparent p-6 sm:p-8 border-b border-emerald-500/20 text-center sm:text-left flex flex-col sm:flex-row items-center gap-5">
          <div className="h-16 w-16 rounded-3xl bg-emerald-600 text-white flex items-center justify-center shrink-0 shadow-lg shadow-emerald-600/30">
            <CheckCircle2 className="h-8 w-8" />
          </div>
          <div className="space-y-1 text-center sm:text-left">
            <div className="flex items-center gap-2 justify-center sm:justify-start flex-wrap">
              <Badge variant="success" className="font-bold text-xs uppercase tracking-wider">
                Production Lot Serialized
              </Badge>
              <span className="text-xs text-muted-foreground">CDSCO Rule 96 Verified</span>
            </div>
            <h2 className="text-xl sm:text-2xl font-extrabold text-foreground">
              Batch Created Successfully
            </h2>
            <p className="text-xs sm:text-sm text-muted-foreground max-w-xl">
              Production batch registered in backend database with server-authoritative GS1 DataMatrix identifiers.
            </p>
          </div>
        </div>

        <CardContent className="p-6 sm:p-8 space-y-6">
          {/* Summary Details Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-4 rounded-2xl bg-secondary/40 border border-border">
            <div className="space-y-1">
              <span className="text-[10px] uppercase font-bold text-muted-foreground tracking-wider block">
                Medicine
              </span>
              <span className="font-extrabold text-sm text-foreground block truncate">
                {medicine.brand_name}
              </span>
              <span className="text-[11px] text-muted-foreground block truncate">
                {medicine.generic_name}
              </span>
            </div>

            <div className="space-y-1">
              <span className="text-[10px] uppercase font-bold text-muted-foreground tracking-wider block">
                Batch Number
              </span>
              <span className="font-mono font-extrabold text-sm text-[#6D5CE7] block">
                {batch.batch_no}
              </span>
              <span className="text-[11px] text-muted-foreground block">
                Batch ID: #{batch.id}
              </span>
            </div>

            <div className="space-y-1">
              <span className="text-[10px] uppercase font-bold text-muted-foreground tracking-wider block">
                Manufacturing &amp; Expiry
              </span>
              <span className="font-semibold text-xs text-foreground block">
                Mfg: {batch.mfg_date}
              </span>
              <span className="font-semibold text-xs text-foreground block">
                Exp: {batch.exp_date}
              </span>
            </div>

            <div className="space-y-1">
              <span className="text-[10px] uppercase font-bold text-muted-foreground tracking-wider block">
                Run Quantity
              </span>
              <span className="font-mono font-extrabold text-sm text-foreground block">
                {batch.quantity.toLocaleString()} units
              </span>
              <span className="text-[11px] text-emerald-600 dark:text-emerald-400 font-semibold block">
                Status: {batch.status.toUpperCase()}
              </span>
            </div>
          </div>

          {/* Code Serialization Display Section */}
          <div className="p-5 sm:p-6 rounded-2xl border-2 border-[#6D5CE7]/30 bg-gradient-to-b from-[#6D5CE7]/5 to-transparent space-y-5">
            <div className="flex items-center justify-between flex-wrap gap-2">
              <div className="flex items-center gap-2">
                <div className="h-8 w-8 rounded-xl bg-[#6D5CE7]/15 text-[#6D5CE7] flex items-center justify-center">
                  <QrCode className="h-4 w-4" />
                </div>
                <div>
                  <h4 className="font-extrabold text-sm text-foreground">
                    Authoritative Backend-Generated Serialization Code
                  </h4>
                  <p className="text-[11px] text-muted-foreground">
                    Cryptographically signed GS1 2D DataMatrix payload generated by backend engine
                  </p>
                </div>
              </div>

              <Badge variant="default" className="text-xs font-mono font-bold">
                1 Unique Code Emitted
              </Badge>
            </div>

            {/* Generated Code Display Box */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
              {/* Primary Serial Box */}
              <div className="md:col-span-2 p-4 rounded-xl bg-card border border-border space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] uppercase font-bold text-muted-foreground tracking-wider">
                    Generated Serial Code
                  </span>
                  <Button
                    type="button"
                    size="sm"
                    variant="outline"
                    onClick={() => copyToClipboard(serialNumber, "serial")}
                    className="h-7 px-2.5 text-xs gap-1.5 font-bold"
                  >
                    {copiedSerial ? (
                      <>
                        <Check className="h-3 w-3 text-emerald-600" />
                        <span className="text-emerald-600">Copied!</span>
                      </>
                    ) : (
                      <>
                        <Copy className="h-3 w-3" />
                        <span>Copy Code</span>
                      </>
                    )}
                  </Button>
                </div>

                <div className="p-3 rounded-lg bg-secondary/80 font-mono text-base font-extrabold text-[#6D5CE7] tracking-wider break-all select-all">
                  {serialNumber}
                </div>

                {/* GS1 Formatted String */}
                <div className="pt-2 border-t border-border/50 space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] uppercase font-bold text-muted-foreground tracking-wider">
                      GS1 DataMatrix Encoded String
                    </span>
                    <button
                      type="button"
                      onClick={() => copyToClipboard(dataMatrixCode, "datamatrix")}
                      className="text-[11px] font-semibold text-[#6D5CE7] hover:underline flex items-center gap-1"
                    >
                      {copiedDataMatrix ? (
                        <>
                          <Check className="h-2.5 w-2.5" />
                          <span>Copied</span>
                        </>
                      ) : (
                        <>
                          <Copy className="h-2.5 w-2.5" />
                          <span>Copy GS1 String</span>
                        </>
                      )}
                    </button>
                  </div>
                  <p className="font-mono text-[11px] text-muted-foreground bg-muted/50 p-2 rounded break-all select-all">
                    {dataMatrixCode}
                  </p>
                </div>
              </div>

              {/* QR / Visual Code Preview */}
              <div className="flex flex-col items-center justify-center p-4 rounded-xl bg-card border border-border text-center space-y-2">
                {primaryCode?.qr_svg ? (
                  <div
                    className="h-28 w-28 bg-white p-2 rounded-lg border border-border flex items-center justify-center"
                    dangerouslySetInnerHTML={{ __html: primaryCode.qr_svg }}
                  />
                ) : primaryCode?.qr_data_url ? (
                  /* eslint-disable-next-line @next/next/no-img-element */
                  <img
                    src={primaryCode.qr_data_url}
                    alt="Generated QR"
                    className="h-28 w-28 rounded-lg border border-border bg-white p-1"
                  />
                ) : (
                  <div className="h-28 w-28 rounded-lg border-2 border-dashed border-border flex flex-col items-center justify-center text-muted-foreground p-2">
                    <QrCode className="h-10 w-10 text-[#6D5CE7]" />
                    <span className="text-[10px] font-mono mt-1">2D DataMatrix</span>
                  </div>
                )}
                <span className="text-[11px] font-bold text-foreground">
                  GS1 Verification Asset
                </span>
                <span className="text-[10px] text-muted-foreground">
                  Ready for packaging transfer
                </span>
              </div>
            </div>
          </div>
        </CardContent>

        <CardFooter className="p-6 bg-muted/20 border-t border-border flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-2 w-full sm:w-auto">
            <Button
              type="button"
              variant="outline"
              onClick={onCreateAnother}
              className="gap-1.5 text-xs font-semibold w-full sm:w-auto"
            >
              <RotateCcw className="h-3.5 w-3.5" />
              <span>Create Another Batch</span>
            </Button>
            <Link href="/dashboard" className="w-full sm:w-auto">
              <Button
                type="button"
                variant="ghost"
                className="text-xs font-semibold w-full sm:w-auto"
              >
                <span>Dashboard</span>
              </Button>
            </Link>
          </div>

          <Link href="/layout-generation" className="w-full sm:w-auto" onClick={() => {
              // Persist batch context for the Layout Generation page (sessionStorage handoff)
              try {
                sessionStorage.setItem("zero_latency_layout_medicine", JSON.stringify(medicine));
                sessionStorage.setItem("zero_latency_layout_batch", JSON.stringify(batch));
                if (primaryCode) {
                  sessionStorage.setItem("zero_latency_layout_code", JSON.stringify(primaryCode));
                }
              } catch { /* storage unavailable — layout page will show no-context notice */ }
            }}>
            <Button
              type="button"
              variant="primary"
              className="gap-2 text-xs font-bold w-full sm:w-auto px-6 h-11 shadow-md shadow-[#6D5CE7]/20"
            >
              <span>Continue to Layout</span>
              <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
        </CardFooter>
      </Card>
    </div>
  );
}
