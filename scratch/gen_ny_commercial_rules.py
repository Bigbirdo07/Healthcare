"""Generate evidence_spec rules for New York individual and small-group plans
from the CMS 2026 New York State-Based Exchange PUF (NYBenefits / NYPlans).

The New York counterpart of gen_ri_commercial_rules.py: each rule quotes its
plan's CMS row verbatim, so build_ri_verified_rules.py re-checks it against the
hashed zip. Dollar copays are not in the benefits file, so item costs point to
the plan's Summary of Benefits and Coverage; plan-level deductible / MOOP /
coinsurance come from the NYPlans row.

Usage: python3 scratch/build_ny_roster.py && python3 scratch/gen_ny_commercial_rules.py
       python3 scratch/build_ri_verified_rules.py data/ny_verified_coverage_2026/evidence_spec.json
"""
import collections
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
import build_ri_verified_rules as B
from gen_ri_commercial_rules import PLAN_FIELDS, cut, explanation, limit

ROOT = B.ROOT
SPEC = os.path.join(ROOT, "data/ny_verified_coverage_2026/evidence_spec.json")
ZIP = "data/official_source_indexes_2026/SBE_NEW_YORK_add2693a835b.zip"
URL = "https://www.cms.gov/files/zip/newyorksbepuf2026.zip"
SRC, PLANS_SRC, SPLIT_SRC = "CMS_NY_SBE_PUF", "CMS_NY_SBE_PLANS", "CMS_NY_SBE_PLANS_SPLIT_DED"
# NY plans file either an integrated medical+drug deductible (TEHB columns, as
# in RI) or separate medical (MEHB) and drug (DEHB) deductibles; the MOOP is
# always the TEHB total. Each plan quotes the row layout it actually filed.
SPLIT_FIELDS = [["Variation", "CSR VARIATION TYPE"], ["Medical deductible (individual)", "MEHB DED INN TIER1 INDIVIDUAL"],
                ["Medical deductible (family)", "MEHB DED INN TIER1 FAMILY"], ["Drug deductible (individual)", "DEHB DED INN TIER1 INDIVIDUAL"],
                ["Out-of-pocket max (individual)", "TEHB INN TIER 1 INDIVIDUAL MOOP"], ["Out-of-pocket max (family)", "TEHB INN TIER 1 FAMILY MOOP"],
                ["Coinsurance after deductible", "MEHB DED INN TIER1 COINSURNACE"]]

TEMPLATES = {
    "DME": {"pathway": "Durable medical equipment (medical benefit)",
            "requirements": "Must be medically necessary and ordered by your provider; use a plan-contracted DME supplier; prior authorization may be required"},
    "QHP_HEARING": {"pathway": "Hearing aids (medical benefit)",
                    "requirements": "Through a network hearing provider; the limits in the plan's filing apply"},
}
GROUPS = {"DME": ["P-MOB-CANES", "P-MOB-ROLLATOR", "P-MOB-WHEELCHAIR", "P-RSP-CPAP"], "HEARING_PRODUCT": ["P-EAR-HEARING"]}


