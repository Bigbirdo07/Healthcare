"""Official New York 2026 plan roster for the marketplace selector.

Same sources as the Rhode Island roster, plus New York's own Medicaid list:
  Medicare      CMS CY2026 MA/PD Landscape (September 2026), State = NY
  Individual /  CMS 2026 New York State-Based Exchange PUF (NYPlans), medical
  small group   plans only; issuer names from the CMS 2026 Unified Rate Review PUF
  Medicaid      NYS DOH Medicaid Managed Care Enrollment Report, September 2026,
                Table IIb (plans with enrollees), counties from Table IIa

Writes data/ny_verified_coverage_2026/NY_OFFICIAL_PLAN_ROSTER.csv and the
"new_plans" of data/ny_verified_coverage_2026/evidence_spec.json (the NY
selector plans; NY has no older plan rows to replace).
Usage: python3 scratch/build_ny_roster.py
"""
import csv
import io
import json
import os
import re
import zipfile

import pypdf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDX = os.path.join(ROOT, "data", "official_source_indexes_2026")
OUT_DIR = os.path.join(ROOT, "data", "ny_verified_coverage_2026")
LANDSCAPE = os.path.join(IDX, "CMS_MA_PD_LANDSCAPE_75f2797b5104.zip")
SBE = os.path.join(IDX, "SBE_NEW_YORK_add2693a835b.zip")
URR = os.path.join(IDX, "CMS_URR_PUF_2026_9575fccc0ec2.zip")
ENROLLMENT = os.path.join(IDX, "NY_DOH_MMC_ENROLLMENT_2026_09_b94538f19f80.pdf")

# HIOS issuer ID -> (selector insurer id, name on the card). Company names are
# the CMS 2026 URR PUF's; IDs sharing a brand are grouped under one card name.
QHP_ISSUERS = {
    "11177": ("metroplus", "MetroPlusHealth"),
    "18029": ("independent_health", "Independent Health"),
    "25303": ("fidelis", "Fidelis Care (Ambetter from Fidelis Care)"),
    "40064": ("highmark_ny", "Highmark BlueCross BlueShield of Western and Northeastern New York"),
    "41046": ("anthem_ny", "Anthem Blue Cross and Blue Shield"),
    "44113": ("anthem_ny", "Anthem Blue Cross and Blue Shield"),
    "54235": ("unitedhealthcare", "UnitedHealthcare"),
    "85629": ("oxford_uhc", "Oxford Health Insurance (UnitedHealthcare)"),
    "56184": ("mvp", "MVP Health Care"),
    "89846": ("mvp", "MVP Health Care"),
    "74289": ("oscar", "Oscar Health"),
    "78124": ("excellus", "Excellus BlueCross BlueShield"),
    "88582": ("emblemhealth", "EmblemHealth"),
    "91237": ("healthfirst", "Healthfirst"),
    "92551": ("cdphp", "CDPHP"),
    "94788": ("cdphp", "CDPHP"),
}

