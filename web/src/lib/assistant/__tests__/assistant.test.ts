import { test, describe } from "node:test";
import assert from "node:assert";
import { processAssistantQuery } from "../engine.ts";
import type { VerifiedMedicineContext } from "../../../types/assistant";

const SAMPLE_VERIFIED_CONTEXT: VerifiedMedicineContext = {
  brand_name: "Dolo-650",
  generic_name: "Paracetamol Tablets IP",
  strength: "650 mg",
  dosage_form: "Tablet",
  manufacturer: "Micro Labs Limited",
  batch_no: "BTH-DOLO-2026A1",
  mfg_date: "2026-09-01",
  exp_date: "2028-09-01",
  active_ingredients: [
    { name: "Paracetamol IP", strength: "650", unit: "mg", purpose: "Analgesic & Antipyretic" },
  ],
  storage_conditions: "Store below 30°C in a dry place. Protect from direct sunlight.",
  warnings_and_precautions: "Overdose may cause serious liver damage. Avoid alcohol.",
  side_effects: "Rare allergic skin reactions, nausea.",
  indications: "Relief of mild to moderate pain and reduction of fever.",
  is_genuine: true,
  verification_status: "GENUINE",
};

describe("General Assistant Engine - Deterministic Pharmaceutical Queries", () => {
  // A. Valid medicine-name query
  test("A. Valid medicine-name query", () => {
    const res = processAssistantQuery({
      query: "What is the name of this medicine?",
      context: SAMPLE_VERIFIED_CONTEXT,
    });

    assert.strictEqual(res.success, true);
    assert.strictEqual(res.intent, "medicine_name");
    assert.strictEqual(res.source, "verified_medicine_data");
    assert.strictEqual(res.has_verified_context, true);
    assert.ok(res.answer.includes("Dolo-650"));
    assert.ok(res.answer.includes("Paracetamol Tablets IP"));
  });

  // B. Strength query
  test("B. Strength query", () => {
    const res = processAssistantQuery({
      query: "What is the strength of this drug?",
      context: SAMPLE_VERIFIED_CONTEXT,
    });

    assert.strictEqual(res.success, true);
    assert.strictEqual(res.intent, "strength");
    assert.strictEqual(res.source, "verified_medicine_data");
    assert.ok(res.answer.includes("650 mg"));
    assert.strictEqual(res.data?.strength, "650 mg");
  });

  // C. Manufacturer query
  test("C. Manufacturer query", () => {
    const res = processAssistantQuery({
      query: "Who manufactured this product?",
      context: SAMPLE_VERIFIED_CONTEXT,
    });

    assert.strictEqual(res.success, true);
    assert.strictEqual(res.intent, "manufacturer");
    assert.strictEqual(res.source, "verified_medicine_data");
    assert.ok(res.answer.includes("Micro Labs Limited"));
    assert.strictEqual(res.data?.manufacturer, "Micro Labs Limited");
  });

  // D. Batch query
  test("D. Batch query", () => {
    const res = processAssistantQuery({
      query: "What is the batch number?",
      context: SAMPLE_VERIFIED_CONTEXT,
    });

    assert.strictEqual(res.success, true);
    assert.strictEqual(res.intent, "batch_number");
    assert.strictEqual(res.source, "verified_medicine_data");
    assert.ok(res.answer.includes("BTH-DOLO-2026A1"));
    assert.strictEqual(res.data?.batch_no, "BTH-DOLO-2026A1");
  });

  // E. Expiry query
  test("E. Expiry query", () => {
    const res = processAssistantQuery({
      query: "When does it expire?",
      context: SAMPLE_VERIFIED_CONTEXT,
    });

    assert.strictEqual(res.success, true);
    assert.strictEqual(res.intent, "expiry_date");
    assert.strictEqual(res.source, "verified_medicine_data");
    assert.ok(res.answer.includes("2028-09-01"));
    assert.strictEqual(res.data?.expiry_date, "2028-09-01");
  });

  // F. Storage query
  test("F. Storage query", () => {
    const res = processAssistantQuery({
      query: "How should I store this medicine?",
      context: SAMPLE_VERIFIED_CONTEXT,
    });

    assert.strictEqual(res.success, true);
    assert.strictEqual(res.intent, "storage");
    assert.strictEqual(res.source, "verified_medicine_data");
    assert.ok(res.answer.includes("Store below 30°C"));
    assert.strictEqual(
      res.data?.storage_conditions,
      "Store below 30°C in a dry place. Protect from direct sunlight."
    );
  });

  // G. Warning query
  test("G. Warning query", () => {
    const res = processAssistantQuery({
      query: "What are the warnings and precautions?",
      context: SAMPLE_VERIFIED_CONTEXT,
    });

    assert.strictEqual(res.success, true);
    assert.strictEqual(res.intent, "warnings");
    assert.strictEqual(res.source, "verified_medicine_data");
    assert.ok(res.answer.includes("Overdose may cause serious liver damage"));
  });

  // H. Ingredients query
  test("H. Ingredients query", () => {
    const res = processAssistantQuery({
      query: "What are the active ingredients?",
      context: SAMPLE_VERIFIED_CONTEXT,
    });

    assert.strictEqual(res.success, true);
    assert.strictEqual(res.intent, "ingredients");
    assert.strictEqual(res.source, "verified_medicine_data");
    assert.ok(res.answer.includes("Paracetamol IP"));
    assert.ok(res.answer.includes("650 mg"));
  });

  // I. Dosage-form query
  test("I. Dosage-form query", () => {
    const res = processAssistantQuery({
      query: "What dosage form is this?",
      context: SAMPLE_VERIFIED_CONTEXT,
    });

    assert.strictEqual(res.success, true);
    assert.strictEqual(res.intent, "dosage_form");
    assert.strictEqual(res.source, "verified_medicine_data");
    assert.ok(res.answer.includes("Tablet"));
  });

  // J. Authenticity-status query
  test("J. Authenticity-status query", () => {
    const res = processAssistantQuery({
      query: "Is this medicine authentic and genuine?",
      context: SAMPLE_VERIFIED_CONTEXT,
    });

    assert.strictEqual(res.success, true);
    assert.strictEqual(res.intent, "authenticity");
    assert.strictEqual(res.source, "verified_medicine_data");
    assert.ok(res.answer.includes("GENUINE"));
    assert.strictEqual(res.data?.is_genuine, true);
  });

  // K. Query with no verified context
  test("K. Query with no verified context returns controlled unknown response", () => {
    const res = processAssistantQuery({
      query: "What is the expiry date?",
      context: null,
    });

    assert.strictEqual(res.success, true);
    assert.strictEqual(res.intent, "expiry_date");
    assert.strictEqual(res.source, "unverified_context");
    assert.strictEqual(res.has_verified_context, false);
    assert.strictEqual(
      res.answer,
      "I don't have enough verified medicine information to answer that question."
    );
  });

  // L. Unsupported/unknown query
  test("L. Unsupported/unknown query does not hallucinate", () => {
    const res = processAssistantQuery({
      query: "What is the stock market price of pharma companies?",
      context: SAMPLE_VERIFIED_CONTEXT,
    });

    assert.strictEqual(res.success, true);
    assert.strictEqual(res.intent, "unsupported");
    assert.strictEqual(res.source, "unverified_context");
    assert.ok(
      res.answer.includes("I don't have enough verified medicine information to answer that.")
    );
  });

  // M. Personalized dosage request is blocked by safety guardrail
  test("M. Personalized dosage request is safely blocked", () => {
    const res = processAssistantQuery({
      query: "What dosage should I personally take for my fever?",
      context: SAMPLE_VERIFIED_CONTEXT,
    });

    assert.strictEqual(res.success, true);
    assert.strictEqual(res.intent, "personalized_dosage");
    assert.strictEqual(res.source, "safety_guardrail");
    assert.ok(
      res.answer.includes("I cannot provide personalized medical diagnosis, prescriptions, or individualized dosage")
    );
    assert.ok(res.answer.includes("consult a qualified doctor or licensed healthcare professional"));
  });

  // N. Malformed request (empty query)
  test("N. Malformed request with empty query", () => {
    const res = processAssistantQuery({
      query: "   ",
      context: SAMPLE_VERIFIED_CONTEXT,
    });

    assert.strictEqual(res.success, false);
    assert.strictEqual(res.error?.code, "EMPTY_QUERY");
  });
});

