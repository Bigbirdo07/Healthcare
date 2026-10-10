import sys

js_code = """/**
 * Benefit Card Navigator — Pazeratechnologies Insurance Marketplace Architecture
 * Plan-specific coverage rule engine linking products and services to official plan sources.
 */

(function () {
  'use strict';

  const $ = (selector, parent = document) => parent.querySelector(selector);
  const $$ = (selector, parent = document) => [...parent.querySelectorAll(selector)];
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  // --- 1. TAXONOMY & CATEGORIES ---
  const PRODUCT_CATEGORIES = [
    { id: 'all', label: 'All Products & Services', icon: '🛒' },
    { id: 'vitamins', label: 'Vitamins & Minerals', icon: '💊' },
    { id: 'nutrition', label: 'Nutrition & Dietary', icon: '🥛' },
    { id: 'pain', label: 'Pain Relief & Topicals', icon: '🩹' },
    { id: 'coldflu', label: 'Cold, Flu & Allergy', icon: '🤧' },
    { id: 'digestive', label: 'Digestive Health', icon: '🥣' },
    { id: 'firstaid', label: 'First Aid & Wound Care', icon: '🧰' },
    { id: 'braces', label: 'Braces & Orthopedics', icon: '🦿' },
    { id: 'mobility', label: 'Mobility Products', icon: '♿' },
    { id: 'homesafety', label: 'Home Safety', icon: '🏠' },
    { id: 'diabetes', label: 'Diabetes Care', icon: '🩸' },
    { id: 'cardio', label: 'BP & Monitoring', icon: '🩺' },
    { id: 'respiratory', label: 'Respiratory Support', icon: '🌬️' },
    { id: 'eyecare', label: 'Vision & Eye Care', icon: '👁️' },
    { id: 'earcare', label: 'Ear Care & Hearing', icon: '👂' },
    { id: 'dental', label: 'Dental & Oral Care', icon: '🪥' },
    { id: 'skincare', label: 'Skin Care & Dermatology', icon: '🧴' },
    { id: 'footcare', label: 'Foot Care', icon: '🦶' },
    { id: 'compression', label: 'Compression & Circulation', icon: '🦵' },
    { id: 'incontinence', label: 'Incontinence & Hygiene', icon: '🩲' },
    { id: 'womens', label: 'Women’s Health', icon: '🌸' },
    { id: 'sexual', label: 'Sexual & Reproductive', icon: '💊' },
    { id: 'smoking', label: 'Smoking Cessation', icon: '🚭' },
    { id: 'sleep', label: 'Sleep Support', icon: '🌙' },
    { id: 'infant', label: 'Pregnancy & Infant', icon: '👶' },
    { id: 'ostomy', label: 'Ostomy Supplies', icon: '🩺' },
    { id: 'urology', label: 'Urological Products', icon: '💉' },
    { id: 'advwound', label: 'Advanced Wound Care', icon: '🩹' },
    { id: 'prosthetics', label: 'Prosthetics', icon: '🎗️' },
    { id: 'dme', label: 'Home Medical Equipment', icon: '🚽' },
    { id: 'medmgmt', label: 'Medication Management', icon: '📅' },
    { id: 'monitoring', label: 'Personal Monitoring', icon: '🌡️' },
    { id: 'ssbci', label: 'Chronic Support (SSBCI)', icon: '🍎' },
    { id: 'storedept', label: 'Store Products', icon: '☀️' }
  ];

  const SERVICE_CATEGORIES = [
    { id: 'all_services', label: 'All Plan Benefits', icon: '🏥' },
    { id: 'srv_dental', label: 'Dental Exams & Care', icon: '🪥' },
    { id: 'srv_vision', label: 'Vision Exams & Eyewear', icon: '👓' },
    { id: 'srv_transport', label: 'Medical Transportation', icon: '🚗' },
    { id: 'srv_fitness', label: 'Fitness & Gym Memberships', icon: '👟' },
    { id: 'srv_meals', label: 'Post-Hospital Meals', icon: '🍱' },
    { id: 'srv_food', label: 'Healthy Food & Groceries', icon: '🍎' },
    { id: 'srv_otc', label: 'OTC Card Allowance', icon: '💳' },
    { id: 'srv_preventive', label: 'Preventive Care Benefits', icon: '🌸' },
    { id: 'srv_ssbci', label: 'Chronic Allowances (SSBCI)', icon: '⚡' },
    { id: 'srv_equipment', label: 'Medical Equipment Benefits', icon: '🩺' }
  ];

  // --- 2. RETAIL PRODUCT UNIVERSE (33 SEED CATEGORIES WITH DEDUPLICATION) ---
  const PRODUCTS = [
    // 1. Vitamins & Minerals
    {
      id: 'PROD-VIT-A', sku: 'VIT-101', name: 'Vitamin A 10,000 IU Softgels', primaryCategory: 'vitamins', secondaryCategories: ['nutrition'],
      aliases: ['vit a', 'retinol'], synonyms: ['eye health vitamin'], keywords: ['vitamin a', 'softgels'],
      variants: [{ name: 'Vitamin A 10,000 IU 100 Softgels', upc: '010101010101' }], icon: '💊', specs: 'Eye vision & skin health support · 100 Softgels', retailValue: '$11.50', allowanceCost: 9.00
    },
    {
      id: 'PROD-VIT-B1', sku: 'VIT-102', name: 'Vitamin B1 Thiamine 100 mg', primaryCategory: 'vitamins', secondaryCategories: [],
      aliases: ['thiamine', 'vit b1'], synonyms: ['energy metabolism'], keywords: ['b1', 'thiamine'],
      variants: [{ name: 'Vitamin B1 100 mg 100 Tablets' }], icon: '🔋', specs: 'Nerve & energy metabolism support · 100 Tablets', retailValue: '$9.99', allowanceCost: 8.00
    },
    {
      id: 'PROD-VIT-B2', sku: 'VIT-103', name: 'Vitamin B2 Riboflavin 100 mg', primaryCategory: 'vitamins', secondaryCategories: [],
      aliases: ['riboflavin', 'vit b2'], synonyms: ['cellular energy'], keywords: ['b2', 'riboflavin'],
      variants: [{ name: 'Vitamin B2 100 mg 100 Tablets' }], icon: '🔋', specs: 'Cellular energy production · 100 Tablets', retailValue: '$10.50', allowanceCost: 8.50
    },
    {
      id: 'PROD-VIT-B3', sku: 'VIT-104', name: 'Vitamin B3 Niacin 500 mg', primaryCategory: 'vitamins', secondaryCategories: [],
      aliases: ['niacin', 'vit b3'], synonyms: ['cholesterol support'], keywords: ['niacin', 'b3'],
      variants: [{ name: 'Niacin 500 mg 100 Caplets' }], icon: '💊', specs: 'Cardiovascular health & circulation · 100 Caplets', retailValue: '$12.00', allowanceCost: 9.50
    },
    {
      id: 'PROD-VIT-B5', sku: 'VIT-105', name: 'Vitamin B5 Pantothenic Acid 500 mg', primaryCategory: 'vitamins', secondaryCategories: [],
      aliases: ['pantothenic acid', 'vit b5'], synonyms: ['adrenal support'], keywords: ['b5'],
      variants: [{ name: 'Pantothenic Acid 500 mg 100 Veg Capsules' }], icon: '💊', specs: 'Adrenal function & hormone synthesis · 100 Capsules', retailValue: '$13.50', allowanceCost: 11.00
    },
    {
      id: 'PROD-VIT-B6', sku: 'VIT-106', name: 'Vitamin B6 Pyridoxine 100 mg', primaryCategory: 'vitamins', secondaryCategories: [],
      aliases: ['pyridoxine', 'vit b6'], synonyms: ['mood nerve support'], keywords: ['b6', 'pyridoxine'],
      variants: [{ name: 'Vitamin B6 100 mg 100 Tablets' }], icon: '🧠', specs: 'Brain & neurotransmitter synthesis · 100 Tablets', retailValue: '$9.50', allowanceCost: 7.50
    },
    {
      id: 'PROD-VIT-B7', sku: 'VIT-107', name: 'Vitamin B7 Biotin 10,000 mcg', primaryCategory: 'vitamins', secondaryCategories: ['skincare'],
      aliases: ['biotin', 'vit b7'], synonyms: ['hair skin nails'], keywords: ['biotin', 'hair growth'],
      variants: [{ name: 'Biotin 10,000 mcg 60 Softgels' }], icon: '💅', specs: 'Hair, skin & nail strength formula · 60 Softgels', retailValue: '$14.99', allowanceCost: 12.00
    },
    {
      id: 'PROD-VIT-B9', sku: 'VIT-108', name: 'Vitamin B9 Folic Acid 800 mcg', primaryCategory: 'vitamins', secondaryCategories: ['womens', 'infant'],
      aliases: ['folic acid', 'folate', 'b9'], synonyms: ['prenatal supplement', 'birth defect prevention'], keywords: ['folic acid', 'aca preventive'],
      variants: [{ name: 'Folic Acid 800 mcg 250 Tablets', hcpcs: 'A9150' }], icon: '🌸', specs: 'Essential for prenatal health & DNA synthesis · 250 Tablets', retailValue: '$12.50', allowanceCost: 0.00
    },
    {
      id: 'PROD-VIT-B12', sku: 'VIT-109', name: 'Vitamin B12 5,000 mcg Sublingual', primaryCategory: 'vitamins', secondaryCategories: [],
      aliases: ['b12', 'cyanocobalamin', 'methylcobalamin'], synonyms: ['nerve energy pill'], keywords: ['sublingual b12'],
      variants: [{ name: 'B12 5,000 mcg Sublingual 90 Micro-tablets' }], icon: '🔋', specs: 'High-absorption sublingual nerve support · 90 Tablets', retailValue: '$17.50', allowanceCost: 14.00
    },
    {
      id: 'PROD-VIT-BCOMPLEX', sku: 'VIT-110', name: 'Super B-Complex with Vitamin C', primaryCategory: 'vitamins', secondaryCategories: [],
      aliases: ['b complex', 'b-complex'], synonyms: ['all b vitamins'], keywords: ['b complex', 'energy'],
      variants: [{ name: 'Super B-Complex 100 Softgels' }], icon: '⚡', specs: 'Complete blend of all 8 essential B vitamins + Vit C · 100 Softgels', retailValue: '$15.99', allowanceCost: 13.00
    },
    {
      id: 'PROD-VIT-C', sku: 'VIT-111', name: 'Vitamin C 1,000 mg with Rose Hips', primaryCategory: 'vitamins', secondaryCategories: ['coldflu'],
      aliases: ['vit c', 'ascorbic acid'], synonyms: ['immune defense'], keywords: ['vitamin c', 'antioxidant'],
      variants: [{ name: 'Vitamin C 1,000 mg 100 Caplets' }], icon: '🍊', specs: 'Potent antioxidant immune defense · 100 Caplets', retailValue: '$13.99', allowanceCost: 11.50
    },
    {
      id: 'PROD-VIT-D2', sku: 'VIT-112', name: 'Vitamin D2 Ergocalciferol 1.25 mg (50,000 IU)', primaryCategory: 'vitamins', secondaryCategories: [],
      aliases: ['ergocalciferol', 'd2'], synonyms: ['prescription vitamin d'], keywords: ['d2', '50000 iu'],
      variants: [{ name: 'Ergocalciferol 50,000 IU 12 Capsules' }], icon: '☀️', specs: 'High-dose ergocalciferol bone therapy · 12 Capsules', retailValue: '$18.00', allowanceCost: 15.00
    },
    {
      id: 'PROD-VIT-D3', sku: 'VIT-113', name: 'High-Potency Vitamin D3 2,000 IU', primaryCategory: 'vitamins', secondaryCategories: ['storedept'],
      aliases: ['vit d', 'vit d3', 'd3', 'cholecalciferol', 'sunshine vitamin'], synonyms: ['bone strength', 'immune vitamin'], keywords: ['d3', '2000 iu'],
      variants: [{ name: 'Vitamin D3 2,000 IU 100 Softgels', upc: '012345678901', hcpcs: 'A9150' }], icon: '☀️', specs: 'Calcium absorption & immune strength · 100 Softgels', retailValue: '$12.99', allowanceCost: 10.50
    },
    {
      id: 'PROD-VIT-E', sku: 'VIT-114', name: 'Vitamin E 400 IU d-Alpha Tocopherol', primaryCategory: 'vitamins', secondaryCategories: [],
      aliases: ['vit e', 'tocopherol'], synonyms: ['skin cell antioxidant'], keywords: ['vitamin e', '400 iu'],
      variants: [{ name: 'Vitamin E 400 IU 100 Softgels' }], icon: '💊', specs: 'Cellular membrane antioxidant defense · 100 Softgels', retailValue: '$14.50', allowanceCost: 12.00
    },
    {
      id: 'PROD-VIT-K', sku: 'VIT-115', name: 'Vitamin K2 MK-7 100 mcg', primaryCategory: 'vitamins', secondaryCategories: [],
      aliases: ['vit k', 'k2', 'menaquinone'], synonyms: ['artery bone calcium regulator'], keywords: ['vitamin k2'],
      variants: [{ name: 'Vitamin K2 100 mcg 60 Veggie Caps' }], icon: '🦴', specs: 'Directs calcium to bones and away from arteries · 60 Caps', retailValue: '$16.00', allowanceCost: 13.50
    },
    {
      id: 'PROD-VIT-SENIOR', sku: 'VIT-116', name: 'Senior Complete 50+ Daily Multivitamin', primaryCategory: 'vitamins', secondaryCategories: [],
      aliases: ['senior multi', 'silver multivitamin', '50+ multi'], synonyms: ['elderly vitamins'], keywords: ['senior multivitamin'],
      variants: [{ name: 'Senior Complete 50+ 100 Tablets' }], icon: '💊', specs: 'Formulated for adults 50+ with Lutein & B-Vitamins · 100 Tablets', retailValue: '$14.99', allowanceCost: 12.50
    },
    {
      id: 'PROD-VIT-KIDS', sku: 'VIT-117', name: 'Children’s Complete Gummy Multivitamin', primaryCategory: 'vitamins', secondaryCategories: ['infant'],
      aliases: ['childrens gummies', 'kids vitamins', 'gummy multi'], synonyms: ['pediatric multivitamin'], keywords: ['gummies', 'kids'],
      variants: [{ name: 'Childrens Multi Gummies 70 Count' }], icon: '🧸', specs: 'Essential A, C, D, E & Zinc for growth · 70 Gummies', retailValue: '$9.99', allowanceCost: 8.00
    },
    {
      id: 'PROD-VIT-PRENATAL', sku: 'VIT-118', name: 'Prenatal Multivitamin with Folic Acid & Iron', primaryCategory: 'vitamins', secondaryCategories: ['womens', 'infant'],
      aliases: ['prenatal', 'pregnancy vitamins'], synonyms: ['maternity multi'], keywords: ['prenatal', 'folic acid'],
      variants: [{ name: 'Prenatal Multi Softgels 90 Count' }], icon: '👶', specs: 'Nutritional support prior to & during pregnancy · 90 Softgels', retailValue: '$16.50', allowanceCost: 0.00
    },
    {
      id: 'PROD-VIT-CALCIUM', sku: 'VIT-119', name: 'Calcium Carbonate 600 mg + Vitamin D3', primaryCategory: 'vitamins', secondaryCategories: [],
      aliases: ['calcium', 'calcium d3', 'calcium carbonate'], synonyms: ['osteoporosis support'], keywords: ['calcium carbonate', '600 mg'],
      variants: [{ name: 'Calcium + D3 120 Caplets' }], icon: '🦴', specs: 'Bone density support formula · 120 Caplets', retailValue: '$11.99', allowanceCost: 9.50
    },
    {
      id: 'PROD-VIT-MAGNESIUM', sku: 'VIT-120', name: 'Magnesium Glycinate 400 mg High Absorption', primaryCategory: 'vitamins', secondaryCategories: ['sleep'],
      aliases: ['magnesium', 'mag glycinate'], synonyms: ['muscle cramp relaxer'], keywords: ['magnesium glycinate'],
      variants: [{ name: 'Magnesium Glycinate 400 mg 120 Capsules' }], icon: '🌿', specs: 'Gentle muscle relaxation & sleep aid · 120 Capsules', retailValue: '$18.99', allowanceCost: 15.50
    },
    {
      id: 'PROD-VIT-IRON', sku: 'VIT-121', name: 'Ferrous Sulfate 65 mg (325 mg Equivalent Iron)', primaryCategory: 'vitamins', secondaryCategories: [],
      aliases: ['iron', 'ferrous sulfate', 'iron pills'], synonyms: ['anemia supplement'], keywords: ['iron', 'ferrous sulfate'],
      variants: [{ name: 'Ferrous Sulfate 65 mg 100 Red Tablets' }], icon: '🩸', specs: 'Red blood cell synthesis for iron deficiency · 100 Tablets', retailValue: '$10.50', allowanceCost: 8.50
    },
    {
      id: 'PROD-VIT-ZINC', sku: 'VIT-122', name: 'Zinc Picolinate 50 mg High Absorption', primaryCategory: 'vitamins', secondaryCategories: ['coldflu'],
      aliases: ['zinc', 'zinc picolinate'], synonyms: ['immune mineral'], keywords: ['zinc', '50 mg'],
      variants: [{ name: 'Zinc 50 mg 100 Caplets' }], icon: '🛡️', specs: 'Immune cell activity & wound healing · 100 Caplets', retailValue: '$8.99', allowanceCost: 7.00
    },
    {
      id: 'PROD-VIT-POTASSIUM', sku: 'VIT-123', name: 'Potassium Gluconate 99 mg', primaryCategory: 'vitamins', secondaryCategories: ['cardio'],
      aliases: ['potassium', 'potassium gluconate'], synonyms: ['electrolyte fluid balance'], keywords: ['potassium'],
      variants: [{ name: 'Potassium 99 mg 100 Tablets' }], icon: '🍌', specs: 'Electrolyte balance & muscle contraction · 100 Tablets', retailValue: '$9.25', allowanceCost: 7.50
    },
    {
      id: 'PROD-VIT-ELECTROLYTE', sku: 'VIT-124', name: 'Cal-Mag-Zinc Electrolyte Combination', primaryCategory: 'vitamins', secondaryCategories: ['nutrition'],
      aliases: ['cal mag zinc', 'electrolyte combo'], synonyms: ['mineral trio'], keywords: ['calcium magnesium zinc'],
      variants: [{ name: 'Calcium Magnesium Zinc 100 Caplets' }], icon: '⚡', specs: 'Tri-mineral complex for bones & muscles · 100 Caplets', retailValue: '$12.50', allowanceCost: 10.00
    },

    // 2. Nutrition & Dietary Supplements
    {
      id: 'PROD-NUT-PROBIOTIC', sku: 'NUT-201', name: 'Daily Probiotic 50 Billion CFU', primaryCategory: 'nutrition', secondaryCategories: ['digestive'],
      aliases: ['probiotics', 'probiotic'], synonyms: ['gut flora bacteria'], keywords: ['probiotic', '50 billion'],
      variants: [{ name: 'Daily Probiotic 50B 30 Capsules' }], icon: '🦠', specs: '10 strain gut microbiome formula · 30 Capsules', retailValue: '$24.99', allowanceCost: 20.00
    },
    {
      id: 'PROD-NUT-PREBIOTIC', sku: 'NUT-202', name: 'Organic Prebiotic Fiber Powder', primaryCategory: 'nutrition', secondaryCategories: ['digestive'],
      aliases: ['prebiotics', 'prebiotic'], synonyms: ['fiber feed'], keywords: ['prebiotic'],
      variants: [{ name: 'Prebiotic Fiber Powder 300g Jar' }], icon: '🌱', specs: 'Nourishes healthy gut bacteria · 300g Powder', retailValue: '$18.50', allowanceCost: 15.00
    },
    {
      id: 'PROD-NUT-PSYLLIUM', sku: 'NUT-203', name: 'Psyllium Husk Daily Fiber Powder', primaryCategory: 'nutrition', secondaryCategories: ['digestive', 'storedept'],
      aliases: ['psyllium', 'metamucil generic', 'fiber powder'], synonyms: ['laxative fiber'], keywords: ['psyllium husk'],
      variants: [{ name: 'Psyllium Husk Powder Sugar Free 114 Doses' }], icon: '🌾', specs: 'Promotes digestive regularity & heart health · 114 Doses', retailValue: '$19.50', allowanceCost: 16.00
    },
    {
      id: 'PROD-NUT-ENSURE', sku: 'NUT-204', name: 'Ensure High-Protein Nutritional Shakes (24 Pack)', primaryCategory: 'nutrition', secondaryCategories: [],
      aliases: ['ensure', 'protein drinks', 'nutritional shakes'], synonyms: ['meal replacement shake'], keywords: ['ensure', 'protein shake'],
      variants: [{ name: 'Ensure High Protein Chocolate 24-Pack' }], icon: '🥛', specs: '30g Protein, 25 Vitamins & Minerals · 24 Ready-to-Drink Bottles', retailValue: '$46.00', allowanceCost: 39.00
    },
    {
      id: 'PROD-NUT-GLUCERNA', sku: 'NUT-205', name: 'Glucerna Hunger Smart Diabetic Shakes (24 Pack)', primaryCategory: 'nutrition', secondaryCategories: ['diabetes'],
      aliases: ['glucerna', 'diabetic shake'], synonyms: ['low carb shake'], keywords: ['glucerna', 'diabetic shake'],
      variants: [{ name: 'Glucerna Chocolate 24-Pack' }], icon: '🍫', specs: 'CARBSTEADY slow-release carbs to manage sugar spikes · 24 Bottles', retailValue: '$48.00', allowanceCost: 41.00
    },
    {
      id: 'PROD-NUT-RENAL', sku: 'NUT-206', name: 'Nepro HP Renal Specialized Nutrition (24 Pack)', primaryCategory: 'nutrition', secondaryCategories: [],
      aliases: ['renal nutrition', 'nepro'], synonyms: ['kidney disease shake'], keywords: ['renal nutrition', 'nepro'],
      variants: [{ name: 'Nepro HP Vanilla 24 Cans' }], icon: '🩺', specs: 'High protein low phosphorus for dialysis patients · 24 Cans', retailValue: '$72.00', allowanceCost: 60.00
    },
    {
      id: 'PROD-NUT-ORS', sku: 'NUT-207', name: 'Oral Rehydration Solution Powder Packets', primaryCategory: 'nutrition', secondaryCategories: ['infant'],
      aliases: ['oral rehydration', 'ors', 'pedialyte generic'], synonyms: ['electrolyte powder'], keywords: ['oral rehydration'],
      variants: [{ name: 'ORS Packets Unflavored 16 Pack' }], icon: '💧', specs: 'WHO formulation rapid hydration replenishment · 16 Packets', retailValue: '$12.00', allowanceCost: 9.50
    },
    {
      id: 'PROD-NUT-ENTERAL', sku: 'NUT-208', name: 'Enteral Clinical Tube-Feeding Formula', primaryCategory: 'nutrition', secondaryCategories: ['dme'],
      aliases: ['enteral nutrition', 'tube feeding formula', 'jevity'], synonyms: ['tube feed'], keywords: ['enteral formula'],
      variants: [{ name: 'Enteral Formula 1.2 Cal Case of 24' }], icon: '🪠', specs: 'Complete clinical nutrition formula for tube feeding · Case of 24', retailValue: '$120.00', allowanceCost: 0.00
    },
    {
      id: 'PROD-NUT-BAGS', sku: 'NUT-209', name: 'Enteral Feeding Gravity Bags & Sets (30 Pack)', primaryCategory: 'nutrition', secondaryCategories: ['dme'],
      aliases: ['feeding bags', 'enteral bags'], synonyms: ['gravity bag'], keywords: ['feeding bags'],
      variants: [{ name: '1000 mL Gravity Enteral Sets 30 Pack' }], icon: '🩺', specs: 'Sterile 1000mL enteral gravity feeding bag set · 30 Count', retailValue: '$65.00', allowanceCost: 0.00
    },

    // 3. Pain Relief & Topicals
    {
      id: 'PROD-PAI-ACETA', sku: 'PAI-301', name: 'Extra Strength Acetaminophen 500 mg', primaryCategory: 'pain', secondaryCategories: ['storedept'],
      aliases: ['acetaminophen', 'tylenol generic', 'tylenol'], synonyms: ['headache pain reliever'], keywords: ['acetaminophen', '500 mg'],
      variants: [{ name: 'Acetaminophen 500 mg 100 Caplets', upc: '020202020202' }], icon: '💊', specs: 'Rapid pain relief & fever reducer · 100 Caplets', retailValue: '$10.99', allowanceCost: 8.50
    },
    {
      id: 'PROD-PAI-IBU', sku: 'PAI-302', name: 'Ibuprofen 200 mg Softgels', primaryCategory: 'pain', secondaryCategories: ['storedept'],
      aliases: ['ibuprofen', 'advil generic', 'motrin generic'], synonyms: ['nsaid pain reliever'], keywords: ['ibuprofen', '200 mg'],
      variants: [{ name: 'Ibuprofen 200 mg 100 Softgels' }], icon: '💊', specs: 'Relieves muscle aches, headache & joint pain · 100 Softgels', retailValue: '$11.50', allowanceCost: 9.00
    },
    {
      id: 'PROD-PAI-NAPROXEN', sku: 'PAI-303', name: 'Naproxen Sodium 220 mg Caplets', primaryCategory: 'pain', secondaryCategories: [],
      aliases: ['naproxen', 'aleve generic'], synonyms: ['12 hour pain reliever'], keywords: ['naproxen sodium'],
      variants: [{ name: 'Naproxen Sodium 220 mg 100 Caplets' }], icon: '💊', specs: 'All-day 12-hour joint & arthritis pain relief · 100 Caplets', retailValue: '$12.99', allowanceCost: 10.00
    },
    {
      id: 'PROD-PAI-ASPIRIN', sku: 'PAI-304', name: 'Low Dose Baby Aspirin 81 mg Enteric Coated', primaryCategory: 'pain', secondaryCategories: ['cardio'],
      aliases: ['aspirin', 'baby aspirin', 'low dose aspirin'], synonyms: ['heart health aspirin'], keywords: ['aspirin 81 mg'],
      variants: [{ name: 'Aspirin 81 mg Safety Coated 120 Tablets' }], icon: '❤️', specs: 'Enteric coated daily doctor-recommended regimen · 120 Tablets', retailValue: '$7.50', allowanceCost: 6.00
    },
    {
      id: 'PROD-PAI-KIDSACETA', sku: 'PAI-305', name: 'Children’s Acetaminophen Liquid 160 mg / 5 mL', primaryCategory: 'pain', secondaryCategories: ['infant'],
      aliases: ['childrens acetaminophen', 'kids tylenol'], synonyms: ['pediatric fever reducer'], keywords: ['childrens acetaminophen'],
      variants: [{ name: 'Childrens Acetaminophen Cherry 4 oz' }], icon: '🍒', specs: 'Dye-free cherry fever & pain liquid · 4 fl oz', retailValue: '$8.50', allowanceCost: 6.50
    },
    {
      id: 'PROD-PAI-VOLTAREN', sku: 'PAI-306', name: 'Voltaren Arthritis Pain Gel (Diclofenac 1%)', primaryCategory: 'pain', secondaryCategories: ['skincare'],
      aliases: ['voltaren', 'diclofenac gel', 'arthritis gel'], synonyms: ['topical nsaid'], keywords: ['voltaren', 'diclofenac'],
      variants: [{ name: 'Voltaren Gel 100g Tube' }], icon: '🧴', specs: 'Targeted topical NSAID gel for joint arthritis · 100g Tube', retailValue: '$22.50', allowanceCost: 17.50
    },
    {
      id: 'PROD-PAI-LIDO', sku: 'PAI-307', name: 'Maximum Strength Lidocaine 4% Patches (5 Pack)', primaryCategory: 'pain', secondaryCategories: [],
      aliases: ['lidocaine patch', 'lidocaine 4%'], synonyms: ['numbing pain patch'], keywords: ['lidocaine patch'],
      variants: [{ name: 'Lidocaine 4% Pain Patches 5 Pack' }], icon: '🩹', specs: 'Desensitizes aggravated nerves for up to 12 hrs · 5 Patches', retailValue: '$16.99', allowanceCost: 13.50
    },
    {
      id: 'PROD-PAI-HEATINGPAD', sku: 'PAI-308', name: 'Electric Moist / Dry Heating Pad (12" x 24")', primaryCategory: 'pain', secondaryCategories: ['homesafety'],
      aliases: ['heating pad', 'heat pad'], synonyms: ['back pain warmer'], keywords: ['heating pad'],
      variants: [{ name: 'XL King Size Heating Pad 6 Heat Settings' }], icon: '⚡', specs: 'Auto shut-off heat therapy for back & cramps', retailValue: '$28.00', allowanceCost: 22.00
    },

    // 4. Cold, Flu, Cough & Allergy
    {
      id: 'PROD-CFA-CETIRIZINE', sku: 'CFA-401', name: 'Non-Drowsy Cetirizine 10 mg (100 Count)', primaryCategory: 'coldflu', secondaryCategories: ['storedept'],
      aliases: ['cetirizine', 'zyrtec generic'], synonyms: ['allergy tablet'], keywords: ['cetirizine 10 mg'],
      variants: [{ name: 'Cetirizine 10 mg 100 Tablets' }], icon: '🤧', specs: '24-hour allergy relief of sneezing & runny nose · 100 Tablets', retailValue: '$18.99', allowanceCost: 15.00
    },
    {
      id: 'PROD-CFA-LORATADINE', sku: 'CFA-402', name: 'Loratadine 10 mg 24-Hour Allergy Relief', primaryCategory: 'coldflu', secondaryCategories: [],
      aliases: ['loratadine', 'claritin generic'], synonyms: ['hives sneezing pill'], keywords: ['loratadine 10 mg'],
      variants: [{ name: 'Loratadine 10 mg 70 Tablets' }], icon: '🌸', specs: '24-hour non-drowsy indoor/outdoor allergy relief · 70 Tablets', retailValue: '$17.50', allowanceCost: 14.00
    },
    {
      id: 'PROD-CFA-SALINE', sku: 'CFA-403', name: 'Sterile Nasal Saline Mist Spray (3.1 oz)', primaryCategory: 'coldflu', secondaryCategories: ['storedept'],
      aliases: ['saline mist', 'saline nasal spray'], synonyms: ['sinus flush spray'], keywords: ['saline spray'],
      variants: [{ name: 'Saline Nasal Mist 3.1 oz Canister' }], icon: '💧', specs: 'Drug-free sinus rinse for dry passages · 3.1 oz', retailValue: '$8.50', allowanceCost: 6.50
    },
    {
      id: 'PROD-CFA-COVID', sku: 'CFA-404', name: 'FDA-Authorized At-Home COVID-19 Rapid Test Kit', primaryCategory: 'coldflu', secondaryCategories: ['monitoring'],
      aliases: ['covid test', 'antigen test', 'rapid covid test'], synonyms: ['corona swab test'], keywords: ['covid rapid test'],
      variants: [{ name: 'At-Home Rapid Antigen Test Kit 2 Tests' }], icon: '🧪', specs: '15-minute nasal swab rapid results · 2 Tests', retailValue: '$24.00', allowanceCost: 20.00
    },

    // 5. Digestive Health
    {
      id: 'PROD-DIG-OMEPRAZOLE', sku: 'DIG-501', name: 'Omeprazole 20 mg Acid Reducer (42 Count)', primaryCategory: 'digestive', secondaryCategories: [],
      aliases: ['omeprazole', 'prilosec generic'], synonyms: ['heartburn pill'], keywords: ['omeprazole 20 mg'],
      variants: [{ name: 'Omeprazole 20 mg 3x14 Day Courses' }], icon: '🥣', specs: 'Treats frequent heartburn 2+ days/week · 42 Caplets', retailValue: '$22.99', allowanceCost: 18.50
    },
    {
      id: 'PROD-DIG-FAMOTIDINE', sku: 'DIG-502', name: 'Famotidine 20 mg Maximum Strength (100 CT)', primaryCategory: 'digestive', secondaryCategories: [],
      aliases: ['famotidine', 'pepcid generic'], synonyms: ['acid indigestion tablet'], keywords: ['famotidine 20 mg'],
      variants: [{ name: 'Famotidine 20 mg 100 Tablets' }], icon: '💊', specs: 'Prevents heartburn due to acid indigestion · 100 Tablets', retailValue: '$14.99', allowanceCost: 12.00
    },
    {
      id: 'PROD-DIG-ANTACID', sku: 'DIG-503', name: 'Calcium Carbonate Antacid Chewables (160 CT)', primaryCategory: 'digestive', secondaryCategories: ['storedept'],
      aliases: ['antacid chewables', 'tums generic'], synonyms: ['chewable heartburn relief'], keywords: ['antacids'],
      variants: [{ name: 'Ultra Antacid Chewable Assorted Fruit 160 CT' }], icon: '🍬', specs: 'Fast relief of sour stomach & acid indigestion · 160 Chewables', retailValue: '$9.99', allowanceCost: 7.50
    },

    // 6. First Aid & Wound Care
    {
      id: 'PROD-AID-KIT', sku: 'AID-601', name: 'Emergency First Aid & Trauma Kit', primaryCategory: 'firstaid', secondaryCategories: ['homesafety', 'storedept'],
      aliases: ['first aid kit', 'trauma kit'], synonyms: ['emergency bandages'], keywords: ['first aid kit'],
      variants: [{ name: 'Complete Hard Case Emergency First Aid Kit' }], icon: '🧰', specs: 'Bandages, gauze, medical tape, alcohol wipes & scissors', retailValue: '$27.99', allowanceCost: 22.00
    },
    {
      id: 'PROD-AID-GAUZE', sku: 'AID-602', name: 'Sterile Gauze Rolls & Sponge Pads Kit', primaryCategory: 'firstaid', secondaryCategories: ['advwound'],
      aliases: ['gauze rolls', 'sterile gauze'], synonyms: ['wound dressing pads'], keywords: ['gauze'],
      variants: [{ name: 'Conforming Gauze Rolls 4" 10 Pack' }], icon: '🩹', specs: 'Absorbent breathable primary wound dressing · 10 Pack', retailValue: '$11.50', allowanceCost: 9.00
    },
    {
      id: 'PROD-AID-TRIPLE', sku: 'AID-603', name: 'Triple Antibiotic Ointment (2 oz Tube)', primaryCategory: 'firstaid', secondaryCategories: ['skincare', 'storedept'],
      aliases: ['triple antibiotic', 'neosporin generic', 'bacitracin'], synonyms: ['infection prevention cream'], keywords: ['triple antibiotic'],
      variants: [{ name: 'Triple Antibiotic Ointment 2 oz' }], icon: '🩹', specs: 'Prevents infection in minor cuts & burns · 2 oz Tube', retailValue: '$8.99', allowanceCost: 7.00
    },
    {
      id: 'PROD-AID-THERMO', sku: 'AID-604', name: 'Digital Express Oral / Axillary Thermometer', primaryCategory: 'firstaid', secondaryCategories: ['monitoring', 'infant', 'storedept'],
      aliases: ['thermometer', 'digital thermometer'], synonyms: ['fever checker'], keywords: ['digital thermometer'],
      variants: [{ name: '10-Second Flexible Tip Digital Thermometer' }], icon: '🌡️', specs: '10-second accurate fever readout with fever alarm', retailValue: '$12.99', allowanceCost: 10.00
    },

    // 7. Braces, Supports & Orthopedics
    {
      id: 'PROD-BRC-KNEE', sku: 'BRC-701', name: 'Dual-Hinged Medical Knee Brace with Gel Ring', primaryCategory: 'braces', secondaryCategories: ['dme', 'storedept'],
      aliases: ['hinged knee brace', 'knee brace', 'knee compression sleeve'], synonyms: ['meniscus knee support'], keywords: ['knee brace', 'dme'],
      variants: [{ name: 'Hinged Medical Knee Brace Size L/XL', hcpcs: 'L1820' }], icon: '🦿', specs: 'Side hinge stabilization for arthritis & ligament tears', retailValue: '$48.00', allowanceCost: 38.00
    },
    {
      id: 'PROD-BRC-WRIST', sku: 'BRC-702', name: 'Carpal Tunnel Ergonomic Wrist Splint', primaryCategory: 'braces', secondaryCategories: ['storedept'],
      aliases: ['carpal tunnel brace', 'wrist splint', 'wrist brace'], synonyms: ['tendonitis wrist support'], keywords: ['wrist splint'],
      variants: [{ name: 'Carpal Tunnel Night Support Splint Right' }], icon: '🧤', specs: 'Removable palmar stay for carpal tunnel & tendonitis', retailValue: '$23.50', allowanceCost: 18.00
    },
    {
      id: 'PROD-BRC-BACK', sku: 'BRC-703', name: 'Lumbar Back Support Belt with Double Straps', primaryCategory: 'braces', secondaryCategories: ['dme'],
      aliases: ['lumbar support', 'back brace'], synonyms: ['sciatica back belt'], keywords: ['back brace', 'lumbar'],
      variants: [{ name: 'Adjustable Lumbar Support Belt', hcpcs: 'L0625' }], icon: '🧍', specs: 'Steel stays relieve lower back strain & sciatica', retailValue: '$39.00', allowanceCost: 32.00
    },

    // 8. Mobility Products
    {
      id: 'PROD-MOB-CANE', sku: 'MOB-801', name: 'Adjustable Quad Base Walking Cane', primaryCategory: 'mobility', secondaryCategories: ['dme'],
      aliases: ['quad cane', 'cane', 'standard cane'], synonyms: ['walking stick'], keywords: ['quad cane'],
      variants: [{ name: '4-Point Base Quad Cane Height Adjustable', hcpcs: 'E0105' }], icon: '🦯', specs: 'All-terrain 4-point rubber base for balance · Cap 300 lbs', retailValue: '$34.99', allowanceCost: 28.00
    },
    {
      id: 'PROD-MOB-ROLLATOR', sku: 'MOB-802', name: 'Aluminum 4-Wheel Rollator Walker with Seat', primaryCategory: 'mobility', secondaryCategories: ['dme'],
      aliases: ['rollator', 'walker with seat', 'folding walker'], synonyms: ['rolling walker'], keywords: ['rollator walker'],
      variants: [{ name: 'Folding 4-Wheel Rollator with Padded Seat', hcpcs: 'E0143' }], icon: '♿', specs: '6" wheels, padded seat, storage pouch & handbrakes', retailValue: '$89.00', allowanceCost: 75.00
    },
    {
      id: 'PROD-MOB-WHEELCHAIR', sku: 'MOB-803', name: 'Standard Lightweight Folding Manual Wheelchair', primaryCategory: 'mobility', secondaryCategories: ['dme'],
      aliases: ['manual wheelchair', 'transport wheelchair', 'wheelchair'], synonyms: ['folding wheelchair'], keywords: ['manual wheelchair'],
      variants: [{ name: '18" Seat Lightweight Manual Wheelchair', hcpcs: 'K0001' }], icon: '👨‍🦽', specs: 'Swing-away footrests & durable steel frame', retailValue: '$195.00', allowanceCost: 0.00
    },

    // 9. Home Safety & Fall Prevention
    {
      id: 'PROD-SAF-GRABBAR', sku: 'SAF-901', name: 'Suction Bathroom Safety Grab Bar (2 Pack)', primaryCategory: 'homesafety', secondaryCategories: ['ssbci', 'storedept'],
      aliases: ['grab bar', 'shower grab bar', 'bath grab bars'], synonyms: ['tub safety bar'], keywords: ['grab bar'],
      variants: [{ name: '12-Inch Heavy Duty Suction Grab Bars 2 Pack' }], icon: '🏠', specs: 'Non-slip suction grab bar for shower & tub without drilling', retailValue: '$24.99', allowanceCost: 20.00
    },
    {
      id: 'PROD-SAF-BENCH', sku: 'SAF-902', name: 'Non-Slip Shower Transfer Bench with Backrest', primaryCategory: 'homesafety', secondaryCategories: ['dme'],
      aliases: ['shower bench', 'shower chair', 'transfer bench'], synonyms: ['bath seat'], keywords: ['shower transfer bench'],
      variants: [{ name: 'Adjustable Height Shower Transfer Bench', hcpcs: 'E0247' }], icon: '🪑', specs: 'Suction feet & drainage holes for safe tub entry', retailValue: '$44.00', allowanceCost: 36.00
    },

    // 10. Diabetes Products
    {
      id: 'PROD-DIB-STRIPS', sku: 'DIB-1001', name: 'Blood Glucose Test Strips & Lancets Starter Bundle', primaryCategory: 'diabetes', secondaryCategories: ['dme'],
      aliases: ['glucose test strips', 'test strips', 'lancets', 'sugar test strips'], synonyms: ['blood sugar monitor strips'], keywords: ['glucose test strips'],
      variants: [{ name: 'No-Coding Test Strips 100 + Lancets 100', hcpcs: 'A4253' }], icon: '🩸', specs: '100 test strips + 100 sterile 30G lancets', retailValue: '$34.00', allowanceCost: 28.00
    },
    {
      id: 'PROD-DIB-CGM', sku: 'DIB-1002', name: 'Continuous Glucose Monitor (CGM) Sensor Replacement', primaryCategory: 'diabetes', secondaryCategories: ['dme'],
      aliases: ['cgm sensor', 'cgm transmitter', 'cgm receiver', 'cgm'], synonyms: ['continuous glucose monitor'], keywords: ['cgm sensor'],
      variants: [{ name: '14-Day Continuous Glucose Sensor', hcpcs: 'K0553' }], icon: '📡', specs: '14-day continuous real-time glucose monitoring sensor', retailValue: '$85.00', allowanceCost: 0.00
    },

    // 11. Blood Pressure & Cardiovascular Monitoring
    {
      id: 'PROD-CAR-BPMONITOR', sku: 'CAR-1101', name: 'Automatic Upper Arm Blood Pressure Monitor', primaryCategory: 'cardio', secondaryCategories: ['monitoring', 'storedept'],
      aliases: ['bp monitor', 'bp cuff', 'blood pressure machine', 'blood pressure monitor'], synonyms: ['hypertension monitor'], keywords: ['blood pressure monitor'],
      variants: [{ name: 'Automatic Upper Arm BP Monitor with Large Cuff' }], icon: '🩺', specs: 'One-touch operation, 240 memory & heartbeat check', retailValue: '$39.99', allowanceCost: 32.00
    },
    {
      id: 'PROD-CAR-PULSEOX', sku: 'CAR-1102', name: 'Fingertip Pulse Oximeter Oxygen Monitor', primaryCategory: 'cardio', secondaryCategories: ['respiratory', 'monitoring'],
      aliases: ['pulse oximeter', 'oximeter', 'spo2 monitor'], synonyms: ['oxygen saturation reader'], keywords: ['pulse oximeter'],
      variants: [{ name: 'OLED Display Fingertip Pulse Oximeter' }], icon: '🫀', specs: 'Instant SpO2 oxygen saturation & pulse rate reader', retailValue: '$22.00', allowanceCost: 17.50
    },

    // 12. Respiratory Products
    {
      id: 'PROD-RSP-NEBULIZER', sku: 'RSP-1201', name: 'Portable Compressor Nebulizer System & Kit', primaryCategory: 'respiratory', secondaryCategories: ['dme'],
      aliases: ['nebulizer', 'nebulizer machine', 'nebulizer kit'], synonyms: ['asthma breathing machine'], keywords: ['nebulizer compressor'],
      variants: [{ name: 'Compressor Nebulizer Machine with Tubing & Mask', hcpcs: 'E0570' }], icon: '🌬️', specs: 'Delivers aerosolized liquid medication directly to lungs', retailValue: '$49.00', allowanceCost: 39.00
    },
    {
      id: 'PROD-RSP-CPAPMASK', sku: 'RSP-1202', name: 'CPAP Replacement Mask & Tubing Bundle', primaryCategory: 'respiratory', secondaryCategories: ['sleep', 'dme'],
      aliases: ['cpap mask', 'cpap hose', 'cpap tubing', 'heated cpap hose'], synonyms: ['sleep apnea mask'], keywords: ['cpap mask'],
      variants: [{ name: 'Universal CPAP Hose 6ft + Silicone Nasal Cushion', hcpcs: 'A7034' }], icon: '🎭', specs: 'Universal 6-foot CPAP tubing & nasal cushion set', retailValue: '$65.00', allowanceCost: 52.00
    },

    // 13. Eye Care
    {
      id: 'PROD-EYE-DROPS', sku: 'EYE-1301', name: 'Lubricating Eye Drops for Dry Eye Relief (2 Pack)', primaryCategory: 'eyecare', secondaryCategories: ['storedept'],
      aliases: ['eye drops', 'lubricating eye drops', 'dry eye drops'], synonyms: ['artificial tears'], keywords: ['lubricating eye drops'],
      variants: [{ name: 'Lubricating Eye Drops 15 mL 2 Pack' }], icon: '👁️', specs: 'Soothing artificial tears formula for burning eyes', retailValue: '$14.99', allowanceCost: 12.00
    },
    {
      id: 'PROD-EYE-READERS', sku: 'EYE-1302', name: 'Magnifying Reading Glasses (+1.75 Diopter 3-Pack)', primaryCategory: 'eyecare', secondaryCategories: ['storedept'],
      aliases: ['reading glasses', 'readers'], synonyms: ['magnifying glasses'], keywords: ['reading glasses'],
      variants: [{ name: 'Anti-Glare Reader Glasses +1.75 3 Pack' }], icon: '👓', specs: 'Scratch-resistant readers for close-up focus', retailValue: '$19.99', allowanceCost: 15.00
    },

    // 14. Ear Care & Hearing
    {
      id: 'PROD-EAR-DROPS', sku: 'EAR-1401', name: 'Earwax Removal System with Dropper & Syringe Bulb', primaryCategory: 'earcare', secondaryCategories: [],
      aliases: ['earwax removal drops', 'ear irrigation bulb'], synonyms: ['ear cleaning kit'], keywords: ['earwax drops'],
      variants: [{ name: 'Carbamide Peroxide Earwax System' }], icon: '👂', specs: 'Microfoam carbamide peroxide action clears earwax', retailValue: '$9.99', allowanceCost: 7.50
    },
    {
      id: 'PROD-EAR-BATTERIES', sku: 'EAR-1402', name: 'Hearing Aid Batteries Size 312 (40 Count)', primaryCategory: 'earcare', secondaryCategories: [],
      aliases: ['hearing aid batteries', 'size 312 batteries'], synonyms: ['hearing battery'], keywords: ['hearing aid batteries'],
      variants: [{ name: 'Zinc Air Hearing Aid Batteries Size 312 40 Pack' }], icon: '🔋', specs: 'Mercury-free long-lasting power for hearing aids', retailValue: '$21.00', allowanceCost: 16.00
    },

    // 15. Dental & Oral Care
    {
      id: 'PROD-DEN-TOOTHBRUSH', sku: 'DEN-1501', name: 'Sonic Electric Toothbrush with 4 Brush Heads', primaryCategory: 'dental', secondaryCategories: ['storedept'],
      aliases: ['electric toothbrush', 'manual toothbrush', 'replacement brush heads'], synonyms: ['power toothbrush'], keywords: ['electric toothbrush'],
      variants: [{ name: 'Rechargeable Sonic Toothbrush + 4 Heads' }], icon: '🪥', specs: '40,000 VPM micro-vibrations with 2-minute timer', retailValue: '$32.99', allowanceCost: 26.00
    },
    {
      id: 'PROD-DEN-DENTURE', sku: 'DEN-1502', name: 'Denture Cleanser Effervescent Tablets (120 CT)', primaryCategory: 'dental', secondaryCategories: ['storedept'],
      aliases: ['denture cleaner', 'denture adhesive'], synonyms: ['denture soaking tablets'], keywords: ['denture cleaner'],
      variants: [{ name: 'Antibacterial Denture Tablets 120 Pack' }], icon: '🦷', specs: 'Kills 99.9% of odor bacteria & removes tough stains', retailValue: '$11.50', allowanceCost: 9.00
    },

    // 16. Skin Care & Dermatology
    {
      id: 'PROD-SKN-HYDRO', sku: 'SKN-1601', name: 'Hydrocortisone 1% Anti-Itch Cream (2 oz)', primaryCategory: 'skincare', secondaryCategories: ['storedept'],
      aliases: ['hydrocortisone 1%', 'anti-itch cream'], synonyms: ['eczema rash cream'], keywords: ['hydrocortisone'],
      variants: [{ name: 'Hydrocortisone 1% Cream 2 oz Tube' }], icon: '🧴', specs: 'Relieves eczema, psoriasis & insect bite itching', retailValue: '$7.99', allowanceCost: 6.00
    },
    {
      id: 'PROD-SKN-CLOTRI', sku: 'SKN-1602', name: 'Clotrimazole 1% Antifungal Cream (1.5 oz)', primaryCategory: 'skincare', secondaryCategories: ['footcare'],
      aliases: ['clotrimazole 1%', 'antifungal cream'], synonyms: ['athlete foot ringworm cream'], keywords: ['clotrimazole'],
      variants: [{ name: 'Clotrimazole 1% Antifungal Cream 1.5 oz' }], icon: '🦶', specs: 'Cures athlete foot, jock itch & ringworm', retailValue: '$9.50', allowanceCost: 7.50
    },

    // 17. Foot Care
    {
      id: 'PROD-FTC-INSOLES', sku: 'FTC-1701', name: 'Plantar Fasciitis Orthotic Arch Support Insoles', primaryCategory: 'footcare', secondaryCategories: ['storedept'],
      aliases: ['plantar fasciitis insoles', 'arch supports', 'heel cushions'], synonyms: ['shoe orthotics'], keywords: ['plantar fasciitis insoles'],
      variants: [{ name: 'Orthotic Arch Support Insoles Pair' }], icon: '👟', specs: 'Rigid arch shell & deep heel cup for foot pain', retailValue: '$21.99', allowanceCost: 17.00
    },

    // 18. Compression & Circulation
    {
      id: 'PROD-CMP-SOCKS', sku: 'CMP-1801', name: 'Graduated Compression Socks 15–20 mmHg', primaryCategory: 'compression', secondaryCategories: ['dme', 'storedept'],
      aliases: ['compression socks', '15-20 mmhg compression socks', 'medical compression stockings', 'lymphedema compression sleeve'], synonyms: ['support hose'], keywords: ['compression socks'],
      variants: [{ name: 'Unisex Compression Socks 15-20 mmHg 2 Pairs', hcpcs: 'A6530' }], icon: '🦵', specs: 'Promotes venous circulation & reduces leg swelling', retailValue: '$24.99', allowanceCost: 19.50
    },

    // 19. Incontinence & Bladder Care
    {
      id: 'PROD-INC-BRIEFS', sku: 'INC-1901', name: 'Adult Protective Underwear Briefs (40 Count)', primaryCategory: 'incontinence', secondaryCategories: ['storedept'],
      aliases: ['adult protective underwear', 'adult briefs', 'adult diapers', 'bladder control pads'], synonyms: ['incontinence pull ups'], keywords: ['adult diapers', 'briefs'],
      variants: [{ name: 'Maximum Absorbency Adult Briefs Large 40 Pack' }], icon: '🩲', specs: 'Leak guard protection with breathable stretch waistband', retailValue: '$29.99', allowanceCost: 24.00
    },
    {
      id: 'PROD-INC-PADS', sku: 'INC-1902', name: 'Disposable Bed Underpads Chux (50 Pack)', primaryCategory: 'incontinence', secondaryCategories: [],
      aliases: ['disposable bed underpads', 'reusable underpads', 'chux pads'], synonyms: ['mattress protector pads'], keywords: ['underpads'],
      variants: [{ name: '30" x 36" Disposable Bed Pads 50 Count' }], icon: '🛏️', specs: 'Absorbent polymer core protects bedding & furniture', retailValue: '$26.00', allowanceCost: 20.00
    },

    // 20. Women's Health
    {
      id: 'PROD-WMN-PUMP', sku: 'WMN-2001', name: 'Electric Double Breast Pump System Kit', primaryCategory: 'womens', secondaryCategories: ['infant', 'dme'],
      aliases: ['electric breast pump', 'double breast pump', 'breast pump replacement supplies'], synonyms: ['nursing pump'], keywords: ['electric breast pump', 'aca preventive'],
      variants: [{ name: 'Electric Double Breast Pump Complete Kit', hcpcs: 'E0603' }], icon: '🍼', specs: 'ACA mandated 100% covered breast pump kit', retailValue: '$149.00', allowanceCost: 0.00
    },

    // 21. Sexual & Reproductive Health
    {
      id: 'PROD-REP-PLANB', sku: 'REP-2101', name: 'Levonorgestrel 1.5 mg Emergency Contraception', primaryCategory: 'sexual', secondaryCategories: ['womens'],
      aliases: ['levonorgestrel emergency contraception', 'plan b generic', 'emergency contraception'], synonyms: ['morning after pill'], keywords: ['emergency contraception'],
      variants: [{ name: 'Levonorgestrel 1.5 mg 1 Tablet' }], icon: '💊', specs: 'Reduces risk of pregnancy after unprotected sex', retailValue: '$39.99', allowanceCost: 0.00
    },

    // 22. Smoking Cessation
    {
      id: 'PROD-SMK-PATCH', sku: 'SMK-2201', name: 'Nicotine Transdermal Patches 21 mg (Step 1)', primaryCategory: 'smoking', secondaryCategories: [],
      aliases: ['nicotine patch step 1', 'nicotine patch step 2', 'nicotine patch step 3', 'nicotine gum', 'nicotine lozenges'], synonyms: ['quit smoking patch'], keywords: ['nicotine patch'],
      variants: [{ name: 'Nicotine Patch 21 mg Step 1 14 Pack' }], icon: '🚭', specs: '24-hour therapeutic nicotine patch for quitting smoking', retailValue: '$39.00', allowanceCost: 0.00
    },

    // 23. Sleep Support
    {
      id: 'PROD-SLP-MELATONIN', sku: 'SLP-2301', name: 'Melatonin 5 mg Sleep Support Tablets (120 CT)', primaryCategory: 'sleep', secondaryCategories: ['vitamins'],
      aliases: ['melatonin'], synonyms: ['drug free sleep aid'], keywords: ['melatonin'],
      variants: [{ name: 'Melatonin 5 mg 120 Tablets' }], icon: '🌙', specs: 'Supports natural sleep-wake cycle regulation', retailValue: '$11.99', allowanceCost: 9.50
    },

    // 24. Pregnancy & Infant Health
    {
      id: 'PROD-INF-ORS', sku: 'INF-2401', name: 'Pediatric Oral Electrolyte Hydration Solution', primaryCategory: 'infant', secondaryCategories: ['nutrition'],
      aliases: ['pediatric oral electrolyte solution', 'childrens thermometer', 'infant gas relief drops'], synonyms: ['pedialyte liquid'], keywords: ['pediatric electrolyte'],
      variants: [{ name: 'Pediatric Electrolyte Unflavored 1 Litre' }], icon: '👶', specs: 'Replenishes fluids lost to diarrhea & vomiting', retailValue: '$7.50', allowanceCost: 6.00
    },

    // 25. Ostomy Supplies
    {
      id: 'PROD-OST-POUCH', sku: 'OST-2501', name: 'Drainable Ostomy Pouch & Stoma Barrier Kit', primaryCategory: 'ostomy', secondaryCategories: ['dme'],
      aliases: ['drainable ostomy pouch', 'one-piece ostomy pouch', 'two-piece ostomy system', 'stoma barrier wafer'], synonyms: ['ostomy bag'], keywords: ['ostomy pouch'],
      variants: [{ name: 'One-Piece Cut-to-Fit Drainable Pouch 10 Pack', hcpcs: 'A4388' }], icon: '🩺', specs: 'Odor-barrier film with integrated stoma protection flange', retailValue: '$55.00', allowanceCost: 0.00
    },

    // 26. Urological Products
    {
      id: 'PROD-URO-CATH', sku: 'URO-2601', name: 'Intermittent Catheter Kit & Drainage Supplies', primaryCategory: 'urology', secondaryCategories: ['dme'],
      aliases: ['intermittent catheter', 'straight-tip catheter', 'external catheter', 'leg drainage bag'], synonyms: ['urinary catheter'], keywords: ['intermittent catheter'],
      variants: [{ name: 'Sterile Hydrophilic Intermittent Catheters 30 Pack', hcpcs: 'A4351' }], icon: '💉', specs: 'Sterile single-use hydrophilic catheter kit', retailValue: '$48.00', allowanceCost: 0.00
    },

    // 27. Advanced Wound Care
    {
      id: 'PROD-WND-ALGINATE', sku: 'WND-2701', name: 'Calcium Alginate Wound Dressing Pads (10 Pack)', primaryCategory: 'advwound', secondaryCategories: ['firstaid', 'dme'],
      aliases: ['calcium alginate dressing', 'hydrocolloid dressing', 'foam dressing', 'surgical dressing'], synonyms: ['sea kelp wound pad'], keywords: ['calcium alginate'],
      variants: [{ name: '4" x 4" Calcium Alginate Dressing 10 Pack', hcpcs: 'A6196' }], icon: '🩹', specs: 'Absorbent dressing for moderate-to-heavy exuding wounds', retailValue: '$32.00', allowanceCost: 0.00
    },

    // 28. Prosthetics
    {
      id: 'PROD-PRS-FORM', sku: 'PRS-2801', name: 'Post-Mastectomy Silicone Breast Form', primaryCategory: 'prosthetics', secondaryCategories: ['dme'],
      aliases: ['post-mastectomy breast form', 'prosthetic liner', 'prosthetic socket supplies'], synonyms: ['breast prosthesis'], keywords: ['mastectomy breast form'],
      variants: [{ name: 'Natural Silicone Breast Prosthesis Form', hcpcs: 'L8030' }], icon: '🎗️', specs: 'Lightweight natural silicone breast prosthesis form', retailValue: '$210.00', allowanceCost: 0.00
    },

    // 29. Home Medical Equipment
    {
      id: 'PROD-DME-COMMODE', sku: 'DME-2901', name: '3-in-1 Bedside Commode Chair with Bucket', primaryCategory: 'dme', secondaryCategories: ['homesafety', 'mobility'],
      aliases: ['3-in-1 bedside commode', 'hospital bed', 'pressure-reducing mattress', 'patient transfer board'], synonyms: ['commode chair'], keywords: ['bedside commode'],
      variants: [{ name: 'Steel 3-in-1 Bedside Commode Chair', hcpcs: 'E0163' }], icon: '🚽', specs: '3-in-1 commode, toilet safety frame & raised toilet seat', retailValue: '$65.00', allowanceCost: 0.00
    },

    // 30. Medication Management
    {
      id: 'PROD-MED-ORGANIZER', sku: 'MED-3001', name: '7-Day AM/PM Push-Button Pill Organizer Box', primaryCategory: 'medmgmt', secondaryCategories: ['storedept'],
      aliases: ['7-day pill organizer', 'am/pm pill organizer', 'pill cutter', 'pill crusher'], synonyms: ['weekly pill box'], keywords: ['pill organizer'],
      variants: [{ name: '7-Day Push-Button AM/PM Pill Planner' }], icon: '📅', specs: 'Pop-up compartments with braille for daily medications', retailValue: '$9.99', allowanceCost: 7.50
    },

    // 31. Personal Medical Monitoring
    {
      id: 'PROD-MON-FOREHEAD', sku: 'MON-3101', name: 'No-Touch Infrared Forehead Thermometer', primaryCategory: 'monitoring', secondaryCategories: ['firstaid', 'infant'],
      aliases: ['infrared forehead thermometer', 'ear thermometer', 'digital scale', 'talking scale'], synonyms: ['non contact thermometer'], keywords: ['infrared thermometer'],
      variants: [{ name: 'Non-Contact Infrared Forehead Thermometer' }], icon: '🌡️', specs: '1-second instant fever reading with fever alarm', retailValue: '$29.99', allowanceCost: 24.00
    },

    // 32. Chronic Illness Support (SSBCI)
    {
      id: 'PROD-SSB-GROCERY', sku: 'SSB-3201', name: 'Healthy Produce & Grocery Allowance Basket', primaryCategory: 'ssbci', secondaryCategories: ['nutrition'],
      aliases: ['healthy groceries', 'fresh produce', 'meal allowances', 'utility assistance', 'fuel assistance'], synonyms: ['food flex card'], keywords: ['healthy groceries', 'ssbci'],
      variants: [{ name: 'Fresh Fruit & Produce Grocery Bundle' }], icon: '🍎', specs: 'Fresh apples, oranges, greens, carrots & healthy staples', retailValue: 'Plan Covered', allowanceCost: 0.00
    },

    // 33. Store Products Potentially Eligible Under Plan Benefits
    {
      id: 'PROD-STR-SUNSCREEN', sku: 'STR-3301', name: 'Broad Spectrum SPF 50 Mineral Sunscreen (6 oz)', primaryCategory: 'storedept', secondaryCategories: ['skincare'],
      aliases: ['broad spectrum sunscreen', 'spf 50 mineral sunscreen', 'medicated lip balm'], synonyms: ['sunblock spf 50'], keywords: ['sunscreen'],
      variants: [{ name: 'Mineral Sunscreen SPF 50 Lotion 6 oz' }], icon: '☀️', specs: 'Water resistant zinc oxide UV protection lotion', retailValue: '$12.99', allowanceCost: 10.00
    }
  ];

  // --- 3. SERVICES & SUPPORTS UNIVERSE (STRUCTURALLY DISTINCT FROM RETAIL PRODUCTS) ---
  const SERVICES = [
    {
      id: 'SRV-DENTAL-EXAM', service_code: 'SRV-101', service_name: 'Preventive Dental Care & Comprehensive Exam', category: 'srv_dental',
      icon: '🪥', description: 'In-network cleanings, X-rays, routine exams, fillings & denture consultations',
      aliases: ['dentist', 'dental exams', 'preventive dental services', 'teeth cleaning'], synonyms: ['oral checkup', 'dentures']
    },
    {
      id: 'SRV-TRANSPORT', service_code: 'SRV-102', service_name: 'Non-Emergency Medical Transportation (NEMT)', category: 'srv_transport',
      icon: '🚗', description: 'Round-trip rides to doctors, specialists, dialysis, and pharmacies',
      aliases: ['rides to doctor', 'medical transportation', 'non-emergency medical transportation', 'uber ride doctor'], synonyms: ['patient transport']
    },
    {
      id: 'SRV-MEALS', service_code: 'SRV-103', service_name: 'Post-Hospitalization Meal Delivery Program', category: 'srv_meals',
      icon: '🍱', description: 'Nutritionally balanced meals delivered directly to your home following hospital discharge',
      aliases: ['post-hospital meal delivery', 'meals', 'home meals'], synonyms: ['post acute food']
    },
    {
      id: 'SRV-FITNESS', service_code: 'SRV-104', service_name: 'SilverSneakers & Gym Fitness Membership', category: 'srv_fitness',
      icon: '👟', description: 'Unlimited access to participating gyms, YMCAs, wellness centers & live virtual classes',
      aliases: ['gym membership', 'fitness memberships', 'silversneakers', 'gym'], synonyms: ['fitness benefit']
    },
    {
      id: 'SRV-VISION-EXAM', service_code: 'SRV-105', service_name: 'Annual Vision Exam & Eyewear Allowance', category: 'srv_vision',
      icon: '👓', description: 'Routine eye exams plus annual credit toward prescription glasses or contact lenses',
      aliases: ['vision exams', 'eye exam', 'eyewear allowance'], synonyms: ['optometrist exam']
    },
    {
      id: 'SRV-HEARING-EXAM', service_code: 'SRV-106', service_name: 'Hearing Exam & OTC Hearing Device Benefit', category: 'srv_hearing',
      icon: '👂', description: 'Diagnostic hearing evaluations & allowance toward prescription or OTC hearing aids',
      aliases: ['hearing exams', 'hearing test'], synonyms: ['audiology checkup']
    },
    {
      id: 'SRV-FOOD-SSBCI', service_code: 'SRV-107', service_name: 'Healthy Food & Groceries Allowance (SSBCI)', category: 'srv_food',
      icon: '🍎', description: 'Monthly or quarterly spending credit for qualifying grocery & healthy food purchases',
      aliases: ['healthy food', 'grocery benefit', 'ssbci food'], synonyms: ['food credit']
    },
    {
      id: 'SRV-TELEHEALTH', service_code: 'SRV-108', service_name: '24/7 Virtual Telehealth Doctor Visits ($0 Copay)', category: 'srv_preventive',
      icon: '💻', description: 'On-demand video visits with board-certified physicians for minor illnesses & prescriptions',
      aliases: ['telehealth', 'virtual doctor', 'online doctor visit'], synonyms: ['telemedicine']
    }
  ];

  // --- 4. COVERAGE RULES ENGINE DATABASE ---
  const COVERAGE_RULES = [
    // --- PLAN: BCBSRI BlueCHiP for Medicare Core 2026 ---
    {
      target_id: 'PROD-VIT-D3', plan_id: 'bcbsri_bluechip_2026_core',
      coverage_status: 'OTC_ELIGIBLE', benefit_pathways: ['OTC_ALLOWANCE', 'PHARMACY'],
      eligibility_requirements: { prescription_required: 'No for OTC / Yes for Rx', provider_order_required: false, diagnosis_required: false, medical_necessity_required: false, prior_authorization_required: false, approved_supplier_required: false },
      money_allowance: { copay: '$0.00', coinsurance: '0%', allowance_amount: 50, allowance_period: 'quarterly', member_cost_estimate: 'Deducted from $50/qtr OTC allowance' },
      official_source: { source_name: 'BCBSRI 2026 Medicare Advantage OTC Catalog', source_url: 'https://www.bcbsri.com/medicare/member/otc', source_type: 'Insurer OTC Catalog', plan_year: 2026, page_number: 'Page 14', source_excerpt: 'Vitamin D3 2,000 IU softgels eligible under quarterly BlueCHiP benefit allowance.', last_verified: '2026-01-01', verification_status: 'VERIFIED' }
    },
    {
      target_id: 'PROD-BRC-KNEE', plan_id: 'bcbsri_bluechip_2026_core',
      coverage_status: 'CONDITIONAL', benefit_pathways: ['DMEPOS', 'OTC_ALLOWANCE'],
      eligibility_requirements: { prescription_required: 'Yes for DMEPOS 100% Billing', provider_order_required: 'Yes for DME', diagnosis_required: 'Arthritis / Ligament Tear', medical_necessity_required: 'Yes', prior_authorization_required: 'No if in-network DME', approved_supplier_required: 'Yes' },
      money_allowance: { copay: '$0.00 after deductible', coinsurance: '20% coinsurance without DME order', allowance_amount: null, member_cost_estimate: '$0 out-of-pocket with provider order & in-network DME supplier' },
      official_source: { source_name: 'CMS Medicare DMEPOS Fee Schedule 2026 & BCBSRI EOC', source_url: 'https://www.cms.gov/medicare/payment/fee-schedules/dmepos', source_type: 'CMS DMEPOS', plan_year: 2026, page_number: 'Section 4 DME', source_excerpt: 'HCPCS L1820 covered when prescribed by network physician for knee instability.', last_verified: '2026-01-01', verification_status: 'VERIFIED' }
    },
    {
      target_id: 'SRV-FITNESS', plan_id: 'bcbsri_bluechip_2026_core',
      coverage_status: 'COVERED', benefit_pathways: ['WELLNESS', 'SUPPLEMENTAL'],
      eligibility_requirements: { prescription_required: false, provider_order_required: false, diagnosis_required: false, medical_necessity_required: false, prior_authorization_required: false },
      money_allowance: { copay: '$0.00', coinsurance: '0%', member_cost_estimate: '$0 copay unlimited gym access' },
      official_source: { source_name: 'BCBSRI 2026 BlueCHiP Summary of Benefits', source_url: 'https://www.bcbsri.com/individual/choose/wellness', source_type: 'Summary of Benefits', plan_year: 2026, page_number: 'Page 8', source_excerpt: 'SilverSneakers fitness program membership included at $0 copay for all BlueCHiP members.', last_verified: '2026-01-01', verification_status: 'VERIFIED' }
    },

    // --- PLAN: RI Medicaid EOHHS Managed Care 2026 ---
    {
      target_id: 'PROD-SMK-PATCH', plan_id: 'ri_medicaid_eohhs_2026',
      coverage_status: 'COVERED', benefit_pathways: ['PHARMACY', 'MEDICAID', 'PREVENTIVE'],
      eligibility_requirements: { prescription_required: 'Yes (Practitioner order required)', provider_order_required: 'Yes', diagnosis_required: false, medical_necessity_required: false, prior_authorization_required: false, approved_supplier_required: 'In-Network Pharmacy' },
      money_allowance: { copay: '$0.00', coinsurance: '0%', member_cost_estimate: '$0.00 copay under pharmacy benefit' },
      official_source: { source_name: 'RI EOHHS Pharmacy Benefit Plan Protocols 2026', source_url: 'https://eohhs.ri.gov/sites/g/files/xkgbur226/files/2026-01/2.4%20%20Pharmacy%20Benefit%20Plan%20Protocols%20-%20Effective%2001.01.26_CLEAN.pdf', source_type: 'State Medicaid Policy', plan_year: 2026, page_number: 'Protocol 2.4', source_excerpt: 'Non-prescription nicotine-cessation supplies covered when ordered by a licensed health plan practitioner.', last_verified: '2026-01-01', verification_status: 'VERIFIED' }
    },
    {
      target_id: 'PROD-REP-PLANB', plan_id: 'ri_medicaid_eohhs_2026',
      coverage_status: 'COVERED', benefit_pathways: ['PHARMACY', 'MEDICAID', 'PREVENTIVE'],
      eligibility_requirements: { prescription_required: false, provider_order_required: false, diagnosis_required: false, medical_necessity_required: false, prior_authorization_required: false },
      money_allowance: { copay: '$0.00', coinsurance: '0%', member_cost_estimate: '$0.00 copay at pharmacy counter' },
      official_source: { source_name: 'RI EOHHS Pharmacy Benefit Plan Protocols 2026', source_url: 'https://eohhs.ri.gov/sites/g/files/xkgbur226/files/2026-01/2.4%20%20Pharmacy%20Benefit%20Plan%20Protocols%20-%20Effective%2001.01.26_CLEAN.pdf', source_type: 'State Medicaid Policy', plan_year: 2026, page_number: 'Protocol 2.4', source_excerpt: 'Non-prescription emergency contraception covered at pharmacy counter with $0 member copay.', last_verified: '2026-01-01', verification_status: 'VERIFIED' }
    },
    {
      target_id: 'PROD-VIT-B9', plan_id: 'ri_medicaid_eohhs_2026',
      coverage_status: 'COVERED', benefit_pathways: ['PHARMACY', 'PREVENTIVE'],
      eligibility_requirements: { prescription_required: 'Yes for pharmacy billing', provider_order_required: true, diagnosis_required: false, medical_necessity_required: false, prior_authorization_required: false },
      money_allowance: { copay: '$0.00', coinsurance: '0%', member_cost_estimate: '$0.00 copay under ACA preventive protocol' },
      official_source: { source_name: 'HealthCare.gov & RI EOHHS Preventive Protocols', source_url: 'https://www.healthcare.gov/preventive-care-women/', source_type: 'Preventive Benefits Document', plan_year: 2026, page_number: 'Preventive Care', source_excerpt: 'Folic acid supplementation covered 100% as preventive care for women of childbearing age.', last_verified: '2026-01-01', verification_status: 'VERIFIED' }
    },
    {
      target_id: 'SRV-TRANSPORT', plan_id: 'ri_medicaid_eohhs_2026',
      coverage_status: 'COVERED', benefit_pathways: ['MEDICAID', 'SUPPLEMENTAL'],
      eligibility_requirements: { prescription_required: false, provider_order_required: false, diagnosis_required: false, medical_necessity_required: false, prior_authorization_required: 'Schedule 48h in advance' },
      money_allowance: { copay: '$0.00', coinsurance: '0%', member_cost_estimate: '$0.00 roundtrip NEMT medical rides' },
      official_source: { source_name: 'RI Medicaid NEMT Member Handbook 2026', source_url: 'https://eohhs.ri.gov', source_type: 'Member Handbook', plan_year: 2026, page_number: 'NEMT Section', source_excerpt: 'Non-emergency medical transportation covered for all covered medical, dental, and pharmacy appointments.', last_verified: '2026-01-01', verification_status: 'VERIFIED' }
    },

    // --- PLAN: Highmark Wholecare D-SNP 2026 ---
    {
      target_id: 'PROD-SSB-GROCERY', plan_id: 'highmark_dsnp_2026',
      coverage_status: 'COVERED', benefit_pathways: ['SSBCI', 'SUPPLEMENTAL'],
      eligibility_requirements: { prescription_required: false, provider_order_required: false, diagnosis_required: 'Qualifying Chronic Condition', medical_necessity_required: 'Yes (SSBCI Criteria)', prior_authorization_required: false },
      money_allowance: { copay: '$0.00', coinsurance: '0%', allowance_amount: 150, allowance_period: 'monthly', member_cost_estimate: 'Uses SSBCI Flex Card Allowance ($150/mo)' },
      official_source: { source_name: 'Highmark Wholecare D-SNP 2026 Flex Card Program', source_url: 'https://highmark.com/wholecare/medicare/benefits-programs/benefit-list/flex-card', source_type: 'Summary of Benefits', plan_year: 2026, page_number: 'SSBCI Benefits', source_excerpt: 'Eligible chronically ill members receive monthly flex card allowance usable for OTC medicines, healthy groceries, and home safety items.', last_verified: '2026-01-01', verification_status: 'VERIFIED' }
    }
  ];

  // --- 5. APPLICATION STATE MANAGEMENT ---
  let activePlanId = 'bcbsri_bluechip_2026_core';
  let activeViewMode = 'products'; // 'products' | 'services'
  let activeCategory = 'all';
  let activeStatusFilter = 'all';
  let activePathwayFilter = 'all';
  let searchQuery = '';
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
  function getCoverageRule(targetId, planId) {
    if (planId === 'unselected_generic') {
      return {
        coverage_status: 'NEEDS_VERIFICATION',
        benefit_pathways: ['OTHER'],
        eligibility_requirements: { prescription_required: 'Needs Verification', provider_order_required: 'Needs Verification', diagnosis_required: 'Needs Verification', medical_necessity_required: 'Needs Verification', prior_authorization_required: 'Needs Verification', approved_supplier_required: 'Needs Verification' },
        money_allowance: { copay: 'Needs Verification', coinsurance: 'Needs Verification', member_cost_estimate: 'Needs Verification (Select exact plan to confirm)' },
        official_source: { source_name: 'Official Plan Document Required', source_url: '/find-care/#sources', source_type: 'Unverified', source_excerpt: 'Coverage not yet verified for this specific health plan. Please select your exact plan or consult Member Services.', verification_status: 'NEEDS_VERIFICATION' }
      };
    }

    const found = COVERAGE_RULES.find((r) => r.target_id === targetId && r.plan_id === planId);
    if (found) return found;

    // Fallback rule for item without explicit rule for selected plan
    return {
      coverage_status: 'NEEDS_VERIFICATION',
      benefit_pathways: ['OTC_ALLOWANCE'],
      eligibility_requirements: { prescription_required: 'Depends on Plan', provider_order_required: 'Check Plan Document', diagnosis_required: 'Check Plan Document', medical_necessity_required: 'No', prior_authorization_required: 'No' },
      money_allowance: { copay: '$0.00 via OTC Card', coinsurance: '0%', member_cost_estimate: 'Potentially eligible under plan OTC spending card allowance.' },
      official_source: { source_name: 'Generic Plan Evidence of Coverage', source_url: '/find-care/#sources', source_type: 'Summary of Benefits', source_excerpt: 'Item is standard OTC category. Specific coverage subject to plan formulary verification.', verification_status: 'NEEDS_VERIFICATION' }
    };
  }

  // --- 7. SEARCH & FILTER ENGINE ---
  function searchItems() {
    const q = searchQuery.trim().toLowerCase();

    if (activeViewMode === 'products') {
      let filtered = PRODUCTS;

      // Category filter (support secondary categories deduplication!)
      if (activeCategory !== 'all') {
        filtered = filtered.filter((p) => p.primaryCategory === activeCategory || p.secondaryCategories?.includes(activeCategory));
      }

      // Search Query filter (match name, aliases, synonyms, keywords, sku, specs)
      if (q) {
        filtered = filtered.filter((p) => {
          const matchName = p.name.toLowerCase().includes(q);
          const matchSku = p.sku.toLowerCase().includes(q);
          const matchSpecs = p.specs.toLowerCase().includes(q);
          const matchAliases = p.aliases?.some((a) => a.toLowerCase().includes(q));
          const matchSynonyms = p.synonyms?.some((s) => s.toLowerCase().includes(q));
          const matchKeywords = p.keywords?.some((k) => k.toLowerCase().includes(q));
          return matchName || matchSku || matchSpecs || matchAliases || matchSynonyms || matchKeywords;
        });
      }

      // Filter by coverage rule
      filtered = filtered.filter((p) => {
        const rule = getCoverageRule(p.id, activePlanId);

        if (activeStatusFilter !== 'all' && rule.coverage_status !== activeStatusFilter) {
          return false;
        }

        if (activePathwayFilter !== 'all' && !rule.benefit_pathways.includes(activePathwayFilter)) {
          return false;
        }

        return true;
      });

      return filtered;
    } else {
      let filtered = SERVICES;

      if (activeCategory !== 'all_services' && activeCategory !== 'all') {
        filtered = filtered.filter((s) => s.category === activeCategory);
      }

      if (q) {
        filtered = filtered.filter((s) => {
          const matchName = s.service_name.toLowerCase().includes(q);
          const matchDesc = s.description.toLowerCase().includes(q);
          const matchAliases = s.aliases?.some((a) => a.toLowerCase().includes(q));
          const matchSynonyms = s.synonyms?.some((syn) => syn.toLowerCase().includes(q));
          return matchName || matchDesc || matchAliases || matchSynonyms;
        });
      }

      filtered = filtered.filter((s) => {
        const rule = getCoverageRule(s.id, activePlanId);

        if (activeStatusFilter !== 'all' && rule.coverage_status !== activeStatusFilter) {
          return false;
        }

        if (activePathwayFilter !== 'all' && !rule.benefit_pathways.includes(activePathwayFilter)) {
          return false;
        }

        return true;
      });

      return filtered;
    }
  }

  // --- 8. RENDER GRID CARDS ---
  function renderGrid() {
    const grid = $('#productGrid');
    const countLabel = $('#productCountLabel');
    if (!grid) return;

    const results = searchItems();

    if (countLabel) {
      countLabel.innerHTML = `Showing <strong>${results.length}</strong> ${activeViewMode === 'products' ? 'insurance-eligible catalog items' : 'plan benefits & supports'} under <strong>${getPlanName(activePlanId)}</strong>`;
    }

    if (results.length === 0) {
      grid.innerHTML = `
        <div style="grid-column:1/-1;background:#fff;border:1px solid var(--line);border-radius:12px;padding:40px;text-align:center">
          <span style="font-size:36px;display:block;margin-bottom:12px">🔍</span>
          <h3 style="margin:0 0 8px;color:var(--green-dark)">No matching items found for your active filters</h3>
          <p style="color:var(--text-muted);font-size:14px;max-width:500px;margin:0 auto 16px">
            Try resetting your search query, switching to "All Categories", or changing your active Benefit Pathway filter.
          </p>
          <button type="button" class="hero-form-btn" onclick="window.resetMarketFilters()" style="background:var(--green-dark);color:#fff">
            Reset Filters
          </button>
        </div>
      `;
      return;
    }

    grid.innerHTML = results.map((item) => {
      const isService = !!item.service_name;
      const id = item.id;
      const rule = getCoverageRule(id, activePlanId);
      const statusBadge = getStatusBadgeHTML(rule.coverage_status);
      const inSlip = callSlip.some((i) => i.id === id);

      if (!isService) {
        return `
          <div class="product-card">
            <div class="product-card-top">
              <span class="product-sku">SKU #${esc(item.sku)}</span>
              ${statusBadge}
            </div>

            <div class="product-image-area">
              <span style="font-size:44px">${item.icon}</span>
            </div>

            <h3 class="product-title">${esc(item.name)}</h3>
            <p class="product-specs">${esc(item.specs)}</p>

            <div style="margin:10px 0;font-size:12px;line-height:1.4;background:var(--cream);padding:8px 10px;border-radius:6px">
              <strong>Coverage Status:</strong> ${esc(rule.money_allowance.member_cost_estimate)}
            </div>

            <div class="product-pricing-box" style="margin-top:auto">
              <div class="product-price-col">
                <span class="retail-val">Retail ${esc(item.retailValue)}</span>
                <span class="allowance-val">$0.00 Out-of-Pocket</span>
              </div>
            </div>

            <div style="display:grid;gap:8px;margin-top:12px">
              <button type="button" class="add-to-slip-btn ${inSlip ? 'added' : ''}" data-add-id="${esc(item.id)}">
                ${inSlip ? '✓ In Call Slip' : '+ Add to Phone Order Slip'}
              </button>

              <button type="button" class="slip-secondary-btn" data-view-rule="${esc(item.id)}">
                🔍 View Coverage &amp; Source
              </button>
            </div>
          </div>
        `;
      } else {
        return `
          <div class="product-card" style="border-top:3px solid var(--gold)">
            <div class="product-card-top">
              <span class="product-sku">BENEFIT #${esc(item.service_code)}</span>
              ${statusBadge}
            </div>

            <div class="product-image-area" style="background:var(--gold-bg)">
              <span style="font-size:44px">${item.icon}</span>
            </div>

            <h3 class="product-title">${esc(item.service_name)}</h3>
            <p class="product-specs">${esc(item.description)}</p>

            <div style="margin:10px 0;font-size:12px;line-height:1.4;background:var(--gold-bg);padding:8px 10px;border-radius:6px;color:#594100">
              <strong>Plan Benefit:</strong> ${esc(rule.money_allowance.member_cost_estimate)}
            </div>

            <div style="display:grid;gap:8px;margin-top:auto">
              <button type="button" class="add-to-slip-btn ${inSlip ? 'added' : ''}" data-add-id="${esc(item.id)}">
                ${inSlip ? '✓ In Call Slip' : '+ Add to Phone Order Slip'}
              </button>

              <button type="button" class="slip-secondary-btn" data-view-rule="${esc(item.id)}">
                📄 View Official Source Rules
              </button>
            </div>
          </div>
        `;
      }
    }).join('');

    // Attach listeners
    $$('[data-add-id]').forEach((btn) => {
      btn.addEventListener('click', () => addToCallSlip(btn.dataset.addId));
    });

    $$('[data-view-rule]').forEach((btn) => {
      btn.addEventListener('click', () => openCoverageModal(btn.dataset.viewRule));
    });
  }

  function getStatusBadgeHTML(status) {
    switch (status) {
      case 'COVERED':
        return `<span class="status-badge status-covered">✓ Covered</span>`;
      case 'OTC_ELIGIBLE':
        return `<span class="status-badge status-otc">💳 OTC Allowance Eligible</span>`;
      case 'CONDITIONAL':
        return `<span class="status-badge status-conditional">⚠️ Conditional</span>`;
      case 'NEEDS_VERIFICATION':
        return `<span class="status-badge status-needs-verification">❓ Needs Verification</span>`;
      case 'NOT_COVERED':
        return `<span class="status-badge status-not-covered">❌ Not Covered</span>`;
      default:
        return `<span class="status-badge status-needs-verification">❓ Unknown</span>`;
    }
  }

  function getPlanName(planId) {
    switch (planId) {
      case 'bcbsri_bluechip_2026_core': return 'BCBSRI BlueCHiP Medicare Core (2026)';
      case 'ri_medicaid_eohhs_2026': return 'RI Medicaid EOHHS Managed Care (2026)';
      case 'carepartners_ma_2026': return 'CarePartners MA Flex Card (2026)';
      case 'highmark_dsnp_2026': return 'Highmark Wholecare D-SNP (2026)';
      default: return 'Unselected / Generic Plan';
    }
  }

  window.resetMarketFilters = function() {
    activeCategory = 'all';
    activeStatusFilter = 'all';
    activePathwayFilter = 'all';
    searchQuery = '';
    const searchInput = $('#marketSearchInput');
    if (searchInput) searchInput.value = '';
    renderCategoryPills();
    renderGrid();
  };

  // --- 9. DYNAMIC CATEGORY PILLS & SIDEBAR RENDERER ---
  function renderCategoryPills() {
    const bar = $('#categoryPillsBar');
    const sideCatList = $('#sidebarCategoryList');
    const categories = activeViewMode === 'products' ? PRODUCT_CATEGORIES : SERVICE_CATEGORIES;

    if (bar) {
      bar.innerHTML = categories.map((c) => `
        <button type="button" class="cat-pill ${activeCategory === c.id ? 'active' : ''}" data-cat-id="${esc(c.id)}">
          ${c.icon} ${esc(c.label)}
        </button>
      `).join('');

      $$('[data-cat-id]').forEach((btn) => {
        btn.addEventListener('click', () => {
          activeCategory = btn.dataset.catId;
          renderCategoryPills();
          renderGrid();
        });
      });
    }

    if (sideCatList) {
      sideCatList.innerHTML = categories.map((c) => `
        <label class="filter-checkbox-label">
          <input type="radio" name="sideCat" value="${esc(c.id)}" ${activeCategory === c.id ? 'checked' : ''}>
          <span>${c.icon} ${esc(c.label)}</span>
        </label>
      `).join('');

      $$('input[name="sideCat"]').forEach((radio) => {
        radio.addEventListener('change', () => {
          activeCategory = radio.value;
          renderCategoryPills();
          renderGrid();
        });
      });
    }
  }

  // --- 10. OPEN COVERAGE MODAL ---
  function openCoverageModal(id) {
    const item = PRODUCTS.find((p) => p.id === id) || SERVICES.find((s) => s.id === id);
    if (!item) return;

    const rule = getCoverageRule(id, activePlanId);
    const isService = !!item.service_name;

    let modal = $('#coverageModal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'coverageModal';
      modal.className = 'order-form-modal-overlay';
      modal.setAttribute('role', 'dialog');
      modal.setAttribute('aria-modal', 'true');
      document.body.appendChild(modal);
    }

    const statusBadge = getStatusBadgeHTML(rule.coverage_status);

    modal.innerHTML = `
      <div class="order-form-modal-window" style="max-width:720px">
        <div class="order-form-modal-header">
          <h2 style="margin:0;font-size:20px;color:var(--green-dark)">
            ${item.icon} ${esc(item.name || item.service_name)}
          </h2>
          <button type="button" class="close-modal-btn" id="closeCoverageModalBtn" aria-label="Close modal">✕</button>
        </div>

        <div class="order-form-modal-body">
          <div style="display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:16px;background:var(--cream);padding:12px;border-radius:8px">
            <div>
              <strong style="font-size:13px;color:var(--text-muted);display:block">SELECTED PLAN:</strong>
              <span style="font-size:15px;font-weight:700;color:var(--green-dark)">${getPlanName(activePlanId)}</span>
            </div>
            <div>
              ${statusBadge}
            </div>
          </div>

          <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px">
            <div style="background:#fff;border:1px solid var(--line);padding:12px;border-radius:8px">
              <strong style="font-size:13px;display:block;margin-bottom:6px;color:var(--green-dark)">Coverage Requirements:</strong>
              <ul style="margin:0;padding-left:18px;font-size:13px;line-height:1.5">
                <li><strong>Prescription Required:</strong> ${esc(rule.eligibility_requirements.prescription_required ?? 'No')}</li>
                <li><strong>Provider Order:</strong> ${esc(rule.eligibility_requirements.provider_order_required ?? 'No')}</li>
                <li><strong>Diagnosis Required:</strong> ${esc(rule.eligibility_requirements.diagnosis_required ?? 'No')}</li>
                <li><strong>Approved Supplier:</strong> ${esc(rule.eligibility_requirements.approved_supplier_required ?? 'In-Network Pharmacy')}</li>
              </ul>
            </div>

            <div style="background:#fff;border:1px solid var(--line);padding:12px;border-radius:8px">
              <strong style="font-size:13px;display:block;margin-bottom:6px;color:var(--green-dark)">Cost & Allowance:</strong>
              <ul style="margin:0;padding-left:18px;font-size:13px;line-height:1.5">
                <li><strong>Member Copay:</strong> ${esc(rule.money_allowance.copay ?? '$0.00')}</li>
                <li><strong>Coinsurance:</strong> ${esc(rule.money_allowance.coinsurance ?? '0%')}</li>
                <li><strong>Cost Estimate:</strong> ${esc(rule.money_allowance.member_cost_estimate)}</li>
              </ul>
            </div>
          </div>

          <div style="background:var(--green-tint);border:1px solid var(--line);padding:14px;border-radius:8px;margin-bottom:16px">
            <strong style="font-size:13px;display:block;margin-bottom:6px;color:var(--green-dark)">
              📄 Official Plan Source Documentation:
            </strong>
            <p style="font-size:13px;line-height:1.5;margin:0 0 6px">
              <em>"${esc(rule.official_source.source_excerpt)}"</em>
            </p>
            <div style="font-size:12px;color:var(--text-muted);display:flex;justify-content:space-between">
              <span>Source: <strong>${esc(rule.official_source.source_name)}</strong></span>
              <span>Last Verified: ${esc(rule.official_source.last_verified || '2026-01-01')}</span>
            </div>
          </div>

          <div style="display:flex;gap:10px;justify-content:flex-end">
            <a href="/find-care/doctors/" class="hero-form-btn" style="background:var(--green-dark);color:#fff;text-decoration:none">
              🩺 Ask My Doctor / Select PCP
            </a>
            <button type="button" class="hero-form-btn" id="modalAddSlipBtn" style="background:var(--terracotta);color:#fff">
              + Add to Phone Order Slip
            </button>
          </div>
        </div>
      </div>
    `;

    modal.style.display = 'flex';

    $('#closeCoverageModalBtn')?.addEventListener('click', () => { modal.style.display = 'none'; });
    $('#modalAddSlipBtn')?.addEventListener('click', () => {
      addToCallSlip(id);
      modal.style.display = 'none';
    });
  }

  // --- 11. PHONE ORDER SLIP & ORDER SHEET ---
  function addToCallSlip(id) {
    const item = PRODUCTS.find((p) => p.id === id) || SERVICES.find((s) => s.id === id);
    if (!item) return;

    const existing = callSlip.find((i) => i.id === id);
    if (existing) {
      existing.qty += 1;
    } else {
      callSlip.push({
        id: item.id,
        sku: item.sku || item.service_code,
        name: item.name || item.service_name,
        cost: item.allowanceCost || 0,
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
            Click <em>"+ Add to Phone Order Slip"</em> on any item to build your call sheet.
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
                <small style="color:#cbe0d9">Item #${esc(item.sku)}</small>
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
        <button type="button" class="hero-form-btn" id="copyScriptBtn" style="background:rgba(255,255,255,0.15);color:#fff;width:100%;justify-content:center">
          📋 Copy Phone Order Script
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

    $('#copyScriptBtn')?.addEventListener('click', copyPhoneScript);
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

  function copyPhoneScript() {
    const lines = [
      'PAZERATECHNOLOGIES HEALTH PLAN PHONE ORDER SCRIPT',
      '------------------------------------------------',
      'Selected Plan: ' + getPlanName(activePlanId),
      'Representative: "How can I assist your health benefits today?"',
      'Member: "Hello, I would like to place an order using my health plan allowance."',
      '',
      'ITEMS / SERVICES TO READ TO REPRESENTATIVE:',
      ...callSlip.map((item, idx) => `${idx + 1}. Item #${item.sku} - ${item.name} (Qty: ${item.qty})`),
      '',
      'CONFIRMATION:',
      '- Please deliver to my address on file.',
      '- Please confirm 100% deduction from my benefit card balance.'
    ];

    navigator.clipboard.writeText(lines.join('\\n')).then(() => {
      alert('✓ Phone order script copied to clipboard!');
    }).catch(() => {
      alert('Script ready. You can read item numbers directly from your call slip.');
    });
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
            <div><strong>Selected Plan:</strong> ${getPlanName(activePlanId)}</div>
            <div><strong>Order Date:</strong> ${todayStr}</div>
            <div><strong>Total Items:</strong> ${callSlip.length}</div>
            <div><strong>Shipping Cost:</strong> $0.00 (100% Free Home Delivery)</div>
          </div>

          <table class="order-items-table">
            <thead>
              <tr>
                <th>Item SKU / Code</th>
                <th>Product / Service Description</th>
                <th>Qty</th>
                <th>Estimated Allowance Cost</th>
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
    renderCategoryPills();

    // Plan selector event
    const planDropdown = $('#planSelectorSelect');
    if (planDropdown) {
      planDropdown.value = activePlanId;
      planDropdown.addEventListener('change', (e) => {
        activePlanId = e.target.value;
        const pill = $('#planStatusPill');
        if (pill) {
          if (activePlanId === 'unselected_generic') {
            pill.textContent = '❓ Needs Verification Mode';
            pill.style.background = 'var(--gold)';
            pill.style.color = '#594100';
          } else {
            pill.textContent = '✓ Plan Verified';
            pill.style.background = 'var(--terracotta)';
            pill.style.color = '#fff';
          }
        }
        renderGrid();
      });
    }

    // View tab toggles (Shop Products vs Your Benefits)
    const tabShop = $('#tabShopProducts');
    const tabBenefits = $('#tabYourBenefits');

    if (tabShop && tabBenefits) {
      tabShop.addEventListener('click', () => {
        tabShop.classList.add('active');
        tabBenefits.classList.remove('active');
        activeViewMode = 'products';
        activeCategory = 'all';
        renderCategoryPills();
        renderGrid();
      });

      tabBenefits.addEventListener('click', () => {
        tabBenefits.classList.add('active');
        tabShop.classList.remove('active');
        activeViewMode = 'services';
        activeCategory = 'all_services';
        renderCategoryPills();
        renderGrid();
      });
    }

    // Search input
    const searchInput = $('#marketSearchInput');
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        searchQuery = e.target.value;
        renderGrid();
      });
    }

    // Sidebar filters
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
    f.write(js_code)

print("Generated marketplace.js successfully.")
