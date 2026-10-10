"""Generate evidence_spec rules for Rhode Island individual and small-group
plans from the CMS State-Based Exchange PUF benefit rows (RIBenefits CSV).

Each rule quotes its plan's CMS row verbatim, so build_ri_verified_rules.py
can re-check it against the hashed zip. Dollar cost sharing is not in this
file, so costs point members to the plan's Summary of Benefits and Coverage.

Usage: python3 scratch/gen_ri_commercial_rules.py && python3 scratch/build_ri_verified_rules.py
"""
import collections
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
import build_ri_verified_rules as B

ROOT = B.ROOT
SPEC = os.path.join(ROOT, "data/ri_verified_coverage_2026/evidence_spec.json")
SRC = "CMS_RI_SBE_PUF"
PLANS_SRC = "CMS_RI_SBE_PLANS"
PLAN_FIELDS = [["Variation", "CSR VARIATION TYPE"], ["Deductible (individual)", "TEHB DED INN TIER 1 INDIVIDUAL"],
               ["Deductible (family)", "TEHB DED INN TIER 1 FAMILY"], ["Out-of-pocket max (individual)", "TEHB INN TIER 1 INDIVIDUAL MOOP"],
               ["Out-of-pocket max (family)", "TEHB INN TIER 1 FAMILY MOOP"], ["Coinsurance after deductible", "TEHB DED INN TIER 1 COINSURANCE"]]
COST = "Your plan's deductible, copay or coinsurance applies - see the plan's Summary of Benefits and Coverage"


def explanation(row):
    return re.search(r"Explanation:\s*(.*)$", row).group(1).strip()


def limit(row):
    m = re.search(r"Limit:\s*([^·]*?)\s*·", row)
    return m.group(1).strip() if m else ""


def cut(row, field):
    """The row up to (not including) a field, to quote only what the rule relies on."""
    return row.split(f" · {field}")[0]


