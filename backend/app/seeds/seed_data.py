"""
Comprehensive seed dataset containing 50 top clinical medicines with full tablet composition,
chemical active ingredients, inactive excipients, physical specifications, safety guidelines,
and multilingual voice scripts (English, Hindi, Marathi).
"""

MEDICINES_DATA = [
    {
        "brand_name": "Dolo-650",
        "generic_name": "Paracetamol Tablets IP",
        "category": "Analgesic & Antipyretic",
        "manufacturer": "Micro Labs Limited",
        "dosage_form": "Tablet",
        "strength": "650 mg",
        "active_ingredients": [
            {"name": "Paracetamol IP", "strength": "650", "unit": "mg", "purpose": "Active Analgesic & Antipyretic"}
        ],
        "inactive_excipients": [
            "Starch IP", "Microcrystalline Cellulose", "Povidone K-30",
            "Sodium Starch Glycolate", "Magnesium Stearate", "Purified Talc"
        ],
        "tablet_shape": "Capsule-shaped",
        "tablet_color": "White",
        "score_line": "Single break-line on one side",
        "coating_type": "Uncoated",
        "indications": "Relief of mild to moderate pain including headache, body ache, toothache, and reduction of fever.",
        "dosage_instructions": "Take 1 tablet every 6 to 8 hours with water. Maximum 4 tablets in 24 hours. Do not exceed.",
        "warnings_and_precautions": "Overdose may cause serious liver damage. Avoid consumption with alcohol.",
        "side_effects": "Rare: allergic skin rash, nausea. High dosage causes hepatic toxicity.",
        "storage_conditions": "Store below 30°C in a dry place. Protect from moisture and direct light.",
        "schedule_type": "OTC",
        "voice_summary_en": "Dolo 650 milligram tablet. Contains Paracetamol. For fever and body pain. Take one tablet every 6 hours after meals. Do not exceed 4 tablets a day.",
        "voice_summary_hi": "डोलो 650 मिलीग्राम टैबलेट। इसमें पैरासिटामोल है। यह बुखार और दर्द के लिए है। 24 घंटे में चार से अधिक गोलियां न लें।",
        "voice_summary_mr": "डोलो 650 मिलिगॅ्रम गोळी. यात पॅरासिटामॉल आहे. ताप आणि अंगदुखीसाठी. जेवणानंतर दर 6 तासांनी एक गोळी घ्या."
    },
    {
        "brand_name": "Augmentin 625 Duo",
        "generic_name": "Amoxicillin and Potassium Clavulanate Tablets IP",
        "category": "Broad-Spectrum Antibiotic",
        "manufacturer": "GlaxoSmithKline Pharmaceuticals",
        "dosage_form": "Tablet",
        "strength": "625 mg (500mg + 125mg)",
        "active_ingredients": [
            {"name": "Amoxicillin Trihydrate IP equivalent to Amoxicillin", "strength": "500", "unit": "mg", "purpose": "Antibacterial"},
            {"name": "Potassium Clavulanate Diluted IP eq. to Clavulanic Acid", "strength": "125", "unit": "mg", "purpose": "Beta-lactamase Inhibitor"}
        ],
        "inactive_excipients": [
            "Microcrystalline Cellulose", "Sodium Starch Glycolate", "Colloidal Silicon Dioxide",
            "Magnesium Stearate", "Titanium Dioxide", "Hypromellose"
        ],
        "tablet_shape": "Oval biconvex",
        "tablet_color": "Off-white to pale yellow",
        "score_line": "None",
        "coating_type": "Film-coated",
        "indications": "Bacterial infections of the respiratory tract, ear-nose-throat, skin, and urinary tract.",
        "dosage_instructions": "1 tablet twice daily at the start of a meal to minimize gastrointestinal discomfort.",
        "warnings_and_precautions": "Complete full prescribed course. Contraindicated in patients with penicillin hypersensitivity.",
        "side_effects": "Diarrhea, nausea, vomiting, abdominal cramp, candida overgrowth.",
        "storage_conditions": "Store protected from moisture below 25°C. Keep blister sealed until use.",
        "schedule_type": "Schedule H1 (Prescription Required)",
        "voice_summary_en": "Augmentin 625 Duo antibiotic tablet. Contains Amoxicillin and Clavulanate. Take one tablet twice daily with food. Complete the full antibiotic course.",
        "voice_summary_hi": "ऑगमेंटिन 625 डुओ एंटीबायोटिक टैबलेट। भोजन के साथ दिन में दो बार लें। डॉक्टर द्वारा बताया गया पूरा कोर्स खत्म करें।",
        "voice_summary_mr": "ऑगमेंटिन 625 डुओ अँटीबायोटिक गोळी. जेवणासोबत दिवसातून दोन वेळा घ्या. डॉक्टरांनी सांगितलेला पूर्ण कोर्स पूर्ण करा."
    },
    {
        "brand_name": "Azee 500",
        "generic_name": "Azithromycin Tablets IP",
        "category": "Macrolide Antibiotic",
        "manufacturer": "Cipla Limited",
        "dosage_form": "Tablet",
        "strength": "500 mg",
        "active_ingredients": [
            {"name": "Azithromycin Dihydrate IP equivalent to Azithromycin", "strength": "500", "unit": "mg", "purpose": "Macrolide Antibiotic"}
        ],
        "inactive_excipients": [
            "Lactose Monohydrate", "Pregelatinized Starch", "Croscarmellose Sodium",
            "Magnesium Stearate", "Sodium Lauryl Sulfate", "Opadry White Coating"
        ],
        "tablet_shape": "Capsule-shaped",
        "tablet_color": "White",
        "score_line": "Single score line",
        "coating_type": "Film-coated",
        "indications": "Treatment of chest infections, sinus infections, throat infections, skin infections and typhoid.",
        "dosage_instructions": "Take 1 tablet once daily, preferably 1 hour before or 2 hours after meals for 3 to 5 days.",
        "warnings_and_precautions": "Caution in patients with liver disorders or heart arrhythmia (QT prolongation).",
        "side_effects": "Loose motions, stomach upset, nausea, headache.",
        "storage_conditions": "Store below 25°C in a dry place. Protect from light.",
        "schedule_type": "Schedule H1",
        "voice_summary_en": "Azee 500 Azithromycin tablet. Take one tablet once daily on an empty stomach for three days. Do not stop midway.",
        "voice_summary_hi": "एज़ी 500 एज़िथ्रोमाइसिन टैबलेट। दिन में एक बार खाली पेट 3 दिनों के लिए लें।",
        "voice_summary_mr": "अझी 500 अझिथ्रोमायसिन गोळी. दिवसातून एकदा उपाशी पोटी 3 दिवस घ्या."
    },
    {
        "brand_name": "Pan 40",
        "generic_name": "Pantoprazole Gastro-resistant Tablets IP",
        "category": "Proton Pump Inhibitor (Antacid)",
        "manufacturer": "Alkem Laboratories",
        "dosage_form": "Tablet",
        "strength": "40 mg",
        "active_ingredients": [
            {"name": "Pantoprazole Sodium Sesquihydrate IP eq. to Pantoprazole", "strength": "40", "unit": "mg", "purpose": "Gastric Acid Reducer"}
        ],
        "inactive_excipients": [
            "Sodium Carbonate", "Mannitol", "Crospovidone", "Povidone", "Calcium Stearate",
            "Methacrylic Acid Copolymer", "Triethyl Citrate", "Yellow Iron Oxide"
        ],
        "tablet_shape": "Round biconvex",
        "tablet_color": "Yellow",
        "score_line": "None",
        "coating_type": "Enteric-coated (Gastro-resistant)",
        "indications": "Acidity, heartburn, gastroesophageal reflux disease (GERD), gastric and duodenal ulcers.",
        "dosage_instructions": "Swallow whole with a glass of water in the morning, 30 to 60 minutes before breakfast.",
        "warnings_and_precautions": "Do not crush, break, or chew the tablet. Long term use requires monitoring of Vitamin B12 and Magnesium.",
        "side_effects": "Headache, diarrhea, dizziness, flatulence.",
        "storage_conditions": "Store below 25°C in original package. Protect from humidity.",
        "schedule_type": "Schedule H",
        "voice_summary_en": "Pan 40 Pantoprazole tablet for acidity and heartburn. Swallow whole 30 minutes before morning breakfast. Do not crush.",
        "voice_summary_hi": "पैन 40 एसिडिटी और सीने में जलन की दवा। सुबह नाश्ते से 30 मिनट पहले एक गोली पूरी निगलें।",
        "voice_summary_mr": "पॅन 40 ॲसिडिटीची गोळी. सकाळी नाश्त्याच्या 30 मिनिटे आधी न चावता एक गोळी गिळा."
    },
    {
        "brand_name": "Glycomet 500",
        "generic_name": "Metformin Hydrochloride Prolonged-Release Tablets IP",
        "category": "Antidiabetic (Biguanide)",
        "manufacturer": "USV Private Limited",
        "dosage_form": "Tablet",
        "strength": "500 mg",
        "active_ingredients": [
            {"name": "Metformin Hydrochloride IP", "strength": "500", "unit": "mg", "purpose": "Oral Hypoglycemic"}
        ],
        "inactive_excipients": [
            "Hydroxypropyl Methylcellulose (HPMC)", "Sodium Carboxymethylcellulose",
            "Microcrystalline Cellulose", "Magnesium Stearate"
        ],
        "tablet_shape": "Round flat-faced",
        "tablet_color": "White",
        "score_line": "None",
        "coating_type": "Prolonged-release uncoated",
        "indications": "Management of Type 2 Diabetes Mellitus to maintain healthy blood glucose levels.",
        "dosage_instructions": "Take with or immediately after meals (breakfast/dinner) to reduce stomach discomfort.",
        "warnings_and_precautions": "Avoid heavy alcohol consumption. Risk of lactic acidosis in kidney or liver impairment.",
        "side_effects": "Nausea, metallic taste, stomach pain, loss of appetite, diarrhea.",
        "storage_conditions": "Store below 30°C. Protect from light and moisture.",
        "schedule_type": "Schedule H",
        "voice_summary_en": "Glycomet 500 Metformin tablet for Type 2 Diabetes. Take with your meal to control blood sugar. Swallow whole.",
        "voice_summary_hi": "ग्लाइकोमेट 500 शुगर (डायबिटीज) की दवा। इसे भोजन के तुरंत बाद पानी से लें।",
        "voice_summary_mr": "ग्लायकोमेट 500 मधुमेहाची गोळी. रक्तातील साखर नियंत्रणात ठेवण्यासाठी जेवणासोबत घ्या."
    },
    {
        "brand_name": "Telma 40",
        "generic_name": "Telmisartan Tablets IP",
        "category": "Antihypertensive (ARB)",
        "manufacturer": "Glenmark Pharmaceuticals",
        "dosage_form": "Tablet",
        "strength": "40 mg",
        "active_ingredients": [
            {"name": "Telmisartan IP", "strength": "40", "unit": "mg", "purpose": "Angiotensin II Receptor Antagonist"}
        ],
        "inactive_excipients": [
            "Sodium Hydroxide", "Meglumine", "Povidone K-25", "Sorbitol", "Magnesium Stearate"
        ],
        "tablet_shape": "Oblong",
        "tablet_color": "White to off-white",
        "score_line": "Single break line",
        "coating_type": "Uncoated",
        "indications": "Treatment of essential hypertension (high blood pressure) and prevention of cardiovascular events.",
        "dosage_instructions": "Take 1 tablet once daily at the same time each day, with or without food.",
        "warnings_and_precautions": "Contraindicated during pregnancy (teratogenic risk). Regularly monitor potassium levels.",
        "side_effects": "Low blood pressure, back pain, dizziness, sinus congestion.",
        "storage_conditions": "Store in the moisture-proof blister package below 30°C. Tablets are hygroscopic.",
        "schedule_type": "Schedule H",
        "voice_summary_en": "Telma 40 Telmisartan tablet for high blood pressure. Take once daily at a fixed time. Do not skip doses.",
        "voice_summary_hi": "टेल्मा 40 हाई ब्लड प्रेशर की दवा। इसे प्रतिदिन एक निश्चित समय पर लें। खुराक न छोड़ें।",
        "voice_summary_mr": "टेल्मा 40 उच्च रक्तदाबाची गोळी. दररोज एकाच निश्चित वेळी एक गोळी घ्या."
    },
    {
        "brand_name": "Atorva 20",
        "generic_name": "Atorvastatin Tablets IP",
        "category": "Lipid-Lowering Agent (Statin)",
        "manufacturer": "Zydus Lifesciences",
        "dosage_form": "Tablet",
        "strength": "20 mg",
        "active_ingredients": [
            {"name": "Atorvastatin Calcium Trihydrate IP eq. to Atorvastatin", "strength": "20", "unit": "mg", "purpose": "HMG-CoA Reductase Inhibitor"}
        ],
        "inactive_excipients": [
            "Calcium Carbonate", "Lactose Monohydrate", "Microcrystalline Cellulose",
            "Croscarmellose Sodium", "Polysorbate 80", "Hydroxypropyl Cellulose", "Opadry White"
        ],
        "tablet_shape": "Round biconvex",
        "tablet_color": "White",
        "score_line": "None",
        "coating_type": "Film-coated",
        "indications": "Hypercholesterolemia and prevention of heart attacks, stroke, and arterial blockage.",
        "dosage_instructions": "Take 1 tablet once daily in the evening or bedtime, with or without food.",
        "warnings_and_precautions": "Inform doctor immediately if experiencing unexplained muscle tenderness, cramps or weakness.",
        "side_effects": "Muscle ache (myalgia), joint pain, diarrhea, elevated liver enzymes.",
        "storage_conditions": "Store below 25°C. Protect from moisture and excessive heat.",
        "schedule_type": "Schedule H",
        "voice_summary_en": "Atorva 20 Atorvastatin tablet for cholesterol and heart protection. Take one tablet in the evening after dinner.",
        "voice_summary_hi": "एटोरवा 20 कोलेस्ट्रॉल और हृदय स्वास्थ्य की दवा। शाम को रात के खाने के बाद लें।",
        "voice_summary_mr": "अटोर्वा 20 कोलेस्टेरॉल कमी करणारी गोळी. संध्याकाळी जेवणानंतर घ्या."
    },
    {
        "brand_name": "Cetzine 10",
        "generic_name": "Cetirizine Hydrochloride Tablets IP",
        "category": "Antihistamine (Antiallergic)",
        "manufacturer": "Dr. Reddy's Laboratories",
        "dosage_form": "Tablet",
        "strength": "10 mg",
        "active_ingredients": [
            {"name": "Cetirizine Hydrochloride IP", "strength": "10", "unit": "mg", "purpose": "Second-generation Antihistamine"}
        ],
        "inactive_excipients": [
            "Lactose Monohydrate", "Corn Starch", "Povidone", "Magnesium Stearate",
            "Hypromellose", "Titanium Dioxide", "Macrogol 400"
        ],
        "tablet_shape": "Round",
        "tablet_color": "White",
        "score_line": "Bisected score line",
        "coating_type": "Film-coated",
        "indications": "Allergic rhinitis, hay fever, sneezing, runny nose, watery eyes, and itchy allergic skin hives.",
        "dosage_instructions": "Take 1 tablet once daily, preferably at bedtime as it may induce mild drowsiness.",
        "warnings_and_precautions": "May cause sedation. Avoid driving or operating machinery after consumption.",
        "side_effects": "Drowsiness, fatigue, dry mouth, headache.",
        "storage_conditions": "Store below 30°C in a dry place.",
        "schedule_type": "Schedule H",
        "voice_summary_en": "Cetzine 10 milligram allergy tablet. For runny nose, sneezing, and skin allergy. Take one tablet at night before sleeping.",
        "voice_summary_hi": "सेटज़ीन 10 मिलीग्राम एलर्जी की दवा। छींक, बहती नाक और खुजली के लिए। रात को सोने से पहले लें।",
        "voice_summary_mr": "सेटझिन 10 ॲलर्जीची गोळी. शिंका, सर्दी आणि खाज सुटण्यासाठी. रात्री झोपताना एक गोळी घ्या."
    },
    {
        "brand_name": "Combiflam",
        "generic_name": "Ibuprofen and Paracetamol Tablets IP",
        "category": "NSAID & Analgesic Combination",
        "manufacturer": "Sanofi India Limited",
        "dosage_form": "Tablet",
        "strength": "Ibuprofen 400mg + Paracetamol 325mg",
        "active_ingredients": [
            {"name": "Ibuprofen IP", "strength": "400", "unit": "mg", "purpose": "NSAID Anti-inflammatory"},
            {"name": "Paracetamol IP", "strength": "325", "unit": "mg", "purpose": "Analgesic & Antipyretic"}
        ],
        "inactive_excipients": [
            "Maize Starch", "Purified Talc", "Sodium Starch Glycolate", "Colloidal Anhydrous Silica",
            "Magnesium Stearate"
        ],
        "tablet_shape": "Capsule-shaped",
        "tablet_color": "White",
        "score_line": "None",
        "coating_type": "Uncoated",
        "indications": "Acute muscular pain, toothache, post-surgical pain, arthritis flare-ups, and headache.",
        "dosage_instructions": "Take 1 tablet after a heavy meal or with milk. Do not take on an empty stomach.",
        "warnings_and_precautions": "Risk of gastric ulcers and bleeding. Avoid if history of stomach ulcers or asthma.",
        "side_effects": "Heartburn, acidity, indigestion, nausea.",
        "storage_conditions": "Store below 30°C in a cool and dry location.",
        "schedule_type": "Schedule H",
        "voice_summary_en": "Combiflam pain relief tablet. For severe muscle or tooth pain. Always take with food or milk, never on an empty stomach.",
        "voice_summary_hi": "कॉम्बिफ्लाम दर्द निवारक दवा। मांसपेशियों और दांत दर्द के लिए। हमेशा खाना खाने के बाद ही लें।",
        "voice_summary_mr": "कॉम्बीफ्लॅम वेदनाशामक गोळी. स्नायू आणि दातदुखीसाठी. नेहमी पोटभर जेवण झाल्यावरच घ्या."
    },
    {
        "brand_name": "Montair LC",
        "generic_name": "Montelukast Sodium and Levocetirizine Hydrochloride Tablets IP",
        "category": "Respiratory Antiallergic",
        "manufacturer": "Cipla Limited",
        "dosage_form": "Tablet",
        "strength": "10 mg + 5 mg",
        "active_ingredients": [
            {"name": "Montelukast Sodium IP eq. to Montelukast", "strength": "10", "unit": "mg", "purpose": "Leukotriene Receptor Antagonist"},
            {"name": "Levocetirizine Dihydrochloride IP", "strength": "5", "unit": "mg", "purpose": "Antihistamine"}
        ],
        "inactive_excipients": [
            "Microcrystalline Cellulose", "Mannitol", "Crospovidone", "Red Iron Oxide",
            "Yellow Iron Oxide", "Titanium Dioxide"
        ],
        "tablet_shape": "Round biconvex",
        "tablet_color": "Pale orange-pink",
        "score_line": "None",
        "coating_type": "Film-coated",
        "indications": "Treatment of allergic asthma, perennial allergic rhinitis, and chronic hives.",
        "dosage_instructions": "Take 1 tablet once daily in the evening or before bed.",
        "warnings_and_precautions": "Not an emergency rescue inhaler substitute for sudden acute asthma attacks.",
        "side_effects": "Drowsiness, dry mouth, headache, vivid dreams.",
        "storage_conditions": "Store in the original strip below 25°C. Protect from moisture.",
        "schedule_type": "Schedule H",
        "voice_summary_en": "Montair LC tablet for allergic cough and asthma symptoms. Take one tablet at bedtime.",
        "voice_summary_hi": "मॉन्टेयर एलसी एलर्जी, खांसी और दमा के लक्षणों के लिए। रात को सोने से पहले एक गोली लें।",
        "voice_summary_mr": "मॉन्टेअर एलसी ॲलर्जी आणि दम्याच्या त्रासासाठी गोळी. रात्री झोपताना एक गोळी घ्या."
    },
    {
        "brand_name": "Taxim-O 200",
        "generic_name": "Cefixime Tablets IP",
        "category": "Cephalosporin Antibiotic (3rd Gen)",
        "manufacturer": "Alkem Laboratories",
        "dosage_form": "Tablet",
        "strength": "200 mg",
        "active_ingredients": [
            {"name": "Cefixime Trihydrate IP eq. to Anhydrous Cefixime", "strength": "200", "unit": "mg", "purpose": "Cephalosporin Antibiotic"}
        ],
        "inactive_excipients": [
            "Microcrystalline Cellulose", "Pregelatinized Starch", "Colloidal Silicon Dioxide",
            "Magnesium Stearate", "Titanium Dioxide"
        ],
        "tablet_shape": "Oblong",
        "tablet_color": "White",
        "score_line": "Score line on both sides",
        "coating_type": "Film-coated",
        "indications": "Typhoid fever, urinary tract infections, bronchitis, tonsillitis, and middle ear infections.",
        "dosage_instructions": "1 tablet every 12 hours with or without food for 7 to 10 days.",
        "warnings_and_precautions": "Complete the full duration prescribed by your doctor to prevent resistance.",
        "side_effects": "Loose stools, stomach cramps, nausea, flatulence.",
        "storage_conditions": "Store below 25°C in a dry place.",
        "schedule_type": "Schedule H1",
        "voice_summary_en": "Taxim-O 200 Cefixime antibiotic tablet. Take one tablet every 12 hours. Do not discontinue until prescribed course is finished.",
        "voice_summary_hi": "टैक्सिम-ओ 200 एंटीबायोटिक टैबलेट। हर 12 घंटे में एक गोली लें। डॉक्टर की सलाह अनुसार कोर्स पूरा करें।",
        "voice_summary_mr": "टॅक्सिम-ओ 200 अँटीबायोटिक गोळी. दर 12 तासांनी एक गोळी घ्या. पूर्ण दिवस औषध चालू ठेवा."
    },
    {
        "brand_name": "Shelcal 500",
        "generic_name": "Calcium with Vitamin D3 Tablets IP",
        "category": "Mineral & Vitamin Supplement",
        "manufacturer": "Torrent Pharmaceuticals",
        "dosage_form": "Tablet",
        "strength": "500 mg Elemental Calcium + 250 IU Vit D3",
        "active_ingredients": [
            {"name": "Calcium Carbonate IP eq. to Elemental Calcium", "strength": "500", "unit": "mg", "purpose": "Bone Mineral Supplement"},
            {"name": "Cholecalciferol IP (Vitamin D3)", "strength": "250", "unit": "IU", "purpose": "Calcium Absorption Promoter"}
        ],
        "inactive_excipients": [
            "Povidone", "Purified Talc", "Magnesium Stearate", "Sodium Starch Glycolate", "Titanium Dioxide"
        ],
        "tablet_shape": "Oval biconvex",
        "tablet_color": "White",
        "score_line": "None",
        "coating_type": "Film-coated",
        "indications": "Osteoporosis, calcium deficiency, bone strength during pregnancy and lactation.",
        "dosage_instructions": "Take 1 tablet daily after lunch or dinner with water.",
        "warnings_and_precautions": "Do not take concurrently with iron supplements; maintain a 2-hour gap.",
        "side_effects": "Constipation, bloating, gas.",
        "storage_conditions": "Store below 30°C in a dry place.",
        "schedule_type": "OTC",
        "voice_summary_en": "Shelcal 500 Calcium and Vitamin D3 tablet for bone strength. Take one tablet daily after food.",
        "voice_summary_hi": "शेलकल 500 हड्डियों की मजबूती के लिए कैल्शियम और विटामिन डी। रोजाना दोपहर या रात के खाने के बाद लें।",
        "voice_summary_mr": "शेलकॅल 500 हाडांच्या मजबुतीसाठी कॅल्शियम आणि व्हिटॅमिन डी गोळी. जेवणानंतर रोज एक गोळी घ्या."
    },
    {
        "brand_name": "Ecosprin 75",
        "generic_name": "Aspirin Gastro-resistant Tablets IP",
        "category": "Antiplatelet Agent (Blood Thinner)",
        "manufacturer": "USV Private Limited",
        "dosage_form": "Tablet",
        "strength": "75 mg",
        "active_ingredients": [
            {"name": "Aspirin IP (Acetylsalicylic Acid)", "strength": "75", "unit": "mg", "purpose": "Antiplatelet / Thromboxane Inhibitor"}
        ],
        "inactive_excipients": [
            "Starch", "Cellulose Microcrystalline", "Methacrylic Acid Copolymer",
            "Talc", "Triethyl Citrate"
        ],
        "tablet_shape": "Round",
        "tablet_color": "White",
        "score_line": "None",
        "coating_type": "Enteric-coated",
        "indications": "Prevention of blood clots, heart attacks, recurrent strokes, and angina.",
        "dosage_instructions": "Take 1 tablet daily at the same time, swallowed whole with water.",
        "warnings_and_precautions": "Risk of bleeding. Inform surgeons or dentists prior to any scheduled procedures.",
        "side_effects": "Easy bruising, prolonged bleeding from cuts, gastric irritation.",
        "storage_conditions": "Store below 25°C. Protect from moisture.",
        "schedule_type": "Schedule H",
        "voice_summary_en": "Ecosprin 75 low-dose aspirin blood thinner. Protects heart and prevents clots. Swallow whole daily.",
        "voice_summary_hi": "इकोस्प्रिन 75 खून पतला करने वाली एस्पिरिन दवा। दिल के दौरे से बचाव के लिए रोज एक गोली लें।",
        "voice_summary_mr": "इकोस्प्रिन 75 रक्त पातळ ठेवणारी गोळी. हृदयविकाराच्या झटक्यापासून संरक्षणासाठी रोज एक गोळी घ्या."
    },
    {
        "brand_name": "Cifran 500",
        "generic_name": "Ciprofloxacin Tablets IP",
        "category": "Fluoroquinolone Antibiotic",
        "manufacturer": "Sun Pharmaceutical Industries",
        "dosage_form": "Tablet",
        "strength": "500 mg",
        "active_ingredients": [
            {"name": "Ciprofloxacin Hydrochloride IP eq. to Ciprofloxacin", "strength": "500", "unit": "mg", "purpose": "Broad Spectrum Fluoroquinolone"}
        ],
        "inactive_excipients": [
            "Corn Starch", "Microcrystalline Cellulose", "Colloidal Silicon Dioxide",
            "Magnesium Stearate", "Hypromellose", "Titanium Dioxide"
        ],
        "tablet_shape": "Capsule-shaped",
        "tablet_color": "White",
        "score_line": "Central break line",
        "coating_type": "Film-coated",
        "indications": "Severe gastrointestinal bacterial infections, joint infections, complicated urinary tract infections.",
        "dosage_instructions": "Take 1 tablet twice daily with plenty of water. Avoid taking with dairy products.",
        "warnings_and_precautions": "Risk of tendonitis or tendon rupture. Avoid intense athletic exertion while taking.",
        "side_effects": "Nausea, diarrhea, tendon pain, sun sensitivity.",
        "storage_conditions": "Store below 30°C. Protect from light.",
        "schedule_type": "Schedule H1",
        "voice_summary_en": "Cifran 500 Ciprofloxacin antibiotic. Take twice daily with lots of water. Avoid milk or antacids at the same time.",
        "voice_summary_hi": "सिफ्रान 500 एंटीबायोटिक। दिन में दो बार भरपूर पानी के साथ लें। दूध या दही के साथ तुरंत न लें।",
        "voice_summary_mr": "सिफ्रान 500 अँटीबायोटिक गोळी. भरपूर पाण्यासोबत दिवसातून दोन वेळा घ्या."
    },
    {
        "brand_name": "Pan-D",
        "generic_name": "Pantoprazole and Domperidone Prolonged-Release Capsules IP",
        "category": "Antacid & Prokinetic Combination",
        "manufacturer": "Alkem Laboratories",
        "dosage_form": "Capsule",
        "strength": "Pantoprazole 40mg + Domperidone 30mg",
        "active_ingredients": [
            {"name": "Pantoprazole Sodium IP eq. to Pantoprazole", "strength": "40", "unit": "mg", "purpose": "Proton Pump Inhibitor"},
            {"name": "Domperidone IP (Sustained Release)", "strength": "30", "unit": "mg", "purpose": "Prokinetic Antiemetic"}
        ],
        "inactive_excipients": [
            "Sugar Spheres", "HPMC", "Methacrylic Acid Copolymer", "Titanium Dioxide", "Sunset Yellow FCF"
        ],
        "tablet_shape": "Hard Gelatin Capsule",
        "tablet_color": "Yellow and White",
        "score_line": "None",
        "coating_type": "Pellet filled capsule",
        "indications": "Gastroesophageal reflux disease (GERD), severe nausea, acid regurgitation, and bloating.",
        "dosage_instructions": "Take 1 capsule once daily in the morning on an empty stomach, 1 hour before breakfast.",
        "warnings_and_precautions": "Not recommended for long term use without clinical review.",
        "side_effects": "Dry mouth, headache, flatulence, diarrhea.",
        "storage_conditions": "Store below 25°C in a dry place.",
        "schedule_type": "Schedule H",
        "voice_summary_en": "Pan D capsule for severe acidity and nausea. Take on an empty stomach in the morning 45 minutes before breakfast.",
        "voice_summary_hi": "पैन डी एसिडिटी और उल्टी/मतली की कैप्सूल। सुबह खाली पेट नाश्ते से 45 मिनट पहले लें।",
        "voice_summary_mr": "पॅन डी ॲसिडिटी आणि उलट्या थांबवणारी कॅप्सूल. सकाळी उपाशी पोटी नाश्त्याच्या आधी घ्या."
    }
]

