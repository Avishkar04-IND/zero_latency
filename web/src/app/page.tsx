"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import { ShieldCheck, Loader2 } from "lucide-react";

export default function RootPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuth();

  useEffect(() => {
    if (!isLoading) {
      if (isAuthenticated) {
        router.push("/dashboard");
      } else {
        router.push("/login");
      }
    }
  }, [isAuthenticated, isLoading, router]);

  return (
    <div className="flex min-h-screen w-full items-center justify-center bg-background">
      <div className="flex flex-col items-center gap-3 p-6 rounded-2xl bg-card border border-border shadow-sm text-center">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-[#5B48D9] to-[#8B7CF6] text-white">
          <ShieldCheck className="h-5 w-5" />
        </div>
        <p className="text-xs font-semibold text-muted-foreground flex items-center gap-1.5">
          <Loader2 className="h-3.5 w-3.5 animate-spin text-[#6D5CE7]" />
          <span>Routing to Zero Latency Admin Console...</span>
        </p>
      </div>
    </div>
  );
}
