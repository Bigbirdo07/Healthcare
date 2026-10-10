#!/usr/bin/env python3
"""Build the browser provider index from the reproducible research ZIP."""

from __future__ import annotations

import csv
import io
import json
import sys
import zipfile
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DEFAULT_ARCHIVE = ROOT / "ri_provider_directory_research_2026-09-24.zip"
MEDICAID_STATUS_FILE = ROOT / "data" / "ri_doctor_medicaid_status.csv"
OUTPUT = ROOT / "dist" / "providers.json"

PROVIDER_FIELDS = (
    "provider_record_id",
    "npi",
    "first_name",
    "middle_name",
    "last_name",
    "suffix",
    "credentials",
    "practice_name",
    "provider_category",
    "taxonomy_description",
    "specialty",
    "subspecialty",
    "license_status",
    "license_active_status",
    "address_line_1",
    "address_line_2",
    "city",
    "state",
    "zip",
    "public_phone",
    "public_website",
    "profile_page_url",
    "telehealth_status",
    "wheelchair_accessible_status",
    "accepting_new_patients_status",
    "medicare_enrollment_status",
    "medicare_assignment_status",
    "ri_medicaid_ffs_status",
    "last_verified_at",
    "record_confidence",
    "manual_review_required",
    "routing_status",
)


def read_csv(archive: zipfile.ZipFile, name: str) -> list[dict[str, str]]:
    with archive.open(name) as raw:
        text = io.TextIOWrapper(raw, encoding="utf-8-sig", newline="")
        return list(csv.DictReader(text))


def main() -> int:
    archive_path = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_ARCHIVE
    if not archive_path.is_file():
        raise SystemExit(f"Research archive not found: {archive_path}")

    with zipfile.ZipFile(archive_path) as archive:
        providers = [
            {field: value for field in PROVIDER_FIELDS if (value := row.get(field, ""))}
            for row in read_csv(archive, "ri_providers.csv")
        ]
        networks = read_csv(archive, "ri_provider_networks.csv")
        languages = read_csv(archive, "ri_provider_languages.csv")
        sources = read_csv(archive, "ri_provider_sources.csv")
        validation = json.loads(archive.read("validation_summary.json"))

    if validation.get("provider_records") != len(providers):
        raise SystemExit("Provider count does not match validation_summary.json")
    if any(row.get("state") != "RI" for row in providers):
        raise SystemExit("Provider import contains a non-Rhode Island record")
    if len({row["provider_record_id"] for row in providers}) != len(providers):
        raise SystemExit("Provider record IDs are not unique")

    medicaid_counts: Counter[str] = Counter()
    if MEDICAID_STATUS_FILE.is_file():
        with MEDICAID_STATUS_FILE.open(newline="", encoding="utf-8-sig") as stream:
            medicaid_rows = list(csv.DictReader(stream))
        medicaid_by_npi = {row["NPI"]: row for row in medicaid_rows}
        if len(medicaid_by_npi) != len(medicaid_rows):
            raise SystemExit("Medicaid status file contains duplicate NPIs")
        provider_npis = {row.get("npi") for row in providers if row.get("npi")}
        if set(medicaid_by_npi) != provider_npis:
            raise SystemExit("Medicaid status NPIs do not exactly match the provider baseline")
        normalized = {
            "Active": "historical_active",
            "Eligibility verification only": "eligibility_verification_only",
            "No RI record in 2018–2024 extract": "no_record_in_extract",
            "Terminated": "terminated",
            "Conflicting latest records": "source_conflict",
            "Active — do not pay": "active_do_not_pay",
            "Other/unclear": "unclear",
        }
        medicaid_counts.update(row["Medicaid enrollment status"] for row in medicaid_rows)
        for provider in providers:
            medicaid = medicaid_by_npi[provider["npi"]]
            label = medicaid["Medicaid enrollment status"]
            provider["ri_medicaid_ffs_status"] = normalized.get(label, "unclear")
            provider["ri_medicaid_enrollment_label"] = label

    counts = Counter(row.get("provider_category") or "unknown" for row in providers)
    unique_npis = len({row["npi"] for row in providers if row.get("npi")})
    payload = {
        "meta": {
            "state": "RI",
            "generated_at": validation.get("validated_at"),
            "status": "cms_baseline_imported",
            "schema_version": 1,
            "record_count": len(providers),
            "unique_npi_count": unique_npis,
            "category_counts": dict(sorted(counts.items())),
            "scope_note": "CMS Medicare Care Compare baseline; not a complete statewide directory.",
            "unverified_fields": [
                "Rhode Island license",
                "current 2026 Medicaid participation",
                "Medicaid managed-care plan participation",
                "commercial plan networks",
                "language support",
                "accessibility",
                "accepting new patients",
                "practice inquiry routing",
            ],
            "medicaid_status_data_through": "2024-12-31" if medicaid_counts else None,
            "medicaid_status_counts_by_unique_npi": dict(sorted(medicaid_counts.items())),
        },
        "providers": providers,
        "networks": networks,
        "languages": languages,
        "sources": sources,
    }
    OUTPUT.write_text(json.dumps(payload, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(providers):,} provider-location records ({unique_npis:,} NPIs) to {OUTPUT}")
    print(f"Category counts: {dict(sorted(counts.items()))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