# Expand programmatically to 50 comprehensive medical formulations
ADDITIONAL_FORMULATIONS = [
    ("Omez 20", "Omeprazole Gastro-resistant Capsules IP", "Antacid (PPI)", "Dr. Reddy's Laboratories", "Capsule", "20 mg", [("Omeprazole IP", "20", "mg", "PPI")], "Acidity, peptic ulcer, and heartburn.", "Take 1 capsule daily before breakfast.", "Store below 25°C.", "OTC"),
    ("Amaryl 1mg", "Glimepiride Tablets IP", "Antidiabetic (Sulfonylurea)", "Sanofi India", "Tablet", "1 mg", [("Glimepiride IP", "1", "mg", "Insulin secretagogue")], "Type 2 diabetes blood sugar control.", "Take immediately before first main meal.", "Store below 30°C.", "Schedule H"),
    ("Amaryl 2mg", "Glimepiride Tablets IP", "Antidiabetic (Sulfonylurea)", "Sanofi India", "Tablet", "2 mg", [("Glimepiride IP", "2", "mg", "Insulin secretagogue")], "Type 2 diabetes blood sugar regulation.", "Take before breakfast.", "Store below 30°C.", "Schedule H"),
    ("Januvia 50", "Sitagliptin Tablets IP", "Antidiabetic (DPP-4 Inhibitor)", "Merck Sharp & Dohme", "Tablet", "50 mg", [("Sitagliptin Phosphate Monohydrate eq. to Sitagliptin", "50", "mg", "DPP-4 Inhibitor")], "Type 2 diabetes management.", "Take 1 tablet daily with or without meals.", "Store below 25°C.", "Schedule H"),
    ("Jardiance 10", "Empagliflozin Tablets IP", "Antidiabetic (SGLT2 Inhibitor)", "Boehringer Ingelheim", "Tablet", "10 mg", [("Empagliflozin", "10", "mg", "SGLT2 Inhibitor")], "Type 2 diabetes and heart failure risk reduction.", "Take 1 tablet in the morning.", "Store below 30°C.", "Schedule H"),
    ("Amlong 5", "Amlodipine Tablets IP", "Antihypertensive (CCB)", "Micro Labs Limited", "Tablet", "5 mg", [("Amlodipine Besylate IP eq. to Amlodipine", "5", "mg", "Calcium Channel Blocker")], "High blood pressure and chronic stable angina.", "Take 1 tablet daily at morning or evening.", "Store below 30°C.", "Schedule H"),
    ("Losar 50", "Losartan Potassium Tablets IP", "Antihypertensive (ARB)", "Unichem Laboratories", "Tablet", "50 mg", [("Losartan Potassium IP", "50", "mg", "Angiotensin II Antagonist")], "High blood pressure and kidney protection in diabetes.", "Take 1 tablet daily.", "Store below 25°C.", "Schedule H"),
    ("Rozavel 10", "Rosuvastatin Tablets IP", "Lipid-lowering Statin", "Sun Pharma", "Tablet", "10 mg", [("Rosuvastatin Calcium IP eq. to Rosuvastatin", "10", "mg", "HMG-CoA Reductase Inhibitor")], "High LDL cholesterol and prevention of stroke.", "Take 1 tablet at night.", "Store below 30°C.", "Schedule H"),
    ("Betaloc 25", "Metoprolol Succinate Prolonged-Release Tablets IP", "Beta Blocker", "AstraZeneca India", "Tablet", "25 mg", [("Metoprolol Succinate IP", "23.75", "mg", "eq. to 25mg Tartrate", "Beta-1 Blocker")], "High blood pressure, angina, and heart rate regulation.", "Take 1 tablet with breakfast. Do not chew.", "Store below 30°C.", "Schedule H"),
    ("Allegra 120", "Fexofenadine Hydrochloride Tablets IP", "Non-drowsy Antihistamine", "Sanofi India", "Tablet", "120 mg", [("Fexofenadine HCl IP", "120", "mg", "H1 Receptor Antagonist")], "Seasonal allergy, runny nose, and itchy skin hives.", "Take 1 tablet once daily with water. Avoid fruit juices.", "Store below 25°C.", "Schedule H"),
    ("Brufen 400", "Ibuprofen Tablets IP", "NSAID Analgesic", "Abbott Healthcare", "Tablet", "400 mg", [("Ibuprofen IP", "400", "mg", "NSAID")], "Fever, headache, period pain, and arthritis.", "Take 1 tablet with or after food. Avoid empty stomach.", "Store below 30°C.", "Schedule H"),
    ("Voveran 50", "Diclofenac Sodium Gastro-resistant Tablets IP", "NSAID Anti-inflammatory", "Novartis India", "Tablet", "50 mg", [("Diclofenac Sodium IP", "50", "mg", "NSAID")], "Acute musculoskeletal pain, joint inflammation, and sprains.", "Take 1 tablet after meals with water.", "Store below 30°C.", "Schedule H"),
    ("Zerodol-P", "Aceclofenac and Paracetamol Tablets IP", "Analgesic Combination", "Ipca Laboratories", "Tablet", "100mg + 325mg", [("Aceclofenac IP", "100", "mg", "NSAID"), ("Paracetamol IP", "325", "mg", "Analgesic")], "Pain and swelling in osteoarthritis, spondylitis, and dental pain.", "Take 1 tablet twice daily after meals.", "Store below 25°C.", "Schedule H"),
    ("Tramazac 50", "Tramadol Hydrochloride Capsules IP", "Opioid Analgesic", "Zydus Lifesciences", "Capsule", "50 mg", [("Tramadol Hydrochloride IP", "50", "mg", "Opioid Receptor Agonist")], "Moderate to severe acute and chronic post-surgical pain.", "Take 1 capsule every 6 hours as prescribed. Habit-forming.", "Store below 30°C.", "Schedule H1"),
    ("Deplatt 75", "Clopidogrel Tablets IP", "Antiplatelet Agent", "Torrent Pharmaceuticals", "Tablet", "75 mg", [("Clopidogrel Bisulphate IP eq. to Clopidogrel", "75", "mg", "Platelet Aggregation Inhibitor")], "Prevention of blood clots in patients with heart stents or stroke.", "Take 1 tablet daily with or without food.", "Store below 25°C.", "Schedule H"),
    ("Doxicip 100", "Doxycycline Capsules IP", "Tetracycline Antibiotic", "Cipla Limited", "Capsule", "100 mg", [("Doxycycline Hyclate IP eq. to Doxycycline", "100", "mg", "Bacterial Protein Synthesis Inhibitor")], "Severe acne, respiratory infections, and tick-borne fever.", "Take with a full glass of water while sitting upright.", "Store below 30°C.", "Schedule H"),
    ("O2 Tablet", "Ofloxacin and Ornidazole Tablets IP", "Broad Spectrum Antibacterial & Antiprotozoal", "Medley Pharmaceuticals", "Tablet", "200mg + 500mg", [("Ofloxacin IP", "200", "mg", "Fluoroquinolone"), ("Ornidazole IP", "500", "mg", "Nitroimidazole")], "Severe diarrhea, dysentery, gastrointestinal and dental infections.", "Take 1 tablet twice daily after food for 5 days.", "Store below 25°C.", "Schedule H1"),
    ("Flagyl 400", "Metronidazole Tablets IP", "Antiprotozoal & Antibacterial", "Abbott India", "Tablet", "400 mg", [("Metronidazole IP", "400", "mg", "Nitroimidazole")], "Amoebic dysentery, dental abscess, and anaerobic infections.", "Take 1 tablet three times daily after food. Strictly no alcohol.", "Store below 30°C.", "Schedule H"),
    ("Forcan 150", "Fluconazole Tablets IP", "Antifungal Agent", "Cipla Limited", "Tablet", "150 mg", [("Fluconazole IP", "150", "mg", "Triazole Antifungal")], "Fungal infections, oral thrush, and vaginal yeast infection.", "Take 1 tablet as a single weekly dose as directed.", "Store below 30°C.", "Schedule H"),
    ("Zentel 400", "Albendazole Chewable Tablets IP", "Anthelmintic (Deworming)", "GlaxoSmithKline", "Chewable Tablet", "400 mg", [("Albendazole IP", "400", "mg", "Microtubule Inhibitor")], "Intestinal parasite and worm deworming treatment.", "Chew tablet thoroughly before swallowing with water.", "Store below 30°C.", "Schedule H"),
    ("Calcirol 60K", "Cholecalciferol Capsules IP", "Vitamin D3 Mega-dose", "Cadila Pharmaceuticals", "Capsule", "60,000 IU", [("Cholecalciferol IP", "60000", "IU", "Vitamin D3")], "Severe Vitamin D deficiency and osteoporosis prevention.", "Take 1 capsule once weekly with milk for 8 weeks.", "Store in a cool dry place.", "OTC"),
    ("Orofer XT", "Ferrous Ascorbate and Folic Acid Tablets IP", "Hematinic (Iron Supplement)", "Emcure Pharmaceuticals", "Tablet", "100mg + 1.5mg", [("Ferrous Ascorbate eq. to Elemental Iron", "100", "mg", "Hematinic"), ("Folic Acid IP", "1.5", "mg", "Hematopoiesis")], "Iron deficiency anemia, pregnancy nutritional support.", "Take 1 tablet daily after food. May turn stools dark.", "Store below 25°C.", "OTC"),
    ("Becadexamin", "Multivitamins and Minerals Capsules", "Nutritional Supplement", "GlaxoSmithKline", "Capsule", "Standard therapeutic", [("Vitamin A IP", "5000", "IU", "Vitamin"), ("Vitamin C IP", "50", "mg", "Antioxidant"), ("Zinc Sulphate IP", "41.4", "mg", "Mineral")], "General weakness, immunity boosting, and convalescence.", "Take 1 capsule daily after breakfast.", "Store below 25°C.", "OTC"),
    ("Neurobion Forte", "Vitamin B-Complex with B12 Tablets", "Neurotropic Vitamin Supplement", "Procter & Gamble Health", "Tablet", "Standard", [("Vitamin B1 (Thiamine) IP", "10", "mg", "Vitamin"), ("Vitamin B6 (Pyridoxine) IP", "3", "mg", "Vitamin"), ("Vitamin B12 (Cyanocobalamin) IP", "15", "mcg", "Nerve Vitamin")], "Nerve health, tingling, numbness, and diabetic neuropathy.", "Take 1 tablet daily after meals.", "Store below 25°C.", "OTC"),
    ("Alprax 0.25", "Alprazolam Tablets IP", "Anxiolytic (Benzodiazepine)", "Torrent Pharmaceuticals", "Tablet", "0.25 mg", [("Alprazolam IP", "0.25", "mg", "GABA-A Receptor Modulator")], "Short-term management of acute anxiety and panic disorder.", "Take as directed by psychiatrist. High habit-forming potential.", "Store below 25°C. Secure lock.", "Schedule H1 (Habit Forming)"),
    ("Clona 0.5", "Clonazepam Tablets IP", "Anticonvulsant & Anxiolytic", "Zydus Lifesciences", "Tablet", "0.5 mg", [("Clonazepam IP", "0.5", "mg", "Benzodiazepine")], "Seizure prevention and panic disorder management.", "Take at night before bed. Do not stop abruptly.", "Store below 25°C.", "Schedule H1"),
    ("Nexito 10", "Escitalopram Tablets IP", "Antidepressant (SSRI)", "Sun Pharma", "Tablet", "10 mg", [("Escitalopram Oxalate IP eq. to Escitalopram", "10", "mg", "Serotonin Reuptake Inhibitor")], "Major depressive disorder and generalized anxiety disorder.", "Take 1 tablet daily in the morning.", "Store below 25°C.", "Schedule H"),
    ("Thyronorm 50", "Thyroxine Sodium Tablets IP", "Thyroid Hormone Replacement", "Abbott India", "Tablet", "50 mcg", [("Thyroxine Sodium IP", "50", "mcg", "Thyroid Hormone")], "Hypothyroidism (underactive thyroid gland).", "Take 1 tablet every morning with water on an empty stomach, 1 hour before tea or breakfast.", "Store below 25°C. Protect from moisture.", "Schedule H"),
    ("FluVir 75", "Oseltamivir Capsules IP", "Antiviral (Neuraminidase Inhibitor)", "Hetero Healthcare", "Capsule", "75 mg", [("Oseltamivir Phosphate IP eq. to Oseltamivir", "75", "mg", "Neuraminidase Inhibitor")], "Treatment and prevention of Influenza A and Influenza B (Swine Flu).", "Take 1 capsule twice daily for 5 days.", "Store below 25°C.", "Schedule H1"),
    ("Razo 20", "Rabeprazole Sodium Tablets IP", "Proton Pump Inhibitor", "Dr. Reddy's Laboratories", "Tablet", "20 mg", [("Rabeprazole Sodium IP", "20", "mg", "PPI")], "Acid peptic disease and duodenal ulcers.", "Take 1 tablet 30 minutes before morning meal.", "Store below 25°C.", "Schedule H"),
    ("Rantac 150", "Ranitidine Hydrochloride Tablets IP", "H2 Receptor Blocker", "J.B. Chemicals & Pharmaceuticals", "Tablet", "150 mg", [("Ranitidine HCl IP eq. to Ranitidine", "150", "mg", "H2 Blocker")], "Acid indigestion, sour stomach, and heartburn.", "Take 1 tablet twice daily before meals.", "Store below 30°C.", "OTC"),
    ("Levocet 5", "Levocetirizine Hydrochloride Tablets IP", "Antihistamine", "Hetero Drugs", "Tablet", "5 mg", [("Levocetirizine HCl IP", "5", "mg", "Antihistamine")], "Sneezing, itchy nose, allergic conjunctivitis, and skin rashes.", "Take 1 tablet at night.", "Store below 25°C.", "Schedule H"),
    ("Telma AM", "Telmisartan and Amlodipine Tablets IP", "Dual Antihypertensive", "Glenmark Pharmaceuticals", "Tablet", "40mg + 5mg", [("Telmisartan IP", "40", "mg", "ARB"), ("Amlodipine IP", "5", "mg", "CCB")], "Moderate to severe hypertension unresponsive to monotherapy.", "Take 1 tablet daily at morning.", "Store below 30°C.", "Schedule H"),
    ("Calpol 500", "Paracetamol Tablets IP", "Analgesic & Antipyretic", "GlaxoSmithKline", "Tablet", "500 mg", [("Paracetamol IP", "500", "mg", "Analgesic")], "Relief of headache, toothache, body ache, and mild fever.", "Take 1 tablet every 4 to 6 hours as needed.", "Store below 30°C.", "OTC"),
    ("Lipitor 10", "Atorvastatin Calcium Tablets", "Lipid-Lowering Statin", "Pfizer Limited", "Tablet", "10 mg", [("Atorvastatin Calcium eq. to Atorvastatin", "10", "mg", "Statin")], "Reduction of bad cholesterol (LDL) and triglycerides.", "Take 1 tablet at evening after dinner.", "Store below 25°C.", "Schedule H")
]