# Enrollment-report plan name -> (id key, insurer id, insurer name, plan name).
# Insurer names follow the NYS DOH member handbook page.
MEDICAID = {
    "ANTHEM BLUE CROSS AND BLUE SHIELD": ("ANTHEM", "anthem_ny", "Anthem Blue Cross and Blue Shield HP", "Anthem Blue Cross and Blue Shield HP - Medicaid Managed Care"),
    "CAPITAL DISTRICT PHYSICIANS HEALTH PLAN": ("CDPHP", "cdphp", "CDPHP (Capital District Physicians' Health Plan)", "CDPHP - Medicaid Managed Care"),
    "EXCELLUS HEALTH PLAN": ("EXCELLUS", "excellus", "Excellus Health Plan (Excellus BlueCross BlueShield / Univera Healthcare)", "Excellus Health Plan - Medicaid Managed Care"),
    "FIDELIS CARE": ("FIDELIS", "fidelis", "Fidelis Care (New York Quality Healthcare Corporation)", "Fidelis Care - Medicaid Managed Care"),
    "HEALTHFIRST PHSP": ("HEALTHFIRST", "healthfirst", "Healthfirst", "Healthfirst - Medicaid Managed Care"),
    "HIGHMARK WESTERN AND NORTHEASTERN NEW YORK INC.": ("HIGHMARK", "highmark_ny", "Highmark Western and Northeastern New York", "Highmark - Medicaid Managed Care"),
    "HIP OF GREATER NEW YORK": ("EMBLEM", "emblemhealth", "EmblemHealth (Health Insurance Plan of Greater New York)", "EmblemHealth Enhanced Care - Medicaid Managed Care"),
    "INDEPENDENT HEALTH ASSOCIATION": ("INDEPENDENT", "independent_health", "Independent Health", "Independent Health MediSource - Medicaid Managed Care"),
    "METROPLUS HEALTH PLAN": ("METROPLUS", "metroplus", "MetroPlusHealth", "MetroPlusHealth - Medicaid Managed Care"),
    "METROPLUS SN": ("METROPLUS_SNP", "metroplus", "MetroPlusHealth", "MetroPlusHealth - HIV Special Needs Plan"),
    "MOLINA HEALTHCARE OF NEW YORK": ("MOLINA", "molina", "Molina Healthcare of New York (incl. Affinity by Molina)", "Molina Healthcare - Medicaid Managed Care"),
    "MVP HEALTH PLAN": ("MVP", "mvp", "MVP Health Care", "MVP Health Plan - Medicaid Managed Care"),
    "UNITED HEALTHCARE": ("UHC", "unitedhealthcare", "UnitedHealthcare Community Plan", "UnitedHealthcare Community Plan - Medicaid Managed Care"),
    "AMIDA CARE SN": ("AMIDA", "amida", "Amida Care", "Amida Care - HIV Special Needs Plan"),
    "VNS CHOICE SNP": ("VNS_SNP", "vns_health", "VNS Health", "VNS Health - HIV Special Needs Plan"),
}

COMMON = {"plan_year": 2026, "state": "NY", "source_status": "SOURCE_CONFIRMED", "is_test_fixture": False,
          "environment": "PRODUCTION", "production_visibility": True}


def norm(s):
    return re.sub(r"\s+", " ", s).strip().rstrip(",").strip()


def medicare():
    with zipfile.ZipFile(LANDSCAPE) as z:
        name = next(n for n in z.namelist() if n.endswith(".csv"))
        rows = csv.DictReader(io.TextIOWrapper(z.open(name), encoding="utf-8-sig"))
        plans = {}
        for r in rows:
            if r["Contract Year"] != "2026" or r["State Territory Abbreviation"] != "NY":
                continue
            pbp, seg = r["Plan ID"].zfill(3), r["Segment ID"].zfill(3)
            key = f"CMS:NY:{r['Contract ID']}:{pbp}:{seg}:2026"
            p = plans.setdefault(key, {"row": r, "counties": set()})
            p["counties"].add(r["County Name"])
    out = []
    for key, p in sorted(plans.items()):
        r = p["row"]
        pdp = r["Plan Type"] == "PDP"
        insurer = r["Organization Marketing Name"]
        out.append({
            "id": key, "canonical_plan_key": key,
            "insurer_id": "ny_mcr_" + re.sub(r"[^a-z0-9]+", "_", insurer.lower()).strip("_"), "insurer_name": insurer,
            "official_plan_name": r["Plan Name"], "display_name": r["Plan Name"], **COMMON,
            "plan_type": r["Plan Type"],
            "insurance_category": "Medicare Part D" if pdp else "Medicare Advantage",
            "category_display": "Medicare Part D" if pdp else "Medicare Advantage",
            "contract_id": r["Contract ID"], "plan_id": r["Plan ID"].zfill(3), "segment_id": r["Segment ID"].zfill(3),
            "market_segment": "MEDICARE_PART_D" if pdp else "MEDICARE_ADVANTAGE",
            "plan_identity_status": "OFFICIAL_2026_ROSTER_VERIFIED",
            "official_roster_source": "CMS_MA_PD_LANDSCAPE_202609",
            "service_area_counties": sorted(p["counties"]),
            "_roster": {"market": "MEDICARE", "issuer": insurer, "part_d": r["Part D Coverage Indicator"]},
        })
    return out


