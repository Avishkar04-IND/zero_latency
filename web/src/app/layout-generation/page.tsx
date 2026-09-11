"use client";

import React, { useState, useCallback } from "react";
import Link from "next/link";
import { AdminShell } from "@/components/layout/AdminShell";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import {
  Layers,
  ArrowLeft,
  Play,
  RotateCcw,
  Download,
  AlertCircle,
  Loader2,
  CheckCircle2,
  Package,
  Pill,
  ChevronDown,
  ChevronUp,
  BarChart3,
  Eye,
} from "lucide-react";
import {
  optimizeLayout,
  previewLayout,
  downloadLayoutPdf,
  LAYOUT_ENGINE_BASE_URL,
} from "@/services/api/layout";
import type {
  LayoutOptimizeRequest,
  LayoutOptimizeResponse,
  LayoutPreviewResponse,
  PackageDimensions,
  LayoutAlternative,
} from "@/types/layout";
import { DEFAULT_PACKAGE_DIMENSIONS } from "@/types/layout";
import type { MedicineResponse } from "@/types/medicine";
import type { BatchResponse, CodeResponse } from "@/types/batch";

// ─── Batch context recovery from sessionStorage ─────────────────────────────
//
// The batch workflow lives at /batches (a separate client component).
// After successful creation the user clicks "Continue to Layout" which
// navigates here. To avoid prop-drilling across page boundaries we use
// sessionStorage as the handoff mechanism — the same pattern used by
// the assistant module for verified medicine context.

const SESSION_KEY_MEDICINE = "zero_latency_layout_medicine";
const SESSION_KEY_BATCH = "zero_latency_layout_batch";
const SESSION_KEY_CODE = "zero_latency_layout_code";

/** Called from BatchSuccessResult (injected via storage write) */
function loadBatchContextFromSession(): {
  medicine: MedicineResponse | null;
  batch: BatchResponse | null;
  code: CodeResponse | null;
} {
  if (typeof window === "undefined")
    return { medicine: null, batch: null, code: null };
  try {
    const m = sessionStorage.getItem(SESSION_KEY_MEDICINE);
    const b = sessionStorage.getItem(SESSION_KEY_BATCH);
    const c = sessionStorage.getItem(SESSION_KEY_CODE);
    return {
      medicine: m ? (JSON.parse(m) as MedicineResponse) : null,
      batch: b ? (JSON.parse(b) as BatchResponse) : null,
      code: c ? (JSON.parse(c) as CodeResponse) : null,
    };
  } catch {
    return { medicine: null, batch: null, code: null };
  }
}

// ─── Dimension form component ─────────────────────────────────────────────────

interface DimFieldProps {
  id: string;
  label: string;
  value: number;
  onChange: (v: number) => void;
  min?: number;
  step?: number;
  unit?: string;
}

function DimField({ id, label, value, onChange, min = 1, step = 0.5, unit = "mm" }: DimFieldProps) {
  return (
    <div className="space-y-1">
      <label htmlFor={id} className="text-[11px] font-bold text-muted-foreground uppercase tracking-wide">
        {label} <span className="font-normal normal-case">({unit})</span>
      </label>
      <input
        id={id}
        type="number"
        min={min}
        step={step}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value) || min)}
        className="w-full rounded-lg border border-border bg-background px-3 py-1.5 text-sm font-mono text-foreground focus:outline-none focus:ring-2 focus:ring-[#6D5CE7]/40"
      />
    </div>
  );
}

// ─── Score bar component ──────────────────────────────────────────────────────

function ScoreBar({ label, value }: { label: string; value: number | null | undefined }) {
  const pct = value != null ? Math.round(value * 100) : null;
  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-[11px]">
        <span className="text-muted-foreground font-medium">{label}</span>
        <span className="font-bold text-foreground">
          {pct != null ? `${pct}%` : "—"}
        </span>
      </div>
      <div className="h-1.5 w-full rounded-full bg-muted overflow-hidden">
        <div
          className="h-full rounded-full bg-gradient-to-r from-[#6D5CE7] to-indigo-400 transition-all duration-700"
          style={{ width: `${pct ?? 0}%` }}
        />
      </div>
    </div>
  );
}