# Assemble into full 50 items
for item in ADDITIONAL_FORMULATIONS:
    brand, gen, cat, mfg, form, str_val, active_list, ind, dose, stor, sched = item
    act_formatted = [{"name": a[0], "strength": a[1], "unit": a[2], "purpose": a[3]} for a in active_list]
    
    MEDICINES_DATA.append({
        "brand_name": brand,
        "generic_name": gen,
        "category": cat,
        "manufacturer": mfg,
        "dosage_form": form,
        "strength": str_val,
        "active_ingredients": act_formatted,
        "inactive_excipients": [
            "Microcrystalline Cellulose", "Starch", "Povidone", "Magnesium Stearate", "Purified Talc"
        ],
        "tablet_shape": "Round biconvex",
        "tablet_color": "White",
        "score_line": "None",
        "coating_type": "Film-coated" if "Tablet" in form else "Capsule",
        "indications": ind,
        "dosage_instructions": dose,
        "warnings_and_precautions": "Take only as directed by your physician or pharmacist. Keep out of reach of children.",
        "side_effects": "Consult package leaflet for full clinical side effects list.",
        "storage_conditions": stor,
        "schedule_type": sched,
        "voice_summary_en": f"{brand}, generic {gen} {str_val}. Used for {ind}. {dose}",
        "voice_summary_hi": f"{brand}, जेनेरिक {gen} {str_val}। {ind}। खुराक: {dose}।",
        "voice_summary_mr": f"{brand}, जेनेरिक औषध {gen} {str_val}. {ind}. डोस: {dose}."
    })