def qhp():
    with zipfile.ZipFile(URR) as z:
        name = next(n for n in z.namelist() if "WKSH1" in n)
        urr = {r["ISSUER_ID"] for r in csv.DictReader(io.TextIOWrapper(z.open(name), encoding="latin-1")) if r["STATE"] == "NY"}
    missing = set(QHP_ISSUERS) - urr
    if missing:
        raise SystemExit(f"issuer IDs not in the CMS URR PUF for NY: {sorted(missing)}")
    with zipfile.ZipFile(SBE) as z:
        name = next(n for n in z.namelist() if re.fullmatch(r"NYPlans.*\.csv", n))
        rows = list(csv.DictReader(io.TextIOWrapper(z.open(name), encoding="utf-8-sig")))
    plans = {}
    for r in rows:
        if r["BUSINESS YEAR"] != "2026" or r["STATE CODE"] != "NY" or r["DENTAL ONLY PLAN"] != "No":
            continue
        plans.setdefault(r["STANDARD COMPONENT ID"], r)
    out = []
    for comp, r in sorted(plans.items()):
        insurer_id, insurer = QHP_ISSUERS[r["ISSUER ID"]]
        name = norm(r["PLAN MARKETING NAME"])
        if r["ISSUER ID"] == "78124" and name.startswith("Univera"):
            insurer_id, insurer = "univera", "Univera Healthcare"
        individual = r["MARKET COVERAGE"] == "Individual"
        key = f"QHP:NY:{comp}:2026"
        out.append({
            "id": key, "canonical_plan_key": key, "insurer_id": insurer_id, "insurer_name": insurer,
            "official_plan_name": name, "display_name": name, **COMMON, "plan_type": r["PLAN TYPE"],
            "insurance_category": "Individual / ACA" if individual else "Small Group",
            "category_display": "Individual Marketplace" if individual else "Small Group / Employer",
            "contract_id": "N/A", "plan_id": "N/A", "segment_id": "000",
            "market_segment": "INDIVIDUAL_ACA" if individual else "SMALL_GROUP",
            "metal_level": r["METAL LEVEL"],
            "plan_identity_status": "OFFICIAL_2026_ROSTER_VERIFIED", "official_roster_source": "CMS_NY_SBE_PUF_2026",
            "_roster": {"market": r["MARKET COVERAGE"], "issuer": r["ISSUER ID"], "part_d": ""},
        })
    return out