def roster():
    js = ("const w=require(process.argv[1])(process.argv[2]);"
          "console.log(JSON.stringify(w.__D.RI_OFFICIAL_SELECTOR_PLANS.filter(p=>p.id.startsWith('QHP:'))"
          ".map(p=>[p.id,p.market_segment])))")
    loader = os.path.join(os.path.dirname(__file__), "bundle_loader.js")
    out = subprocess.run(["node", "-e", js, loader, os.path.join(ROOT, "dist/marketplace/marketplace.js")],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def main():
    spec = json.load(open(SPEC, encoding="utf-8"))
    spec["sources"][SRC] = {
        "file": "data/official_source_indexes_2026/SBE_RHODE_ISLAND_99f29381837a.zip",
        "sha256": "99f29381837a27bc25a2d4fadb7bf53fa30693ad7f4e2068be07cf994f7c6615",
        "url": "https://www.cms.gov/files/zip/rhodeislandsbepuf2026.zip",
        "title": "CMS 2026 Rhode Island State-Based Exchange PUF - plan benefits (RIBenefits05052026.csv)",
        "format": "csv_rows", "zip_member": "RIBenefits05052026.csv"}
    spec["sources"][PLANS_SRC] = {
        "file": "data/official_source_indexes_2026/SBE_RHODE_ISLAND_99f29381837a.zip",
        "sha256": "99f29381837a27bc25a2d4fadb7bf53fa30693ad7f4e2068be07cf994f7c6615",
        "url": "https://www.cms.gov/files/zip/rhodeislandsbepuf2026.zip",
        "title": "CMS 2026 Rhode Island State-Based Exchange PUF - plan attributes (RIPlans05052026.csv)",
        "format": "csv_rows", "zip_member": "RIPlans05052026.csv", "fields": PLAN_FIELDS}
    plan_rows = {re.match(r"PLAN (\S+) ·", r).group(1): r for r in B.load_source(spec["sources"][PLANS_SRC])}
    if not any(b["id"] == "B-RI26-PLAN-COSTS" for b in spec["new_benefits"]):
        spec["new_benefits"].append({"id": "B-RI26-PLAN-COSTS", "benefit_name": "Your Plan's Costs (deductible & out-of-pocket max)",
                                     "benefit_type": "PLAN_COST_SHARING", "category": "medmgmt", "icon": "🧾",
                                     "description": "The deductible, out-of-pocket maximum and coinsurance that apply across this plan."})
    index = {}
    for row in B.load_source(spec["sources"][SRC]):
        m = re.match(r"PLAN (\w+)-(\d\d) · ([^·]+?) · ", row)
        if m:
            index.setdefault((m.group(1), m.group(3)), {})[m.group(2)] = row

    def get(pid, benefit):
        variants = index.get((pid, benefit), {})
        return variants.get("01") or (variants[sorted(variants)[0]] if variants else None)

    # Plan-specific CMS rows beat the HealthSource RI guide's general pediatric-dental line.
    for r in spec["rules"]:
        if r["source"] == "HSRI_2026_GUIDE" and r["targets"] == "S-DEN-EXAM":
            r["fallback"] = True

    rules, stats = [], collections.Counter()
    for plan_id, market in roster():
        pid = plan_id.split(":")[2]
        key = "QHP_" + pid
        spec["plans"][key] = [plan_id]
        prow = plan_rows.get(pid + "-01")
        field = lambda label: re.search(re.escape(label) + r": ([^·]*)", prow).group(1).strip() if prow else ""
        ded, moop, coins = field("Deductible (individual)"), field("Out-of-pocket max (individual)"), field("Coinsurance after deductible").replace(".00%", "%")
        COST = (f"Plan terms: {ded} deductible, then {coins} coinsurance (out-of-pocket max {moop}); this item's exact cost is in the plan's SBC"
                if prow else "Your plan's deductible, copay or coinsurance applies - see the plan's Summary of Benefits and Coverage")
        cite = [{"source": PLANS_SRC, "text": prow}] if prow else []
        _R = lambda **kw: dict(plans=key, source=SRC, **kw)
        R = lambda **kw: _R(**{**kw, "excerpts": kw["excerpts"] + (cite if kw.get("member_cost") == COST else [])})
        if prow:
            rules.append(dict(plans=key, source=PLANS_SRC, targets="B-RI26-PLAN-COSTS", type="BENEFIT", status="Covered", pathway="Plan cost sharing (in-network)",
                              member_cost=f"Deductible {ded} per person ({field('Deductible (family)')}); out-of-pocket max {moop} per person ({field('Out-of-pocket max (family)')}); {coins} coinsurance after the deductible",
                              requirements="In-network amounts for the standard plan version; members in a cost-sharing-reduction or zero-cost-sharing version pay less",
                              excerpts=[prow]))
            stats["plan_costs"] += 1

        dme = get(pid, "Durable Medical Equipment")
        if dme and "Covered: Yes" in dme:
            rules.append(R(targets="DME", template="DME", status="Conditional", member_cost=COST, excerpts=[cut(dme, "Limit")]))
            stats["dme"] += 1

        hear = get(pid, "Hearing Aids")
        if hear and "Covered: Yes" in hear:
            req = "; ".join(x for x in [("Limit: " + limit(hear)) if limit(hear) else "", explanation(hear)] if x) or "Network hearing provider"
            rules += [R(targets="HEARING_PRODUCT", template="HEARING_PRODUCT", status="Conditional", member_cost=COST, excerpts=[hear]),
                      R(targets="B-RI26-HEARING-AIDS", type="BENEFIT", status="Covered", pathway="Hearing aid benefit",
                        member_cost=COST, requirements=req, excerpts=[hear])]
            stats["hearing"] += 1

        eye = get(pid, "Routine Eye Exam (Adult)")
        if eye:
            yes = "Covered: Yes" in eye
            rules.append(R(targets="S-VIS-EXAM", type="SERVICE", status="Covered" if yes else "Not Covered", pathway="Routine eye exam",
                           member_cost=COST if yes else "You pay all costs",
                           requirements=("Limit: " + limit(eye)) if limit(eye) else "Network eye doctor", excerpts=[cut(eye, "Exclusions")]))
            stats["eye_exam"] += 1

        glasses = get(pid, "Eye Glasses for Children")
        if glasses and "Covered: Yes" in glasses:
            rules.append(R(targets="B-RI26-EYEWEAR", type="BENEFIT", status="Conditional", pathway="Pediatric vision (ACA essential health benefit)",
                           member_cost=COST, requirements="Children only" + (f"; limit: {limit(glasses)}" if limit(glasses) else ""),
                           excerpts=[cut(glasses, "Exclusions")]))
            stats["child_glasses"] += 1

        adult, child = get(pid, "Routine Dental Services (Adult)"), get(pid, "Dental Check-Up for Children")
        if adult and "Covered: Yes" in adult:
            rules.append(R(targets="S-DEN-EXAM", type="SERVICE", status="Covered", pathway="Adult routine dental", member_cost=COST,
                           requirements=explanation(adult) or f"Limit: {limit(adult)}", excerpts=[adult]))
            stats["dental_adult"] += 1
        elif child and "Covered: Yes" in child:
            rules.append(R(targets="S-DEN-EXAM", type="SERVICE", status="Conditional", pathway="Pediatric dental (ACA essential health benefit)",
                           member_cost=COST, requirements="Children only - adult routine dental is not covered" + (f"; limit: {limit(child)}" if limit(child) else ""),
                           excerpts=[cut(child, "Exclusions")] + ([cut(adult, "Limit")] if adult else [])))
            stats["dental_child_only"] += 1
        elif adult:
            rules.append(R(targets="S-DEN-EXAM", type="SERVICE", status="Not Covered", pathway="Not covered by this plan", member_cost="You pay all costs",
                           requirements="Routine dental is not covered for adults or children in this plan's filing",
                           excerpts=[cut(adult, "Limit")] + ([cut(child, "Limit")] if child else [])))
            stats["dental_none"] += 1

        basic = get(pid, "Basic Dental Care - Adult")
        if basic:
            yes = "Covered: Yes" in basic
            rules.append(R(targets="B-RI26-DENTAL-COMP", type="BENEFIT", status="Covered" if yes else "Not Covered",
                           pathway="Adult basic dental" if yes else "Not covered by this plan", member_cost=COST if yes else "You pay all costs",
                           requirements=(explanation(basic) or f"Limit: {limit(basic)}") if yes else "Adult basic dental care is not covered",
                           excerpts=[basic if yes else cut(basic, "Limit")]))
            stats["adult_basic_dental"] += 1

        prev = get(pid, "Preventive Care/Screening/Immunization")
        # Individual plans already cite HealthSource RI's "$0" statement for preventive care.
        if market == "SMALL_GROUP" and prev and "Covered: Yes" in prev:
            rules.append(R(targets="S-PREV-WELLNESS", type="SERVICE", status="Covered", pathway="Preventive care", member_cost=COST,
                           requirements="In-network preventive care" + (f"; limit: {limit(prev)}" if limit(prev) else ""),
                           excerpts=[cut(prev, "Exclusions")]))
            stats["preventive"] += 1

    spec["rules"] = [r for r in spec["rules"] if not str(r["plans"]).startswith("QHP_")] + rules
    json.dump(spec, open(SPEC, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(f"{len(rules)} evidence entries for {len(roster())} plans: {dict(stats)}")


if __name__ == "__main__":
    main()
