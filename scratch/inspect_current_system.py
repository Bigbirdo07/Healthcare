import json
import csv
import hashlib
import os

print("--- PHASE 22 STEP 1: CURRENT PROJECT INSPECTION ---")

# 1. Census Verification
census_path = "NEW_ENGLAND_2026_PLAN_CENSUS_V4.csv"
with open(census_path, "rb") as f:
    census_bytes = f.read()
    census_hash = hashlib.sha256(census_bytes).hexdigest()

EXPECTED_HASH = "e9ae11af0e074f9d819fa8f2339d19b463a515fd5d5dd00db3f71894c770d8af"
assert census_hash == EXPECTED_HASH, f"Census Hash Mismatch: {census_hash}"

with open(census_path, "r", encoding="utf-8") as f:
    census_plans = list(csv.DictReader(f))

print(f"1. CENSUS: Verified exact SHA256 ({census_hash}), {len(census_plans)} plans.")
print(f"   Census Headers: {list(census_plans[0].keys())}")

# 2. Marketplace Dump Inspection
dump_path = "scratch/marketplace_dump.json"
with open(dump_path, "r", encoding="utf-8") as f:
    dump = json.load(f)

print(f"\n2. MARKETPLACE DUMP KEYS: {list(dump.keys())}")
products = dump.get("PRODUCTS", [])
rules = dump.get("COVERAGE_RULES", [])
print(f"   Products: {len(products)}")
print(f"   Coverage Rules: {len(rules)}")

if products:
    print(f"   Product fields: {list(products[0].keys())}")
if rules:
    print(f"   Rule fields: {list(rules[0].keys())}")

# Extract Products, Product Variants, Services, Benefits
categories = set()
departments = set()
for p in products:
    categories.add(p.get("category", ""))
    departments.add(p.get("department", ""))

print(f"   Product Categories ({len(categories)}): {sorted(list(categories))}")
print(f"   Product Departments ({len(departments)}): {sorted(list(departments))}")

# 3. Source Documents & Provenance
provenance_files = [
    "BATCH_1_RULE_PROVENANCE.csv", "BATCH_2_RULE_PROVENANCE.csv", "BATCH_3_RULE_PROVENANCE.csv",
    "BATCH_4_RULE_PROVENANCE.csv", "BATCH_5_RULE_PROVENANCE.csv", "BATCH_6_RULE_PROVENANCE.csv",
    "BATCH_7_RULE_PROVENANCE.csv", "BATCH_9_RULE_PROVENANCE.csv"
]
total_prov_rows = 0
for pf in provenance_files:
    if os.path.exists(pf):
        with open(pf, "r", encoding="utf-8") as f:
            total_prov_rows += len(list(csv.DictReader(f)))
print(f"\n3. RULE PROVENANCE ROWS ACROSS BATCHES: {total_prov_rows}")

source_doc_files = [
    "BATCH_1_SOURCE_DOCUMENTS.csv", "BATCH_2_SOURCE_DOCUMENTS.csv", "BATCH_3_SOURCE_DOCUMENTS.csv",
    "BATCH_4_SOURCE_DOCUMENTS.csv", "BATCH_5_SOURCE_DOCUMENTS.csv", "BATCH_6_SOURCE_DOCUMENTS.csv",
    "BATCH_7_SOURCE_DOCUMENTS.csv", "BATCH_9_SOURCE_DOCUMENTS.csv"
]
all_sources = {}
for sf in source_doc_files:
    if os.path.exists(sf):
        with open(sf, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
            for r in rows:
                h = r.get("source_document_sha256") or r.get("sha256")
                if h:
                    all_sources[h] = r

print(f"   Unique Source Documents (by SHA256): {len(all_sources)}")

# 4. Ingestion Queue Inspection
queue_file = "BENEFIT_SOURCE_INGESTION_QUEUE_V12.csv"
with open(queue_file, "r", encoding="utf-8") as f:
    queue_tasks = list(csv.DictReader(f))

status_counts = {}
for q in queue_tasks:
    st = q.get("source_status", "UNKNOWN")
    status_counts[st] = status_counts.get(st, 0) + 1

print(f"\n4. INGESTION QUEUE (V12): Total Tasks = {len(queue_tasks)}")
print(f"   Status breakdown: {status_counts}")
print(f"   Queue Headers: {list(queue_tasks[0].keys())}")

# 5. Audit Summary / Readiness / Domain Completeness
summary_file = "PLAN_BENEFIT_AUDIT_SUMMARY_V12.csv"
with open(summary_file, "r", encoding="utf-8") as f:
    audit_summary = list(csv.DictReader(f))

print(f"\n5. PLAN BENFIT AUDIT SUMMARY (V12): {len(audit_summary)} plans")
readiness_dist = {}
for s in audit_summary:
    cls = s.get("plan_readiness_classification") or s.get("primary_plan_audit_status")
    readiness_dist[cls] = readiness_dist.get(cls, 0) + 1
print(f"   Readiness Breakdown: {readiness_dist}")

post_matrix_file = "DOMAIN_COMPLETENESS_POST_BATCH9.csv"
with open(post_matrix_file, "r", encoding="utf-8") as f:
    post_matrix = list(csv.DictReader(f))

print(f"\n6. POST-BATCH 9 DOMAIN MATRIX: {len(post_matrix)} domains")
for m in post_matrix:
    print(f"   - {m['benefit_domain']}: Complete={m['complete_count']}, Partial={m['partial_count']}, NotIngested={m['not_ingested_count']}, NotApp={m['not_applicable_count']}")

print("\n--- INSPECTION COMPLETE ---")
