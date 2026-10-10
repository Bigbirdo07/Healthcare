// Export a New York-only copy of the project for a Base44 rebuild:
// ../ny-benefit-navigator/ with NY plans, coverage rules, catalog, providers,
// official sources and the pipeline scripts. Re-run after rebuilding NY data.
//
// Usage: node scratch/export_ny_base44.js [outDir]

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const loadBundle = require('./bundle_loader');

const ROOT = path.resolve(__dirname, '..');
const OUT = path.resolve(process.argv[2] || path.join(ROOT, '..', 'ny-benefit-navigator'));
const DATA = path.join(OUT, 'data');

const csvCell = (v) => {
  const s = v == null ? '' : Array.isArray(v) ? v.join('; ') : typeof v === 'object' ? JSON.stringify(v) : String(v);
  return /[",\n\r]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
};
function writeCsv(file, rows, columns) {
  const out = [columns.join(',')];
  for (const r of rows) out.push(columns.map((c) => csvCell(r[c])).join(','));
  fs.writeFileSync(file, out.join('\n') + '\n');
}
const sha256 = (f) => crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const copy = (from, to) => { fs.mkdirSync(path.dirname(to), { recursive: true }); fs.copyFileSync(from, to); };

fs.mkdirSync(DATA, { recursive: true });

// Plans + rules (same content the marketplace lazy-loads).
const verified = JSON.parse(fs.readFileSync(path.join(ROOT, 'data/ny_verified_coverage_2026/NY_VERIFIED_RULES_2026.json'), 'utf8'));
const { plans } = JSON.parse(fs.readFileSync(path.join(ROOT, 'dist/marketplace/states/ny/plans.json'), 'utf8'));
const ruleCount = new Map();
verified.rules.forEach((r) => ruleCount.set(r.plan_id, (ruleCount.get(r.plan_id) || 0) + 1));
const planRows = plans.map((p) => ({
  plan_key: p.id, card_type: p.market_segment === 'MEDICAID' ? 'MEDICAID_CARD' : 'INSURANCE_CARD',
  market_segment: p.market_segment, insurance_category: p.insurance_category, insurer_id: p.insurer_id, insurer_name: p.insurer_name,
  plan_name: p.official_plan_name, plan_type: p.plan_type, metal_level: p.metal_level || '',
  contract_id: p.contract_id && p.contract_id !== 'N/A' ? p.contract_id : '', pbp_id: p.plan_id && p.plan_id !== 'N/A' ? p.plan_id : '',
  segment_id: p.market_segment.startsWith('MEDICARE') ? p.segment_id : '', service_area_counties: p.service_area_counties || [],
  benefits_under_review: p.benefits_under_review, verified_rule_count: ruleCount.get(p.id) || 0, roster_source: p.official_roster_source,
}));
fs.writeFileSync(path.join(DATA, 'ny_plans.json'), JSON.stringify(planRows, null, 1));
writeCsv(path.join(DATA, 'ny_plans.csv'), planRows, Object.keys(planRows[0]));

const ruleColumns = ['rule_id', 'plan_id', 'target_type', 'target_id', 'coverage_status', 'benefit_pathway', 'member_cost', 'requirements',
  'evidence_excerpt', 'source_page', 'official_source_name', 'official_source_url', 'source_document_sha256', 'verification_status', 'last_verified_date'];
const rules = verified.rules.map((r) => Object.fromEntries(ruleColumns.map((c) => [c, r[c]])));
fs.writeFileSync(path.join(DATA, 'ny_coverage_rules.json'), JSON.stringify(rules));
writeCsv(path.join(DATA, 'ny_coverage_rules.csv'), rules, ruleColumns);

// Catalog: every product/service in the marketplace plus the benefits NY rules use.
const b = loadBundle(path.join(ROOT, 'dist/marketplace/marketplace.js')).__D;
const used = new Set(verified.rules.map((r) => r.target_id));
const catalog = [
  ...b.PRODUCTS.map((p) => ({ item_id: p.id, item_type: 'PRODUCT', name: p.product_name, category: p.category, subcategory: p.subcategory || '',
    description: p.description || '', icon: p.icon || '', search_terms: [...(p.aliases || []), ...(p.synonyms || []), ...(p.keywords || [])] })),
  ...b.SERVICES.map((s) => ({ item_id: s.id || s.service_id, item_type: 'SERVICE', name: s.service_name, category: s.category, subcategory: '',
    description: s.description || '', icon: s.icon || '', search_terms: [] })),
  ...[...b.BENEFITS, ...verified.benefits].filter((x, i, all) => used.has(x.id) && all.findIndex((y) => y.id === x.id) === i)
    .map((x) => ({ item_id: x.id, item_type: 'BENEFIT', name: x.benefit_name, category: x.category || x.benefit_type || '', subcategory: '',
      description: x.description || '', icon: x.icon || '', search_terms: [] })),
];
const missing = [...used].filter((id) => !catalog.some((c) => c.item_id === id));
if (missing.length) throw new Error('rules target items missing from catalog: ' + missing.join(', '));
fs.writeFileSync(path.join(DATA, 'catalog_items.json'), JSON.stringify(catalog, null, 1));
writeCsv(path.join(DATA, 'catalog_items.csv'), catalog, Object.keys(catalog[0]));

// Providers: expand the compact file into flat rows.
const prov = JSON.parse(fs.readFileSync(path.join(ROOT, 'dist/providers/ny.json'), 'utf8'));
const labels = prov.meta.medicaid_status_labels;
const provColumns = ['npi', 'first_name', 'middle_name', 'last_name', 'suffix', 'credentials', 'provider_category', 'specialty', 'practice_name',
  'address_line_1', 'address_line_2', 'city', 'state', 'zip', 'public_phone', 'telehealth_status', 'medicare_assignment_status',
  'medicaid_status', 'medicaid_status_label', 'medicaid_status_as_of', 'npi_registry_url'];
const providers = prov.provider_rows.map((row) => {
  const p = Object.fromEntries(prov.provider_columns.map((c, i) => [c, row[i]]));
  return { ...p, state: 'NY', medicaid_status: p.ri_medicaid_ffs_status, medicaid_status_label: labels[p.ri_medicaid_ffs_status],
    medicaid_status_as_of: prov.meta.medicaid_status_as_of, npi_registry_url: `https://npiregistry.cms.hhs.gov/provider-view/${p.npi}` };
});
writeCsv(path.join(DATA, 'ny_providers.csv'), providers, provColumns);
fs.writeFileSync(path.join(DATA, 'ny_providers_meta.json'), JSON.stringify(prov.meta, null, 1));

// Official sources: the files rules quote, plus roster/provider indexes.
const spec = JSON.parse(fs.readFileSync(path.join(ROOT, 'data/ny_verified_coverage_2026/evidence_spec.json'), 'utf8'));
const files = new Map(Object.values(spec.sources).map((s) => [s.file, { title: s.title, url: s.url }]));
[
  ['data/official_source_indexes_2026/CMS_MA_PD_LANDSCAPE_75f2797b5104.zip', 'CMS CY2026 MA/PD Landscape (Sept 2026)', 'https://www.cms.gov/files/zip/cy2026-landscape-202609.zip'],
  ['data/official_source_indexes_2026/CMS_URR_PUF_2026_9575fccc0ec2.zip', 'CMS 2026 Unified Rate Review PUF (issuer names)', 'https://www.cms.gov/files/zip/py2026-puf-20260327.zip'],
  ['data/official_source_indexes_2026/NY_DOH_MMC_ENROLLMENT_2026_09_b94538f19f80.pdf', 'NYS DOH Medicaid Managed Care Enrollment Report, Sept 2026', 'https://www.health.ny.gov/health_care/managed_care/reports/enrollment/monthly/2026/docs/en09_26.pdf'],
  ['data/official_source_indexes_2026/NY_DOH_MMC_MEMBER_HANDBOOKS_PAGE_939a3a8358e5.html', 'NYS DOH Medicaid Managed Care member handbooks page', 'https://www.health.ny.gov/health_care/managed_care/member_handbooks.htm'],
  ['data/official_source_indexes_2026/CMS_PBP_BENEFITS_2026_1720048e668f.zip', 'CMS 2026 Plan Benefit Package (PBP) benefits data', 'https://www.cms.gov/files/zip/pbp-benefits-2026.zip'],
].forEach(([f, title, url]) => files.set(f, { title, url }));
const medicaidDir = path.join(ROOT, 'data/ny_downloads/medicaid');
fs.readdirSync(medicaidDir).forEach((f) => files.set(path.join('data/ny_downloads/medicaid', f), { title: f.replace(/\.[a-z]+$/, '').replace(/_/g, ' '), url: '', pending_review: true }));
const manifest = [];
for (const [rel, info] of files) {
  const src = path.join(ROOT, rel);
  const dest = path.join('sources', path.basename(rel));
  copy(src, path.join(OUT, dest));
  manifest.push({ file: dest, title: info.title, url: info.url, sha256: sha256(src), bytes: fs.statSync(src).size,
    status: info.pending_review ? 'downloaded - awaiting review, not yet quoted' : 'used' });
}
manifest.push(...prov.meta.sources.map((s) => ({ file: '(not included - too large for GitHub)', title: s.source_name, url: s.url, sha256: s.sha256, status: 'used for ny_providers.csv' })));
fs.writeFileSync(path.join(OUT, 'sources', 'SOURCES.json'), JSON.stringify(manifest, null, 1));

// Pipeline scripts and evidence spec, for reference / rebuilding.
['build_ri_verified_rules.py', 'gen_ri_commercial_rules.py', 'build_ny_roster.py', 'gen_ny_commercial_rules.py', 'gen_ny_original_medicare_rules.py',
  'build_ny_providers.py', 'apply_ny_verified_rules.js', 'bundle_loader.js', 'export_ny_base44.js']
  .forEach((f) => copy(path.join(ROOT, 'scratch', f), path.join(OUT, 'pipeline', f)));
copy(path.join(ROOT, 'data/ny_verified_coverage_2026/evidence_spec.json'), path.join(OUT, 'pipeline', 'evidence_spec.json'));
copy(path.join(ROOT, 'data/ny_verified_coverage_2026/NY_OFFICIAL_PLAN_ROSTER.csv'), path.join(DATA, 'ny_official_plan_roster.csv'));

const mb = (f) => (fs.statSync(path.join(OUT, f)).size / 1e6).toFixed(1) + ' MB';
console.log(`Exported to ${OUT}`);
['data/ny_plans.csv', 'data/ny_coverage_rules.csv', 'data/catalog_items.csv', 'data/ny_providers.csv'].forEach((f) => console.log('  ' + f, mb(f)));
console.log(`  ${planRows.length} plans, ${rules.length} rules, ${catalog.length} catalog items, ${providers.length} provider rows, ${manifest.length} sources`);
