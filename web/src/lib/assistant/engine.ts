import type {
  AssistantIntent,
  AssistantQueryRequest,
  AssistantQueryResponse,
  NormalizedMedicineData,
  VerifiedMedicineContext,
} from "../../types/assistant";
import type { ActiveIngredient } from "../../types/medicine";

/**
 * Normalizes varied context shapes into a single canonical NormalizedMedicineData structure.
 * Handles nested objects ({ medicine: ..., batch: ..., verification: ... }) as well as flat fields.
 */
export function normalizeContext(
  context?: VerifiedMedicineContext | null
): NormalizedMedicineData | null {
  if (!context) return null;

  const med = context.medicine || {};
  const batch = context.batch || {};
  const verif = context.verification || {};

  const brand_name =
    context.brand_name || context.name || med.brand_name || med.name || null;
  const generic_name = context.generic_name || med.generic_name || null;
  const strength =
    context.strength || context.dosage || med.strength || med.dosage || null;
  const dosage_form = context.dosage_form || med.dosage_form || null;
  const manufacturer = context.manufacturer || med.manufacturer || null;
  const category = med.category || null;

  const batch_no =
    context.batch_no ||
    context.batch_number ||
    batch.batch_no ||
    batch.batch_number ||
    null;
  const mfg_date = context.mfg_date || batch.mfg_date || null;
  const exp_date =
    context.exp_date ||
    context.expiry_date ||
    batch.exp_date ||
    batch.expiry_date ||
    null;
  const quantity = batch.quantity || null;
  const mrp = batch.mrp || null;

  const active_ingredients =
    context.active_ingredients || med.active_ingredients || null;
  const inactive_excipients = med.inactive_excipients || null;
  const indications = context.indications || med.indications || null;
  const warnings_and_precautions =
    context.warnings_and_precautions ||
    context.warnings ||
    med.warnings_and_precautions ||
    med.warnings ||
    null;
  const storage_conditions =
    context.storage_conditions ||
    context.storage_instructions ||
    med.storage_conditions ||
    med.storage_instructions ||
    null;
  const schedule_type = context.schedule_type || med.schedule_type || null;
  const side_effects = context.side_effects || med.side_effects || null;
  const dosage_instructions =
    context.dosage_instructions || med.dosage_instructions || null;

  const is_genuine =
    context.is_genuine !== undefined
      ? context.is_genuine
      : verif.is_genuine !== undefined
      ? verif.is_genuine
      : null;

  const verification_status =
    context.verification_status ||
    verif.verification_status ||
    context.status ||
    verif.status ||
    (is_genuine === true ? "GENUINE" : is_genuine === false ? "INVALID" : null);

  // If completely empty, return null
  const hasAnyField =
    Boolean(brand_name) ||
    Boolean(generic_name) ||
    Boolean(batch_no) ||
    Boolean(exp_date) ||
    Boolean(manufacturer) ||
    Boolean(active_ingredients && active_ingredients.length > 0) ||
    is_genuine !== null;

  if (!hasAnyField) return null;

  return {
    brand_name,
    generic_name,
    strength,
    dosage_form,
    manufacturer,
    category,
    batch_no,
    mfg_date,
    exp_date,
    quantity,
    mrp,
    active_ingredients,
    inactive_excipients,
    indications,
    warnings_and_precautions,
    storage_conditions,
    schedule_type,
    side_effects,
    dosage_instructions,
    is_genuine,
    verification_status,
  };
}

/**
 * Detects whether a query is attempting to solicit personalized medical diagnoses,
 * individualized dosage guidance, or clinician-level prescriptions.
 */
