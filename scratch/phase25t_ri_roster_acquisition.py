#!/usr/bin/env python3
"""Rhode Island-first official 2026 roster and source acquisition.

This pass is intentionally read-only with respect to PostgreSQL.  It builds the
selection roster from fresh official CMS bytes, compares the existing RI plan
records, and archives fresh carrier/state source responses without creating or
changing coverage rules.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import re
import urllib.parse
import zipfile
from collections import Counter
from pathlib import Path

import psycopg2

from phase25t_codex_pipeline import (
    ARCHIVE,
    HttpClient,
    baseline,
    domain_allowed,
    extract_pdf,
    identify_document_type,
    links_from_html,
    normalize_space,
    response_log_row,
    sha256_bytes,
    utcnow,
    year_from_text,
)


ROOT = Path(__file__).resolve().parents[1]
INDEX_ARCHIVE = ROOT / "data" / "official_source_indexes_2026"
PREFIX = "PHASE25T_CODEX_RI_"

CMS_INDEX_URL = "https://www.cms.gov/files/zip/cy2026-landscape-202609.zip"
SBE_INDEX_URL = "https://www.cms.gov/files/zip/rhodeislandsbepuf2026.zip"

SOURCE_URLS = [
    ("CMS_MA_PD_ROSTER", CMS_INDEX_URL, "OFFICIAL_STRUCTURED_INDEX", "ROSTER_INDEX"),
    ("CMS_RI_SBE_ROSTER", SBE_INDEX_URL, "OFFICIAL_STRUCTURED_INDEX", "ROSTER_INDEX"),
    ("HSRI_2026_INDIVIDUAL_PLAN_COMPARISON", "https://healthsourceri.com/wp-content/uploads/OE2026-IF_English_Web_Final.pdf", "OFFICIAL_STATE_EXCHANGE", "PLAN_COMPARISON"),
    ("BCBSRI_CORE_PLAN_PAGE", "https://www.bcbsri.com/medicare/shop/2026/bluechip-medicare/bluechip-medicare-core", "OFFICIAL_INSURER_PORTAL", "PLAN_PAGE"),
    ("BCBSRI_ENHANCED_PLAN_PAGE", "https://www.bcbsri.com/medicare/shop/2026/bluechip-medicare/bluechip-medicare-enhanced", "OFFICIAL_INSURER_PORTAL", "PLAN_PAGE"),
    ("BCBSRI_EXTRA_PLAN_PAGE", "https://www.bcbsri.com/medicare/shop/2026/bluechip-medicare/bluechip-medicare-extra", "OFFICIAL_INSURER_PORTAL", "PLAN_PAGE"),
    ("BCBSRI_ACCESS_PLAN_PAGE", "https://www.bcbsri.com/medicare/shop/2026/bluechip-medicare/bluechip-medicare-access", "OFFICIAL_INSURER_PORTAL", "PLAN_PAGE"),
    ("BCBSRI_DUALS_PLAN_PAGE", "https://www.bcbsri.com/medicare/shop/2026/blueri-duals/blueri-duals", "OFFICIAL_INSURER_PORTAL", "PLAN_PAGE"),
    ("BCBSRI_CORE_EOC", "https://www.bcbsri.com/sitefiles/system/files/2025-09/Y0146_2026EOCcore_C.pdf", "OFFICIAL_INSURER_DOCUMENT", "EOC"),
    ("BCBSRI_ENHANCED_EOC", "https://www.bcbsri.com/sitefiles/system/files/2025-09/Y0146_2026EOCenhanced_C.pdf", "OFFICIAL_INSURER_DOCUMENT", "EOC"),
    ("BCBSRI_EXTRA_EOC", "https://www.bcbsri.com/sitefiles/system/files/2025-10/Y0146_2026EOCextra_C_0.pdf", "OFFICIAL_INSURER_DOCUMENT", "EOC"),
    ("BCBSRI_ESSENTIAL_EOC", "https://www.bcbsri.com/sitefiles/system/files/2025-09/Y0146_2026EOCessential_C.pdf", "OFFICIAL_INSURER_DOCUMENT", "EOC"),
    ("BCBSRI_MA_SUMMARY_OF_BENEFITS", "https://www.bcbsri.com/sitefiles/system/files/2025-10/Y0146_2026bensumG_M.pdf", "OFFICIAL_INSURER_DOCUMENT", "SUMMARY_OF_BENEFITS"),
    ("BCBSRI_MEDICARE_FORMULARY_PORTAL", "https://www.bcbsri.com/medicare/member/prescriptionlookup", "OFFICIAL_INSURER_PORTAL", "FORMULARY_PORTAL"),
    ("BCBSRI_MEDICARE_DOCUMENT_INDEX", "https://www.bcbsri.com/medicare/formsresources/grievanceandappeals", "OFFICIAL_INSURER_PORTAL", "DOCUMENT_INDEX"),
    ("RI_MEDICAID_PHARMACY_PORTAL", "https://eohhs.ri.gov/providers-partners/provider-directories/pharmacy", "OFFICIAL_STATE_PROGRAM", "PHARMACY_PORTAL"),
    ("RI_MEDICAID_2026_PHARMACY_PROTOCOL", "https://eohhs.ri.gov/sites/g/files/xkgbur226/files/2026-01/2.4%20%20Pharmacy%20Benefit%20Plan%20Protocols%20-%20Effective%2001.01.26_CLEAN.pdf", "OFFICIAL_STATE_PROGRAM", "PHARMACY_PROTOCOL"),
    ("NHPRI_DUAL_CONNECT_EOC", "https://www.nhpri.org/wp-content/uploads/2025/11/H2126_1025DUALEOC_C-V2.pdf", "OFFICIAL_INSURER_DOCUMENT", "EOC"),
]


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def fresh_indexes(client: HttpClient) -> tuple[bytes, bytes, list[dict]]:
    logs = []
    payloads = []
    for name, url in (("CMS_MA_PD_ROSTER", CMS_INDEX_URL), ("CMS_RI_SBE_ROSTER", SBE_INDEX_URL)):
        resp = client.get(0, url, "OFFICIAL_STRUCTURED_INDEX", "Rhode Island 2026 official plan roster")
        row = response_log_row(resp)
        row["source_name"] = name
        row["sha256"] = sha256_bytes(resp.raw) if resp.raw else ""
        row["validation"] = "VALID_OFFICIAL_ZIP" if resp.status == 200 and resp.raw.startswith(b"PK") and domain_allowed(resp.final_url) else "INVALID_INDEX"
        row["archive_path"] = ""
        if row["validation"] == "VALID_OFFICIAL_ZIP":
            target = INDEX_ARCHIVE / f"RI_{name}_{row['sha256'][:12]}.zip"
            target.write_bytes(resp.raw)
            if sha256_bytes(target.read_bytes()) != row["sha256"]:
                raise AssertionError("roster archive SHA mismatch")
            row["archive_path"] = str(target)
        logs.append(row)
        if row["validation"] != "VALID_OFFICIAL_ZIP":
            raise RuntimeError(f"official roster download failed: {name}: {row}")
        payloads.append(resp.raw)
    return payloads[0], payloads[1], logs


def parse_cms_ri(raw: bytes) -> list[dict]:
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        csv_name = next(n for n in archive.namelist() if n.lower().endswith(".csv"))
        reader = csv.DictReader(io.TextIOWrapper(archive.open(csv_name), encoding="utf-8-sig", newline=""))
        by_key = {}
        for row in reader:
            if row["Contract Year"] != "2026" or row["State Territory Abbreviation"] != "RI":
                continue
            contract, pbp = row["Contract ID"], row["Plan ID"].zfill(3)
            segment = row["Segment ID"].zfill(3)
            key = f"CMS:RI:{contract}:{pbp}:{segment}:2026"
            by_key[key] = {
                "official_plan_key": key,
                "state": "RI",
                "market": "MEDICARE",
                "contract_id": contract,
                "pbp_id": pbp,
                "segment_id": segment,
                "official_plan_name": row["Plan Name"],
                "issuer": row["Organization Marketing Name"],
                "plan_type": row["Plan Type"],
                "part_d": row["Part D Coverage Indicator"],
                "source": "CMS_MA_PD_LANDSCAPE_202609",
            }
        return [by_key[k] for k in sorted(by_key)]


def parse_sbe_ri(raw: bytes) -> list[dict]:
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        csv_name = next(n for n in archive.namelist() if re.fullmatch(r"RIPlans.*\.csv", Path(n).name, re.I))
        reader = csv.DictReader(io.TextIOWrapper(archive.open(csv_name), encoding="utf-8-sig", newline=""))
        by_key = {}
        for row in reader:
            if row["BUSINESS YEAR"] != "2026" or row["STATE CODE"] != "RI" or row["DENTAL ONLY PLAN"] != "No":
                continue
            component = row["STANDARD COMPONENT ID"]
            key = f"QHP:RI:{component}:2026"
            by_key[key] = {
                "official_plan_key": key,
                "state": "RI",
                "market": row["MARKET COVERAGE"],
                "contract_id": "",
                "pbp_id": "",
                "segment_id": "",
                "official_plan_name": normalize_space(row["PLAN MARKETING NAME"]),
                "issuer": row["ISSUER ID"],
                "plan_type": row["PLAN TYPE"],
                "part_d": "",
                "source": "CMS_RI_SBE_PUF_2026",
            }
        return [by_key[k] for k in sorted(by_key)]


def load_db_ri(conn) -> list[dict]:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT p.canonical_plan_key,p.official_plan_name,p.market_segment,
                   COALESCE(p.contract_id,''),COALESCE(p.segment_id,'')
            FROM plans p JOIN plan_years py ON py.plan_id=p.id
            WHERE py.year=2026 AND p.state='RI' ORDER BY p.canonical_plan_key
        """)
        return [dict(zip(("canonical_plan_key","database_plan_name","market_segment","contract_id","segment_id"), row)) for row in cur.fetchall()]