// ─── Strategy badge ───────────────────────────────────────────────────────────

function StrategyBadge({ strategy }: { strategy: string }) {
  const colours: Record<string, string> = {
    ACCESSIBILITY: "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20",
    BALANCED: "bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/20",
    COST: "bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20",
  };
  return (
    <span
      className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold border ${
        colours[strategy] ?? "bg-secondary text-foreground border-border"
      }`}
    >
      {strategy}
    </span>
  );
}

// ─── Main page ────────────────────────────────────────────────────────────────

export default function LayoutGenerationPage() {
  // Batch context from session (populated by the batch creation workflow)
  const [sessionCtx] = useState(() => loadBatchContextFromSession());

  // Dimension form
  const [dims, setDims] = useState<PackageDimensions>(DEFAULT_PACKAGE_DIMENSIONS);
  const setDim = (key: keyof PackageDimensions) => (val: number) =>
    setDims((prev) => ({ ...prev, [key]: val }));

  // Result state
  const [optimizeResult, setOptimizeResult] = useState<LayoutOptimizeResponse | null>(null);
  const [previewResult, setPreviewResult] = useState<LayoutPreviewResponse | null>(null);
  const [svgExpanded, setSvgExpanded] = useState(false);
  const [altExpanded, setAltExpanded] = useState(false);

  // Operation state
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [isPreviewing, setIsPreviewing] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // ── Build request from session context + dimension form ──────────────────
  const buildRequest = useCallback((): LayoutOptimizeRequest => {
    const { medicine, batch, code } = sessionCtx;
    return {
      package: {
        package_width_mm: dims.package_width_mm,
        package_height_mm: dims.package_height_mm,
        printing_area_width_mm: dims.printing_area_width_mm,
        printing_area_height_mm: dims.printing_area_height_mm,
        printing_area_x_mm:
          (dims.package_width_mm - dims.printing_area_width_mm) / 2,
        printing_area_y_mm:
          (dims.package_height_mm - dims.printing_area_height_mm) / 2,
      },
      tablet: {
        tablet_count: dims.tablet_count,
        tablet_diameter_mm: dims.tablet_diameter_mm,
      },
      ...(medicine && {
        medicine: {
          name: medicine.brand_name,
          dosage: medicine.strength,
          manufacturer: medicine.manufacturer,
        },
      }),
      ...(batch && {
        batch: {
          batch_number: batch.batch_no,
          manufacturing_date: batch.mfg_date,
          expiry_date: batch.exp_date,
        },
      }),
      ...(code && {
        code: {
          type: "QR",
          value: code.serial_number,
          min_size_mm: 13.0,
          serial_number: code.serial_number,
        },
      }),
      optimization_target: "RECOMMEND",
    };
  }, [dims, sessionCtx]);

  // ── Handlers ─────────────────────────────────────────────────────────────
  const handleOptimize = async () => {
    setError(null);
    setOptimizeResult(null);
    setPreviewResult(null);
    setIsOptimizing(true);
    try {
      const req = buildRequest();
      const result = await optimizeLayout(req);
      setOptimizeResult(result);
    } catch (err: unknown) {
      setError(
        err instanceof Error
          ? err.message
          : "Layout optimization failed. Check that the Layout Engine is running."
      );
    } finally {
      setIsOptimizing(false);
    }
  };

  const handlePreview = async () => {
    setError(null);
    setIsPreviewing(true);
    try {
      const req = buildRequest();
      const result = await previewLayout(req);
      setPreviewResult(result);
      setSvgExpanded(true);
    } catch (err: unknown) {
      setError(
        err instanceof Error ? err.message : "SVG preview failed."
      );
    } finally {
      setIsPreviewing(false);
    }
  };

  const handleDownloadPdf = async () => {
    setError(null);
    setIsDownloading(true);
    try {
      const req = buildRequest();
      const blob = await downloadLayoutPdf(req);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      const batchNo = sessionCtx.batch?.batch_no ?? "layout";
      a.href = url;
      a.download = `layout-${batchNo}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (err: unknown) {
      setError(
        err instanceof Error ? err.message : "PDF download failed."
      );
    } finally {
      setIsDownloading(false);
    }
  };

  const handleReset = () => {
    setOptimizeResult(null);
    setPreviewResult(null);
    setError(null);
    setSvgExpanded(false);
    setAltExpanded(false);
    setDims(DEFAULT_PACKAGE_DIMENSIONS);
  };

  // ─── Derived ─────────────────────────────────────────────────────────────
  const { medicine, batch, code } = sessionCtx;
  const hasContext = !!(medicine && batch && code);
  const primaryCode = code;

  return (
    <AdminShell>
      <div className="max-w-5xl mx-auto space-y-6 pb-12">
        {/* Top nav */}
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div className="flex items-center gap-3">
            <Link href="/dashboard">
              <Button variant="outline" size="sm" className="gap-1.5 text-xs">
                <ArrowLeft className="h-3.5 w-3.5" />
                <span>Back to Dashboard</span>
              </Button>
            </Link>
            <div className="h-4 w-px bg-border hidden sm:block" />
            <span className="text-xs text-muted-foreground font-medium">
              Packaging Layout Optimization
            </span>
          </div>
          <Badge variant="secondary" className="gap-1 font-semibold text-[11px]">
            <Layers className="h-3.5 w-3.5 text-indigo-500" />
            <span>Layout Engine v1</span>
          </Badge>
        </div>

        {/* Page header */}
        <div className="space-y-1">
          <h1 className="text-xl sm:text-2xl font-extrabold text-foreground tracking-tight flex items-center gap-2.5">
            <div className="h-8 w-8 rounded-xl bg-indigo-500/10 text-indigo-600 flex items-center justify-center">
              <Layers className="h-4 w-4" />
            </div>
            Stage 3 &amp; 4: Packaging Layout Optimization &amp; Preview
          </h1>
          <p className="text-xs sm:text-sm text-muted-foreground max-w-2xl">
            Compute blister-pack printing boundaries, calculate 2D code placement, avoid cutting
            zones, and preview print-ready vector layouts via the Layout Engine.
          </p>
        </div>

        {/* Error banner */}
        {error && (
          <div className="p-4 rounded-2xl border border-destructive/30 bg-destructive/5 flex items-start gap-3 text-destructive animate-in fade-in-50">
            <AlertCircle className="h-5 w-5 shrink-0 mt-0.5" />
            <div className="space-y-1">
              <h4 className="font-bold text-xs uppercase tracking-wide">Layout Engine Error</h4>
              <p className="text-xs">{error}</p>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* ── LEFT COLUMN: Context + Form ───────────────────────────── */}
          <div className="lg:col-span-1 space-y-4">
            {/* Batch context card */}
            <Card className="border-border/80">
              <CardHeader className="pb-3">
                <div className="flex items-center gap-2">
                  <div className="h-7 w-7 rounded-lg bg-[#6D5CE7]/10 text-[#6D5CE7] flex items-center justify-center">
                    <Package className="h-3.5 w-3.5" />
                  </div>
                  <div>
                    <CardTitle className="text-sm">Batch Context</CardTitle>
                    <CardDescription className="text-[11px]">From Create Batch workflow</CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="pt-0 space-y-3">
                {hasContext ? (
                  <>
                    <div className="p-3 rounded-xl bg-emerald-500/5 border border-emerald-500/20 space-y-2">
                      <div className="flex items-center gap-1.5 text-emerald-600 dark:text-emerald-400">
                        <CheckCircle2 className="h-3.5 w-3.5" />
                        <span className="text-[11px] font-bold">Batch context loaded</span>
                      </div>
                      <div className="space-y-1 text-[11px] text-muted-foreground">
                        <p>
                          <span className="font-semibold text-foreground">{medicine!.brand_name}</span>
                          {" — "}{medicine!.generic_name}
                        </p>
                        <p>Batch: <span className="font-mono text-[#6D5CE7] font-bold">{batch!.batch_no}</span></p>
                        <p>Serial: <span className="font-mono font-bold text-foreground">{primaryCode!.serial_number}</span></p>
                        <p>Mfg: {batch!.mfg_date} · Exp: {batch!.exp_date}</p>
                      </div>
                    </div>
                  </>
                ) : (
                  <div className="p-3 rounded-xl bg-secondary/60 border border-border/60 space-y-2">
                    <div className="flex items-center gap-1.5 text-amber-600">
                      <AlertCircle className="h-3.5 w-3.5" />
                      <span className="text-[11px] font-bold">No batch context</span>
                    </div>
                    <p className="text-[11px] text-muted-foreground">
                      Navigate from{" "}
                      <Link href="/batches" className="text-[#6D5CE7] font-semibold hover:underline">
                        Create Batch
                      </Link>{" "}
                      to carry medicine, batch, and serial data here automatically. You can still run a
                      layout with custom dimensions below.
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Package dimension form */}
            <Card className="border-border/80">
              <CardHeader className="pb-3">
                <div className="flex items-center gap-2">
                  <div className="h-7 w-7 rounded-lg bg-[#6D5CE7]/10 text-[#6D5CE7] flex items-center justify-center">
                    <Pill className="h-3.5 w-3.5" />
                  </div>
                  <div>
                    <CardTitle className="text-sm">Package &amp; Tablet Dimensions</CardTitle>
                    <CardDescription className="text-[11px]">Physical blister pack parameters</CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="pt-0">
                <div className="grid grid-cols-2 gap-3">
                  <DimField id="pkg-w" label="Pack width" value={dims.package_width_mm} onChange={setDim("package_width_mm")} />
                  <DimField id="pkg-h" label="Pack height" value={dims.package_height_mm} onChange={setDim("package_height_mm")} />
                  <DimField id="print-w" label="Print area W" value={dims.printing_area_width_mm} onChange={setDim("printing_area_width_mm")} />
                  <DimField id="print-h" label="Print area H" value={dims.printing_area_height_mm} onChange={setDim("printing_area_height_mm")} />
                  <DimField id="tab-count" label="Tablet count" value={dims.tablet_count} onChange={setDim("tablet_count")} min={1} step={1} unit="pcs" />
                  <DimField id="tab-dia" label="Tablet ⌀" value={dims.tablet_diameter_mm} onChange={setDim("tablet_diameter_mm")} />
                </div>

                <p className="text-[10px] text-muted-foreground mt-3">
                  Dimensions are session-only and are not persisted to the backend database.
                </p>
              </CardContent>
              <CardFooter className="flex flex-col gap-2 pt-0">
                <Button
                  type="button"
                  variant="primary"
                  className="w-full gap-2 text-xs font-bold"
                  onClick={handleOptimize}
                  disabled={isOptimizing || isPreviewing || isDownloading}
                  id="btn-run-optimization"
                >
                  {isOptimizing ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      <span>Optimizing...</span>
                    </>
                  ) : (
                    <>
                      <Play className="h-4 w-4" />
                      <span>Run Layout Optimization</span>
                    </>
                  )}
                </Button>

                {optimizeResult?.success && (
                  <div className="flex gap-2 w-full">
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      className="flex-1 gap-1.5 text-xs"
                      onClick={handlePreview}
                      disabled={isPreviewing}
                      id="btn-preview-svg"
                    >
                      {isPreviewing ? (
                        <Loader2 className="h-3.5 w-3.5 animate-spin" />
                      ) : (
                        <Eye className="h-3.5 w-3.5" />
                      )}
                      <span>SVG Preview</span>
                    </Button>
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      className="flex-1 gap-1.5 text-xs"
                      onClick={handleDownloadPdf}
                      disabled={isDownloading}
                      id="btn-download-pdf"
                    >
                      {isDownloading ? (
                        <Loader2 className="h-3.5 w-3.5 animate-spin" />
                      ) : (
                        <Download className="h-3.5 w-3.5" />
                      )}
                      <span>PDF</span>
                    </Button>
                  </div>
                )}

                {(optimizeResult || error) && (
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="w-full text-xs gap-1.5 text-muted-foreground"
                    onClick={handleReset}
                    id="btn-reset"
                  >
                    <RotateCcw className="h-3.5 w-3.5" />
                    <span>Reset</span>
                  </Button>
                )}
              </CardFooter>
            </Card>

            {/* Layout Engine connection info */}
            <p className="text-[10px] text-muted-foreground text-center px-2">
              Connected to Layout Engine at{" "}
              <span className="font-mono">{LAYOUT_ENGINE_BASE_URL}</span>
              <br />
              <span className="opacity-60">POST /api/v1/layout/optimize</span>
            </p>
          </div>

          {/* ── RIGHT COLUMN: Results ──────────────────────────────────── */}
          <div className="lg:col-span-2 space-y-4">
            {!optimizeResult && !isOptimizing && (
              <Card className="border-dashed border-2 border-border p-8 text-center space-y-3">
                <div className="h-14 w-14 mx-auto rounded-3xl bg-indigo-500/10 text-indigo-600 flex items-center justify-center">
                  <BarChart3 className="h-7 w-7" />
                </div>
                <p className="text-sm font-semibold text-foreground">Awaiting optimization</p>
                <p className="text-xs text-muted-foreground max-w-xs mx-auto">
                  Configure the package dimensions and click{" "}
                  <span className="font-bold text-[#6D5CE7]">Run Layout Optimization</span> to compute
                  the recommended packaging strategy.
                </p>
              </Card>
            )}

            {isOptimizing && (
              <Card className="p-8 text-center space-y-3 border-indigo-500/20">
                <Loader2 className="h-10 w-10 mx-auto animate-spin text-indigo-500" />
                <p className="text-sm font-semibold">Contacting Layout Engine…</p>
                <p className="text-[11px] text-muted-foreground">
                  Computing COST · BALANCED · ACCESSIBILITY strategies
                </p>
              </Card>
            )}

            {optimizeResult && (
              <>
                {/* Recommendation summary */}
                <Card className="border-indigo-500/20 overflow-hidden">
                  <div className="bg-gradient-to-r from-indigo-500/10 via-indigo-500/5 to-transparent px-6 py-4 border-b border-indigo-500/20 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2 flex-wrap">
                        <Badge variant="success" className="font-bold text-xs uppercase tracking-wider">
                          Optimization Complete
                        </Badge>
                        {optimizeResult.recommended_strategy && (
                          <StrategyBadge strategy={optimizeResult.recommended_strategy} />
                        )}
                      </div>
                      <p className="text-[11px] text-muted-foreground">
                        {optimizeResult.candidates_evaluated ?? 3} strategies evaluated ·{" "}
                        {optimizeResult.elements.length} layout elements placed
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-[10px] text-muted-foreground uppercase tracking-wide">Overall Score</p>
                      <p className="text-3xl font-extrabold text-indigo-600 dark:text-indigo-400 font-mono">
                        {optimizeResult.score != null
                          ? `${Math.round(optimizeResult.score * 100)}%`
                          : "—"}
                      </p>
                    </div>
                  </div>

                  <CardContent className="p-5 space-y-4">
                    {/* Validation */}
                    {optimizeResult.validation && (
                      <div
                        className={`flex items-center gap-2 p-3 rounded-xl border text-xs font-semibold ${
                          optimizeResult.validation.valid
                            ? "bg-emerald-500/5 border-emerald-500/20 text-emerald-600 dark:text-emerald-400"
                            : "bg-destructive/5 border-destructive/20 text-destructive"
                        }`}
                      >
                        <CheckCircle2 className="h-4 w-4 shrink-0" />
                        <span>
                          {optimizeResult.validation.valid
                            ? "Layout validation passed — all elements fit within printing bounds"
                            : `Validation issues: ${optimizeResult.validation.errors.join("; ")}`}
                        </span>
                      </div>
                    )}

                    {/* Metrics grid */}
                    <div className="grid grid-cols-2 gap-x-6 gap-y-3">
                      <ScoreBar label="Space utilisation" value={optimizeResult.space_utilization} />
                      <ScoreBar label="Readability" value={optimizeResult.readability} />
                      <ScoreBar label="Print efficiency" value={optimizeResult.print_efficiency} />
                      <ScoreBar label="Cost efficiency" value={optimizeResult.cost_efficiency} />
                      <ScoreBar label="Scan reliability" value={optimizeResult.scan_reliability} />
                      {optimizeResult.accessibility_score != null && (
                        <ScoreBar label="Accessibility" value={optimizeResult.accessibility_score} />
                      )}
                    </div>

                    {/* Printable area stats */}
                    {optimizeResult.used_printable_area != null && (
                      <div className="grid grid-cols-2 gap-3 p-3 rounded-xl bg-secondary/40 border border-border text-[11px]">
                        <div>
                          <span className="text-muted-foreground block">Used printable area</span>
                          <span className="font-bold font-mono">{optimizeResult.used_printable_area.toFixed(1)} mm²</span>
                        </div>
                        <div>
                          <span className="text-muted-foreground block">Unused area</span>
                          <span className="font-bold font-mono">{(optimizeResult.unused_printable_area ?? 0).toFixed(1)} mm²</span>
                        </div>
                      </div>
                    )}

                    {/* Warnings */}
                    {optimizeResult.warnings.length > 0 && (
                      <div className="p-3 rounded-xl bg-amber-500/5 border border-amber-500/20 text-[11px] text-amber-700 dark:text-amber-400 space-y-1">
                        {optimizeResult.warnings.map((w, i) => (
                          <p key={i}>⚠ {w}</p>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Alternatives accordion */}
                {(optimizeResult.alternatives?.length ?? 0) > 0 && (
                  <Card className="border-border/80">
                    <button
                      type="button"
                      className="w-full flex items-center justify-between px-5 py-3 text-left hover:bg-secondary/40 transition-colors rounded-t-2xl"
                      onClick={() => setAltExpanded((v) => !v)}
                      id="btn-toggle-alternatives"
                    >
                      <span className="text-sm font-bold text-foreground">
                        Alternative Strategies ({optimizeResult.alternatives!.length})
                      </span>
                      {altExpanded ? (
                        <ChevronUp className="h-4 w-4 text-muted-foreground" />
                      ) : (
                        <ChevronDown className="h-4 w-4 text-muted-foreground" />
                      )}
                    </button>
                    {altExpanded && (
                      <CardContent className="pt-0 space-y-3">
                        {optimizeResult.alternatives!.map((alt: LayoutAlternative) => (
                          <div
                            key={alt.strategy}
                            className="p-4 rounded-xl bg-secondary/40 border border-border space-y-2"
                          >
                            <div className="flex items-center justify-between">
                              <StrategyBadge strategy={alt.strategy} />
                              <span className="font-mono font-bold text-sm text-foreground">
                                {Math.round(alt.score * 100)}%
                              </span>
                            </div>
                            <div className="grid grid-cols-2 gap-x-4 gap-y-1.5">
                              <ScoreBar label="Space" value={alt.space_utilization} />
                              <ScoreBar label="Readability" value={alt.readability} />
                              <ScoreBar label="Cost" value={alt.cost_efficiency} />
                              <ScoreBar label="Scan" value={alt.scan_reliability} />
                            </div>
                          </div>
                        ))}
                      </CardContent>
                    )}
                  </Card>
                )}

                {/* Elements table */}
                {optimizeResult.elements.length > 0 && (
                  <Card className="border-border/80">
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm">
                        Layout Elements ({optimizeResult.elements.length})
                      </CardTitle>
                      <CardDescription className="text-[11px]">
                        Computed positions for all printing and code elements
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="pt-0">
                      <div className="overflow-x-auto rounded-xl border border-border">
                        <table className="w-full text-[11px]">
                          <thead className="bg-secondary/60 text-muted-foreground uppercase tracking-wide">
                            <tr>
                              <th className="text-left px-3 py-2 font-bold">Type</th>
                              <th className="text-left px-3 py-2 font-bold">Content</th>
                              <th className="text-right px-3 py-2 font-bold">X (mm)</th>
                              <th className="text-right px-3 py-2 font-bold">Y (mm)</th>
                              <th className="text-right px-3 py-2 font-bold">W (mm)</th>
                              <th className="text-right px-3 py-2 font-bold">H (mm)</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-border">
                            {optimizeResult.elements.map((el) => (
                              <tr key={el.id} className="hover:bg-secondary/30 transition-colors">
                                <td className="px-3 py-1.5">
                                  <span className="font-mono text-[10px] bg-muted px-1.5 py-0.5 rounded">
                                    {el.type}
                                  </span>
                                </td>
                                <td className="px-3 py-1.5 max-w-[120px] truncate text-muted-foreground">
                                  {el.content ?? "—"}
                                </td>
                                <td className="px-3 py-1.5 text-right font-mono">{el.x_mm.toFixed(1)}</td>
                                <td className="px-3 py-1.5 text-right font-mono">{el.y_mm.toFixed(1)}</td>
                                <td className="px-3 py-1.5 text-right font-mono">{el.width_mm.toFixed(1)}</td>
                                <td className="px-3 py-1.5 text-right font-mono">{el.height_mm.toFixed(1)}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </CardContent>
                  </Card>
                )}
              </>
            )}

            {/* SVG preview panel */}
            {previewResult?.svg && (
              <Card className="border-indigo-500/20 overflow-hidden">
                <button
                  type="button"
                  className="w-full flex items-center justify-between px-5 py-3 text-left hover:bg-secondary/40 transition-colors rounded-t-2xl"
                  onClick={() => setSvgExpanded((v) => !v)}
                  id="btn-toggle-svg"
                >
                  <div className="flex items-center gap-2">
                    <Eye className="h-4 w-4 text-indigo-600" />
                    <span className="text-sm font-bold text-foreground">
                      SVG Layout Preview
                    </span>
                    {previewResult.validation?.valid && (
                      <Badge variant="success" className="text-[10px]">Valid</Badge>
                    )}
                  </div>
                  {svgExpanded ? (
                    <ChevronUp className="h-4 w-4 text-muted-foreground" />
                  ) : (
                    <ChevronDown className="h-4 w-4 text-muted-foreground" />
                  )}
                </button>
                {svgExpanded && (
                  <CardContent className="pt-0">
                    <div
                      className="w-full rounded-xl bg-white border border-border overflow-auto p-4 flex items-center justify-center min-h-[200px]"
                      /* SVG comes from our own Layout Engine — controlled, trusted source */
                      /* eslint-disable-next-line react/no-danger */
                      dangerouslySetInnerHTML={{ __html: previewResult.svg }}
                    />
                    <p className="text-[10px] text-muted-foreground mt-2 text-center">
                      SVG rendered from Layout Engine · POST /api/layouts/preview
                    </p>
                  </CardContent>
                )}
              </Card>
            )}
          </div>
        </div>
      </div>
    </AdminShell>
  );
}
