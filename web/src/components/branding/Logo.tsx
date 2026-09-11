import React from "react";
import { ShieldCheck } from "lucide-react";
import { cn } from "@/lib/utils";

interface LogoProps {
  className?: string;
  size?: "sm" | "md" | "lg";
  subtitle?: string;
  showSubtitle?: boolean;
}

export function Logo({
  className,
  size = "md",
  subtitle = "Pharmaceutical Admin",
  showSubtitle = true,
}: LogoProps) {
  const iconSizes = {
    sm: "h-5 w-5",
    md: "h-6 w-6",
    lg: "h-8 w-8",
  };

  const containerSizes = {
    sm: "h-8 w-8 rounded-lg",
    md: "h-10 w-10 rounded-xl",
    lg: "h-12 w-12 rounded-2xl",
  };

  const titleSizes = {
    sm: "text-sm",
    md: "text-base",
    lg: "text-xl",
  };

  return (
    <div className={cn("flex items-center gap-3", className)}>
      <div
        className={cn(
          "flex items-center justify-center bg-gradient-to-tr from-[#5B48D9] to-[#8B7CF6] text-white shadow-md shadow-[#6D5CE7]/30",
          containerSizes[size]
        )}
      >
        <ShieldCheck className={iconSizes[size]} />
      </div>
      <div>
        <div className={cn("font-extrabold tracking-tight text-foreground flex items-center gap-1.5", titleSizes[size])}>
          <span>ZERO</span>
          <span className="text-[#6D5CE7]">LATENCY</span>
        </div>
        {showSubtitle && (
          <p className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">
            {subtitle}
          </p>
        )}
      </div>
    </div>
  );
}