def qhp_component_from_db_key(key: str) -> str:
    parts = key.split(":")
    return parts[3] if len(parts) == 6 and parts[0] == "QHP" else ""


def reconcile(db_rows: list[dict], official: list[dict]) -> list[dict]:
    official_cms = {r["official_plan_key"]: r for r in official if r["official_plan_key"].startswith("CMS:")}
    official_qhp = {r["official_plan_key"].split(":")[2]: r for r in official if r["official_plan_key"].startswith("QHP:")}
    out = []
    for db in db_rows:
        key = db["canonical_plan_key"]
        match = official_cms.get(key)
        if key.startswith("QHP:"):
            match = official_qhp.get(qhp_component_from_db_key(key))
        if key.startswith(("MEDICAID:", "CHIP:", "MEDIGAP:")):
            status = "SEPARATE_PROGRAM_AUTHORITY_REQUIRED"
        else:
            status = "EXACT_OFFICIAL_ROSTER_MATCH" if match else "NOT_IN_OFFICIAL_2026_ROSTER"
        out.append({
            **db,
            "match_status": status,
            "official_plan_key": match["official_plan_key"] if match else "",
            "official_plan_name": match["official_plan_name"] if match else "",
            "official_roster_source": match["source"] if match else "",
        })
    return out


def archive_source(name: str, expected_type: str, resp, page_rows: list[dict]) -> dict:
    raw = resp.raw
    sha = sha256_bytes(raw) if raw else ""
    is_pdf = raw.startswith(b"%PDF-")
    is_zip = raw.startswith(b"PK")
    is_html = b"<html" in raw[:20000].lower() or b"<!doctype html" in raw[:20000].lower()
    pages = []
    parser_valid = False
    if is_pdf:
        try:
            pages = extract_pdf(raw)
            parser_valid = bool(pages)
        except Exception:
            pages = []
    if is_pdf:
        classification = "VALID_OFFICIAL_PDF" if parser_valid else "INVALID_FILE"
        suffix = ".pdf"
    elif is_zip:
        try:
            with zipfile.ZipFile(io.BytesIO(raw)) as zf:
                parser_valid = bool(zf.namelist())
        except Exception:
            parser_valid = False
        classification = "VALID_OFFICIAL_ZIP" if parser_valid else "INVALID_FILE"
        suffix = ".zip"
    elif is_html and resp.status == 200:
        classification = "VALID_OFFICIAL_PORTAL_HTML" if domain_allowed(resp.final_url) else "UNAPPROVED_DOMAIN"
        suffix = ".html"
    else:
        classification = "DOWNLOAD_FAILED" if resp.status < 200 or resp.status >= 300 else "INVALID_FILE"
        suffix = ".bin"
    path = ""
    if raw:
        safe = re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_")
        target = ARCHIVE / f"RI_{safe}_{sha[:12]}{suffix}"
        target.write_bytes(raw)
        if sha256_bytes(target.read_bytes()) != sha:
            raise AssertionError("archive SHA mismatch")
        path = str(target)
    text = "\n".join(pages)
    for page_no, page in enumerate(pages, 1):
        page_rows.append({
            "source_name": name,
            "source_sha256": sha,
            "page_number": page_no,
            "complete_extracted_text": page,
            "character_count": len(page),
        })
    authoritative_type = {
        "EOC": "EOC",
        "SUMMARY_OF_BENEFITS": "SUMMARY_OF_BENEFITS",
        "PLAN_COMPARISON": "APPLICABILITY_SCHEDULE",
        "PHARMACY_PROTOCOL": "OTHER_OFFICIAL_PLAN_DOCUMENT",
    }.get(expected_type)
    detected_type = authoritative_type or (identify_document_type(pages, name) if pages else expected_type)
    return {
        "source_name": name,
        "expected_document_type": expected_type,
        **response_log_row(resp),
        "allowlist_status": "ALLOWED_OFFICIAL_DOMAIN" if domain_allowed(resp.final_url) else "OFFICIAL_DOMAIN_REQUIRES_ALLOWLIST_REVIEW",
        "classification": classification,
        "archive_path": path,
        "sha256": sha,
        "page_count": len(pages),
        "detected_document_type": detected_type,
        "year_verification": year_from_text(text) if pages else ("YEAR_2026_VERIFIED" if "2026" in raw.decode("utf-8", errors="ignore") else "YEAR_NOT_VERIFIED"),
    }


