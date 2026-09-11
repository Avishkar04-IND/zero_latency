"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import { Logo } from "@/components/branding/Logo";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/Card";
import {
  Lock,
  Mail,
  ShieldCheck,
  Building2,
  MapPin,
  AlertCircle,
  Loader2,
  KeyRound,
  CheckCircle2,
} from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const { login, isAuthenticated, isLoading: authLoading, error: authError, clearError } = useAuth();

  const [email, setEmail] = useState("admin@sunpharma.com");
  const [password, setPassword] = useState("Admin@12345");
  const [validationErrors, setValidationErrors] = useState<{ email?: string; password?: string }>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  // If already authenticated, redirect to dashboard
  useEffect(() => {
    if (!authLoading && isAuthenticated) {
      router.push("/dashboard");
    }
  }, [authLoading, isAuthenticated, router]);

  const validate = (): boolean => {
    const errors: { email?: string; password?: string } = {};

    if (!email.trim()) {
      errors.email = "Admin identity / email is required.";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) {
      errors.email = "Please enter a valid email address.";
    }

    if (!password) {
      errors.password = "Password is required.";
    } else if (password.length < 4) {
      errors.password = "Password must be at least 4 characters.";
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);
    clearError();

    if (!validate()) return;

    setIsSubmitting(true);
    try {
      await login({
        email: email.trim(),
        password: password,
      });
      // Redirect handled by AuthContext
    } catch (err: any) {
      setFormError(err.message || "Authentication failed. Please verify your credentials.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleFillSeedCredentials = () => {
    setEmail("admin@sunpharma.com");
    setPassword("Admin@12345");
    setValidationErrors({});
    setFormError(null);
    clearError();
  };

  return (
    <div className="min-h-screen w-full flex flex-col justify-center items-center p-4 sm:p-6 lg:p-8 bg-gradient-to-br from-background via-slate-50 to-lavender-50/40 dark:from-background dark:via-background dark:to-card">
      <div className="w-full max-w-md space-y-6">
        {/* Branding & Platform Title */}
        <div className="text-center flex flex-col items-center space-y-2">
          <Logo size="lg" subtitle="Serialization & Manufacturing Administration" />
          <p className="text-xs text-muted-foreground max-w-sm mt-1">
            Enterprise Pharmaceutical Administration & Track-and-Trace Control System
          </p>
        </div>

        {/* Login Card */}
        <Card className="border-border/80 shadow-card bg-card/95 backdrop-blur">
          <CardHeader className="space-y-1 pb-4">
            <div className="flex items-center justify-between">
              <CardTitle className="text-xl">Admin Authentication</CardTitle>
              <span className="flex items-center gap-1 text-[11px] font-semibold text-emerald-600 dark:text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full">
                <ShieldCheck className="h-3 w-3" />
                <span>Authorized Only</span>
              </span>
            </div>
            <CardDescription className="text-xs">
              Sign in with your verified manufacturer credentials to access the serialization console.
            </CardDescription>
          </CardHeader>

          <form onSubmit={handleSubmit} noValidate>
            <CardContent className="space-y-4 pt-0">
              {/* Organization & Facility Context Notice */}
              <div className="rounded-xl bg-secondary/70 p-3 text-xs space-y-1.5 border border-border/70">
                <div className="flex items-center gap-2 font-semibold text-foreground">
                  <Building2 className="h-3.5 w-3.5 text-[#6D5CE7]" />
                  <span>Assigned Organization: Sun Pharmaceutical Industries Ltd.</span>
                </div>
                <div className="flex items-center gap-2 text-muted-foreground text-[11px]">
                  <MapPin className="h-3.5 w-3.5 text-muted-foreground" />
                  <span>Facility: Plant Unit 01 — Serialization & Packaging</span>
                </div>
              </div>

              {/* Error Alert (Validation, Auth, or Network) */}
              {(formError || authError) && (
                <div
                  className="p-3 rounded-xl bg-destructive/10 border border-destructive/20 text-destructive text-xs flex items-start gap-2.5 animate-fadeIn"
                  role="alert"
                >
                  <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
                  <div className="flex-1">
                    <p className="font-semibold">Authentication Error</p>
                    <p className="mt-0.5">{formError || authError}</p>
                  </div>
                </div>
              )}

              {/* Admin Identity / Username / Email Field */}
              <div className="space-y-1.5">
                <label
                  htmlFor="admin-email"
                  className="text-xs font-bold text-foreground flex items-center justify-between"
                >
                  <span>Admin Identity (Email)</span>
                  <span className="text-[11px] text-muted-foreground font-normal">
                    Assigned QC ID
                  </span>
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-muted-foreground">
                    <Mail className="h-4 w-4" />
                  </div>
                  <Input
                    id="admin-email"
                    type="email"
                    autoComplete="email"
                    value={email}
                    onChange={(e) => {
                      setEmail(e.target.value);
                      if (validationErrors.email) {
                        setValidationErrors((prev) => ({ ...prev, email: undefined }));
                      }
                    }}
                    placeholder="admin@sunpharma.com"
                    className="pl-9"
                    disabled={isSubmitting}
                    error={!!validationErrors.email}
                    aria-invalid={!!validationErrors.email}
                    aria-describedby={validationErrors.email ? "email-error" : undefined}
                    required
                  />
                </div>
                {validationErrors.email && (
                  <p id="email-error" className="text-[11px] font-medium text-destructive">
                    {validationErrors.email}
                  </p>
                )}
              </div>

              {/* Password Field */}
              <div className="space-y-1.5">
                <label
                  htmlFor="admin-password"
                  className="text-xs font-bold text-foreground flex items-center justify-between"
                >
                  <span>Password</span>
                  <span className="text-[11px] text-muted-foreground font-normal">
                    Encrypted Token
                  </span>
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-muted-foreground">
                    <Lock className="h-4 w-4" />
                  </div>
                  <Input
                    id="admin-password"
                    type="password"
                    autoComplete="current-password"
                    value={password}
                    onChange={(e) => {
                      setPassword(e.target.value);
                      if (validationErrors.password) {
                        setValidationErrors((prev) => ({ ...prev, password: undefined }));
                      }
                    }}
                    placeholder="••••••••••••"
                    className="pl-9"
                    disabled={isSubmitting}
                    error={!!validationErrors.password}
                    aria-invalid={!!validationErrors.password}
                    aria-describedby={validationErrors.password ? "password-error" : undefined}
                    required
                  />
                </div>
                {validationErrors.password && (
                  <p id="password-error" className="text-[11px] font-medium text-destructive">
                    {validationErrors.password}
                  </p>
                )}
              </div>
            </CardContent>

            <CardFooter className="flex flex-col space-y-3 pt-2">
              <Button
                type="submit"
                variant="primary"
                size="lg"
                className="w-full text-sm"
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <span className="flex items-center gap-2">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span>Signing in to Manufacturing Console...</span>
                  </span>
                ) : (
                  <span className="flex items-center gap-2">
                    <KeyRound className="h-4 w-4" />
                    <span>Authenticate as Admin</span>
                  </span>
                )}
              </Button>

              {/* Demo Credentials Quick-Fill Helper */}
              <button
                type="button"
                onClick={handleFillSeedCredentials}
                className="text-[11px] text-[#6D5CE7] hover:underline font-medium flex items-center justify-center gap-1 transition-colors"
              >
                <span>Autofill verified seed credentials (admin@sunpharma.com)</span>
              </button>
            </CardFooter>
          </form>
        </Card>

        {/* Security & Audit Footer Notice */}
        <div className="text-center space-y-1">
          <p className="text-[11px] text-muted-foreground flex items-center justify-center gap-1.5">
            <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600 dark:text-emerald-400" />
            <span>Server-Authoritative Authentication via FastAPI REST API</span>
          </p>
          <p className="text-[10px] text-muted-foreground/80">
            All administrative logins are cryptographically logged for CDSCO regulatory audits.
          </p>
        </div>
      </div>
    </div>
  );
}