def main():
    spec = json.load(open(SPEC, encoding="utf-8"))
    sha = hashlib.sha256(open(os.path.join(ROOT, ZIP), "rb").read()).hexdigest()
    spec["sources"][SRC] = {"file": ZIP, "sha256": sha, "url": URL, "format": "csv_rows", "zip_member": "NYBenefits05052026.csv",
                            "title": "CMS 2026 New York State-Based Exchange PUF - plan benefits (NYBenefits05052026.csv)"}
    spec["sources"][PLANS_SRC] = {"file": ZIP, "sha256": sha, "url": URL, "format": "csv_rows", "zip_member": "NYPlans05052026.csv",
                                  "fields": PLAN_FIELDS, "title": "CMS 2026 New York State-Based Exchange PUF - plan attributes (NYPlans05052026.csv)"}
    spec["sources"][SPLIT_SRC] = {**spec["sources"][PLANS_SRC], "fields": SPLIT_FIELDS,
                                  "title": "CMS 2026 New York State-Based Exchange PUF - plan attributes, separate medical/drug deductibles (NYPlans05052026.csv)"}
    spec["templates"].update(TEMPLATES)
    spec["groups"].update(GROUPS)

    def rows_by_plan(src, label):
        rows = {re.match(r"PLAN (\S+) ·", r).group(1): r for r in B.load_source(spec["sources"][src])}
        return {k: (src, r) for k, r in rows.items() if not re.search(re.escape(label) + r": ·", r + " ·")}
    # A plan's row counts only if its deductible column is filled in.
    plan_rows = {**rows_by_plan(SPLIT_SRC, "Medical deductible (individual)"), **rows_by_plan(PLANS_SRC, "Deductible (individual)")}
    index = {}
    for row in B.load_source(spec["sources"][SRC]):
        m = re.match(r"PLAN (\w+)-(\d\d) · ([^·]+?) · ", row)
        if m:
            index.setdefault((m.group(1), m.group(3)), {})[m.group(2)] = row

    def get(pid, benefit):
        variants = index.get((pid, benefit), {})
        return variants.get("01") or (variants[sorted(variants)[0]] if variants else None)

    roster = [(p["id"], p["market_segment"]) for p in spec["new_plans"] if p["id"].startswith("QHP:NY:")]
    rules, stats = [], collections.Counter()
    for plan_id, market in roster:
        pid = plan_id.split(":")[2]
        key = "QHP_" + pid
        spec["plans"][key] = [plan_id]
        psrc, prow = plan_rows.get(pid + "-01", (None, None))
        field = lambda label: re.search(re.escape(label) + r": ([^·]*)", prow).group(1).strip() if prow else ""
        split = psrc == SPLIT_SRC
        # The PUF says "Not Applicable" when a plan has no deductible.
        amount = lambda label: "$0" if field(label).lower().startswith("not applicable") else field(label)
        ded = amount("Medical deductible (individual)") if split else amount("Deductible (individual)")
        moop, coins = field("Out-of-pocket max (individual)"), (field("Coinsurance after deductible") or "0.00%").replace(".00%", "%")
        if split:
            ded = f"{ded} medical / {amount('Drug deductible (individual)')} drug"
        COST = (f"Plan terms: {ded} deductible, then {coins} coinsurance (out-of-pocket max {moop}); this item's exact cost is in the plan's SBC"
                if prow else "Your plan's deductible, copay or coinsurance applies - see the plan's Summary of Benefits and Coverage")
        cite = [{"source": psrc, "text": prow}] if prow else []
        R = lambda **kw: dict(plans=key, source=SRC, **{**kw, "excerpts": kw["excerpts"] + (cite if kw.get("member_cost") == COST else [])})

        if prow:
            # Family amounts read "$X per person | $Y per group"; aggregate (HSA-style)
            # plans have no per-person amount.
            family = lambda label: field(label).replace("per person not applicable | per group not applicable", "none").replace("per person not applicable | ", "")
            fam = family("Medical deductible (family)" if split else "Deductible (family)")
            rules.append(dict(plans=key, source=psrc, targets="B-RI26-PLAN-COSTS", type="BENEFIT", status="Covered", pathway="Plan cost sharing (in-network)",
                              member_cost=f"Deductible {ded} individual (family: {fam}); out-of-pocket max {moop} individual (family: {family('Out-of-pocket max (family)')}); {coins} coinsurance after the deductible",
                              requirements="In-network amounts for the standard plan version; members in a cost-sharing-reduction or zero-cost-sharing version pay less",
                              excerpts=[prow]))
            stats["plan_costs"] += 1

        dme = get(pid, "Durable Medical Equipment")
        if dme and "Covered: Yes" in dme:
            rules.append(R(targets="DME", template="DME", status="Conditional", member_cost=COST, excerpts=[cut(dme, "Limit")]))
            stats["dme"] += 1

        hear = get(pid, "Hearing Aids")
        if hear and "Covered: Yes" in hear:
            req = "; ".join(x for x in [("Limit: " + limit(hear)) if limit(hear) else "", explanation(hear)] if x) or TEMPLATES["QHP_HEARING"]["requirements"]
            rules += [R(targets="HEARING_PRODUCT", template="QHP_HEARING", status="Conditional", member_cost=COST, excerpts=[hear]),
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
                           requirements=explanation(adult) or (f"Limit: {limit(adult)}" if limit(adult) else "Network dentist"), excerpts=[adult]))
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
                           requirements=(explanation(basic) or (f"Limit: {limit(basic)}" if limit(basic) else "Network dentist")) if yes else "Adult basic dental care is not covered",
                           excerpts=[basic if yes else cut(basic, "Limit")]))
            stats["adult_basic_dental"] += 1

        prev = get(pid, "Preventive Care/Screening/Immunization")
        if prev and "Covered: Yes" in prev:
            rules.append(R(targets="S-PREV-WELLNESS", type="SERVICE", status="Covered", pathway="Preventive care", member_cost=COST,
                           requirements="In-network preventive care" + (f"; limit: {limit(prev)}" if limit(prev) else ""),
                           excerpts=[cut(prev, "Exclusions")]))
            stats["preventive"] += 1

    spec["rules"] = [r for r in spec["rules"] if not str(r["plans"]).startswith("QHP_")] + rules
    json.dump(spec, open(SPEC, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(f"{len(rules)} evidence entries for {len(roster)} plans: {dict(stats)}")


if __name__ == "__main__":
    main()