def main() -> None:
    conn = psycopg2.connect(dbname="benefit_card_navigator", user=os.environ.get("USER", "albertopaz"), host="localhost")
    conn.autocommit = False
    initial = baseline(conn)
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    client = HttpClient(timeout=60)

    cms_raw, sbe_raw, roster_requests = fresh_indexes(client)
    official = parse_cms_ri(cms_raw) + parse_sbe_ri(sbe_raw)
    db_rows = load_db_ri(conn)
    comparison = reconcile(db_rows, official)

    page_rows: list[dict] = []
    downloads: list[dict] = []
    for name, url, channel, expected_type in SOURCE_URLS[2:]:
        resp = client.get(0, url, channel, f"Rhode Island 2026 {expected_type}")
        downloads.append(archive_source(name, expected_type, resp, page_rows))
        print(f"{name}: HTTP {resp.status}, {len(resp.raw)} bytes", flush=True)

    conn.rollback()
    final = baseline(conn)
    conn.close()
    if initial != final:
        raise AssertionError("database invariants changed during read-only RI acquisition")

    write_csv(ROOT / f"{PREFIX}OFFICIAL_PLAN_ROSTER.csv", official,
              ["official_plan_key","state","market","contract_id","pbp_id","segment_id","official_plan_name","issuer","plan_type","part_d","source"])
    write_csv(ROOT / f"{PREFIX}DATABASE_ROSTER_COMPARISON.csv", comparison,
              ["canonical_plan_key","database_plan_name","market_segment","contract_id","segment_id","match_status","official_plan_key","official_plan_name","official_roster_source"])
    write_csv(ROOT / f"{PREFIX}ROSTER_REQUEST_LOG.csv", roster_requests,
              ["source_name","task_id","request_id","discovery_channel","query","requested_url","final_url","redirect_chain","http_status","content_type","content_length","downloaded_byte_count","timestamp","error","archive_path","sha256","validation"])
    download_fields = ["source_name","expected_document_type","task_id","request_id","discovery_channel","query","requested_url","final_url","redirect_chain","http_status","content_type","content_length","downloaded_byte_count","timestamp","error","allowlist_status","classification","archive_path","sha256","page_count","detected_document_type","year_verification"]
    write_csv(ROOT / f"{PREFIX}SOURCE_DOWNLOADS.csv", downloads, download_fields)
    write_csv(ROOT / f"{PREFIX}PAGE_TEXT.csv", page_rows,
              ["source_name","source_sha256","page_number","complete_extracted_text","character_count"])

    official_counts = Counter(r["market"] for r in official)
    comparison_counts = Counter(r["match_status"] for r in comparison)
    doc_counts = Counter(r["classification"] for r in downloads)
    report = {
        "generated_at": utcnow(),
        "database_mutations": 0,
        "coverage_rule_mutations": 0,
        "official_roster_total": len(official),
        "official_roster_distribution": dict(sorted(official_counts.items())),
        "database_ri_plan_records": len(db_rows),
        "database_comparison_distribution": dict(sorted(comparison_counts.items())),
        "fresh_roster_gets": len(roster_requests),
        "fresh_source_gets": len(downloads),
        "source_download_distribution": dict(sorted(doc_counts.items())),
        "validated_pdfs": sum(r["classification"] == "VALID_OFFICIAL_PDF" for r in downloads),
        "unique_source_hashes": len({r["sha256"] for r in downloads if r["sha256"]}),
        "pages_extracted": len(page_rows),
        "baseline": initial,
        "final_invariants": final,
    }
    (ROOT / f"{PREFIX}REPORT.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2), flush=True)


if __name__ == "__main__":
    main()