export function isUnsafeMedicalQuery(query: string): boolean {
  const q = query.toLowerCase().trim();

  const unsafePatterns = [
    // Personalized quantity or administration queries ("how many tablets should I personally take?", "how much medicine should I take?", etc.)
    /how\s+(many|much)\b.*?\b(should|can|could|do|may)\s+i\s+(personally\s+)?(take|eat|swallow|consume|use|drink|have)/i,
    /how\s+(many|much)\s+(should|can|could|do|may)\s+i\s+(personally\s+)?(take|eat|swallow|consume|use|drink|have)/i,
    /how\s+(much|many)\s+should\s+i\s+(personally\s+)?take/i,

    // Personalized dosage/dose queries ("what dose should I personally take?", "what dosage should I take?", etc.)
    /what\s+(dose|dosage)\b.*?\b(should|can|could|do|may)\s+i\s+(personally\s+)?(take|eat|swallow|consume|use|drink|have)/i,
    /what\s+is\s+the\s+(dose|dosage)\b.*?\bi\s+(should|can|could|do|may)\s+(personally\s+)?(take|eat|swallow|consume|use|drink|have)/i,

    // Self-directed intake queries ("can I take two tablets?", "should I take 3 pills?", etc.)
    /(can|should|could|may|do)\s+i\s+(personally\s+)?(take|eat|swallow|consume|drink|use|have)\s+(\d+|one|two|three|four|five|six|seven|eight|nine|ten|a|an|another|more|some|this|it)\b/i,
    /can\s+i\s+(personally\s+)?take\s+(\d+|one|two|three|four|five)\s+(tablets?|pills?|capsules?|drops?|spoons?)/i,
    /can\s+i\s+take\s+(this|it)\s+with\s+alcohol/i,
    /can\s+i\s+double\s+(the\s+)?(dose|dosage)/i,
    /is\s+it\s+(safe|okay|ok|alright)\s+(for\s+me\s+)?to\s+take/i,
    /is\s+it\s+okay\s+for\s+me\s+to\s+take\s+(\d+)/i,
    /how\s+often\s+(should|can|do)\s+i\s+(take|use|consume)/i,

    // Prescription & Diagnosis requests
    /prescribe\s+(me|for\s+me|a\s+dose|something)/i,
    /give\s+me\s+a\s+prescription/i,
    /can\s+you\s+diagnose\s+(me|my\s+condition|my\s+symptoms)/i,
    /what\s+disease\s+do\s+i\s+have/i,
    /do\s+i\s+have\s+(cancer|covid|diabetes|infection|flu)/i,
  ];

  return unsafePatterns.some((pattern) => pattern.test(q));
}

/**
 * Formats a list of active ingredients into a clear human-readable string.
 */
function formatIngredients(
  ingredients: ActiveIngredient[] | string[] | null | undefined
): string {
  if (!ingredients || ingredients.length === 0) return "";
  return ingredients
    .map((item) => {
      if (typeof item === "string") return item;
      return `${item.name} (${item.strength}${item.unit ? ` ${item.unit}` : ""}${
        item.purpose ? ` - ${item.purpose}` : ""
      })`;
    })
    .join(", ");
}

/**
 * Humanizes date strings for conversational TTS playback.
 */
function formatTtsDate(dateStr: string): string {
  try {
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return dateStr;
    const months = [
      "January", "February", "March", "April", "May", "June",
      "July", "August", "September", "October", "November", "December",
    ];
    return `${months[d.getMonth()]} ${d.getDate()}, ${d.getFullYear()}`;
  } catch {
    return dateStr;
  }
}

/**
 * Main Deterministic Query Processor
 */
