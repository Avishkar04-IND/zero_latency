"use client";

import React, { useState } from "react";
import Link from "next/link";
import { AdminShell } from "@/components/layout/AdminShell";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/Card";
import { MedicineSelector } from "@/components/batches/MedicineSelector";
import { MedicineDetailsCard } from "@/components/batches/MedicineDetailsCard";
import { BatchForm } from "@/components/batches/BatchForm";
import { BatchSuccessResult } from "@/components/batches/BatchSuccessResult";
import { MedicineResponse } from "@/types/medicine";
import { BatchCreateRequest, BatchResponse, CodeGenerateBatchResponse } from "@/types/batch";
import { createBatch, generateBatchCodes } from "@/services/api/batches";
import {
  Boxes,
  ArrowLeft,
  CheckCircle,
  AlertCircle,
  Pill,
  Calendar,
  QrCode,
  ShieldCheck,
  ChevronRight,
} from "lucide-react";

type WorkflowStep = "select_medicine" | "enter_details" | "success";

export default function CreateBatchPage() {
  const [currentStep, setCurrentStep] = useState<WorkflowStep>("select_medicine");
  const [selectedMedicine, setSelectedMedicine] = useState<MedicineResponse | null>(null);

  // Submission state
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Result state
  const [createdBatch, setCreatedBatch] = useState<BatchResponse | null>(null);
  const [codeResult, setCodeResult] = useState<CodeGenerateBatchResponse | null>(null);

  const handleSelectMedicine = (medicine: MedicineResponse) => {
    setSelectedMedicine(medicine);
    setErrorMessage(null);
    setCurrentStep("enter_details");
  };

  const handleChangeMedicine = () => {
    setSelectedMedicine(null);
    setErrorMessage(null);
    setCurrentStep("select_medicine");
  };

  const handleBatchSubmit = async (formData: BatchCreateRequest) => {
    setIsSubmitting(true);
    setErrorMessage(null);

    try {
      // 1. Submit batch creation to authoritative backend endpoint: POST /api/v1/batches
      const batch = await createBatch(formData);
      setCreatedBatch(batch);

      // 2. Request backend code generation for this batch: POST /api/v1/codes/generate
      const generated = await generateBatchCodes(batch.id, 1);
      setCodeResult(generated);

      // 3. Advance to success screen
      setCurrentStep("success");
    } catch (err: any) {
      console.error("Batch creation failed", err);
      setErrorMessage(
        err.message ||
          "Unable to create batch or generate serialization code. Please verify backend service and input parameters."
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleResetWorkflow = () => {
    setSelectedMedicine(null);
    setCreatedBatch(null);
    setCodeResult(null);
    setErrorMessage(null);
    setCurrentStep("select_medicine");
  };

  return (
    <AdminShell>
      <div className="max-w-5xl mx-auto space-y-6 pb-12">
        {/* Top Navigation Bar */}
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div className="flex items-center gap-3">
            <Link href="/dashboard">
              <Button variant="outline" size="sm" className="gap-1.5 text-xs">
                <ArrowLeft className="h-3.5 w-3.5" />
                <span>Back to Dashboard</span>
              </Button>
            </Link>

            <div className="h-4 w-px bg-border hidden sm:block" />

            <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
              <Link href="/dashboard" className="hover:text-foreground">
                Dashboard
              </Link>
              <ChevronRight className="h-3 w-3" />
              <span className="font-semibold text-foreground">Create Batch</span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Badge variant="secondary" className="gap-1 font-semibold text-[11px]">
              <ShieldCheck className="h-3.5 w-3.5 text-[#6D5CE7]" />
              <span>CDSCO Rule 96 Verified</span>
            </Badge>
          </div>
        </div>

        {/* Page Header */}
        <div className="space-y-1">
          <h1 className="text-xl sm:text-2xl font-extrabold text-foreground tracking-tight flex items-center gap-2.5">
            <div className="h-8 w-8 rounded-xl bg-[#6D5CE7]/10 text-[#6D5CE7] flex items-center justify-center">
              <Boxes className="h-4 w-4" />
            </div>
            <span>Manufacturing Batch Creation</span>
          </h1>
          <p className="text-xs sm:text-sm text-muted-foreground max-w-2xl">
            Select an authorized medicine formulation, configure production lot parameters, and generate server-authoritative GS1 DataMatrix serialization codes.
          </p>
        </div>

        {/* Multi-Step Visual Progress Stepper */}
        <div className="grid grid-cols-3 gap-2 sm:gap-4 p-2 sm:p-3 rounded-2xl bg-card border border-border">
          {/* Step 1 */}
          <div
            className={`flex items-center gap-2 sm:gap-3 p-2 rounded-xl transition-all ${
              currentStep === "select_medicine"
                ? "bg-[#6D5CE7]/10 border border-[#6D5CE7]/30 text-[#6D5CE7]"
                : selectedMedicine
                ? "text-foreground"
                : "text-muted-foreground opacity-60"
            }`}
          >
            <div
              className={`h-7 w-7 rounded-lg flex items-center justify-center text-xs font-bold shrink-0 ${
                selectedMedicine
                  ? "bg-emerald-600 text-white"
                  : currentStep === "select_medicine"
                  ? "bg-[#6D5CE7] text-white"
                  : "bg-muted text-muted-foreground"
              }`}
            >
              {selectedMedicine ? <CheckCircle className="h-4 w-4" /> : "1"}
            </div>
            <div className="truncate">
              <span className="text-xs font-bold block truncate">Select Medicine</span>
              <span className="text-[10px] text-muted-foreground hidden sm:block truncate">
                {selectedMedicine ? selectedMedicine.brand_name : "Active catalog"}
              </span>
            </div>
          </div>

          {/* Step 2 */}
          <div
            className={`flex items-center gap-2 sm:gap-3 p-2 rounded-xl transition-all ${
              currentStep === "enter_details"
                ? "bg-[#6D5CE7]/10 border border-[#6D5CE7]/30 text-[#6D5CE7]"
                : createdBatch
                ? "text-foreground"
                : "text-muted-foreground opacity-60"
            }`}
          >
            <div
              className={`h-7 w-7 rounded-lg flex items-center justify-center text-xs font-bold shrink-0 ${
                createdBatch
                  ? "bg-emerald-600 text-white"
                  : currentStep === "enter_details"
                  ? "bg-[#6D5CE7] text-white"
                  : "bg-muted text-muted-foreground"
              }`}
            >
              {createdBatch ? <CheckCircle className="h-4 w-4" /> : "2"}
            </div>
            <div className="truncate">
              <span className="text-xs font-bold block truncate">Batch Parameters</span>
              <span className="text-[10px] text-muted-foreground hidden sm:block truncate">
                {createdBatch ? createdBatch.batch_no : "Lot dates & run size"}
              </span>
            </div>
          </div>

          {/* Step 3 */}
          <div
            className={`flex items-center gap-2 sm:gap-3 p-2 rounded-xl transition-all ${
              currentStep === "success"
                ? "bg-emerald-500/10 border border-emerald-500/30 text-emerald-600 dark:text-emerald-400"
                : "text-muted-foreground opacity-60"
            }`}
          >
            <div
              className={`h-7 w-7 rounded-lg flex items-center justify-center text-xs font-bold shrink-0 ${
                currentStep === "success"
                  ? "bg-emerald-600 text-white"
                  : "bg-muted text-muted-foreground"
              }`}
            >
              3
            </div>
            <div className="truncate">
              <span className="text-xs font-bold block truncate">Serialized Code</span>
              <span className="text-[10px] text-muted-foreground hidden sm:block truncate">
                GS1 DataMatrix Result
              </span>
            </div>
          </div>
        </div>

        {/* Global Error Banner */}
        {errorMessage && (
          <div className="p-4 rounded-2xl border border-destructive/30 bg-destructive/5 flex items-start gap-3 text-destructive animate-in fade-in-50">
            <AlertCircle className="h-5 w-5 shrink-0 mt-0.5" />
            <div className="space-y-1">
              <h4 className="font-bold text-xs uppercase tracking-wide">Operation Error</h4>
              <p className="text-xs text-destructive/90">{errorMessage}</p>
            </div>
          </div>
        )}

        {/* STEP 1: Medicine Selection */}
        {currentStep === "select_medicine" && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-sm font-bold uppercase tracking-wider text-foreground">
                  Step 1: Select Registered Formulation
                </h2>
                <p className="text-xs text-muted-foreground">
                  Choose a medicine from your company&apos;s authorized formulation registry.
                </p>
              </div>
            </div>

            <MedicineSelector
              selectedMedicineId={selectedMedicine?.id}
              onSelectMedicine={handleSelectMedicine}
            />
          </div>
        )}

        {/* STEP 2: Medicine Details & Batch Creation Form */}
        {currentStep === "enter_details" && selectedMedicine && (
          <div className="space-y-6 animate-in fade-in-50">
            {/* Step 2 Registered Information Card */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-sm font-bold uppercase tracking-wider text-foreground">
                    Step 2: Registered Medicine Information
                  </h2>
                  <p className="text-xs text-muted-foreground">
                    Server-verified pharmaceutical composition and regulatory specs.
                  </p>
                </div>
              </div>

              <MedicineDetailsCard
                medicine={selectedMedicine}
                onChangeMedicine={handleChangeMedicine}
              />
            </div>

            {/* Step 3 Batch Parameters Form */}
            <div className="space-y-2">
              <BatchForm
                medicine={selectedMedicine}
                onSubmit={handleBatchSubmit}
                isLoading={isSubmitting}
                onCancel={handleChangeMedicine}
              />
            </div>
          </div>
        )}

        {/* STEP 3: Success Result and Code Serialization Display */}
        {currentStep === "success" && selectedMedicine && createdBatch && codeResult && (
          <BatchSuccessResult
            medicine={selectedMedicine}
            batch={createdBatch}
            codeData={codeResult}
            onCreateAnother={handleResetWorkflow}
          />
        )}
      </div>
    </AdminShell>
  );
}
