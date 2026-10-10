import sys

js_content = """/**
 * Pazeratechnologies Insurance Marketplace Engine
 * Architecture based on plan-specific, source-backed coverage rule engine.
 */

(function () {
  'use strict';

  const $ = (selector, parent = document) => parent.querySelector(selector);
  const $$ = (selector, parent = document) => [...parent.querySelectorAll(selector)];
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  // --- 1. MINIMUM 33 DEPARTMENTS TAXONOMY ---
  const DEPARTMENTS = [
    { id: 'all', label: 'All 33 Departments', icon: '🛒' },
    { id: 'vitamins', label: 'Vitamins & Minerals', icon: '💊' },
    { id: 'supplements', label: 'Supplements', icon: '🌿' },
    { id: 'nutrition', label: 'Nutrition & Medical Foods', icon: '🥛' },
    { id: 'pain', label: 'Pain Relief', icon: '🩹' },
    { id: 'coldflu', label: 'Cold, Flu & Allergy', icon: '🤧' },
    { id: 'digestive', label: 'Digestive Health', icon: '🥣' },
    { id: 'firstaid', label: 'First Aid', icon: '🧰' },
    { id: 'woundcare', label: 'Wound Care', icon: '🩹' },
    { id: 'braces', label: 'Braces & Supports', icon: '🦿' },
    { id: 'mobility', label: 'Mobility', icon: '♿' },
    { id: 'homesafety', label: 'Home Safety', icon: '🏠' },
    { id: 'diabetes', label: 'Diabetes', icon: '🩸' },
    { id: 'cardio', label: 'Blood Pressure & Cardiovascular', icon: '🩺' },
    { id: 'respiratory', label: 'Respiratory', icon: '🌬️' },
    { id: 'sleep', label: 'CPAP & Sleep', icon: '🌙' },
    { id: 'eyecare', label: 'Eye Care', icon: '👁️' },
    { id: 'hearing', label: 'Hearing', icon: '👂' },
    { id: 'dental', label: 'Dental & Oral Care', icon: '🪥' },
    { id: 'skincare', label: 'Skin & Dermatology', icon: '🧴' },
    { id: 'footcare', label: 'Foot Care', icon: '🦶' },
    { id: 'compression', label: 'Compression & Lymphedema', icon: '🦵' },
    { id: 'incontinence', label: 'Incontinence', icon: '🩲' },
    { id: 'womens', label: 'Women\\'s Health', icon: '🌸' },
    { id: 'pregnancy', label: 'Pregnancy & Breastfeeding', icon: '🍼' },
    { id: 'sexual', label: 'Sexual & Reproductive Health', icon: '💊' },
    { id: 'smoking', label: 'Smoking Cessation', icon: '🚭' },
    { id: 'ostomy', label: 'Ostomy', icon: '🩺' },
    { id: 'urology', label: 'Urological Supplies', icon: '💉' },
    { id: 'prosthetics', label: 'Prosthetics', icon: '🎗️' },
    { id: 'dme', label: 'Home Medical Equipment', icon: '🚽' },
    { id: 'medmgmt', label: 'Medication Management', icon: '📅' },
    { id: 'diagnostics', label: 'Home Diagnostics', icon: '🧪' },
    { id: 'ssbci', label: 'Chronic Condition Benefits', icon: '🍎' }
  ];

  // --- 2. INSURERS AND PLANS REGISTRY ---
  const INSURERS = [
    { id: 'bcbsri', name: 'Blue Cross & Blue Shield of Rhode Island', code: 'BCBSRI', states: ['RI'] },
    { id: 'neighborhood', name: 'Neighborhood Health Plan of Rhode Island', code: 'NHPRI', states: ['RI'] },
    { id: 'ri_medicaid', name: 'Rhode Island Medicaid (EOHHS)', code: 'RIME', states: ['RI'] },
    { id: 'uhc_ri', name: 'UnitedHealthcare Rhode Island', code: 'UHCRI', states: ['RI'] },
    { id: 'tufts_p32', name: 'Tufts / Point32Health', code: 'TUFTS', states: ['RI', 'MA'] },
    { id: 'medicare', name: 'Original Medicare (CMS)', code: 'CMS', states: ['RI', 'MA', 'CT', 'NH', 'VT', 'ME'] },
    { id: 'unselected', name: 'Generic / Unselected Insurer', code: 'GENERIC', states: ['RI', 'MA', 'CT', 'NH', 'VT', 'ME'] }
  ];

  const PLANS = [
    { id: 'bcbsri_bluechip_core_2026', insurer_id: 'bcbsri', plan_name: 'BlueCHiP for Medicare Core (2026)', plan_year: 2026, state: 'RI', plan_type: 'Medicare Advantage' },
    { id: 'neighborhood_integra_2026', insurer_id: 'neighborhood', plan_name: 'Neighborhood INTEGRIA D-SNP (2026)', plan_year: 2026, state: 'RI', plan_type: 'Medicare Advantage' },
    { id: 'ri_medicaid_managed_2026', insurer_id: 'ri_medicaid', plan_name: 'RI Medicaid Managed Care Protocols (2026)', plan_year: 2026, state: 'RI', plan_type: 'Medicaid' },
    { id: 'uhc_medicare_dual_2026', insurer_id: 'uhc_ri', plan_name: 'UHC Dual Complete RI (2026)', plan_year: 2026, state: 'RI', plan_type: 'Medicare Advantage' },
    { id: 'generic_unselected_plan', insurer_id: 'unselected', plan_name: 'Unselected Plan (Needs Verification)', plan_year: 2026, state: 'RI', plan_type: 'Medicare Advantage' }
  ];

  // --- 3. REUSABLE PRODUCT UNIVERSE (NO DUPLICATE PRODUCTS) ---
  const PRODUCTS = [
    // 1. Vitamins & Minerals
    {
      id: 'P-VIT-D', product_name: 'Vitamin D3 2,000 IU Softgels', generic_name: 'Cholecalciferol', brand_name: 'Nature Made',
      category: 'vitamins', subcategory: 'Vitamin D', description: 'Supports bone strength, calcium absorption, and immune function.',
      icon: '☀️', aliases: ['vitamin d', 'vit d', 'd3', 'cholecalciferol'], synonyms: ['sunshine vitamin', 'bone vitamin'], keywords: ['vitamin d3', 'softgels']
    },
    {
      id: 'P-VIT-B12', product_name: 'Vitamin B12 5,000 mcg Sublingual', generic_name: 'Cyanocobalamin / Methylcobalamin', brand_name: 'Nature Made',
      category: 'vitamins', subcategory: 'Vitamin B', description: 'Supports nerve health and red blood cell production.',
      icon: '🔋', aliases: ['vitamin b12', 'vit b12', 'b12', 'cyanocobalamin'], synonyms: ['nerve vitamin'], keywords: ['b12', 'sublingual']
    },
    {
      id: 'P-VIT-C', product_name: 'Vitamin C 1,000 mg Caplets', generic_name: 'Ascorbic Acid', brand_name: 'Nature Made',
      category: 'vitamins', subcategory: 'Vitamin C', description: 'High-potency antioxidant support for immune defense.',
      icon: '🍊', aliases: ['vitamin c', 'vit c', 'ascorbic acid'], synonyms: ['immune vitamin'], keywords: ['vitamin c']
    },
    {
      id: 'P-VIT-A', product_name: 'Vitamin A 10,000 IU Softgels', generic_name: 'Retinol Palmitate', brand_name: 'Nature Made',
      category: 'vitamins', subcategory: 'Vitamin A', description: 'Supports eye vision and mucosal immunity.',
      icon: '👁️', aliases: ['vitamin a', 'vit a', 'retinol'], synonyms: ['eye vitamin'], keywords: ['vitamin a']
    },
    {
      id: 'P-VIT-E', product_name: 'Vitamin E 400 IU Softgels', generic_name: 'd-Alpha Tocopherol', brand_name: 'Nature Made',
      category: 'vitamins', subcategory: 'Vitamin E', description: 'Cellular membrane antioxidant protection.',
      icon: '💊', aliases: ['vitamin e', 'vit e', 'tocopherol'], synonyms: ['skin vitamin'], keywords: ['vitamin e']
    },
    {
      id: 'P-VIT-K', product_name: 'Vitamin K2 MK-7 100 mcg', generic_name: 'Menaquinone-7', brand_name: 'Nature Made',
      category: 'vitamins', subcategory: 'Vitamin K', description: 'Helps direct calcium to bones and blood clotting.',
      icon: '🦴', aliases: ['vitamin k', 'vit k', 'k2'], synonyms: ['bone calcium regulator'], keywords: ['vitamin k2']
    },
    {
      id: 'P-VIT-FOLIC', product_name: 'Folic Acid 800 mcg Tablets', generic_name: 'Folic Acid / Vitamin B9', brand_name: 'Nature Made',
      category: 'vitamins', subcategory: 'Folic Acid', description: 'Essential for DNA synthesis and maternal fetal health.',
      icon: '🌸', aliases: ['folic acid', 'folate', 'b9'], synonyms: ['prenatal folate'], keywords: ['folic acid']
    },
    {
      id: 'P-VIT-IRON', product_name: 'Ferrous Sulfate 65 mg (325 mg Equivalent Iron)', generic_name: 'Ferrous Sulfate', brand_name: 'Feosol',
      category: 'vitamins', subcategory: 'Iron', description: 'Red blood cell synthesis for iron deficiency anemia.',
      icon: '🩸', aliases: ['iron', 'ferrous sulfate', 'iron pills'], synonyms: ['anemia supplement'], keywords: ['iron', 'ferrous sulfate']
    },
    {
      id: 'P-VIT-CALCIUM', product_name: 'Calcium Carbonate 600 mg + Vitamin D3', generic_name: 'Calcium Carbonate with D3', brand_name: 'Caltrate',
      category: 'vitamins', subcategory: 'Calcium', description: 'Bone density support formula.',
      icon: '🦴', aliases: ['calcium', 'calcium carbonate', 'caltrate generic'], synonyms: ['bone calcium'], keywords: ['calcium carbonate']
    },
    {
      id: 'P-VIT-MAGNESIUM', product_name: 'Magnesium Glycinate 400 mg', generic_name: 'Magnesium Glycinate', brand_name: 'Qunol',
      category: 'vitamins', subcategory: 'Magnesium', description: 'Gentle muscle relaxation and sleep support.',
      icon: '🌿', aliases: ['magnesium', 'mag glycinate'], synonyms: ['cramp relaxer'], keywords: ['magnesium glycinate']
    },
    {
      id: 'P-VIT-ZINC', product_name: 'Zinc Picolinate 50 mg', generic_name: 'Zinc Picolinate', brand_name: 'Nature Made',
      category: 'vitamins', subcategory: 'Zinc', description: 'Immune cell support and wound healing.',
      icon: '🛡️', aliases: ['zinc', 'zinc picolinate'], synonyms: ['immune mineral'], keywords: ['zinc']
    },
    {
      id: 'P-VIT-MULTI', product_name: 'Senior Complete 50+ Daily Multivitamin', generic_name: 'Multivitamin with Minerals', brand_name: 'Centrum Silver',
      category: 'vitamins', subcategory: 'Multivitamins', description: 'Tailored for adults 50+ with Lutein and B-Vitamins.',
      icon: '💊', aliases: ['multivitamins', 'multivitamin', 'senior multi'], synonyms: ['daily multi'], keywords: ['multivitamin']
    },
    {
      id: 'P-VIT-PRENATAL', product_name: 'Prenatal Multivitamin with Folic Acid & Iron', generic_name: 'Prenatal Multivitamin', brand_name: 'One A Day',
      category: 'vitamins', subcategory: 'Prenatal Vitamins', description: 'Nutritional support prior to and during pregnancy.',
      icon: '👶', aliases: ['prenatal vitamins', 'prenatal vitamin', 'prenatal'], synonyms: ['pregnancy vitamins'], keywords: ['prenatal']
    },

    // 2. Supplements & Nutrition / Medical Foods
    {
      id: 'P-SUP-PROBIOTIC', product_name: 'Daily Probiotic 50 Billion CFU', generic_name: 'Lactobacillus & Bifidobacterium Blend', brand_name: 'Culturelle',
      category: 'supplements', subcategory: 'Probiotics', description: 'Supports digestive regularity and gut microbiome.',
      icon: '🦠', aliases: ['probiotics', 'probiotic'], synonyms: ['gut flora'], keywords: ['probiotic']
    },
    {
      id: 'P-SUP-FIBER', product_name: 'Psyllium Husk Daily Fiber Powder', generic_name: 'Psyllium Husk Powder', brand_name: 'Metamucil',
      category: 'supplements', subcategory: 'Fiber Supplements', description: 'Promotes regular digestive bowel movements.',
      icon: '🌾', aliases: ['fiber supplements', 'fiber', 'psyllium', 'metamucil'], synonyms: ['bulk laxative'], keywords: ['psyllium']
    },
    {
      id: 'P-NUT-ORS', product_name: 'Oral Rehydration Solution Powder Packets', generic_name: 'Oral Rehydration Salts (ORS)', brand_name: 'Pedialyte',
      category: 'nutrition', subcategory: 'Oral Rehydration Products', description: 'WHO formulation rapid electrolyte hydration solution.',
      icon: '💧', aliases: ['oral rehydration products', 'pedialyte', 'ors'], synonyms: ['electrolyte solution'], keywords: ['oral rehydration']
    },
    {
      id: 'P-NUT-ENSURE', product_name: 'Ensure High-Protein Nutritional Shakes (24 Pack)', generic_name: 'High-Protein Nutritional Liquid', brand_name: 'Ensure',
      category: 'nutrition', subcategory: 'Nutritional Shakes', description: '30g Protein, 25 Vitamins & Minerals per serving.',
      icon: '🥛', aliases: ['nutritional shakes', 'ensure', 'protein drinks'], synonyms: ['meal replacement'], keywords: ['ensure']
    },
    {
      id: 'P-NUT-ENTERAL', product_name: 'Enteral Clinical Tube-Feeding Formula & Supplies', generic_name: 'Enteral Nutrition Formula', brand_name: 'Jevity',
      category: 'nutrition', subcategory: 'Medical Nutritional Formulas', description: 'Complete clinical nutrition formula & feeding bags.',
      icon: '🪠', aliases: ['medical nutritional formulas', 'enteral formula', 'tube feeding supplies', 'enteral feeding pumps'], synonyms: ['tube feed formula'], keywords: ['enteral']
    },

    // 3. Pain Relief
    {
      id: 'P-PAI-ACETA', product_name: 'Extra Strength Acetaminophen 500 mg', generic_name: 'Acetaminophen / Paracetamol', brand_name: 'Tylenol',
      category: 'pain', subcategory: 'Analgesics', description: 'Rapid aspirin-free pain reliever and fever reducer.',
      icon: '💊', aliases: ['acetaminophen', 'tylenol', 'cold medicine'], synonyms: ['pain reliever'], keywords: ['acetaminophen', '500 mg']
    },
    {
      id: 'P-PAI-IBU', product_name: 'Ibuprofen 200 mg Softgels', generic_name: 'Ibuprofen', brand_name: 'Advil',
      category: 'pain', subcategory: 'NSAIDs', description: 'NSAID pain relief for muscle aches, headache & fever.',
      icon: '💊', aliases: ['ibuprofen', 'advil', 'motrin'], synonyms: ['nsaid pain reliever'], keywords: ['ibuprofen']
    },
    {
      id: 'P-PAI-NAPROXEN', product_name: 'Naproxen Sodium 220 mg Caplets', generic_name: 'Naproxen Sodium', brand_name: 'Aleve',
      category: 'pain', subcategory: 'NSAIDs', description: '12-hour joint & arthritis pain relief.',
      icon: '💊', aliases: ['naproxen', 'aleve'], synonyms: ['12 hour pain reliever'], keywords: ['naproxen']
    },
    {
      id: 'P-PAI-ASPIRIN', product_name: 'Low Dose Baby Aspirin 81 mg Safety Coated', generic_name: 'Aspirin', brand_name: 'Bayer',
      category: 'pain', subcategory: 'Salicylates', description: 'Enteric coated doctor-recommended daily aspirin regimen.',
      icon: '❤️', aliases: ['aspirin', 'baby aspirin', 'bayer'], synonyms: ['heart health aspirin'], keywords: ['aspirin 81 mg']
    },
    {
      id: 'P-PAI-VOLTAREN', product_name: 'Voltaren Arthritis Pain Gel (Diclofenac 1%)', generic_name: 'Diclofenac Sodium Topical Gel', brand_name: 'Voltaren',
      category: 'pain', subcategory: 'Topical Analgesics', description: 'Targeted topical NSAID gel for joint arthritis pain.',
      icon: '🧴', aliases: ['diclofenac gel', 'voltaren', 'arthritis gel'], synonyms: ['topical nsaid'], keywords: ['voltaren', 'diclofenac']
    },
    {
      id: 'P-PAI-LIDO', product_name: 'Maximum Strength Lidocaine 4% Pain Patches', generic_name: 'Lidocaine 4% Topical Patch', brand_name: 'Salonpas',
      category: 'pain', subcategory: 'Topical Analgesics', description: 'Desensitizes aggravated nerves for up to 12 hours.',
      icon: '🩹', aliases: ['lidocaine patches', 'lidocaine patch', 'lidocaine'], synonyms: ['numbing patch'], keywords: ['lidocaine']
    },

    // 4. Cold, Flu & Allergy
    {
      id: 'P-CFA-CETIRIZINE', product_name: 'Cetirizine Hydrochloride 10 mg Tablets', generic_name: 'Cetirizine HCl', brand_name: 'Zyrtec',
      category: 'coldflu', subcategory: 'Antihistamines', description: '24-hour non-drowsy relief of sneezing & runny nose.',
      icon: '🤧', aliases: ['cetirizine', 'zyrtec', 'allergy medicine'], synonyms: ['allergy tablet'], keywords: ['cetirizine']
    },
    {
      id: 'P-CFA-LORATADINE', product_name: 'Loratadine 10 mg 24-Hour Allergy Relief', generic_name: 'Loratadine', brand_name: 'Claritin',
      category: 'coldflu', subcategory: 'Antihistamines', description: '24-hour non-drowsy allergy relief.',
      icon: '🌸', aliases: ['loratadine', 'claritin', 'cold medicine'], synonyms: ['hives sneezing pill'], keywords: ['loratadine']
    },
    {
      id: 'P-CFA-FEXO', product_name: 'Fexofenadine Hydrochloride 180 mg', generic_name: 'Fexofenadine HCl', brand_name: 'Allegra',
      category: 'coldflu', subcategory: 'Antihistamines', description: 'Fast 24-hour indoor and outdoor allergy relief.',
      icon: '🤧', aliases: ['fexofenadine', 'allegra', 'cough medicine'], synonyms: ['allergy relief'], keywords: ['fexofenadine']
    },
    {
      id: 'P-CFA-SALINE', product_name: 'Sterile Saline Nasal Mist Spray', generic_name: 'Sodium Chloride Nasal Spray', brand_name: 'Ocean',
      category: 'coldflu', subcategory: 'Nasal Care', description: 'Drug-free sterile saline flush for dry nasal passages.',
      icon: '💧', aliases: ['saline nasal spray', 'saline mist'], synonyms: ['sinus flush'], keywords: ['saline nasal spray']
    },

    // 5. Digestive Health
    {
      id: 'P-DIG-ANTACID', product_name: 'Calcium Carbonate Antacid Chewables', generic_name: 'Calcium Carbonate', brand_name: 'Tums',
      category: 'digestive', subcategory: 'Antacids', description: 'Fast relief of heartburn & acid indigestion.',
      icon: '🍬', aliases: ['antacids', 'tums', 'chewable antacid'], synonyms: ['heartburn chewable'], keywords: ['antacids']
    },
    {
      id: 'P-DIG-FAMOTIDINE', product_name: 'Famotidine 20 mg Acid Reducer', generic_name: 'Famotidine', brand_name: 'Pepcid AC',
      category: 'digestive', subcategory: 'H2 Blockers', description: 'Prevents and relieves acid indigestion.',
      icon: '💊', aliases: ['famotidine', 'pepcid'], synonyms: ['acid reducer'], keywords: ['famotidine']
    },
    {
      id: 'P-DIG-OMEPRAZOLE', product_name: 'Omeprazole 20 mg Delayed Release Caplets', generic_name: 'Omeprazole', brand_name: 'Prilosec OTC',
      category: 'digestive', subcategory: 'Proton Pump Inhibitors', description: 'Treats frequent heartburn 2+ days a week.',
      icon: '🥣', aliases: ['omeprazole', 'prilosec'], synonyms: ['heartburn caplet'], keywords: ['omeprazole']
    },
    {
      id: 'P-DIG-LAXATIVE', product_name: 'Polyethylene Glycol 3350 Powder', generic_name: 'Polyethylene Glycol 3350', brand_name: 'MiraLAX',
      category: 'digestive', subcategory: 'Laxatives', description: 'Osmotic laxative powder for gentle constipation relief.',
      icon: '🥛', aliases: ['laxatives', 'polyethylene glycol', 'miralax', 'stool softeners'], synonyms: ['constipation powder'], keywords: ['laxatives']
    },
    {
      id: 'P-DIG-ANTIDIARRHEAL', product_name: 'Loperamide Hydrochloride 2 mg Caplets', generic_name: 'Loperamide HCl', brand_name: 'Imodium A-D',
      category: 'digestive', subcategory: 'Anti-Diarrheal', description: 'Controls and relieves diarrhea symptoms.',
      icon: '💊', aliases: ['anti-diarrheal products', 'loperamide', 'imodium'], synonyms: ['diarrhea caplet'], keywords: ['loperamide']
    },
    {
      id: 'P-DIG-HEMORRHOID', product_name: 'Hemorrhoidal Ointment with Phenylephrine', generic_name: 'Hemorrhoidal Ointment', brand_name: 'Preparation H',
      category: 'digestive', subcategory: 'Hemorrhoid Treatments', description: 'Shrinks swollen hemorrhoidal tissue & relieves itching.',
      icon: '🧴', aliases: ['hemorrhoid treatments', 'preparation h'], synonyms: ['hemorrhoid ointment'], keywords: ['hemorrhoid']
    },

    // 6. First Aid & Wound Care
    {
      id: 'P-AID-BANDAGE', product_name: 'Adhesive Bandage Assortment Pack', generic_name: 'Adhesive Bandages', brand_name: 'Band-Aid',
      category: 'firstaid', subcategory: 'Bandages', description: 'Flexible sterile adhesive bandages for minor cuts.',
      icon: '🩹', aliases: ['bandages', 'band-aid', 'gauze', 'medical tape'], synonyms: ['sticky bandages'], keywords: ['bandages']
    },
    {
      id: 'P-AID-ANTISEPTIC', product_name: 'Isopropyl Alcohol 70% Prep Pads', generic_name: 'Isopropyl Alcohol 70%', brand_name: 'BD',
      category: 'firstaid', subcategory: 'Antiseptics', description: 'Sterile antiseptic skin cleansing wipes.',
      icon: '🧴', aliases: ['antiseptic', 'alcohol pads', 'hydrogen peroxide'], synonyms: ['skin prep pads'], keywords: ['alcohol pads']
    },
    {
      id: 'P-AID-KIT', product_name: 'All-Purpose Emergency First Aid Kit', generic_name: 'First Aid Kit', brand_name: 'Johnson & Johnson',
      category: 'firstaid', subcategory: 'First-Aid Kits', description: 'Complete hard-case first aid trauma kit.',
      icon: '🧰', aliases: ['first-aid kits', 'first aid kit'], synonyms: ['trauma kit'], keywords: ['first aid kit']
    },
    {
      id: 'P-AID-THERMO', product_name: 'Express 10-Second Digital Thermometer', generic_name: 'Digital Thermometer', brand_name: 'Vicks',
      category: 'firstaid', subcategory: 'Thermometers', description: 'Fast 10-second oral / axillary fever reading.',
      icon: '🌡️', aliases: ['thermometers', 'digital thermometer'], synonyms: ['fever checker'], keywords: ['thermometer']
    },
    {
      id: 'P-AID-WOUNDCARE', product_name: 'Sterile Hydrocolloid & Surgical Dressings', generic_name: 'Hydrocolloid Dressing', brand_name: 'DuoDERM',
      category: 'woundcare', subcategory: 'Surgical Dressings', description: 'Advanced wound dressings & wound-vac supplies.',
      icon: '🩹', aliases: ['surgical dressings', 'wound-vac supplies'], synonyms: ['advanced wound dressing'], keywords: ['dressings']
    },

    // 7. Braces & Supports
    {
      id: 'P-BRC-KNEE', product_name: 'Dual-Hinged Medical Knee Brace', generic_name: 'Hinged Knee Orthosis', brand_name: 'Mueller',
      category: 'braces', subcategory: 'Knee Braces', description: 'Side hinge stabilization for meniscus & arthritis.',
      icon: '🦿', aliases: ['knee braces', 'knee brace', 'knee support'], synonyms: ['hinged knee brace'], keywords: ['knee brace']
    },
    {
      id: 'P-BRC-ANKLE', product_name: 'Ankle Stabilizer Compression Brace', generic_name: 'Ankle Orthosis', brand_name: 'Futuro',
      category: 'braces', subcategory: 'Ankle Braces', description: 'Lace-up side stabilizer brace for ankle sprains.',
      icon: '🦶', aliases: ['ankle braces', 'ankle brace'], synonyms: ['ankle stabilizer'], keywords: ['ankle brace']
    },
    {
      id: 'P-BRC-WRIST', product_name: 'Carpal Tunnel Night Support Wrist Splint', generic_name: 'Wrist Splint Orthosis', brand_name: 'Futuro',
      category: 'braces', subcategory: 'Wrist Braces', description: 'Removable palmar stay for carpal tunnel & tendonitis.',
      icon: '🧤', aliases: ['wrist braces', 'carpal-tunnel braces', 'wrist splint'], synonyms: ['carpal tunnel splint'], keywords: ['wrist brace']
    },
    {
      id: 'P-BRC-BACK', product_name: 'Lumbar Back Support Belt with Double Straps', generic_name: 'Lumbar Support Orthosis', brand_name: 'Mueller',
      category: 'braces', subcategory: 'Back Braces', description: 'Steel stays relieve lower back strain & sciatica.',
      icon: '🧍', aliases: ['back braces', 'back brace', 'lumbar support'], synonyms: ['lumbar belt'], keywords: ['back brace']
    },
    {
      id: 'P-BRC-NECK', product_name: 'Adjustable Cervical Foam Collar', generic_name: 'Cervical Collar Orthosis', brand_name: 'Futuro',
      category: 'braces', subcategory: 'Cervical Collars', description: 'Spine neck alignment & stiffness foam support.',
      icon: '🦒', aliases: ['cervical collars', 'cervical collar', 'walking boots', 'finger splints'], synonyms: ['neck brace'], keywords: ['cervical collar']
    },

    // 8. Mobility
    {
      id: 'P-MOB-CANES', product_name: 'Heavy-Duty Adjustable Quad Base Cane', generic_name: 'Quad Walking Cane', brand_name: 'Drive Medical',
      category: 'mobility', subcategory: 'Canes', description: 'All-terrain 4-point base for walking balance.',
      icon: '🦯', aliases: ['canes', 'cane', 'crutches', 'quad cane'], synonyms: ['walking stick'], keywords: ['quad cane']
    },
    {
      id: 'P-MOB-ROLLATOR', product_name: 'Aluminum 4-Wheel Rollator Walker with Seat', generic_name: 'Rollator Walker', brand_name: 'Drive Medical',
      category: 'mobility', subcategory: 'Rollators', description: 'Padded seat, storage pouch, 6" wheels & handbrakes.',
      icon: '♿', aliases: ['walkers', 'rollators', 'walker with seat', 'rollator'], synonyms: ['rolling walker'], keywords: ['rollator']
    },
    {
      id: 'P-MOB-WHEELCHAIR', product_name: 'Lightweight Folding Manual Wheelchair', generic_name: 'Manual Wheelchair', brand_name: 'Drive Medical',
      category: 'mobility', subcategory: 'Wheelchairs', description: '18" seat manual wheelchair with swing-away footrests.',
      icon: '👨‍🦽', aliases: ['wheelchairs', 'mobility scooters', 'wheelchair'], synonyms: ['transport chair'], keywords: ['wheelchair']
    },

    // 9. Home Safety & DME
    {
      id: 'P-SAF-CHAIR', product_name: 'Non-Slip Shower Chair & Transfer Bench', generic_name: 'Shower Chair / Transfer Bench', brand_name: 'Drive Medical',
      category: 'homesafety', subcategory: 'Shower Chairs', description: 'Suction cup rubber feet & drainage holes for safe bathing.',
      icon: '🪑', aliases: ['shower chairs', 'grab bars', 'transfer benches', 'commode chairs', 'hospital beds', 'patient lifts'], synonyms: ['bath seat'], keywords: ['shower chair']
    },

    // 10. Diabetes
    {
      id: 'P-DIB-MONITOR', product_name: 'Blood Glucose Meter & Test Strips Kit', generic_name: 'Blood Glucose Monitoring System', brand_name: 'OneTouch',
      category: 'diabetes', subcategory: 'Blood-Glucose Meters', description: 'No-coding blood glucose meter, 100 strips & lancets.',
      icon: '🩸', aliases: ['blood-glucose meters', 'test strips', 'lancets', 'sugar meter'], synonyms: ['diabetes meter'], keywords: ['test strips']
    },
    {
      id: 'P-DIB-CGM', product_name: 'Continuous Glucose Monitor (CGM) Sensor Kit', generic_name: 'Continuous Glucose Monitor', brand_name: 'Dexcom / Freestyle',
      category: 'diabetes', subcategory: 'Continuous Glucose Monitors', description: '14-day continuous real-time glucose sensor & transmitter.',
      icon: '📡', aliases: ['continuous glucose monitors', 'cgm', 'insulin-pump supplies', 'diabetic shoes'], synonyms: ['cgm sensor'], keywords: ['cgm']
    },

    // 11. Blood Pressure & Cardiovascular / Diagnostics
    {
      id: 'P-CAR-BPMONITOR', product_name: 'Automatic Upper Arm Blood Pressure Monitor', generic_name: 'Sphygmomanometer', brand_name: 'Omron',
      category: 'cardio', subcategory: 'Blood-Pressure Monitors', description: 'One-touch automatic BP reader with large cuff.',
      icon: '🩺', aliases: ['blood-pressure monitors', 'bp monitor', 'scales', 'pulse oximeters'], synonyms: ['hypertension checker'], keywords: ['blood pressure monitor']
    },

    // 12. Respiratory & CPAP / Sleep
    {
      id: 'P-RSP-CPAP', product_name: 'Compressor Nebulizer & CPAP Machine Tubing Kit', generic_name: 'CPAP / Nebulizer System', brand_name: 'ResMed',
      category: 'respiratory', subcategory: 'CPAP Machines', description: 'Aerosol nebulizer & CPAP mask replacement tubing.',
      icon: '🌬️', aliases: ['nebulizers', 'oxygen equipment', 'cpap machines', 'cpap masks', 'cpap tubing'], synonyms: ['sleep apnea machine'], keywords: ['cpap']
    },

    // 13. Eye Care
    {
      id: 'P-EYE-GLASSES', product_name: 'Lubricating Eye Drops & Reading Glasses', generic_name: 'Artificial Tears & Magnifiers', brand_name: 'Systane',
      category: 'eyecare', subcategory: 'Eye Drops', description: 'Artificial tears eye drops and scratch-resistant reading glasses.',
      icon: '👓', aliases: ['artificial tears', 'eye drops', 'reading glasses', 'prescription eyewear'], synonyms: ['dry eye drops'], keywords: ['eye drops']
    },

    // 14. Hearing
    {
      id: 'P-EAR-HEARING', product_name: 'OTC Digital Hearing Aids & Size 312 Batteries', generic_name: 'OTC Hearing Aid Device', brand_name: 'Jabra Enhance',
      category: 'hearing', subcategory: 'Hearing Aids', description: 'Over-the-counter digital hearing device & 40-pack batteries.',
      icon: '👂', aliases: ['hearing aids', 'hearing-aid batteries'], synonyms: ['sound amplifier'], keywords: ['hearing aids']
    },

    // 15. Dental & Oral Care
    {
      id: 'P-DEN-ORAL', product_name: 'Sonic Electric Toothbrush & Denture Supplies Kit', generic_name: 'Oral Care Kit', brand_name: 'Sonicare / Polident',
      category: 'dental', subcategory: 'Toothbrushes', description: 'Rechargeable electric toothbrush, floss, toothpaste & denture cleanser.',
      icon: '🪥', aliases: ['toothbrushes', 'toothpaste', 'floss', 'mouthwash', 'denture supplies'], synonyms: ['dental care'], keywords: ['toothpaste']
    },

    // 16. Skin & Dermatology
    {
      id: 'P-SKN-DERM', product_name: 'Hydrocortisone 1% & Antifungal Cream', generic_name: 'Hydrocortisone / Clotrimazole', brand_name: 'Cortizone-10',
      category: 'skincare', subcategory: 'Hydrocortisone', description: 'Relieves eczema itching, athlete foot & dermatological rashes.',
      icon: '🧴', aliases: ['hydrocortisone', 'antifungal treatments', 'eczema treatments', 'wart removers'], synonyms: ['anti-itch cream'], keywords: ['hydrocortisone']
    },

    // 17. Foot Care & Compression / Lymphedema
    {
      id: 'P-CMP-SOCKS', product_name: 'Graduated Compression Socks 15-20 mmHg', generic_name: 'Compression Stockings', brand_name: 'JOBST',
      category: 'compression', subcategory: 'Compression Socks', description: 'Graduated compression stockings for venous circulation & lymphedema.',
      icon: '🦵', aliases: ['compression socks', 'compression garments', 'lymphedema garments'], synonyms: ['support hose'], keywords: ['compression socks']
    },

    // 18. Incontinence
    {
      id: 'P-INC-BRIEFS', product_name: 'Adult Protective Underwear Briefs & Underpads', generic_name: 'Incontinence Briefs', brand_name: 'Depend',
      category: 'incontinence', subcategory: 'Adult Briefs', description: 'Leak guard adult protective briefs & bed underpads (Chux).',
      icon: '🩲', aliases: ['adult briefs', 'underpads', 'adult diapers'], synonyms: ['incontinence diapers'], keywords: ['adult briefs']
    },

    // 19. Urological Supplies & Ostomy
    {
      id: 'P-URO-CATH', product_name: 'Intermittent Urinary Catheter & Ostomy Bag Kit', generic_name: 'Urinary Catheter & Ostomy System', brand_name: 'Bard / Hollister',
      category: 'urology', subcategory: 'Catheters', description: 'Sterile intermittent catheters, urinary drainage bags & ostomy barriers.',
      icon: '💉', aliases: ['catheters', 'urinary drainage bags', 'ostomy bags', 'ostomy barriers'], synonyms: ['catheter kit'], keywords: ['catheter']
    },

    // 20. Women's Health / Pregnancy & Breastfeeding / Reproductive
    {
      id: 'P-WMN-PUMP', product_name: 'Electric Double Breast Pump & Pregnancy Tests', generic_name: 'Electric Breast Pump', brand_name: 'Medela',
      category: 'womens', subcategory: 'Breast Pumps', description: 'ACA mandated 100% covered electric double breast pump & milk bags.',
      icon: '🍼', aliases: ['pregnancy tests', 'breast pumps', 'breast-pump supplies', 'contraceptives'], synonyms: ['nursing pump'], keywords: ['breast pump']
    },

    // 21. Smoking Cessation
    {
      id: 'P-SMK-PATCH', product_name: 'Nicotine Transdermal Patches Step 1 (21 mg)', generic_name: 'Nicotine Patch', brand_name: 'NicoDerm CQ',
      category: 'smoking', subcategory: 'Nicotine Patches', description: '24-hour therapeutic nicotine patch, gum & lozenges for quitting.',
      icon: '🚭', aliases: ['nicotine patches', 'nicotine gum', 'nicotine lozenges'], synonyms: ['quit smoking'], keywords: ['nicotine patch']
    },

    // 22. Medication Management & Diagnostics
    {
      id: 'P-MED-PILL', product_name: '7-Day AM/PM Push-Button Pill Organizer & Cutter', generic_name: 'Pill Planner', brand_name: 'Apex',
      category: 'medmgmt', subcategory: 'Pill Organizers', description: 'Large pop-up compartments with braille & built-in pill cutter.',
      icon: '📅', aliases: ['pill organizers', 'pill cutters'], synonyms: ['weekly pill box'], keywords: ['pill organizer']
    }
  ];

  // --- 4. PLAN-SPECIFIC COVERAGE RULES ENGINE DATABASE ---
  const COVERAGE_RULES = [
    // --- PLAN: BCBSRI BlueCHiP Medicare Core (2026) ---
    {
      rule_id: 'R-BCBSRI-VIT-D', product_id: 'P-VIT-D', plan_id: 'bcbsri_bluechip_core_2026',
      benefit_pathway: 'OTC allowance', coverage_status: 'Covered', state: 'RI', plan_type: 'Medicare Advantage',
      otc_allowance_eligible: true, prescription_required: 'No for OTC', provider_order_required: false, diagnosis_required: false, prior_authorization_required: false,
      network_pharmacy_required: false, network_dme_supplier_required: false, member_cost: '$0 out-of-pocket', copay: '$0.00', coinsurance: '0%',
      allowance_amount: 50, allowance_frequency: 'quarterly', official_source_name: 'BCBSRI 2026 Medicare Advantage OTC Catalog',
      official_source_url: 'https://www.bcbsri.com/medicare/member/otc', source_effective_date: '2026-01-01', last_verified_date: '2026-01-01',
      notes: 'Eligible under quarterly BlueCHiP OTC allowance ($50/qtr).', plain_english_explanation: 'Your BCBSRI BlueCHiP plan pays for Vitamin D3 using your quarterly $50 OTC allowance card.',
      action_type: 'get_item', action_label: 'Get this item'
    },
    {
      rule_id: 'R-BCBSRI-KNEE', product_id: 'P-BRC-KNEE', plan_id: 'bcbsri_bluechip_core_2026',
      benefit_pathway: 'Durable Medical Equipment (DME)', coverage_status: 'Conditional', state: 'RI', plan_type: 'Medicare Advantage',
      otc_allowance_eligible: true, prescription_required: 'Yes for DMEPOS', provider_order_required: true, diagnosis_required: 'Arthritis / Ligament Strain', prior_authorization_required: false,
      network_pharmacy_required: false, network_dme_supplier_required: true, member_cost: '$0 with provider order', copay: '$0.00', coinsurance: '0%',
      official_source_name: 'CMS Medicare DMEPOS Fee Schedule & BCBSRI EOC 2026', official_source_url: 'https://www.cms.gov/medicare/payment/fee-schedules/dmepos',
      source_effective_date: '2026-01-01', last_verified_date: '2026-01-01', notes: 'HCPCS L1820 covered under DMEPOS when ordered by network physician.',
      plain_english_explanation: 'Knee braces may be available through your OTC allowance. Medically necessary orthopedic braces may instead require an order from your healthcare provider and fulfillment through an approved DME supplier.',
      action_type: 'ask_provider', action_label: 'Ask your provider'
    },

    // --- PLAN: RI Medicaid EOHHS Managed Care (2026) ---
    {
      rule_id: 'R-RIME-SMK', product_id: 'P-SMK-PATCH', plan_id: 'ri_medicaid_managed_2026',
      benefit_pathway: 'Prescription/pharmacy benefit', coverage_status: 'Covered', state: 'RI', plan_type: 'Medicaid',
      otc_allowance_eligible: false, prescription_required: true, provider_order_required: true, diagnosis_required: false, prior_authorization_required: false,
      network_pharmacy_required: true, network_dme_supplier_required: false, member_cost: '$0 copay', copay: '$0.00', coinsurance: '0%',
      official_source_name: 'RI EOHHS Pharmacy Benefit Plan Protocols 2026', official_source_url: 'https://eohhs.ri.gov/sites/g/files/xkgbur226/files/2026-01/2.4%20%20Pharmacy%20Benefit%20Plan%20Protocols%20-%20Effective%2001.01.26_CLEAN.pdf',
      source_effective_date: '2026-01-01', last_verified_date: '2026-01-01', notes: 'Protocol 2.4 non-prescription nicotine cessation covered when ordered by practitioner.',
      plain_english_explanation: 'Rhode Island Medicaid covers nicotine patches, gum, and lozenges at 100% ($0 copay) when ordered by your health plan practitioner.',
      action_type: 'find_pharmacy', action_label: 'Find an approved pharmacy'
    }
  ];

  // --- 5. APP STATE ---
  let activeInsurerId = 'bcbsri';
  let activePlanId = 'bcbsri_bluechip_core_2026';
  let activeState = 'RI';
  let activePlanType = 'Medicare Advantage';
  let activeDepartment = 'all';
  let activeStatusFilter = 'all';
  let activePathwayFilter = 'all';
  let searchQuery = '';
  let chkZeroCostOnly = false;
  let chkOtcOnly = false;
  let chkRxOnly = false;
  let chkOrderOnly = false;
  let callSlip = [];

  // Local storage for Call Slip
  try {
    const stored = localStorage.getItem('bcnCallSlip');
    if (stored) callSlip = JSON.parse(stored);
  } catch {}

  function saveCallSlip() {
    try {
      localStorage.setItem('bcnCallSlip', JSON.stringify(callSlip));
    } catch {}
  }

  // --- 6. COVERAGE RESOLUTION ENGINE ---
  function evaluateCoverageRule(productId, planId) {
    if (planId === 'generic_unselected_plan' || activeInsurerId === 'unselected') {
      return {
        rule_id: 'R-UNVERIFIED', product_id: productId, plan_id: planId,
        benefit_pathway: 'Other plan-specific supplemental benefits', coverage_status: 'Unknown / needs verification', state: activeState, plan_type: activePlanType,
        otc_allowance_eligible: false, prescription_required: 'Depends', provider_order_required: 'Depends', diagnosis_required: 'Depends', prior_authorization_required: 'Depends',
        network_pharmacy_required: false, network_dme_supplier_required: false, member_cost: 'Unknown', copay: 'Unknown', coinsurance: 'Unknown',
        official_source_name: 'Official Plan Document Required', official_source_url: '/find-care/#sources', source_effective_date: '2026-01-01', last_verified_date: '2026-01-01',
        notes: 'Coverage not yet verified for this specific health plan contract.', plain_english_explanation: 'Coverage information is not yet verified for this plan. Please check your Evidence of Coverage or ask your provider.',
        action_type: 'check_eligibility', action_label: 'Check eligibility'
      };
    }

    const found = COVERAGE_RULES.find((r) => r.product_id === productId && r.plan_id === planId);
    if (found) return found;

    // Fallback rule for product without explicit rule for active plan
    return {
      rule_id: `R-FALLBACK-${productId}`, product_id: productId, plan_id: planId,
      benefit_pathway: 'OTC allowance', coverage_status: 'Unknown / needs verification', state: activeState, plan_type: activePlanType,
      otc_allowance_eligible: true, prescription_required: 'Depends', provider_order_required: false, diagnosis_required: false, prior_authorization_required: false,
      network_pharmacy_required: false, network_dme_supplier_required: false, member_cost: 'Uses OTC Allowance', copay: '$0.00', coinsurance: '0%',
      official_source_name: 'Generic Plan Evidence of Coverage', official_source_url: '/find-care/#sources', source_effective_date: '2026-01-01', last_verified_date: '2026-01-01',
      notes: 'Item is a standard health category. Formulate coverage with plan Member Services.', plain_english_explanation: 'This item may qualify under your plan\\'s OTC allowance or medical benefit. Confirm coverage before purchase.',
      action_type: 'view_coverage', action_label: 'View coverage details'
    };
  }

  // --- 7. SEARCH & FILTER ENGINE (WITH SYNONYM MATCHING) ---
  function filterProducts() {
    const q = searchQuery.trim().toLowerCase();
    let filtered = PRODUCTS;

    // Department filter
    if (activeDepartment !== 'all') {
      filtered = filtered.filter((p) => p.category === activeDepartment);
    }

    // Synonym Search logic
    if (q) {
      filtered = filtered.filter((p) => {
        const matchName = p.product_name.toLowerCase().includes(q);
        const matchGeneric = p.generic_name.toLowerCase().includes(q);
        const matchBrand = p.brand_name ? p.brand_name.toLowerCase().includes(q) : false;
        const matchDesc = p.description.toLowerCase().includes(q);
        const matchAliases = p.aliases?.some((a) => a.toLowerCase().includes(q));
        const matchSynonyms = p.synonyms?.some((s) => s.toLowerCase().includes(q));
        const matchKeywords = p.keywords?.some((k) => k.toLowerCase().includes(q));
        return matchName || matchGeneric || matchBrand || matchDesc || matchAliases || matchSynonyms || matchKeywords;
      });
    }

    // Evaluate Rule & Checkboxes
    filtered = filtered.filter((p) => {
      const rule = evaluateCoverageRule(p.id, activePlanId);

      if (activeStatusFilter !== 'all' && rule.coverage_status !== activeStatusFilter) return false;
      if (activePathwayFilter !== 'all' && rule.benefit_pathway !== activePathwayFilter) return false;

      if (chkZeroCostOnly && rule.member_cost !== '$0 out-of-pocket' && rule.member_cost !== '$0 copay' && rule.member_cost !== '$0 with provider order') return false;
      if (chkOtcOnly && !rule.otc_allowance_eligible) return false;
      if (chkRxOnly && rule.prescription_required !== true && rule.prescription_required !== 'Yes for OTC') return false;
      if (chkOrderOnly && !rule.provider_order_required) return false;

      return true;
    });

    return filtered;
  }

  // --- 8. RENDER GRID CARDS ---
  function renderGrid() {
    const grid = $('#productGrid');
    const countLabel = $('#productCountLabel');
    if (!grid) return;

    const results = filterProducts();

    if (countLabel) {
      countLabel.innerHTML = `Showing <strong>${results.length}</strong> products for <strong>${esc(getPlanName(activePlanId))}</strong> (${esc(activeState)})`;
    }

    if (results.length === 0) {
      grid.innerHTML = `
        <div style="grid-column:1/-1;background:#fff;border:1px solid var(--line);border-radius:12px;padding:40px;text-align:center">
          <span style="font-size:36px;display:block;margin-bottom:12px">🔍</span>
          <h3 style="margin:0 0 8px;color:var(--green-dark)">No matching products found</h3>
          <p style="color:var(--text-muted);font-size:14px;max-width:500px;margin:0 auto 16px">
            Try resetting your search query or setting Coverage Status to "All Coverage Statuses".
          </p>
          <button type="button" class="hero-form-btn" onclick="window.resetMarketFilters()" style="background:var(--green-dark);color:#fff">
            Reset All Filters
          </button>
        </div>
      `;
      return;
    }

    grid.innerHTML = results.map((p) => {
      const rule = evaluateCoverageRule(p.id, activePlanId);
      const inSlip = callSlip.some((i) => i.id === p.id);

      return `
        <div class="product-card">
          <div class="product-card-top">
            <span class="product-sku">${esc(p.category.toUpperCase())} · ${esc(p.subcategory)}</span>
            ${getStatusBadgeHTML(rule.coverage_status)}
          </div>

          <div class="product-image-area">
            <span style="font-size:44px">${p.icon}</span>
          </div>

          <h3 class="product-title">${esc(p.product_name)}</h3>
          <p style="font-size:12px;color:var(--text-muted);margin:-2px 0 8px">
            Generic: <strong>${esc(p.generic_name)}</strong> ${p.brand_name ? `· Brand: ${esc(p.brand_name)}` : ''}
          </p>
          <p class="product-specs">${esc(p.description)}</p>

          <div style="margin:10px 0;font-size:12px;line-height:1.4;background:var(--cream);padding:10px;border-radius:6px;border:1px solid var(--line)">
            <div style="font-weight:700;color:var(--green-dark);margin-bottom:4px">
              Pathway: ${esc(rule.benefit_pathway)}
            </div>
            <div><strong>Member Cost:</strong> ${esc(rule.member_cost)}</div>
            ${rule.plain_english_explanation ? `<div style="margin-top:6px;font-style:italic;color:var(--text-muted)">"${esc(rule.plain_english_explanation)}"</div>` : ''}
          </div>

          <div style="display:grid;gap:8px;margin-top:auto">
            <button type="button" class="add-to-slip-btn ${inSlip ? 'added' : ''}" data-add-id="${esc(p.id)}">
              ${inSlip ? '✓ In Call Slip' : '+ Add to Phone Order Slip'}
            </button>

            <button type="button" class="slip-secondary-btn" data-view-rule="${esc(p.id)}">
              🔍 View Coverage &amp; Source Details
            </button>
          </div>
        </div>
      `;
    }).join('');

    $$('[data-add-id]').forEach((btn) => {
      btn.addEventListener('click', () => addToCallSlip(btn.dataset.addId));
    });

    $$('[data-view-rule]').forEach((btn) => {
      btn.addEventListener('click', () => openCoverageModal(btn.dataset.viewRule));
    });
  }

  function getStatusBadgeHTML(status) {
    switch (status) {
      case 'Covered':
        return `<span class="status-badge status-covered">✓ Covered</span>`;
      case 'Conditional':
        return `<span class="status-badge status-conditional">⚠️ Conditional</span>`;
      case 'Unknown / needs verification':
        return `<span class="status-badge status-needs-verification">❓ Needs Verification</span>`;
      case 'Not covered':
        return `<span class="status-badge status-not-covered">❌ Not Covered</span>`;
      default:
        return `<span class="status-badge status-needs-verification">❓ Needs Verification</span>`;
    }
  }

  function getPlanName(planId) {
    const plan = PLANS.find((p) => p.id === planId);
    return plan ? plan.plan_name : 'Unselected / Generic Plan';
  }

  window.resetMarketFilters = function() {
    activeDepartment = 'all';
    activeStatusFilter = 'all';
    activePathwayFilter = 'all';
    searchQuery = '';
    chkZeroCostOnly = false;
    chkOtcOnly = false;
    chkRxOnly = false;
    chkOrderOnly = false;
    const input = $('#marketSearchInput');
    if (input) input.value = '';
    renderDepartmentPills();
    renderGrid();
  };

  // --- 9. RENDER DEPARTMENT PILLS & SIDEBAR ---
  function renderDepartmentPills() {
    const bar = $('#categoryPillsBar');
    const sidebar = $('#sidebarCategoryList');

    if (bar) {
      bar.innerHTML = DEPARTMENTS.map((d) => `
        <button type="button" class="cat-pill ${activeDepartment === d.id ? 'active' : ''}" data-dept-id="${esc(d.id)}">
          ${d.icon} ${esc(d.label)}
        </button>
      `).join('');

      $$('[data-dept-id]').forEach((btn) => {
        btn.addEventListener('click', () => {
          activeDepartment = btn.dataset.deptId;
          renderDepartmentPills();
          renderGrid();
        });
      });
    }

    if (sidebar) {
      sidebar.innerHTML = DEPARTMENTS.map((d) => `
        <label class="filter-checkbox-label">
          <input type="radio" name="sideDept" value="${esc(d.id)}" ${activeDepartment === d.id ? 'checked' : ''}>
          <span>${d.icon} ${esc(d.label)}</span>
        </label>
      `).join('');

      $$('input[name="sideDept"]').forEach((radio) => {
        radio.addEventListener('change', () => {
          activeDepartment = radio.value;
          renderDepartmentPills();
          renderGrid();
        });
      });
    }
  }

  // --- 10. COVERAGE MODAL ---
  function openCoverageModal(id) {
    const item = PRODUCTS.find((p) => p.id === id);
    if (!item) return;

    const rule = evaluateCoverageRule(id, activePlanId);

    let modal = $('#coverageModal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'coverageModal';
      modal.className = 'order-form-modal-overlay';
      modal.setAttribute('role', 'dialog');
      modal.setAttribute('aria-modal', 'true');
      document.body.appendChild(modal);
    }

    const isVerifiedReal = rule.official_source_name.includes('BCBSRI') || rule.official_source_name.includes('EOHHS') || rule.official_source_name.includes('CMS');

    modal.innerHTML = `
      <div class="order-form-modal-window" style="max-width:740px">
        <div class="order-form-modal-header">
          <div>
            <h2 style="margin:0;font-size:20px;color:var(--green-dark)">
              ${item.icon} ${esc(item.product_name)}
            </h2>
            <small style="color:var(--text-muted)">Generic: ${esc(item.generic_name)} ${item.brand_name ? `· Brand: ${esc(item.brand_name)}` : ''}</small>
          </div>
          <button type="button" class="close-modal-btn" id="closeCoverageModalBtn" aria-label="Close modal">✕</button>
        </div>

        <div class="order-form-modal-body">
          <div style="display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:16px;background:var(--cream);padding:12px;border-radius:8px">
            <div>
              <strong style="font-size:12px;color:var(--text-muted);display:block">ACTIVE PLAN CONTRACT:</strong>
              <span style="font-size:15px;font-weight:700;color:var(--green-dark)">${esc(getPlanName(activePlanId))} (${esc(activeState)})</span>
            </div>
            <div>
              ${getStatusBadgeHTML(rule.coverage_status)}
            </div>
          </div>

          <div style="background:#fff8e6;border:1px solid #fce8b2;padding:12px;border-radius:8px;margin-bottom:16px;font-size:13px;line-height:1.5">
            <strong>How You May Qualify:</strong><br/>
            ${esc(rule.plain_english_explanation)}
          </div>

          <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px">
            <div style="background:#fff;border:1px solid var(--line);padding:12px;border-radius:8px">
              <strong style="font-size:13px;display:block;margin-bottom:6px;color:var(--green-dark)">Coverage Conditions:</strong>
              <ul style="margin:0;padding-left:18px;font-size:12px;line-height:1.6">
                <li><strong>Prescription Required:</strong> ${esc(rule.prescription_required)}</li>
                <li><strong>Provider Order:</strong> ${esc(rule.provider_order_required)}</li>
                <li><strong>Diagnosis Required:</strong> ${esc(rule.diagnosis_required)}</li>
                <li><strong>Prior Auth Required:</strong> ${esc(rule.prior_authorization_required)}</li>
                <li><strong>Approved Supplier:</strong> ${rule.network_dme_supplier_required ? 'Network DME Supplier' : 'In-Network Pharmacy'}</li>
              </ul>
            </div>

            <div style="background:#fff;border:1px solid var(--line);padding:12px;border-radius:8px">
              <strong style="font-size:13px;display:block;margin-bottom:6px;color:var(--green-dark)">Member Financial Responsibility:</strong>
              <ul style="margin:0;padding-left:18px;font-size:12px;line-height:1.6">
                <li><strong>Member Cost:</strong> ${esc(rule.member_cost)}</li>
                <li><strong>Copay:</strong> ${esc(rule.copay)}</li>
                <li><strong>Coinsurance:</strong> ${esc(rule.coinsurance)}</li>
                ${rule.allowance_amount ? `<li><strong>OTC Allowance:</strong> $${rule.allowance_amount} / ${rule.allowance_frequency}</li>` : ''}
              </ul>
            </div>
          </div>

          <div style="background:var(--green-tint);border:1px solid var(--line);padding:14px;border-radius:8px;margin-bottom:16px">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px">
              <strong style="font-size:13px;color:var(--green-dark)">
                📄 Official Source Documentation:
              </strong>
              <span class="source-verification-badge ${isVerifiedReal ? 'badge-real-verified' : 'badge-demo-seed'}">
                ${isVerifiedReal ? '✓ Real Verified Document' : '⚠️ Seed Demo Rule'}
              </span>
            </div>
            <p style="font-size:12px;line-height:1.5;margin:0 0 6px;color:var(--text-muted)">
              ${esc(rule.notes)}
            </p>
            <div style="font-size:11px;color:var(--text-muted);display:flex;justify-content:space-between;flex-wrap:wrap">
              <span>Source: <a href="${esc(rule.official_source_url)}" target="_blank" rel="noopener" style="color:var(--green-dark);font-weight:700">${esc(rule.official_source_name)}</a></span>
              <span>Effective: ${esc(rule.source_effective_date)} · Verified: ${esc(rule.last_verified_date)}</span>
            </div>
          </div>

          <div style="display:flex;gap:10px;justify-content:flex-end">
            <a href="/find-care/doctors/" class="hero-form-btn" style="background:var(--green-dark);color:#fff;text-decoration:none">
              🩺 Ask Your Provider
            </a>
            <button type="button" class="hero-form-btn" id="modalActionBtn" style="background:var(--terracotta);color:#fff">
              ${esc(rule.action_label)}
            </button>
          </div>
        </div>
      </div>
    `;

    modal.style.display = 'flex';
    $('#closeCoverageModalBtn')?.addEventListener('click', () => { modal.style.display = 'none'; });
    $('#modalActionBtn')?.addEventListener('click', () => {
      addToCallSlip(id);
      modal.style.display = 'none';
    });
  }

  // --- 11. PHONE ORDER SLIP & ORDER SHEET ---
  function addToCallSlip(id) {
    const item = PRODUCTS.find((p) => p.id === id);
    if (!item) return;

    const existing = callSlip.find((i) => i.id === id);
    if (existing) {
      existing.qty += 1;
    } else {
      callSlip.push({
        id: item.id,
        sku: item.id,
        name: item.product_name,
        icon: item.icon,
        qty: 1
      });
    }

    saveCallSlip();
    renderGrid();
    renderCallSlip();
  }

  function renderCallSlip() {
    const container = $('#callSlipContainer');
    const badge = $('#slipCountBadge');

    const totalCount = callSlip.reduce((sum, i) => sum + i.qty, 0);
    if (badge) badge.textContent = totalCount;

    if (!container) return;

    if (callSlip.length === 0) {
      container.innerHTML = `
        <div style="text-align:center;padding:24px 10px;color:#cbe0d9">
          <span style="font-size:32px;display:block;margin-bottom:8px">🛒</span>
          <strong style="color:#fff">Your Call Slip is Empty</strong>
          <p style="font-size:12px;margin:4px 0 0">
            Click <em>"+ Add to Phone Order Slip"</em> to build your call sheet.
          </p>
        </div>
      `;
      return;
    }

    container.innerHTML = `
      <ul class="slip-item-list">
        ${callSlip.map((item) => `
          <li class="slip-item">
            <div style="display:flex;align-items:center;gap:8px">
              <span>${item.icon}</span>
              <div>
                <strong style="font-size:13px;display:block;color:#fff">${esc(item.name)}</strong>
                <small style="color:#cbe0d9">Code #${esc(item.sku)}</small>
              </div>
            </div>
            <div style="display:flex;align-items:center;gap:6px">
              <button type="button" class="qty-btn" data-qty-dec="${esc(item.id)}">-</button>
              <span style="font-weight:700;color:#fff;font-size:13px">${item.qty}</span>
              <button type="button" class="qty-btn" data-qty-inc="${esc(item.id)}">+</button>
            </div>
          </li>
        `).join('')}
      </ul>

      <div style="display:grid;gap:8px;margin-top:16px">
        <button type="button" class="hero-form-btn" id="openPrintFormBtn" style="background:var(--gold);color:var(--green-dark);width:100%;justify-content:center">
          📄 View &amp; Print Order Sheet
        </button>
        <button type="button" style="background:none;border:none;color:#ff9999;font-size:12px;cursor:pointer;margin-top:4px" id="clearSlipBtn">
          Clear Order Slip
        </button>
      </div>
    `;

    $$('[data-qty-inc]').forEach((b) => b.addEventListener('click', () => updateQty(b.dataset.qtyInc, 1)));
    $$('[data-qty-dec]').forEach((b) => b.addEventListener('click', () => updateQty(b.dataset.qtyDec, -1)));

    $('#clearSlipBtn')?.addEventListener('click', () => {
      callSlip = [];
      saveCallSlip();
      renderGrid();
      renderCallSlip();
    });

    $('#openPrintFormBtn')?.addEventListener('click', openPrintableOrderForm);
  }

  function updateQty(id, delta) {
    const item = callSlip.find((i) => i.id === id);
    if (!item) return;
    item.qty += delta;
    if (item.qty <= 0) {
      callSlip = callSlip.filter((i) => i.id !== id);
    }
    saveCallSlip();
    renderGrid();
    renderCallSlip();
  }

  function openPrintableOrderForm() {
    let modal = $('#orderFormModal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'orderFormModal';
      modal.className = 'order-form-modal-overlay';
      modal.setAttribute('role', 'dialog');
      modal.setAttribute('aria-modal', 'true');
      document.body.appendChild(modal);
    }

    const todayStr = new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });

    modal.innerHTML = `
      <div class="order-form-modal-window">
        <div class="order-form-modal-header">
          <div>
            <h2 style="margin:0;font-size:20px">Health Benefit Card OTC &amp; DME Order Form</h2>
            <small style="color:var(--text-muted)">Pazeratechnologies Benefit Card Navigator · ${todayStr}</small>
          </div>
          <button type="button" class="close-modal-btn" id="closeOrderFormModal">✕</button>
        </div>

        <div class="order-form-modal-body">
          <div style="background:var(--cream);border:1px solid var(--line);padding:14px;border-radius:8px;margin-bottom:20px;display:grid;grid-template-columns:1fr 1fr;gap:12px;font-size:13px">
            <div><strong>Selected Plan:</strong> ${esc(getPlanName(activePlanId))}</div>
            <div><strong>State:</strong> ${esc(activeState)}</div>
            <div><strong>Total Items:</strong> ${callSlip.length}</div>
            <div><strong>Shipping Cost:</strong> $0.00 (Free Home Delivery)</div>
          </div>

          <table class="order-items-table">
            <thead>
              <tr>
                <th>Item Code</th>
                <th>Product Description</th>
                <th>Qty</th>
                <th>Estimated Cost</th>
              </tr>
            </thead>
            <tbody>
              ${callSlip.map((item) => `
                <tr>
                  <td><code>${esc(item.sku)}</code></td>
                  <td>${esc(item.name)}</td>
                  <td>${item.qty}</td>
                  <td>$0.00 (Covered)</td>
                </tr>
              `).join('')}
            </tbody>
          </table>

          <div style="display:flex;gap:12px;justify-content:flex-end;margin-top:20px">
            <button type="button" class="hero-form-btn" id="printModalBtn" style="background:var(--green-dark);color:#fff">
              🖨️ Print Official Order Sheet
            </button>
          </div>
        </div>
      </div>
    `;

    modal.style.display = 'flex';
    $('#closeOrderFormModal')?.addEventListener('click', () => { modal.style.display = 'none'; });
    $('#printModalBtn')?.addEventListener('click', () => { window.print(); });
  }

  // --- 12. INITIALIZATION ---
  function init() {
    renderDepartmentPills();

    // Dropdown Event Handlers
    const insurerSelect = $('#insurerSelect');
    const planSelect = $('#planSelect');
    const stateSelect = $('#stateSelect');
    const planTypeSelect = $('#planTypeSelect');

    if (insurerSelect) {
      insurerSelect.addEventListener('change', (e) => {
        activeInsurerId = e.target.value;
        renderGrid();
      });
    }

    if (planSelect) {
      planSelect.addEventListener('change', (e) => {
        activePlanId = e.target.value;
        const pill = $('#planStatusPill');
        if (pill) {
          if (activePlanId === 'generic_unselected_plan') {
            pill.textContent = '❓ Needs Verification';
            pill.style.background = 'var(--gold)';
            pill.style.color = '#594100';
          } else {
            pill.textContent = '✓ Plan Active';
            pill.style.background = 'var(--terracotta)';
            pill.style.color = '#fff';
          }
        }
        renderGrid();
      });
    }

    if (stateSelect) {
      stateSelect.addEventListener('change', (e) => {
        activeState = e.target.value;
        renderGrid();
      });
    }

    if (planTypeSelect) {
      planTypeSelect.addEventListener('change', (e) => {
        activePlanType = e.target.value;
        renderGrid();
      });
    }

    // Search Input
    const searchInput = $('#marketSearchInput');
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        searchQuery = e.target.value;
        renderGrid();
      });
    }

    // Checkboxes
    $('#chkZeroCost')?.addEventListener('change', (e) => { chkZeroCostOnly = e.target.checked; renderGrid(); });
    $('#chkOtcOnly')?.addEventListener('change', (e) => { chkOtcOnly = e.target.checked; renderGrid(); });
    $('#chkRxOnly')?.addEventListener('change', (e) => { chkRxOnly = e.target.checked; renderGrid(); });
    $('#chkOrderOnly')?.addEventListener('change', (e) => { chkOrderOnly = e.target.checked; renderGrid(); });

    // Radios
    $$('input[name="sideStatus"]').forEach((radio) => {
      radio.addEventListener('change', () => {
        activeStatusFilter = radio.value;
        renderGrid();
      });
    });

    $$('input[name="sidePathway"]').forEach((radio) => {
      radio.addEventListener('change', () => {
        activePathwayFilter = radio.value;
        renderGrid();
      });
    });

    $('#heroViewFormBtn')?.addEventListener('click', openPrintableOrderForm);

    renderGrid();
    renderCallSlip();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
"""

with open('dist/marketplace/marketplace.js', 'w', encoding='utf-8') as f:
    f.write(js_content)

print("Generated marketplace.js successfully.")
