"use client";

import React, { useState } from "react";
import {
  Calendar,
  Hash,
  Layers,
  IndianRupee,
  AlertCircle,
  Loader2,
  CheckCircle2,
  ShieldCheck,
  ArrowRight,
} from "lucide-react";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/Card";
import { MedicineResponse } from "@/types/medicine";
import { BatchCreateRequest } from "@/types/batch";

interface BatchFormProps {
  medicine: MedicineResponse;
  onSubmit: (data: BatchCreateRequest) => Promise<void>;
  isLoading: boolean;
  onCancel: () => void;
}

export function BatchForm({
  medicine,
  onSubmit,
  isLoading,
  onCancel,
}: BatchFormProps) {
  // Current default dates
  const todayStr = new Date().toISOString().slice(0, 10);
  const twoYearsFromNow = new Date(Date.now() + 2 * 365 * 24 * 60 * 60 * 1000)
    .toISOString()
    .slice(0, 10);

  // Suggested default batch number prefix based on medicine brand
  const defaultBatchNo = `BTH-${medicine.brand_name.replace(/[^a-zA-Z0-9]/g, "").slice(0, 4).toUpperCase()}-2026A1`;

  const [batchNo, setBatchNo] = useState(defaultBatchNo);
  const [mfgDate, setMfgDate] = useState(todayStr);
  const [expDate, setExpDate] = useState(twoYearsFromNow);
  const [quantity, setQuantity] = useState("10000");
  const [mrp, setMrp] = useState("50.00");

  const [errors, setErrors] = useState<Record<string, string>>({});

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!batchNo.trim()) {
      newErrors.batchNo = "Batch number is required.";
    } else if (batchNo.trim().length < 3) {
      newErrors.batchNo = "Batch number must be at least 3 characters.";
    }

    if (!mfgDate) {
      newErrors.mfgDate = "Manufacture date is required.";
    }

    if (!expDate) {
      newErrors.expDate = "Expiry date is required.";
    }

    if (mfgDate && expDate) {
      const mfg = new Date(mfgDate);
      const exp = new Date(expDate);
      if (exp <= mfg) {
        newErrors.expDate = "Expiry date must be after manufacture date.";
      }
    }

    const qtyNum = parseInt(quantity, 10);
    if (!quantity || isNaN(qtyNum) || qtyNum <= 0) {
      newErrors.quantity = "Quantity must be a positive integer.";
    }

    const mrpNum = parseFloat(mrp);
    if (!mrp || isNaN(mrpNum) || mrpNum < 0) {
      newErrors.mrp = "MRP must be a valid price.";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    await onSubmit({
      medicine_id: medicine.id,
      batch_no: batchNo.trim().toUpperCase(),
      mfg_date: mfgDate,
      exp_date: expDate,
      quantity: parseInt(quantity, 10),
      mrp: parseFloat(mrp),
      status: "active",
    });
  };

  return (
    <Card className="border-border bg-card shadow-card">
      <CardHeader className="space-y-1 pb-4">
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-xl bg-[#6D5CE7]/10 text-[#6D5CE7] flex items-center justify-center font-bold text-xs">
            03
          </div>
          <div>
            <CardTitle className="text-base font-bold text-foreground">
              Production Batch Parameters
            </CardTitle>
            <CardDescription className="text-xs">
              Specify lot numbering, manufacturing/expiry dates, and batch run size.
            </CardDescription>
          </div>
        </div>
      </CardHeader>

      <form onSubmit={handleSubmit}>
        <CardContent className="space-y-4 pt-0">
          {/* Batch Number */}
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-foreground flex items-center gap-1.5">
              <Hash className="h-3.5 w-3.5 text-[#6D5CE7]" />
              <span>Authoritative Batch Number</span>
              <span className="text-destructive">*</span>
            </label>
            <Input
              type="text"
              value={batchNo}
              onChange={(e) => {
                setBatchNo(e.target.value);
                if (errors.batchNo) setErrors((prev) => ({ ...prev, batchNo: "" }));
              }}
              placeholder="e.g. BTH-2026-001"
              className="font-mono text-sm uppercase tracking-wider"
              error={!!errors.batchNo}
              disabled={isLoading}
            />
            {errors.batchNo ? (
              <p className="text-[11px] font-semibold text-destructive flex items-center gap-1">
                <AlertCircle className="h-3 w-3" />
                <span>{errors.batchNo}</span>
              </p>
            ) : (
              <p className="text-[11px] text-muted-foreground">
                Unique lot identifier etched into blister packaging and embedded into GS1 DataMatrix.
              </p>
            )}
          </div>

          {/* Date Pickers: Manufacture & Expiry */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Manufacture Date */}
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-foreground flex items-center gap-1.5">
                <Calendar className="h-3.5 w-3.5 text-[#6D5CE7]" />
                <span>Manufacture Date</span>
                <span className="text-destructive">*</span>
              </label>
              <Input
                type="date"
                value={mfgDate}
                onChange={(e) => {
                  setMfgDate(e.target.value);
                  if (errors.mfgDate) setErrors((prev) => ({ ...prev, mfgDate: "" }));
                  if (errors.expDate && expDate) {
                    const mfg = new Date(e.target.value);
                    const exp = new Date(expDate);
                    if (exp > mfg) setErrors((prev) => ({ ...prev, expDate: "" }));
                  }
                }}
                className="text-sm"
                error={!!errors.mfgDate}
                disabled={isLoading}
              />
              {errors.mfgDate ? (
                <p className="text-[11px] font-semibold text-destructive flex items-center gap-1">
                  <AlertCircle className="h-3 w-3" />
                  <span>{errors.mfgDate}</span>
                </p>
              ) : (
                <p className="text-[11px] text-muted-foreground">Production packaging date</p>
              )}
            </div>

            {/* Expiry Date */}
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-foreground flex items-center gap-1.5">
                <Calendar className="h-3.5 w-3.5 text-[#6D5CE7]" />
                <span>Expiry Date</span>
                <span className="text-destructive">*</span>
              </label>
              <Input
                type="date"
                value={expDate}
                onChange={(e) => {
                  setExpDate(e.target.value);
                  if (errors.expDate) setErrors((prev) => ({ ...prev, expDate: "" }));
                }}
                className="text-sm"
                error={!!errors.expDate}
                disabled={isLoading}
              />
              {errors.expDate ? (
                <p className="text-[11px] font-semibold text-destructive flex items-center gap-1">
                  <AlertCircle className="h-3 w-3" />
                  <span>{errors.expDate}</span>
                </p>
              ) : (
                <p className="text-[11px] text-muted-foreground">
                  Must be strictly after manufacture date
                </p>
              )}
            </div>
          </div>

          {/* Quantity and MRP */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Quantity */}
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-foreground flex items-center gap-1.5">
                <Layers className="h-3.5 w-3.5 text-[#6D5CE7]" />
                <span>Production Run Quantity (Units)</span>
                <span className="text-destructive">*</span>
              </label>
              <Input
                type="number"
                min="1"
                step="1"
                value={quantity}
                onChange={(e) => {
                  setQuantity(e.target.value);
                  if (errors.quantity) setErrors((prev) => ({ ...prev, quantity: "" }));
                }}
                placeholder="10000"
                className="font-mono text-sm"
                error={!!errors.quantity}
                disabled={isLoading}
              />
              {errors.quantity ? (
                <p className="text-[11px] font-semibold text-destructive flex items-center gap-1">
                  <AlertCircle className="h-3 w-3" />
                  <span>{errors.quantity}</span>
                </p>
              ) : (
                <p className="text-[11px] text-muted-foreground">
                  Total individual blisters/strips to be manufactured
                </p>
              )}
            </div>

            {/* MRP */}
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-foreground flex items-center gap-1.5">
                <IndianRupee className="h-3.5 w-3.5 text-[#6D5CE7]" />
                <span>Maximum Retail Price (₹ MRP)</span>
              </label>
              <Input
                type="number"
                min="0"
                step="0.5"
                value={mrp}
                onChange={(e) => {
                  setMrp(e.target.value);
                  if (errors.mrp) setErrors((prev) => ({ ...prev, mrp: "" }));
                }}
                placeholder="50.00"
                className="font-mono text-sm"
                error={!!errors.mrp}
                disabled={isLoading}
              />
              {errors.mrp ? (
                <p className="text-[11px] font-semibold text-destructive flex items-center gap-1">
                  <AlertCircle className="h-3 w-3" />
                  <span>{errors.mrp}</span>
                </p>
              ) : (
                <p className="text-[11px] text-muted-foreground">
                  Consumer packaging ceiling price as registered
                </p>
              )}
            </div>
          </div>

          {/* CDSCO Regulatory Verification Note */}
          <div className="p-3 rounded-xl bg-secondary/40 border border-border flex items-start gap-2.5 text-xs text-muted-foreground">
            <ShieldCheck className="h-4 w-4 text-emerald-600 dark:text-emerald-400 shrink-0 mt-0.5" />
            <div>
              <span className="font-semibold text-foreground">Authoritative Serialization: </span>
              Upon submission, the backend will assign a database record, calculate cryptographic HMAC-SHA256 signatures, and format GS1 Application Identifiers (01, 17, 10, 21).
            </div>
          </div>
        </CardContent>

        <CardFooter className="pt-3 border-t border-border flex items-center justify-between gap-3">
          <Button
            type="button"
            variant="outline"
            onClick={onCancel}
            disabled={isLoading}
            className="text-xs font-semibold"
          >
            Cancel
          </Button>

          <Button
            type="submit"
            variant="primary"
            disabled={isLoading}
            className="text-xs font-bold gap-2 px-5 min-w-[200px]"
          >
            {isLoading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Creating Batch &amp; Code...</span>
              </>
            ) : (
              <>
                <span>Create Batch &amp; Generate Code</span>
                <ArrowRight className="h-3.5 w-3.5" />
              </>
            )}
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
}