export function processAssistantQuery(
  request: AssistantQueryRequest
): AssistantQueryResponse {
  const rawQuery = request.query || request.query_text || "";
  const query = rawQuery.trim();

  // 1. Validate query existence
  if (!query) {
    return {
      success: false,
      intent: "unsupported",
      answer: "Please provide a valid question about your verified medicine.",
      source: "system",
      has_verified_context: false,
      confidence: 0,
      tts_clean_text: "Please provide a valid question about your verified medicine.",
      error: {
        code: "EMPTY_QUERY",
        message: "Query text cannot be empty.",
      },
    };
  }

  // 2. Resolve Verified Medicine Context
  const medData = normalizeContext(request.context || request.medicine_context);
  const qLower = query.toLowerCase();

  // 3. Safety Guardrail: Block Unsafe Personalized Medical Requests
  if (isUnsafeMedicalQuery(query)) {
    const safeAnswer =
      "I cannot provide personalized medical diagnosis, prescriptions, or individualized dosage recommendations. Please consult a qualified doctor or licensed healthcare professional for guidance specific to your condition.";

    return {
      success: true,
      intent: "personalized_dosage",
      answer: safeAnswer,
      source: "safety_guardrail",
      has_verified_context: Boolean(medData),
      confidence: 1.0,
      tts_clean_text: safeAnswer,
      suggested_actions: [
        "Consult Healthcare Provider",
        "View Standard Package Label",
      ],
      data: {
        safety_notice: "PERSONALIZED_MEDICAL_ADVICE_PROHIBITED",
      },
    };
  }

  // Helper response for missing verified data
  const notEnoughInfo = (intent: AssistantIntent, fieldName: string) => ({
    success: true,
    intent,
    answer: `I don't have enough verified medicine information to answer that question.`,
    source: "unverified_context" as const,
    has_verified_context: false,
    confidence: 0.9,
    tts_clean_text:
      "I don't have enough verified medicine information to answer that question.",
    data: {
      missing_field: fieldName,
    },
  });

  // 4. Deterministic Intent Matching

  // A. Expiry Date
  if (
    /expir(y|ation|e|ed|ing)/i.test(qLower) ||
    /shelf life/i.test(qLower) ||
    /valid till|valid until|best before|use by/i.test(qLower)
  ) {
    if (!medData || !medData.exp_date) {
      return notEnoughInfo("expiry_date", "exp_date");
    }

    const expDate = medData.exp_date;
    const isExpired = new Date(expDate).getTime() < Date.now();
    const friendlyDate = formatTtsDate(expDate);

    const answer = isExpired
      ? `The registered expiration date is ${expDate}. WARNING: This batch is expired and must not be consumed.`
      : `The medicine expires on ${expDate}. The batch is within its registered shelf life.`;

    const ttsClean = isExpired
      ? `The registered expiration date is ${friendlyDate}. Warning: This batch is expired and must not be consumed.`
      : `The medicine expires on ${friendlyDate}. The batch is within its registered shelf life.`;

    return {
      success: true,
      intent: "expiry_date",
      answer,
      source: "verified_medicine_data",
      has_verified_context: true,
      confidence: 1.0,
      tts_clean_text: ttsClean,
      data: {
        expiry_date: expDate,
        is_expired: isExpired,
        batch_no: medData.batch_no || null,
      },
    };
  }

  // B. Medicine Name / Brand Name / Generic Name
  if (
    /what('s| is) (the )?(medicine|brand|product|generic)? ?name/i.test(qLower) ||
    /what medicine is this/i.test(qLower) ||
    /which medicine/i.test(qLower) ||
    /name of (this|the) (medicine|tablet|drug|product)/i.test(qLower) ||
    qLower === "medicine name" ||
    qLower === "brand name"
  ) {
    if (!medData || !medData.brand_name) {
      return notEnoughInfo("medicine_name", "brand_name");
    }

    const answer = medData.generic_name
      ? `This medicine is ${medData.brand_name}, generic formulation: ${medData.generic_name}.`
      : `This medicine is ${medData.brand_name}.`;

    return {
      success: true,
      intent: "medicine_name",
      answer,
      source: "verified_medicine_data",
      has_verified_context: true,
      confidence: 1.0,
      tts_clean_text: answer,
      data: {
        brand_name: medData.brand_name,
        generic_name: medData.generic_name || null,
      },
    };
  }

  // C. Strength / Potency
  if (
    /strength/i.test(qLower) ||
    /how many (mg|milligram|mcg|ml|microgram)/i.test(qLower) ||
    /dosage strength/i.test(qLower) ||
    /potency/i.test(qLower) ||
    /dosage (listed|printed|written|stated|given) on (the )?(package|label|box)/i.test(qLower) ||
    /dosage on (the )?(package|label|box)/i.test(qLower)
  ) {
    if (!medData || !medData.strength) {
      return notEnoughInfo("strength", "strength");
    }

    const answer = `The registered strength of ${medData.brand_name || "this medicine"} is ${medData.strength}.`;

    return {
      success: true,
      intent: "strength",
      answer,
      source: "verified_medicine_data",
      has_verified_context: true,
      confidence: 1.0,
      tts_clean_text: answer,
      data: {
        strength: medData.strength,
      },
    };
  }

  // D. Manufacturer / Company
  if (
    !/instructions/i.test(qLower) &&
    (/who (made|manufactured|produced|makes)/i.test(qLower) ||
      /manufacturer/i.test(qLower) ||
      /company (name|produced|made)/i.test(qLower) ||
      /which company/i.test(qLower))
  ) {
    if (!medData || !medData.manufacturer) {
      return notEnoughInfo("manufacturer", "manufacturer");
    }

    const answer = `${medData.brand_name || "This medicine"} is manufactured by ${medData.manufacturer}.`;

    return {
      success: true,
      intent: "manufacturer",
      answer,
      source: "verified_medicine_data",
      has_verified_context: true,
      confidence: 1.0,
      tts_clean_text: answer,
      data: {
        manufacturer: medData.manufacturer,
      },
    };
  }

  // E. Batch Number / Lot Number
  if (
    /batch (number|no|code|id)/i.test(qLower) ||
    /lot (number|no|code)/i.test(qLower) ||
    /what batch/i.test(qLower) ||
    qLower === "batch" ||
    qLower === "batch no"
  ) {
    if (!medData || !medData.batch_no) {
      return notEnoughInfo("batch_number", "batch_no");
    }

    const answer = `The registered manufacturing batch number is ${medData.batch_no}.`;

    return {
      success: true,
      intent: "batch_number",
      answer,
      source: "verified_medicine_data",
      has_verified_context: true,
      confidence: 1.0,
      tts_clean_text: answer,
      data: {
        batch_no: medData.batch_no,
      },
    };
  }

  // F. Active Ingredients / Composition
  if (
    /ingredient/i.test(qLower) ||
    /composition/i.test(qLower) ||
    /what does (this|it) contain/i.test(qLower) ||
    /active (ingredient|salt|substance)/i.test(qLower) ||
    /what is in (this|it)/i.test(qLower) ||
    /chemical composition/i.test(qLower) ||
    /salt/i.test(qLower)
  ) {
    if (
      !medData ||
      !medData.active_ingredients ||
      medData.active_ingredients.length === 0
    ) {
      return notEnoughInfo("ingredients", "active_ingredients");
    }

    const formatted = formatIngredients(medData.active_ingredients);
    const answer = `The active ingredients in ${medData.brand_name || "this medicine"} are: ${formatted}.`;

    return {
      success: true,
      intent: "ingredients",
      answer,
      source: "verified_medicine_data",
      has_verified_context: true,
      confidence: 1.0,
      tts_clean_text: answer,
      data: {
        active_ingredients: medData.active_ingredients,
      },
    };
  }

  // G. Storage Instructions
  if (
    /stor(e|age|ing)/i.test(qLower) ||
    /keep (in|at)/i.test(qLower) ||
    /refrigerat/i.test(qLower) ||
    /temperature/i.test(qLower) ||
    /how to keep/i.test(qLower)
  ) {
    if (!medData || !medData.storage_conditions) {
      return notEnoughInfo("storage", "storage_conditions");
    }

    const answer = `Recommended storage instructions: ${medData.storage_conditions}`;

    return {
      success: true,
      intent: "storage",
      answer,
      source: "verified_medicine_data",
      has_verified_context: true,
      confidence: 1.0,
      tts_clean_text: answer,
      data: {
        storage_conditions: medData.storage_conditions,
      },
    };
  }

  // H. Warnings & Precautions
  if (
    /warning/i.test(qLower) ||
    /precaution/i.test(qLower) ||
    /side effect/i.test(qLower) ||
    /danger/i.test(qLower) ||
    /contraindicat/i.test(qLower) ||
    /adverse/i.test(qLower)
  ) {
    if (!medData || !medData.warnings_and_precautions) {
      return notEnoughInfo("warnings", "warnings_and_precautions");
    }

    let answer = `Warnings and precautions for ${medData.brand_name || "this medicine"}: ${medData.warnings_and_precautions}`;
    if (medData.side_effects) {
      answer += ` Possible side effects: ${medData.side_effects}`;
    }

    return {
      success: true,
      intent: "warnings",
      answer,
      source: "verified_medicine_data",
      has_verified_context: true,
      confidence: 1.0,
      tts_clean_text: answer,
      data: {
        warnings_and_precautions: medData.warnings_and_precautions,
        side_effects: medData.side_effects || null,
      },
    };
  }

  // I. Dosage Form / Physical Specifications
  if (
    /dosage form/i.test(qLower) ||
    /what form/i.test(qLower) ||
    /is (this|it) a (tablet|capsule|syrup|injection|pill)/i.test(qLower) ||
    /tablet shape/i.test(qLower) ||
    /physical form/i.test(qLower)
  ) {
    if (!medData || !medData.dosage_form) {
      return notEnoughInfo("dosage_form", "dosage_form");
    }

    const answer = `This medicine is supplied in ${medData.dosage_form} form.`;

    return {
      success: true,
      intent: "dosage_form",
      answer,
      source: "verified_medicine_data",
      has_verified_context: true,
      confidence: 1.0,
      tts_clean_text: answer,
      data: {
        dosage_form: medData.dosage_form,
      },
    };
  }

  // J. Authenticity / Verification Status
  if (
    /authentic/i.test(qLower) ||
    /genuine/i.test(qLower) ||
    /counterfeit/i.test(qLower) ||
    /real or fake/i.test(qLower) ||
    /is (this|it) (real|fake|original|verified)/i.test(qLower) ||
    /verification status/i.test(qLower) ||
    /is this medicine authentic/i.test(qLower)
  ) {
    if (
      !medData ||
      (medData.is_genuine === null && !medData.verification_status)
    ) {
      return notEnoughInfo("authenticity", "verification_status");
    }

    const isGenuine =
      medData.is_genuine !== null && medData.is_genuine !== undefined
        ? medData.is_genuine
        : medData.verification_status === "GENUINE" ||
          medData.verification_status === "AUTHENTIC";
    const statusText =
      medData.verification_status || (isGenuine ? "GENUINE" : "SUSPECTED");

    const answer = isGenuine
      ? `This medicine is verified as GENUINE by the Zero Latency verification backend.`
      : `Verification notice: Status is ${statusText}. Exercise caution and verify packaging authenticity with the supplier.`;

    return {
      success: true,
      intent: "authenticity",
      answer,
      source: "verified_medicine_data",
      has_verified_context: true,
      confidence: 1.0,
      tts_clean_text: answer,
      data: {
        is_genuine: isGenuine,
        verification_status: statusText,
      },
    };
  }

  // K. Approved Indications
  if (
    /what is (this|it) (used for|for)/i.test(qLower) ||
    /indication/i.test(qLower) ||
    /why (take|use) this/i.test(qLower) ||
    /what does (this|it) treat/i.test(qLower)
  ) {
    if (!medData || !medData.indications) {
      return notEnoughInfo("indications", "indications");
    }

    const answer = `Approved indications for ${medData.brand_name || "this medicine"}: ${medData.indications}`;

    return {
      success: true,
      intent: "indications",
      answer,
      source: "verified_medicine_data",
      has_verified_context: true,
      confidence: 1.0,
      tts_clean_text: answer,
      data: {
        indications: medData.indications,
      },
    };
  }

  // L. General Manufacturer Package Label Directions (Non-personalized)
  if (
    /package instructions/i.test(qLower) ||
    /label (directions|instructions)/i.test(qLower) ||
    /manufacturer directions/i.test(qLower) ||
    /dosage instructions/i.test(qLower) ||
    /manufacturer('?s)? dosage instructions/i.test(qLower) ||
    /manufacturer('?s)? instructions/i.test(qLower) ||
    /directions for use/i.test(qLower)
  ) {
    if (!medData || !medData.dosage_instructions) {
      return notEnoughInfo("dosage_instructions", "dosage_instructions");
    }

    const answer = `Manufacturer package label instructions: ${medData.dosage_instructions}. Note: This is general label information, not personalized medical advice.`;

    return {
      success: true,
      intent: "dosage_instructions",
      answer,
      source: "verified_medicine_data",
      has_verified_context: true,
      confidence: 1.0,
      tts_clean_text: answer,
      data: {
        dosage_instructions: medData.dosage_instructions,
      },
    };
  }

  // M. Friendly Greeting
  if (/^(hi|hello|hey|greetings|good (morning|afternoon|evening))/i.test(qLower)) {
    const medName = medData?.brand_name ? ` regarding ${medData.brand_name}` : "";
    const answer = `Hello! I am your Zero Latency Medicine Assistant. You can ask me about verified medicine details${medName}, such as expiry date, manufacturer, batch number, active ingredients, storage conditions, or authenticity status.`;

    return {
      success: true,
      intent: "general_greeting",
      answer,
      source: "system",
      has_verified_context: Boolean(medData),
      confidence: 1.0,
      tts_clean_text: answer,
      suggested_actions: [
        "What is the expiry date?",
        "Who is the manufacturer?",
        "What are the active ingredients?",
      ],
    };
  }

  // N. Unknown / Unsupported Query
  const fallbackAnswer =
    "I don't have enough verified medicine information to answer that. You can ask about verified medicine name, strength, manufacturer, batch number, expiry date, ingredients, storage, or warnings.";

  return {
    success: true,
    intent: "unsupported",
    answer: fallbackAnswer,
    source: "unverified_context",
    has_verified_context: Boolean(medData),
    confidence: 0.5,
    tts_clean_text: fallbackAnswer,
    suggested_actions: [
      "What is the expiry date?",
      "Who is the manufacturer?",
      "What are the ingredients?",
    ],
  };
}
