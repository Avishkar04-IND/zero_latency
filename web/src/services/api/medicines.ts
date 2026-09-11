import { apiClient, ApiError } from "./client";
import { MedicineResponse, MedicineQueryParams } from "@/types/medicine";

/**
 * Isolated temporary fallback data strictly mirroring backend seed data (backend/app/seeds/seed_data.py).
 * Used only if backend server is unreachable during standalone frontend UI execution.
 */
const FALLBACK_SEED_MEDICINES: MedicineResponse[] = [
  {
    id: 1,
    organization_id: 1,
    brand_name: "Dolo-650",
    generic_name: "Paracetamol Tablets IP",
    category: "Analgesic & Antipyretic",
    manufacturer: "Micro Labs Limited",
    dosage_form: "Tablet",
    strength: "650 mg",
    active_ingredients: [
      { name: "Paracetamol IP", strength: "650", unit: "mg", purpose: "Active Analgesic & Antipyretic" },
    ],
    inactive_excipients: [
      "Starch IP",
      "Microcrystalline Cellulose",
      "Povidone K-30",
      "Sodium Starch Glycolate",
      "Magnesium Stearate",
      "Purified Talc",
    ],
    tablet_shape: "Capsule-shaped",
    tablet_color: "White",
    score_line: "Single break-line on one side",
    coating_type: "Uncoated",
    indications: "Relief of mild to moderate pain including headache, body ache, toothache, and reduction of fever.",
    dosage_instructions: "Take 1 tablet every 6 to 8 hours with water. Maximum 4 tablets in 24 hours. Do not exceed.",
    warnings_and_precautions: "Overdose may cause serious liver damage. Avoid consumption with alcohol.",
    side_effects: "Rare: allergic skin rash, nausea. High dosage causes hepatic toxicity.",
    storage_conditions: "Store below 30°C in a dry place. Protect from moisture and direct light.",
    schedule_type: "OTC",
    voice_summary_en: "Dolo 650 milligram tablet. Contains Paracetamol. For fever and body pain. Take one tablet every 6 hours after meals. Do not exceed 4 tablets a day.",
    voice_summary_hi: "डोलो 650 मिलीग्राम टैबलेट। इसमें पैरासिटामोल है। यह बुखार और दर्द के लिए है। 24 घंटे में चार से अधिक गोलियां न लें।",
    voice_summary_mr: "डोलो 650 मिलिगॅ्रम गोळी. यात पॅरासिटामॉल आहे. ताप आणि अंगदुखीसाठी. जेवणानंतर दर 6 तासांनी एक गोळी घ्या.",
    created_at: "2026-09-01T00:00:00",
  },
  {
    id: 2,
    organization_id: 1,
    brand_name: "Augmentin 625 Duo",
    generic_name: "Amoxicillin and Potassium Clavulanate Tablets IP",
    category: "Broad-Spectrum Antibiotic",
    manufacturer: "GlaxoSmithKline Pharmaceuticals",
    dosage_form: "Tablet",
    strength: "625 mg (500mg + 125mg)",
    active_ingredients: [
      { name: "Amoxicillin Trihydrate IP equivalent to Amoxicillin", strength: "500", unit: "mg", purpose: "Antibacterial" },
      { name: "Potassium Clavulanate Diluted IP eq. to Clavulanic Acid", strength: "125", unit: "mg", purpose: "Beta-lactamase Inhibitor" },
    ],
    inactive_excipients: [
      "Microcrystalline Cellulose",
      "Sodium Starch Glycolate",
      "Colloidal Silicon Dioxide",
      "Magnesium Stearate",
      "Titanium Dioxide",
      "Hypromellose",
    ],
    tablet_shape: "Oval biconvex",
    tablet_color: "Off-white to pale yellow",
    score_line: "None",
    coating_type: "Film-coated",
    indications: "Bacterial infections of the respiratory tract, ear-nose-throat, skin, and urinary tract.",
    dosage_instructions: "1 tablet twice daily at the start of a meal to minimize gastrointestinal discomfort.",
    warnings_and_precautions: "Complete full prescribed course. Contraindicated in patients with penicillin hypersensitivity.",
    side_effects: "Diarrhea, nausea, vomiting, abdominal cramp, candida overgrowth.",
    storage_conditions: "Store protected from moisture below 25°C. Keep blister sealed until use.",
    schedule_type: "Schedule H1 (Prescription Required)",
    voice_summary_en: "Augmentin 625 Duo antibiotic tablet. Contains Amoxicillin and Clavulanate. Take one tablet twice daily with food. Complete the full antibiotic course.",
    voice_summary_hi: "ऑगमेंटिन 625 डुओ एंटीबायोटिक टैबलेट। भोजन के साथ दिन में दो बार लें।",
    voice_summary_mr: "ऑगमेंटिन 625 डुओ अँटीबायोटिक गोळी. जेवणासोबत दिवसातून दोन वेळा घ्या.",
    created_at: "2026-09-01T00:00:00",
  },
  {
    id: 3,
    organization_id: 1,
    brand_name: "Azee 500",
    generic_name: "Azithromycin Tablets IP",
    category: "Macrolide Antibiotic",
    manufacturer: "Cipla Limited",
    dosage_form: "Tablet",
    strength: "500 mg",
    active_ingredients: [
      { name: "Azithromycin Dihydrate IP equivalent to Azithromycin", strength: "500", unit: "mg", purpose: "Macrolide Antibiotic" },
    ],
    inactive_excipients: [
      "Lactose Monohydrate",
      "Pregelatinized Starch",
      "Croscarmellose Sodium",
      "Magnesium Stearate",
      "Sodium Lauryl Sulfate",
      "Opadry White Coating",
    ],
    tablet_shape: "Capsule-shaped",
    tablet_color: "White",
    score_line: "Single score line",
    coating_type: "Film-coated",
    indications: "Treatment of chest infections, sinus infections, throat infections, skin infections and typhoid.",
    dosage_instructions: "Take 1 tablet once daily, preferably 1 hour before or 2 hours after meals for 3 to 5 days.",
    warnings_and_precautions: "Caution in patients with liver disorders or heart arrhythmia (QT prolongation).",
    side_effects: "Loose motions, stomach upset, nausea, headache.",
    storage_conditions: "Store below 25°C in a dry place. Protect from light.",
    schedule_type: "Schedule H1",
    voice_summary_en: "Azee 500 Azithromycin tablet. Take one tablet once daily on an empty stomach for three days. Do not stop midway.",
    voice_summary_hi: "एज़ी 500 एज़िथ्रोमाइसिन टैबलेट। दिन में एक बार खाली पेट 3 दिनों के लिए लें।",
    voice_summary_mr: "अझी 500 अझिथ्रोमायसिन गोळी. दिवसातून एकदा उपाशी पोटी 3 दिवस घ्या.",
    created_at: "2026-09-01T00:00:00",
  },
  {
    id: 4,
    organization_id: 1,
    brand_name: "Pan 40",
    generic_name: "Pantoprazole Gastro-resistant Tablets IP",
    category: "Proton Pump Inhibitor (Antacid)",
    manufacturer: "Alkem Laboratories",
    dosage_form: "Tablet",
    strength: "40 mg",
    active_ingredients: [
      { name: "Pantoprazole Sodium Sesquihydrate IP eq. to Pantoprazole", strength: "40", unit: "mg", purpose: "Gastric Acid Reducer" },
    ],
    inactive_excipients: [
      "Sodium Carbonate",
      "Mannitol",
      "Crospovidone",
      "Povidone K-90",
      "Calcium Stearate",
      "Eudragit L30D-55",
    ],
    tablet_shape: "Oval",
    tablet_color: "Yellow",
    score_line: "None",
    coating_type: "Enteric-coated",
    indications: "Gastroesophageal reflux disease (GERD), peptic ulcer disease, Zollinger-Ellison syndrome.",
    dosage_instructions: "1 tablet once daily in the morning, 30 to 60 minutes before breakfast. Swallow whole.",
    warnings_and_precautions: "Do not crush or chew. Long term use (>3 years) may reduce vitamin B12 absorption.",
    side_effects: "Headache, mild diarrhea, abdominal discomfort, flatulence.",
    storage_conditions: "Store below 25°C. Protect from moisture and heat.",
    schedule_type: "Schedule H",
    voice_summary_en: "Pan 40 Pantoprazole tablet. For acidity and heartburn. Take one tablet daily in the morning before breakfast. Do not chew.",
    voice_summary_hi: "पैन 40 टैबलेट। एसिडिटी और सीने में जलन के लिए। रोज सुबह नाश्ते से आधा घंटा पहले लें।",
    voice_summary_mr: "पॅन 40 गोळी. पित्त आणि ॲसिडिटीसाठी. रोज सकाळी नाश्त्यापूर्वी अर्धा तास घ्या.",
    created_at: "2026-09-01T00:00:00",
  },
  {
    id: 5,
    organization_id: 1,
    brand_name: "Paracetamol 500 mg",
    generic_name: "Paracetamol Tablets IP",
    category: "Analgesic & Antipyretic",
    manufacturer: "Cipla Limited",
    dosage_form: "Tablet",
    strength: "500 mg",
    active_ingredients: [
      { name: "Paracetamol IP", strength: "500", unit: "mg", purpose: "Active Analgesic & Antipyretic" },
    ],
    inactive_excipients: [
      "Starch IP",
      "Microcrystalline Cellulose",
      "Magnesium Stearate",
    ],
    tablet_shape: "Round",
    tablet_color: "White",
    score_line: "Single break-line",
    coating_type: "Uncoated",
    indications: "Relief of mild to moderate pain and reduction of fever.",
    dosage_instructions: "Take 1 tablet every 4 to 6 hours as needed. Maximum 4000 mg per 24 hours.",
    warnings_and_precautions: "Do not exceed recommended dose. Do not take with other paracetamol products.",
    side_effects: "Rare skin reactions or hypersensitivity.",
    storage_conditions: "Store below 25°C in a dry place.",
    schedule_type: "OTC",
    voice_summary_en: "Paracetamol 500 milligram tablet. Take one tablet every 4 to 6 hours for pain or fever.",
    voice_summary_hi: "पैरासिटामोल 500 मिलीग्राम टैबलेट। दर्द या बुखार के लिए हर 4 से 6 घंटे में एक गोली लें।",
    voice_summary_mr: "पॅरासिटामॉल 500 मिग्रॅ गोळी. वेदना किंवा तापासाठी दर 4 ते 6 तासांनी एक गोळी घ्या.",
    created_at: "2026-09-01T00:00:00",
  },
];

