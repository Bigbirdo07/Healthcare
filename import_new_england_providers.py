#!/usr/bin/env python3
"""Split the supplied New England provider/Medicaid extract into lazy state indexes."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "newengland_provider_medicaid_status.csv"
OUTPUT_DIR = ROOT / "dist" / "providers"
STATES = {"CT": "Connecticut", "MA": "Massachusetts", "ME": "Maine", "NH": "New Hampshire", "VT": "Vermont"}
DATA_THROUGH = "2024-12-31"

COLUMNS = [
    "provider_record_id",
    "npi",
    "first_name",
    "last_name",
    "credentials",
    "provider_category",
    "specialty",
    "city",
    "state",
    "zip",
    "public_phone",
    "ri_medicaid_ffs_status",
    "ri_medicaid_enrollment_label",
    "medicaid_status_raw",
    "medicaid_plan",
    "medicaid_latest_segment_end",
]

NORMALIZED_STATUS = {
    "Active": "historical_active",
    "Active - Do Not Pay": "active_do_not_pay",
    "No Medicaid record in extract": "no_record_in_extract",
    "Other/Unclear": "unclear",
    "Denied": "denied",
}


def category_for(specialty: str) -> str:
    value = specialty.upper()
    if re.search(r"DENTIST|DENTAL|ORAL SURGERY", value):
        return "dentist"
    if "OPHTHAL" in value:
        return "ophthalmologist"
    if "OPTOMET" in value:
        return "optometrist"
    if "OPTICIAN" in value:
        return "optician"
    return "doctor_or_other_clinician"


def main() -> int:
    if not SOURCE.is_file():
        raise SystemExit(f"Source file not found: {SOURCE}")
    state_rows: dict[str, list[list[str]]] = defaultdict(list)
    state_npis: dict[str, set[str]] = defaultdict(set)
    category_counts: dict[str, Counter[str]] = defaultdict(Counter)
    status_counts: dict[str, Counter[str]] = defaultdict(Counter)

    with SOURCE.open(newline="", encoding="utf-8-sig") as stream:
        for source in csv.DictReader(stream):
            state = source["State"]
            if state == "RI":
                continue  # Rhode Island retains the more complete location-level baseline.
            if state not in STATES:
                raise SystemExit(f"Unexpected state: {state}")
            npi = source["NPI"]
            if npi in state_npis[state]:
                raise SystemExit(f"Duplicate {state} NPI: {npi}")
            state_npis[state].add(npi)
            category = category_for(source["Primary_Specialty"])
            label = source["Medicaid_Status"]
            values = {
                "provider_record_id": f"{state}-{npi}",
                "npi": npi,
                "first_name": source["First_Name"],
                "last_name": source["Last_Name"],
                "credentials": source["Credential"],
                "provider_category": category,
                "specialty": source["Primary_Specialty"],
                "city": source["City"],
                "state": state,
                "zip": source["ZIP"][:5],
                "public_phone": source["Phone"],
                "ri_medicaid_ffs_status": NORMALIZED_STATUS.get(label, "unclear"),
                "ri_medicaid_enrollment_label": label,
                "medicaid_status_raw": source["Medicaid_Status_Raw"],
                "medicaid_plan": source["Medicaid_Plan"],
                "medicaid_latest_segment_end": source["Latest_Segment_End"],
            }
            state_rows[state].append([values[column] for column in COLUMNS])
            category_counts[state][category] += 1
            status_counts[state][label] += 1

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for state, state_name in STATES.items():
        payload = {
            "meta": {
                "state": state,
                "state_name": state_name,
                "status": "new_england_baseline_imported",
                "schema_version": 1,
                "record_count": len(state_rows[state]),
                "unique_npi_count": len(state_npis[state]),
                "category_counts": dict(sorted(category_counts[state].items())),
                "medicaid_status_data_through": DATA_THROUGH,
                "medicaid_status_counts_by_unique_npi": dict(sorted(status_counts[state].items())),
                "scope_note": "Supplied New England provider baseline with federal Medicaid enrollment status through 2024; current participation is unverified.",
            },
            "provider_columns": COLUMNS,
            "provider_rows": state_rows[state],
            "networks": [],
            "languages": [],
        }
        output = OUTPUT_DIR / f"{state.lower()}.json"
        output.write_text(json.dumps(payload, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
        print(f"{state}: wrote {len(state_rows[state]):,} unique providers to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
