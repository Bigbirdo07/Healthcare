import csv
import json

census_file = "NEW_ENGLAND_2026_PLAN_CENSUS_V4.csv"
with open(census_file, "r", encoding="utf-8") as f:
    v4_plans = list(csv.DictReader(f))

v4_rep_map = {p["repository_plan_id"]: p for p in v4_plans}

with open("scratch/marketplace_dump.json", "r", encoding="utf-8") as f:
    data = json.load(f)

all_rules = data["COVERAGE_RULES"]
pre_rules = all_rules[:952]

DOMAINS = [
    "MEDICAL", "PHARMACY", "OTC", "DME", "DENTAL", "VISION",
    "HEARING", "TRANSPORTATION", "FITNESS", "FOOD_MEALS",
    "MATERNITY", "SMOKING_CESSATION", "OTHER_SUPPLEMENTAL"
]

def get_domain_app(seg, d):
    if seg == "MEDICARE_PART_D": return d in ["PHARMACY", "SMOKING_CESSATION"]
    elif seg == "MEDICARE_SUPPLEMENT": return d in ["MEDICAL", "PHARMACY", "SMOKING_CESSATION"]
    elif seg in ["MEDICAID", "CHIP"]: return d in ["MEDICAL", "PHARMACY", "OTC", "DME", "DENTAL", "VISION", "HEARING", "TRANSPORTATION", "MATERNITY", "SMOKING_CESSATION"]
    else: return True

def compute_plan_domain_status(p_rules, seg, dom):
    if not get_domain_app(seg, dom):
        return "NOT_APPLICABLE"
    elif any(r.get("benefit_domain") == dom for r in p_rules):
        return "COMPLETE"
    elif len(p_rules) > 0:
        return "PARTIAL"
    else:
        return "NOT_INGESTED"

pre_rules_by_plan = {}
for r in pre_rules:
    pid = r.get("plan_id")
    if pid:
        pre_rules_by_plan.setdefault(pid, []).append(r)

post_rules_by_plan = {}
for r in all_rules:
    pid = r.get("plan_id")
    if pid:
        post_rules_by_plan.setdefault(pid, []).append(r)

net_deltas = []
for p in v4_plans:
    pid = p["repository_plan_id"]
    ckey = p["canonical_plan_key"]
    seg = p["market_segment"]

    pre_p_rules = pre_rules_by_plan.get(pid, [])
    post_p_rules = post_rules_by_plan.get(pid, [])

    for dom in DOMAINS:
        s_pre = compute_plan_domain_status(pre_p_rules, seg, dom)
        s_post = compute_plan_domain_status(post_p_rules, seg, dom)

        if s_pre != s_post:
            net_deltas.append({
                "canonical_plan_key": ckey,
                "repository_plan_id": pid,
                "benefit_domain": dom,
                "status_before_batch": s_pre,
                "status_after_batch": s_post
            })

print(f"Total Net Status Deltas across 331 plans: {len(net_deltas)}")

# Now test matrix reconstruction starting from PRE_BATCH5 and applying net_deltas
with open("DOMAIN_COMPLETENESS_PRE_BATCH5.csv", "r", encoding="utf-8") as f:
    pre_matrix = list(csv.DictReader(f))

with open("DOMAIN_COMPLETENESS_POST_BATCH5.csv", "r", encoding="utf-8") as f:
    post_matrix = list(csv.DictReader(f))

pre_matrix_dict = {r["benefit_domain"]: r.copy() for r in pre_matrix}

delta_counts = {}
for d in net_deltas:
    dom = d["benefit_domain"]
    sb = d["status_before_batch"]
    sa = d["status_after_batch"]

    if dom not in delta_counts:
        delta_counts[dom] = {"COMPLETE": 0, "PARTIAL": 0, "NOT_INGESTED": 0}

    if sb == "NOT_INGESTED":
        delta_counts[dom]["NOT_INGESTED"] -= 1
    elif sb == "PARTIAL":
        delta_counts[dom]["PARTIAL"] -= 1

    if sa == "COMPLETE":
        delta_counts[dom]["COMPLETE"] += 1
    elif sa == "PARTIAL":
        delta_counts[dom]["PARTIAL"] += 1

mismatches = 0
for dom_row in pre_matrix:
    dom = dom_row["benefit_domain"]
    d = delta_counts.get(dom, {"COMPLETE": 0, "PARTIAL": 0, "NOT_INGESTED": 0})

    c_new = int(dom_row["complete_count"]) + d["COMPLETE"]
    p_new = int(dom_row["partial_count"]) + d["PARTIAL"]
    n_new = int(dom_row["not_ingested_count"]) + d["NOT_INGESTED"]
    na = int(dom_row["not_applicable_count"])
    src_nf = int(dom_row["source_not_found_count"])
    tot = c_new + p_new + n_new + na + src_nf

    rec_row = {
        "benefit_domain": dom,
        "complete_count": str(c_new),
        "partial_count": str(p_new),
        "not_ingested_count": str(n_new),
        "not_applicable_count": str(na),
        "total_plan_sum": str(tot)
    }

    actual_post_row = [r for r in post_matrix if r["benefit_domain"] == dom][0]
    for k in ["complete_count", "partial_count", "not_ingested_count", "not_applicable_count", "total_plan_sum"]:
        if str(rec_row[k]) != str(actual_post_row[k]):
            print(f"MISMATCH in {dom} for {k}: expected {rec_row[k]}, actual {actual_post_row[k]}")
            mismatches += 1

if mismatches == 0:
    print("RECONSTRUCTION TEST PASSED 100%! Pre-Batch + Net Deltas = Post-Batch Exactly!")