/**
 * Fetches medicines from the backend API: GET /api/v1/medicines
 * Supports search term (q), category filtering, pagination.
 */
export async function getMedicines(
  params?: MedicineQueryParams
): Promise<MedicineResponse[]> {
  const query = new URLSearchParams();
  if (params?.q) query.set("q", params.q.trim());
  if (params?.category) query.set("category", params.category.trim());
  if (params?.organization_id) query.set("organization_id", String(params.organization_id));
  if (params?.limit) query.set("limit", String(params.limit));
  if (params?.offset) query.set("offset", String(params.offset));

  const endpoint = `/medicines${query.toString() ? `?${query.toString()}` : ""}`;

  try {
    const data = await apiClient<MedicineResponse[]>(endpoint, { method: "GET" });
    return data;
  } catch (err: any) {
    // If backend is offline or network error, fallback to isolated seed data for local dev
    if (err instanceof ApiError && err.status === 0) {
      console.warn("[API:Medicines] Backend server unreachable. Using isolated seed dataset for UI development.");
      let results = [...FALLBACK_SEED_MEDICINES];
      if (params?.q) {
        const qLower = params.q.toLowerCase().trim();
        results = results.filter(
          (m) =>
            m.brand_name.toLowerCase().includes(qLower) ||
            m.generic_name.toLowerCase().includes(qLower) ||
            m.category.toLowerCase().includes(qLower)
        );
      }
      return results;
    }
    throw err;
  }
}

/**
 * Fetches a single medicine by ID from the backend API: GET /api/v1/medicines/{id}
 */
export async function getMedicineById(id: number): Promise<MedicineResponse> {
  try {
    return await apiClient<MedicineResponse>(`/medicines/${id}`, { method: "GET" });
  } catch (err: any) {
    if (err instanceof ApiError && err.status === 0) {
      const found = FALLBACK_SEED_MEDICINES.find((m) => m.id === id);
      if (found) return found;
    }
    throw err;
  }
}
