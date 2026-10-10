"""Build dist/providers/ny.json, the New York provider directory baseline.

Same approach as Rhode Island: every New York row of the CMS Doctors and
Clinicians National Downloadable File (Medicare Care Compare) is the baseline,
and each NPI is joined to New York's own Medicaid Enrolled Provider Listing
(NYS DOH / eMedNY, health.data.ny.gov dataset keti-qx5t).

Unlike the 2018-2024 extract used for New England, the NY listing is current:
it holds only *active* enrollments, so an NPI's Medicaid type there is a fact
as of the listing's FILE DATE. Being enrolled does not prove a provider is in
a given managed care plan's network or is taking new patients.

Inputs (data/ny_downloads/):
  DAC_NationalDownloadableFile.csv
  NY_MEDICAID_ENROLLED_PROVIDER_LISTING.csv
Usage: python3 scratch/build_ny_providers.py
"""
import collections
import csv
import hashlib
import json
import os
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "data", "ny_downloads")
DAC = os.path.join(SRC, "DAC_NationalDownloadableFile.csv")
MEDICAID = os.path.join(SRC, "NY_MEDICAID_ENROLLED_PROVIDER_LISTING.csv")
OUT = os.path.join(ROOT, "dist", "providers", "ny.json")

DAC_URL = "https://data.cms.gov/provider-data/sites/default/files/resources/52c3f098d7e56028a298fd297cb0b38d_1787091341/DAC_NationalDownloadableFile.csv"
MEDICAID_URL = "https://health.data.ny.gov/Health/Medicaid-Enrolled-Provider-Listing/keti-qx5t"

DENTAL = {"DENTIST", "ORAL SURGERY", "ENDODONTICS", "PEDIATRIC DENTISTRY", "ORAL AND MAXILLOFACIAL SURGERY",
          "PERIODONTICS", "PROSTHODONTICS", "ORTHODONTICS", "MAXILLOFACIAL SURGERY", "ORAL MEDICINE"}

# Medicaid type -> (status code, label). Definitions are the dataset's own:
# FFS = enrolled in fee-for-service (may or may not be in managed care);
# MCO = managed care only, cannot bill fee-for-service;
# OPRA = enrolled only to order, prescribe, refer or attend - cannot bill.
STATUS = [
    ("FFS", "active_ffs", "Enrolled (fee-for-service)"),
    ("MCO", "active_managed_care_only", "Enrolled (managed care only)"),
    ("OPRA", "active_opra_only", "Enrolled to order/prescribe/refer only"),
]
NO_RECORD = ("not_in_current_listing", "Not in current NY Medicaid listing")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def category(spec):
    if spec in DENTAL:
        return "dentist"
    if spec == "OPHTHALMOLOGY":
        return "ophthalmologist"
    if spec == "OPTOMETRY":
        return "optometrist"
    return "doctor_or_other_clinician"


def main():
    types, file_dates = collections.defaultdict(set), collections.Counter()
    with open(MEDICAID, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            file_dates[row["FILE DATE"]] += 1
            if row["NPI"]:
                types[row["NPI"]].add(row["MEDICAID TYPE"])
    file_date = datetime.strptime(file_dates.most_common(1)[0][0], "%m/%d/%Y").date().isoformat()

    def medicaid(npi):
        found = types.get(npi, set())
        for code, status, label in STATUS:
            if code in found:
                return status, label
        return NO_RECORD

    # 213k rows: fields the provider page can derive (state, NPI Registry link,
    # Medicaid label from status) are left out to keep the file loadable.
    columns = ["npi", "first_name", "middle_name", "last_name", "suffix", "credentials",
               "provider_category", "specialty", "practice_name", "address_line_1", "address_line_2", "city",
               "zip", "public_phone", "telehealth_status", "medicare_assignment_status", "ri_medicaid_ffs_status"]
    rows, seen = [], set()
    with open(DAC, encoding="utf-8", errors="replace") as f:
        for r in csv.DictReader(f):
            if r["State"] != "NY":
                continue
            key = (r["NPI"], r["adrs_id"])
            if key in seen:
                continue
            seen.add(key)
            status, _ = medicaid(r["NPI"])
            zip_code = r["ZIP Code"]
            if len(zip_code) == 9:
                zip_code = f"{zip_code[:5]}-{zip_code[5:]}"
            record = {
                "npi": r["NPI"],
                "first_name": r["Provider First Name"],
                "middle_name": r["Provider Middle Name"],
                "last_name": r["Provider Last Name"],
                "suffix": r["suff"],
                "credentials": r["Cred"],
                "provider_category": category(r["pri_spec"]),
                "specialty": r["pri_spec"],
                "practice_name": r["Facility Name"],
                "address_line_1": r["adr_ln_1"],
                "address_line_2": r["adr_ln_2"],
                "city": r["City/Town"],
                "zip": zip_code,
                "public_phone": r["Telephone Number"],
                "telehealth_status": "yes" if r["Telehlth"] == "Y" else "",
                "medicare_assignment_status": "yes" if r["ind_assgn"] == "Y" else "",
                "ri_medicaid_ffs_status": status,
            }
            rows.append([record[c] or "" for c in columns])

    labels = {status: label for _, status, label in STATUS} | {NO_RECORD[0]: NO_RECORD[1]}
    by_npi = {}
    for row in rows:
        by_npi[row[0]] = (row[columns.index("provider_category")], labels[row[columns.index("ri_medicaid_ffs_status")]])
    meta = {
        "state": "NY",
        "state_name": "New York",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": "cms_baseline_imported",
        "schema_version": 1,
        "record_count": len(rows),
        "unique_npi_count": len(by_npi),
        "category_counts": dict(sorted(collections.Counter(c for c, _ in by_npi.values()).items())),
        "scope_note": "CMS Medicare Care Compare baseline (clinicians who bill Medicare); not a complete statewide directory.",
        "medicaid_status_source": "NYS DOH Medicaid Enrolled Provider Listing (eMedNY)",
        "medicaid_status_as_of": file_date,
        "medicaid_status_note": "Current active NY Medicaid enrollment as of the listing date. Does not confirm a managed care plan network or new-patient acceptance.",
        "medicaid_status_labels": labels,
        "medicaid_status_counts_by_unique_npi": dict(collections.Counter(label for _, label in by_npi.values()).most_common()),
        "unverified_fields": ["New York license", "Medicaid managed-care plan participation", "commercial plan networks",
                              "language support", "accessibility", "accepting new patients"],
        "sources": [
            {"source_id": "CMS_CARE_COMPARE", "source_name": "Doctors and Clinicians National Downloadable File",
             "authority": "Centers for Medicare & Medicaid Services", "url": DAC_URL, "sha256": sha256(DAC)},
            {"source_id": "NY_MEDICAID_ENROLLED_PROVIDERS", "source_name": "Medicaid Enrolled Provider Listing",
             "authority": "New York State Department of Health", "url": MEDICAID_URL, "file_date": file_date,
             "sha256": sha256(MEDICAID)},
        ],
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"meta": meta, "row_defaults": {"state": "NY", "medicare_enrollment_status": "yes"},
                   "provider_columns": columns, "provider_rows": rows, "networks": [], "languages": []},
                  f, separators=(",", ":"), ensure_ascii=False)
    print(json.dumps(meta, indent=1))
    print(f"Wrote {os.path.relpath(OUT, ROOT)} ({os.path.getsize(OUT) / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
