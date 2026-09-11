"use client";

import React, { useState, useEffect } from "react";
import { Search, Pill, Building2, CheckCircle, AlertCircle, Loader2, Sparkles, Filter } from "lucide-react";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { MedicineResponse } from "@/types/medicine";
import { getMedicines } from "@/services/api/medicines";

interface MedicineSelectorProps {
  selectedMedicineId?: number | null;
  onSelectMedicine: (medicine: MedicineResponse) => void;
}

export function MedicineSelector({
  selectedMedicineId,
  onSelectMedicine,
}: MedicineSelectorProps) {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string>("All");
  const [medicines, setMedicines] = useState<MedicineResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch medicines when search or category filter changes
  useEffect(() => {
    let isCancelled = false;
    async function load() {
      setIsLoading(true);
      setError(null);
      try {
        const data = await getMedicines({
          q: searchTerm.trim() || undefined,
          category: selectedCategory === "All" ? undefined : selectedCategory,
        });
        if (!isCancelled) {
          setMedicines(data);
        }
      } catch (err: any) {
        if (!isCancelled) {
          setError(err.message || "Unable to load medicines. Please try again.");
        }
      } finally {
        if (!isCancelled) {
          setIsLoading(false);
        }
      }
    }

    const timer = setTimeout(() => {
      load();
    }, 200);

    return () => {
      isCancelled = true;
      clearTimeout(timer);
    };
  }, [searchTerm, selectedCategory]);

  const categories = [
    "All",
    "Analgesic & Antipyretic",
    "Broad-Spectrum Antibiotic",
    "Macrolide Antibiotic",
    "Proton Pump Inhibitor (Antacid)",
  ];

  return (
    <div className="space-y-4">
      {/* Search and Category Filter Toolbar */}
      <div className="flex flex-col md:flex-row gap-3 items-stretch md:items-center justify-between">
        <div className="relative flex-1">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            type="text"
            placeholder="Search by brand name, generic formulation, or active salt..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10 pr-4 h-11 text-sm bg-card"
          />
          {searchTerm && (
            <button
              onClick={() => setSearchTerm("")}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-xs font-semibold text-muted-foreground hover:text-foreground px-1.5 py-0.5 rounded bg-muted/60"
            >
              Clear
            </button>
          )}
        </div>

        {/* Category Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 md:pb-0 scrollbar-none">
          <div className="flex items-center gap-1 text-xs text-muted-foreground font-semibold shrink-0 mr-1">
            <Filter className="h-3 w-3" />
            <span className="hidden sm:inline">Category:</span>
          </div>
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold shrink-0 transition-all ${
                selectedCategory === cat
                  ? "bg-[#6D5CE7] text-white shadow-sm shadow-[#6D5CE7]/30"
                  : "bg-secondary text-secondary-foreground hover:bg-secondary/80 border border-border/50"
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="p-12 text-center rounded-2xl border border-dashed border-border bg-card/50 space-y-3">
          <Loader2 className="h-8 w-8 mx-auto animate-spin text-[#6D5CE7]" />
          <p className="text-sm font-semibold text-foreground">
            Loading medicines from pharmaceutical catalog...
          </p>
          <p className="text-xs text-muted-foreground">
            Querying backend registry for authorized formulations
          </p>
        </div>
      )}

      {/* Error State */}
      {!isLoading && error && (
        <div className="p-6 rounded-2xl border border-destructive/30 bg-destructive/5 text-center space-y-3">
          <AlertCircle className="h-8 w-8 mx-auto text-destructive" />
          <p className="text-sm font-bold text-destructive">{error}</p>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setSearchTerm(searchTerm + " ")}
            className="text-xs"
          >
            Retry Query
          </Button>
        </div>
      )}

      {/* Empty State */}
      {!isLoading && !error && medicines.length === 0 && (
        <div className="p-12 text-center rounded-2xl border border-dashed border-border bg-card/50 space-y-3">
          <div className="h-12 w-12 mx-auto rounded-2xl bg-muted flex items-center justify-center text-muted-foreground">
            <Pill className="h-6 w-6" />
          </div>
          <div className="space-y-1">
            <p className="text-sm font-bold text-foreground">No medicines available</p>
            <p className="text-xs text-muted-foreground max-w-sm mx-auto">
              No medicines match your search criteria or are registered for this company/branch.
            </p>
          </div>
          {searchTerm && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setSearchTerm("");
                setSelectedCategory("All");
              }}
              className="text-xs mt-2"
            >
              Reset Filters
            </Button>
          )}
        </div>
      )}

      {/* Medicine Grid */}
      {!isLoading && !error && medicines.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
          {medicines.map((med) => {
            const isSelected = selectedMedicineId === med.id;
            return (
              <div
                key={med.id}
                onClick={() => onSelectMedicine(med)}
                className={`p-4 rounded-2xl border transition-all cursor-pointer flex flex-col justify-between group text-left ${
                  isSelected
                    ? "border-[#6D5CE7] bg-[#6D5CE7]/5 shadow-md shadow-[#6D5CE7]/10 ring-2 ring-[#6D5CE7]"
                    : "border-border/80 bg-card hover:border-[#6D5CE7]/50 hover:shadow-sm"
                }`}
              >
                <div className="space-y-2">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <div className="flex items-center gap-2">
                        <h4 className="font-extrabold text-sm text-foreground group-hover:text-[#6D5CE7] transition-colors">
                          {med.brand_name}
                        </h4>
                        <span className="text-xs font-bold text-[#6D5CE7] bg-[#6D5CE7]/10 px-2 py-0.5 rounded-md">
                          {med.strength}
                        </span>
                      </div>
                      <p className="text-xs text-muted-foreground mt-0.5 font-medium">
                        {med.generic_name}
                      </p>
                    </div>

                    {isSelected ? (
                      <Badge variant="success" className="gap-1 font-bold text-[11px] shrink-0">
                        <CheckCircle className="h-3 w-3" />
                        Selected
                      </Badge>
                    ) : (
                      <Badge variant="secondary" className="text-[10px] shrink-0">
                        {med.dosage_form}
                      </Badge>
                    )}
                  </div>

                  <div className="pt-2 border-t border-border/40 flex items-center justify-between text-[11px] text-muted-foreground">
                    <div className="flex items-center gap-1.5 truncate">
                      <Building2 className="h-3.5 w-3.5 shrink-0 text-muted-foreground/70" />
                      <span className="truncate">{med.manufacturer}</span>
                    </div>
                    {med.schedule_type && (
                      <span className="font-semibold text-muted-foreground/80 shrink-0 ml-2">
                        {med.schedule_type}
                      </span>
                    )}
                  </div>
                </div>

                <div className="mt-3.5 pt-2 border-t border-border/30 flex items-center justify-between">
                  <span className="text-[11px] font-medium text-muted-foreground">
                    {med.category}
                  </span>
                  <Button
                    size="sm"
                    variant={isSelected ? "primary" : "outline"}
                    className="text-xs h-7 px-3 font-semibold gap-1.5"
                    onClick={(e) => {
                      e.stopPropagation();
                      onSelectMedicine(med);
                    }}
                  >
                    {isSelected ? (
                      <>
                        <CheckCircle className="h-3 w-3" />
                        <span>Selected</span>
                      </>
                    ) : (
                      <span>Select Formulation</span>
                    )}
                  </Button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