def medicaid():
    reader = pypdf.PdfReader(ENROLLMENT)
    counties, statewide = {}, set()
    county = None  # a county's rows can continue onto the next page
    for page in reader.pages:
        text = page.extract_text()
        table = "IIa" if "TABLE IIa." in text else "IIb" if "TABLE IIb." in text else None
        for line in text.split("\n"):
            line = line.strip()
            if " Total " in f" {line} ":
                county = None
                continue
            m = re.match(r"^(.*?)\s+[\d,]+(?:\s+[\d,]+){3,}$", line)
            if not m:
                continue
            label = m.group(1)
            if label.startswith("NEW YORK CITY NEW YORK CITY "):
                county, label = "NEW YORK CITY", label[len("NEW YORK CITY NEW YORK CITY "):]
            label = re.sub(r"^UPSTATE\s+", "", label)
            plan = next((p for p in MEDICAID if label.endswith(p)), None)
            if not plan:
                continue
            if table == "IIb":
                statewide.add(plan)
            elif table == "IIa":
                county = label[: -len(plan)].strip() or county
                if not county:
                    raise SystemExit(f"no county for enrollment row: {line!r}")
                counties.setdefault(plan, set()).add(county)
    if statewide != set(MEDICAID):
        raise SystemExit(f"Medicaid roster mismatch: report {sorted(statewide)} vs mapping {sorted(MEDICAID)}")
    out = []
    for report_name, (key, insurer_id, insurer, name) in MEDICAID.items():
        snp = "HIV Special Needs" in name
        out.append({
            "id": f"NYMCD:{key}:2026", "canonical_plan_key": f"NYMCD:{key}:2026", "insurer_id": insurer_id, "insurer_name": insurer,
            "official_plan_name": name, "display_name": name, **COMMON,
            "plan_type": "HIV Special Needs Plan (Medicaid)" if snp else "Medicaid Managed Care",
            "insurance_category": "Medicaid", "category_display": "Medicaid", "market_segment": "MEDICAID",
            "plan_identity_status": "STATE_LISTED_MEDICAID_MCO",
            "official_roster_source": "NY_DOH_MMC_ENROLLMENT_REPORT_2026_09",
            "state_report_name": report_name,
            "service_area_counties": sorted(c.title() for c in counties.get(report_name, ())),
            "_roster": {"market": "MEDICAID", "issuer": insurer, "part_d": ""},
        })
    return out


ORIGINAL_MEDICARE = {
    "id": "CMS:NY:ORIGINAL_MEDICARE:2026", "canonical_plan_key": "CMS:ORIGINAL_MEDICARE:2026", "insurer_id": "original_medicare",
    "insurer_name": "Original Medicare (red, white & blue Medicare card)", "official_plan_name": "Original Medicare - Part A & Part B",
    "display_name": "Original Medicare - Part A & Part B", **COMMON, "plan_type": "Original Medicare",
    "insurance_category": "Original Medicare", "category_display": "Original Medicare", "market_segment": "ORIGINAL_MEDICARE",
    "plan_identity_status": "FEDERAL_PROGRAM", "official_roster_source": "CMS_YOUR_MEDICARE_BENEFITS",
}


def main():
    plans = medicare() + qhp() + medicaid()
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "NY_OFFICIAL_PLAN_ROSTER.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["official_plan_key", "state", "market", "contract_id", "pbp_id", "segment_id", "official_plan_name", "issuer", "plan_type", "part_d", "source"])
        for p in plans:
            r = p["_roster"]
            w.writerow([p["id"], "NY", r["market"], p.get("contract_id", "").replace("N/A", ""), p.get("plan_id", "").replace("N/A", ""),
                        p.get("segment_id", "") if r["market"] == "MEDICARE" else "", p["official_plan_name"], r["issuer"], p["plan_type"],
                        r["part_d"], p["official_roster_source"]])
    for p in plans:
        del p["_roster"]
    spec_path = os.path.join(OUT_DIR, "evidence_spec.json")
    spec = json.load(open(spec_path, encoding="utf-8")) if os.path.exists(spec_path) else {
        "_readme": "Hand-curated and generated New York 2026 coverage evidence. Every rule must quote its source document verbatim "
                   "(whitespace-insensitive). scratch/build_ri_verified_rules.py refuses to build if any excerpt is not found in the "
                   "cited document or if a document's SHA-256 changed. Plans without rules show as 'benefits under review'.",
        "state": "NY", "sources": {}, "plans": {}, "new_plans": [], "new_benefits": [], "groups": {}, "templates": {}, "rules": []}
    spec["new_plans"] = [ORIGINAL_MEDICARE] + plans
    json.dump(spec, open(spec_path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    counts = {}
    for p in spec["new_plans"]:
        counts[p["market_segment"]] = counts.get(p["market_segment"], 0) + 1
    print(f"NY roster: {len(spec['new_plans'])} plans {counts}")


if __name__ == "__main__":
    main()