const BACKEND_VERIFICATION_CONTEXT: VerifiedMedicineContext = {
  medicine: {
    name: "Paracetamol 500 mg",
    generic_name: "Paracetamol Tablets IP",
    dosage: "500 mg",
    manufacturer: "Demo Pharma",
    dosage_form: "Tablet",
    storage_instructions: "Store below 30 C in a dry place. Protect from light.",
    warnings: "Do not exceed recommended dose. Avoid consumption with alcohol."
  },
  batch: {
    batch_number: "PCM26A01",
    expiry_date: "2028-09-10",
    status: "active"
  },
  verification: {
    status: "GENUINE",
    verification_status: "AUTHENTIC",
    is_genuine: true,
    risk_score: 0
  }
};

describe("General Assistant Engine - Nested Backend Verification Payload (Member 1 Schema)", () => {
  test("What is the medicine name? → medicine_name → verified_medicine_data → answer contains 'Paracetamol 500 mg'", () => {
    const res = processAssistantQuery({
      query: "What is the medicine name?",
      context: BACKEND_VERIFICATION_CONTEXT,
    });

    assert.strictEqual(res.success, true);
    assert.strictEqual(res.intent, "medicine_name");
    assert.strictEqual(res.source, "verified_medicine_data");
    assert.ok(res.answer.includes("Paracetamol 500 mg"));
  });

  test("What is the strength of this medicine? → strength → verified_medicine_data → answer contains '500 mg'", () => {
    const res = processAssistantQuery({
      query: "What is the strength of this medicine?",
      context: BACKEND_VERIFICATION_CONTEXT,
    });

    assert.strictEqual(res.success, true);
    assert.strictEqual(res.intent, "strength");
    assert.strictEqual(res.source, "verified_medicine_data");
    assert.ok(res.answer.includes("500 mg"));
    assert.strictEqual(res.data?.strength, "500 mg");
  });

  test("manufacturer → Demo Pharma", () => {
    const res = processAssistantQuery({
      query: "Who is the manufacturer of this medicine?",
      context: BACKEND_VERIFICATION_CONTEXT,
    });

    assert.strictEqual(res.success, true);
    assert.strictEqual(res.intent, "manufacturer");
    assert.strictEqual(res.source, "verified_medicine_data");
    assert.ok(res.answer.includes("Demo Pharma"));
    assert.strictEqual(res.data?.manufacturer, "Demo Pharma");
  });

  test("expiry → 2028-09-10", () => {
    const res = processAssistantQuery({
      query: "When does it expire?",
      context: BACKEND_VERIFICATION_CONTEXT,
    });

    assert.strictEqual(res.success, true);
    assert.strictEqual(res.intent, "expiry_date");
    assert.strictEqual(res.source, "verified_medicine_data");
    assert.ok(res.answer.includes("2028-09-10"));
    assert.strictEqual(res.data?.expiry_date, "2028-09-10");
  });

  test("storage → storage instructions", () => {
    const res = processAssistantQuery({
      query: "How should I store this?",
      context: BACKEND_VERIFICATION_CONTEXT,
    });

    assert.strictEqual(res.success, true);
    assert.strictEqual(res.intent, "storage");
    assert.strictEqual(res.source, "verified_medicine_data");
    assert.ok(res.answer.includes("Store below 30 C in a dry place. Protect from light."));
    assert.strictEqual(
      res.data?.storage_conditions,
      "Store below 30 C in a dry place. Protect from light."
    );
  });

  test("warnings → warnings", () => {
    const res = processAssistantQuery({
      query: "What are the warnings?",
      context: BACKEND_VERIFICATION_CONTEXT,
    });

    assert.strictEqual(res.success, true);
    assert.strictEqual(res.intent, "warnings");
    assert.strictEqual(res.source, "verified_medicine_data");
    assert.ok(res.answer.includes("Do not exceed recommended dose. Avoid consumption with alcohol."));
  });

  test("authenticity → GENUINE and verified by Zero Latency verification backend", () => {
    const res = processAssistantQuery({
      query: "Is this medicine authentic?",
      context: BACKEND_VERIFICATION_CONTEXT,
    });

    assert.strictEqual(res.success, true);
    assert.strictEqual(res.intent, "authenticity");
    assert.strictEqual(res.source, "verified_medicine_data");
    assert.ok(res.answer.includes("GENUINE"));
    assert.ok(res.answer.includes("Zero Latency verification backend"));
    assert.strictEqual(res.data?.is_genuine, true);
  });

  test("personalized dosage query remains blocked by safety_guardrail with backend context", () => {
    const res = processAssistantQuery({
      query: "How many tablets of this should I take for my headache?",
      context: BACKEND_VERIFICATION_CONTEXT,
    });

    assert.strictEqual(res.success, true);
    assert.strictEqual(res.intent, "personalized_dosage");
    assert.strictEqual(res.source, "safety_guardrail");
    assert.ok(
      res.answer.includes("I cannot provide personalized medical diagnosis, prescriptions, or individualized dosage recommendations")
    );
  });
});

