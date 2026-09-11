"use client";

import React, { useState, useRef, useEffect } from "react";
import Link from "next/link";
import { AdminShell } from "@/components/layout/AdminShell";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Input } from "@/components/ui/Input";
import { queryAssistant } from "@/services/api/assistant";
import { AssistantQueryResponse, VerifiedMedicineContext } from "@/types/assistant";
import {
  Bot,
  Send,
  Volume2,
  ShieldCheck,
  AlertTriangle,
  Sparkles,
  ArrowLeft,
  Pill,
  RotateCcw,
  CheckCircle2,
  Activity,
  Calendar,
  Layers,
} from "lucide-react";

interface ChatMessage {
  id: string;
  sender: "user" | "assistant";
  text: string;
  intent?: string;
  source?: string;
  hasVerifiedContext?: boolean;
  timestamp: string;
}

// Preset verified medicines for live testing
const SAMPLE_MEDICINE_CONTEXTS: { label: string; context: VerifiedMedicineContext }[] = [
  {
    label: "Dolo-650 (Paracetamol 650mg, Lot BTH-DOLO-2026A1)",
    context: {
      brand_name: "Dolo-650",
      generic_name: "Paracetamol Tablets IP",
      strength: "650 mg",
      dosage_form: "Tablet (Capsule-shaped, Uncoated)",
      manufacturer: "Micro Labs Limited",
      batch_no: "BTH-DOLO-2026A1",
      mfg_date: "2026-09-01",
      exp_date: "2028-09-01",
      active_ingredients: [
        { name: "Paracetamol IP", strength: "650", unit: "mg", purpose: "Analgesic & Antipyretic" },
      ],
      storage_conditions: "Store below 30°C in a dry place. Protect from moisture and direct light.",
      warnings_and_precautions: "Overdose may cause serious liver damage. Avoid consumption with alcohol.",
      indications: "Relief of mild to moderate pain including headache, body ache, toothache, and fever.",
      is_genuine: true,
      verification_status: "GENUINE",
    },
  },
  {
    label: "Augmentin 625 Duo (Amoxicillin + Clavulanate)",
    context: {
      brand_name: "Augmentin 625 Duo",
      generic_name: "Amoxicillin and Potassium Clavulanate Tablets IP",
      strength: "625 mg (500mg + 125mg)",
      dosage_form: "Tablet (Film-coated)",
      manufacturer: "GlaxoSmithKline Pharmaceuticals",
      batch_no: "BTH-AUG-9912",
      mfg_date: "2026-06-15",
      exp_date: "2028-06-15",
      active_ingredients: [
        { name: "Amoxicillin Trihydrate IP", strength: "500", unit: "mg", purpose: "Antibacterial" },
        { name: "Potassium Clavulanate IP", strength: "125", unit: "mg", purpose: "Beta-lactamase Inhibitor" },
      ],
      storage_conditions: "Store protected from moisture below 25°C. Keep blister sealed until use.",
      warnings_and_precautions: "Complete full prescribed course. Contraindicated in penicillin hypersensitivity.",
      indications: "Bacterial infections of the respiratory tract, ear-nose-throat, skin, and urinary tract.",
      is_genuine: true,
      verification_status: "GENUINE",
    },
  },
  {
    label: "Expired Batch Demo (Pan 40, Expired 2024)",
    context: {
      brand_name: "Pan 40",
      generic_name: "Pantoprazole Gastro-resistant Tablets IP",
      strength: "40 mg",
      dosage_form: "Tablet (Enteric-coated)",
      manufacturer: "Alkem Laboratories",
      batch_no: "BTH-PAN-2022X",
      mfg_date: "2022-01-01",
      exp_date: "2024-01-01",
      active_ingredients: [
        { name: "Pantoprazole Sodium IP", strength: "40", unit: "mg", purpose: "Gastric Acid Reducer" },
      ],
      storage_conditions: "Store below 25°C. Protect from moisture.",
      warnings_and_precautions: "Do not crush or chew. Swallow whole.",
      indications: "Gastroesophageal reflux disease (GERD) and peptic ulcer disease.",
      is_genuine: true,
      verification_status: "EXPIRED",
    },
  },
];

export default function AssistantPage() {
  const [selectedContextIdx, setSelectedContextIdx] = useState<number>(0);
  const [useContext, setUseContext] = useState<boolean>(true);
  const [inputQuery, setInputQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "initial-1",
      sender: "assistant",
      text: "Hello! I am your Zero Latency Medicine Voice & Text Assistant. I answer questions about verified pharmaceutical products strictly from authoritative backend data without hallucinating.",
      intent: "general_greeting",
      source: "system",
      hasVerifiedContext: true,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    },
  ]);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const activeContext = useContext ? SAMPLE_MEDICINE_CONTEXTS[selectedContextIdx].context : null;

  const handleSend = async (queryText?: string) => {
    const textToSend = (queryText || inputQuery).trim();
    if (!textToSend || isLoading) return;

    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      sender: "user",
      text: textToSend,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputQuery("");
    setIsLoading(true);

    try {
      const response: AssistantQueryResponse = await queryAssistant({
        query: textToSend,
        context: activeContext,
      });

      const assistantMessage: ChatMessage = {
        id: `assistant-${Date.now()}`,
        sender: "assistant",
        text: response.answer,
        intent: response.intent,
        source: response.source,
        hasVerifiedContext: response.has_verified_context,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };

      setMessages((prev) => [...prev, assistantMessage]);

      // Automatically speak the response if speech synthesis is supported
      if (typeof window !== "undefined" && "speechSynthesis" in window) {
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(response.tts_clean_text || response.answer);
        utterance.rate = 1.0;
        window.speechSynthesis.speak(utterance);
      }
    } catch (err: any) {
      const errorMessage: ChatMessage = {
        id: `error-${Date.now()}`,
        sender: "assistant",
        text: `Error connecting to Assistant API: ${err.message || "Request failed."}`,
        source: "system",
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSpeak = (text: string) => {
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.0;
      window.speechSynthesis.speak(utterance);
    }
  };

  const samplePrompts = [
    "What is the expiry date?",
    "Who is the manufacturer?",
    "What are the active ingredients?",
    "How should I store this medicine?",
    "Is this medicine authentic?",
    "What dosage should I personally take?", // Tests safety guardrail
    "What are the warnings?",
  ];

  return (
    <AdminShell>
      <div className="max-w-5xl mx-auto space-y-6 pb-12">
        {/* Top Navigation */}
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div className="flex items-center gap-3">
            <Link href="/dashboard">
              <Button variant="outline" size="sm" className="gap-1.5 text-xs">
                <ArrowLeft className="h-3.5 w-3.5" />
                <span>Back to Dashboard</span>
              </Button>
            </Link>
            <div className="h-4 w-px bg-border hidden sm:block" />
            <span className="text-xs font-semibold text-foreground">General Assistant &amp; TTS Gateway</span>
          </div>

          <Badge variant="secondary" className="gap-1 font-semibold text-[11px]">
            <ShieldCheck className="h-3.5 w-3.5 text-[#6D5CE7]" />
            <span>POST /api/assistant/query Active</span>
          </Badge>
        </div>

        {/* Header */}
        <div className="space-y-1">
          <h1 className="text-xl sm:text-2xl font-extrabold text-foreground tracking-tight flex items-center gap-2.5">
            <div className="h-8 w-8 rounded-xl bg-[#6D5CE7]/10 text-[#6D5CE7] flex items-center justify-center">
              <Bot className="h-4 w-4" />
            </div>
            <span>General Pharmaceutical Voice &amp; Chat Assistant</span>
          </h1>
          <p className="text-xs sm:text-sm text-muted-foreground max-w-2xl">
            CDSCO-verified deterministic conversational engine. Provides TTS-friendly responses for Web and Mobile screen-reader clients without pharmaceutical hallucination.
          </p>
        </div>

        {/* Context Configuration Card */}
        <Card className="border-border bg-card shadow-sm p-4 space-y-3">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <div className="flex items-center gap-2">
              <Pill className="h-4 w-4 text-[#6D5CE7]" />
              <span className="text-xs font-bold text-foreground">Active Verified Medicine Context</span>
            </div>

            <div className="flex items-center gap-2">
              <label className="text-xs text-muted-foreground flex items-center gap-1.5 cursor-pointer">
                <input
                  type="checkbox"
                  checked={useContext}
                  onChange={(e) => setUseContext(e.target.checked)}
                  className="rounded text-[#6D5CE7] focus:ring-[#6D5CE7]"
                />
                <span className="font-semibold">Supply Verified Context</span>
              </label>
            </div>
          </div>

          {useContext ? (
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
              {SAMPLE_MEDICINE_CONTEXTS.map((sc, idx) => (
                <button
                  key={idx}
                  onClick={() => setSelectedContextIdx(idx)}
                  className={`p-3 rounded-xl border text-left text-xs transition-all ${
                    selectedContextIdx === idx
                      ? "border-[#6D5CE7] bg-[#6D5CE7]/10 ring-1 ring-[#6D5CE7]"
                      : "border-border/60 bg-secondary/40 hover:border-border"
                  }`}
                >
                  <span className="font-bold text-foreground block truncate">{sc.context.brand_name}</span>
                  <span className="text-[11px] text-muted-foreground block truncate">{sc.context.strength}</span>
                  <span className="text-[10px] font-mono text-[#6D5CE7] block mt-1">Lot: {sc.context.batch_no}</span>
                </button>
              ))}
            </div>
          ) : (
            <div className="p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/20 text-xs text-amber-800 dark:text-amber-300 flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 shrink-0" />
              <span>
                Running in <strong>Zero Context Mode</strong>. Testing queries without verified data will trigger controlled fallback responses (&quot;I don&apos;t have enough verified medicine information...&quot;).
              </span>
            </div>
          )}
        </Card>

        {/* Chat Thread Container */}
        <Card className="border-border bg-card shadow-card overflow-hidden flex flex-col h-[520px]">
          {/* Messages Scroll Area */}
          <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex gap-3 max-w-[85%] sm:max-w-[75%] ${
                  msg.sender === "user" ? "ml-auto flex-row-reverse" : "mr-auto"
                }`}
              >
                <div
                  className={`h-8 w-8 rounded-xl flex items-center justify-center shrink-0 text-xs font-bold ${
                    msg.sender === "user"
                      ? "bg-[#6D5CE7] text-white"
                      : "bg-secondary border border-border text-foreground"
                  }`}
                >
                  {msg.sender === "user" ? "You" : <Bot className="h-4 w-4 text-[#6D5CE7]" />}
                </div>

                <div className="space-y-1.5">
                  <div
                    className={`p-3.5 rounded-2xl text-xs sm:text-sm leading-relaxed ${
                      msg.sender === "user"
                        ? "bg-[#6D5CE7] text-white rounded-tr-none shadow-sm"
                        : "bg-secondary/70 border border-border/80 text-foreground rounded-tl-none shadow-sm"
                    }`}
                  >
                    {msg.text}
                  </div>

                  {msg.sender === "assistant" && (
                    <div className="flex items-center gap-2 px-1 text-[11px] text-muted-foreground flex-wrap">
                      <span>{msg.timestamp}</span>

                      {msg.intent && (
                        <span className="font-mono px-1.5 py-0.5 rounded bg-muted text-[10px]">
                          intent: {msg.intent}
                        </span>
                      )}

                      {msg.source === "safety_guardrail" && (
                        <Badge variant="destructive" className="text-[10px] font-bold">
                          Safety Guardrail Blocked
                        </Badge>
                      )}

                      {msg.source === "verified_medicine_data" && (
                        <Badge variant="success" className="text-[10px] font-bold">
                          Verified Source
                        </Badge>
                      )}

                      <button
                        onClick={() => handleSpeak(msg.text)}
                        title="Read aloud with Text-to-Speech"
                        className="hover:text-[#6D5CE7] transition-colors p-1"
                      >
                        <Volume2 className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex gap-3 mr-auto max-w-[75%]">
                <div className="h-8 w-8 rounded-xl bg-secondary border border-border text-foreground flex items-center justify-center shrink-0">
                  <Bot className="h-4 w-4 text-[#6D5CE7] animate-pulse" />
                </div>
                <div className="p-3.5 rounded-2xl bg-secondary/50 border border-border text-xs text-muted-foreground rounded-tl-none flex items-center gap-1.5">
                  <span className="animate-bounce">●</span>
                  <span className="animate-bounce delay-100">●</span>
                  <span className="animate-bounce delay-200">●</span>
                  <span className="ml-1 text-[11px]">Processing deterministic query...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Prompt Chips */}
          <div className="p-3 bg-muted/20 border-t border-border/60 overflow-x-auto scrollbar-none flex items-center gap-2">
            <span className="text-[11px] font-semibold text-muted-foreground shrink-0 flex items-center gap-1">
              <Sparkles className="h-3 w-3 text-[#6D5CE7]" />
              Quick Queries:
            </span>
            {samplePrompts.map((p, idx) => (
              <button
                key={idx}
                disabled={isLoading}
                onClick={() => handleSend(p)}
                className="px-2.5 py-1 rounded-lg bg-card hover:bg-[#6D5CE7]/10 hover:text-[#6D5CE7] border border-border text-[11px] font-medium text-foreground whitespace-nowrap transition-colors"
              >
                {p}
              </button>
            ))}
          </div>

          {/* Input Form */}
          <div className="p-3 sm:p-4 bg-card border-t border-border flex items-center gap-2">
            <Input
              type="text"
              value={inputQuery}
              onChange={(e) => setInputQuery(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              placeholder="Ask about expiry date, manufacturer, strength, batch number, active ingredients, or storage..."
              disabled={isLoading}
              className="text-xs sm:text-sm h-11"
            />
            <Button
              type="button"
              variant="primary"
              disabled={isLoading || !inputQuery.trim()}
              onClick={() => handleSend()}
              className="h-11 px-4 gap-1.5 text-xs font-bold shrink-0"
            >
              <span>Send</span>
              <Send className="h-3.5 w-3.5" />
            </Button>
          </div>
        </Card>
      </div>
    </AdminShell>
  );
}