describe("Safety Guardrail Regression Tests - Personalized Dosage vs Informational Queries", () => {
  // 1. Failing query from bug report
  test("Regression: 'How many tablets should I personally take?' returns personalized_dosage from safety_guardrail", () => {
    const res = processAssistantQuery({
      query: "How many tablets should I personally take?",
      context: SAMPLE_VERIFIED_CONTEXT,
    });

    assert.strictEqual(res.success, true);
    assert.strictEqual(res.intent, "personalized_dosage");
    assert.strictEqual(res.source, "safety_guardrail");
    assert.ok(
      res.answer.includes("I cannot provide personalized medical diagnosis, prescriptions, or individualized dosage recommendations")
    );
  });

  // 2. Personalized dosage variants
  test("Variant: 'How many tablets should I take?' is blocked by safety_guardrail", () => {
    const res = processAssistantQuery({
      query: "How many tablets should I take?",
      context: SAMPLE_VERIFIED_CONTEXT,
    });

    assert.strictEqual(res.success, true);
    assert.strictEqual(res.intent, "personalized_dosage");
    assert.strictEqual(res.source, "safety_guardrail");
  });

  test("Variant: 'How much medicine should I personally take?' is blocked by safety_guardrail", () => {
    const res = processAssistantQuery({
      query: "How much medicine should I personally take?",
      context: SAMPLE_VERIFIED_CONTEXT,
    });

    assert.strictEqual(res.success, true);
    assert.strictEqual(res.intent, "personalized_dosage");
    assert.strictEqual(res.source, "safety_guardrail");
  });

  test("Variant: 'What dose should I personally take?' is blocked by safety_guardrail", () => {
    const res = processAssistantQuery({
      query: "What dose should I personally take?",
      context: SAMPLE_VERIFIED_CONTEXT,
    });

    assert.strictEqual(res.success, true);
    assert.strictEqual(res.intent, "personalized_dosage");
    assert.strictEqual(res.source, "safety_guardrail");
  });

  test("Variant: 'What dosage should I take?' is blocked by safety_guardrail", () => {
    const res = processAssistantQuery({
      query: "What dosage should I take?",
      context: SAMPLE_VERIFIED_CONTEXT,
    });

    assert.strictEqual(res.success, true);
    assert.strictEqual(res.intent, "personalized_dosage");
    assert.strictEqual(res.source, "safety_guardrail");
  });

  test("Variant: 'Can I take two tablets?' is blocked by safety_guardrail", () => {
    const res = processAssistantQuery({
      query: "Can I take two tablets?",
      context: SAMPLE_VERIFIED_CONTEXT,
    });

    assert.strictEqual(res.success, true);
    assert.strictEqual(res.intent, "personalized_dosage");
    assert.strictEqual(res.source, "safety_guardrail");
  });

  // 3. Informational questions must NOT be blocked by safety_guardrail
  test("Informational: 'What is the registered strength?' is NOT blocked by safety_guardrail", () => {
    const res = processAssistantQuery({
      query: "What is the registered strength?",
      context: SAMPLE_VERIFIED_CONTEXT,
    });

    assert.strictEqual(res.success, true);
    assert.strictEqual(res.intent, "strength");
    assert.strictEqual(res.source, "verified_medicine_data");
    assert.ok(res.answer.includes("650 mg"));
  });

  test("Informational: 'What is the dosage listed on the package?' is NOT blocked by safety_guardrail", () => {
    const res = processAssistantQuery({
      query: "What is the dosage listed on the package?",
      context: SAMPLE_VERIFIED_CONTEXT,
    });

    assert.strictEqual(res.success, true);
    assert.strictEqual(res.intent, "strength");
    assert.strictEqual(res.source, "verified_medicine_data");
    assert.ok(res.answer.includes("650 mg"));
  });

  test("Informational: 'What are the manufacturer's dosage instructions?' is NOT blocked by safety_guardrail", () => {
    const contextWithInstructions: VerifiedMedicineContext = {
      ...SAMPLE_VERIFIED_CONTEXT,
      dosage_instructions: "1 tablet every 4 to 6 hours as needed. Do not exceed 4 tablets in 24 hours.",
    };

    const res = processAssistantQuery({
      query: "What are the manufacturer's dosage instructions?",
      context: contextWithInstructions,
    });

    assert.strictEqual(res.success, true);
    assert.strictEqual(res.intent, "dosage_instructions");
    assert.strictEqual(res.source, "verified_medicine_data");
    assert.ok(res.answer.includes("1 tablet every 4 to 6 hours"));
  });
});

