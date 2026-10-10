#!/usr/bin/env python3
"""Fresh official-index verification for Phase25T pending standard identities."""

import csv
import hashlib
import io
import os
import re
import zipfile
from collections import Counter
from pathlib import Path

import psycopg2

import phase25t_codex_pipeline as p


INDEX_DIR = p.ROOT / "data" / "official_source_indexes_2026"
INDEXES = {
    "CMS_MA_PD_LANDSCAPE": "https://www.cms.gov/files/zip/cy2026-landscape-202609.zip",
    "SBE_MAINE": "https://www.cms.gov/files/zip/mainesbepuf2026.zip",
    "SBE_RHODE_ISLAND": "https://www.cms.gov/files/zip/rhodeislandsbepuf2026.zip",
    "SBE_VERMONT": "https://www.cms.gov/files/zip/vermontsbepuf2026.zip",
    "FFE_PLAN_ATTRIBUTES": "https://download.cms.gov/marketplace-puf/2026/plan-attributes-puf.zip",
}


def csv_rows_from_zip(raw, predicate):
    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        for name in zf.namelist():
            if predicate(name):
                with zf.open(name) as binary:
                    yield from csv.DictReader(io.TextIOWrapper(binary, encoding="utf-8-sig", errors="replace", newline=""))


def main():
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    client = p.HttpClient(timeout=90)
    raw_by_name = {}
    request_rows = []
    for name, url in INDEXES.items():
        resp = client.get(0, url, "OFFICIAL_STRUCTURED_INDEX", "2026 exact plan identity lookup")
        if resp.status != 200 or not resp.raw.startswith(b"PK"):
            raise RuntimeError(f"official index download failed: {name} HTTP {resp.status} {resp.error}")
        sha = p.sha256_bytes(resp.raw)
        target = INDEX_DIR / f"{name}_{sha[:12]}.zip"
        target.write_bytes(resp.raw)
        if p.sha256_bytes(target.read_bytes()) != sha:
            raise AssertionError("official index archive hash mismatch")
        raw_by_name[name] = resp.raw
        row = p.response_log_row(resp)
        row.update({"index_name": name, "archive_path": str(target), "sha256": sha, "validation": "VALID_OFFICIAL_ZIP"})
        request_rows.append(row)

    cms = {}
    for row in csv_rows_from_zip(raw_by_name["CMS_MA_PD_LANDSCAPE"], lambda n: n.lower().endswith(".csv")):
        key = (row["State Territory Abbreviation"], row["Contract ID"], row["Plan ID"].zfill(3), row["Segment ID"].zfill(3))
        cms.setdefault(key, row)

    qhp = {}
    for name, state in (("SBE_MAINE", "ME"), ("SBE_RHODE_ISLAND", "RI"), ("SBE_VERMONT", "VT")):
        for row in csv_rows_from_zip(raw_by_name[name], lambda n: "plans" in n.lower() and n.lower().endswith(".csv")):
            plan_id = (row.get("STANDARD COMPONENT ID") or "").strip()
            if plan_id:
                qhp[(state, plan_id)] = row
    for row in csv_rows_from_zip(raw_by_name["FFE_PLAN_ATTRIBUTES"], lambda n: n.lower().endswith(".csv")):
        plan_id = (row.get("StandardComponentId") or "").strip()
        state = (row.get("StateCode") or "").strip()
        if plan_id:
            qhp[(state, plan_id)] = row

    conn = psycopg2.connect(dbname="benefit_card_navigator", user=os.environ.get("USER", "albertopaz"), host="localhost")
    plans, _, _ = p.load_tasks(conn)
    conn.close()
    standard = [x for x in plans if x["task_id"] not in p.SPECIAL_TASK_IDS]
    audit = []
    for plan in standard:
        key = plan["canonical_plan_key"]
        official_name = ""
        index_name = ""
        index_url = ""
        if plan["cms"]:
            c = plan["cms"]
            found = cms.get((c["state"], c["contract"], c["pbp"], c["segment"]))
            status = "OFFICIAL_IDENTITY_EXACT" if found else "OFFICIAL_IDENTITY_NOT_FOUND"
            official_name = found["Plan Name"] if found else ""
            index_name = "CMS_MA_PD_LANDSCAPE"
        elif key.startswith("QHP:"):
            parts = key.split(":")
            state, plan_id = parts[1], parts[3]
            found = qhp.get((state, plan_id))
            status = "OFFICIAL_IDENTITY_EXACT" if found else "OFFICIAL_IDENTITY_NOT_FOUND"
            official_name = (found.get("PLAN MARKETING NAME") or found.get("PlanMarketingName") or "") if found else ""
            index_name = "FFE_PLAN_ATTRIBUTES" if state == "NH" else {"ME":"SBE_MAINE","RI":"SBE_RHODE_ISLAND","VT":"SBE_VERMONT"}.get(state, "")
        else:
            status = "STATE_PROGRAM_ID_NOT_IN_CMS_PLAN_INDEX"
            index_name = ""
        index_url = INDEXES.get(index_name, "")
        audit.append({
            "task_id": plan["task_id"], "canonical_plan_key": key,
            "database_plan_name": plan["official_plan_name"], "official_index_plan_name": official_name,
            "identity_status": status, "official_index_name": index_name,
            "official_index_url": index_url,
        })

    p.write_csv(p.ROOT / "PHASE25T_CODEX_OFFICIAL_IDENTITY_AUDIT.csv", audit,
                ["task_id","canonical_plan_key","database_plan_name","official_index_plan_name","identity_status","official_index_name","official_index_url"])
    p.write_csv(p.ROOT / "PHASE25T_CODEX_INDEX_REQUEST_LOG.csv", request_rows,
                ["index_name","task_id","request_id","discovery_channel","query","requested_url","final_url","redirect_chain","http_status","content_type","content_length","downloaded_byte_count","timestamp","error","archive_path","sha256","validation"])

    # A completed official-index lookup supersedes the prior search-endpoint ACCESS_BLOCKED
    # label. Missing exact identities remain honest non-discoveries, never look-alike matches.
    missing = {str(r["task_id"]) for r in audit if r["identity_status"] == "OFFICIAL_IDENTITY_NOT_FOUND"}
    status_path = p.ROOT / "PHASE25T_CODEX_121_DISCOVERY_STATUS.csv"
    with status_path.open(encoding="utf-8", newline="") as handle:
        statuses = list(csv.DictReader(handle))
    for row in statuses:
        if row["task_id"] in missing:
            row["discovery_status"] = "DOCUMENT_NOT_DISCOVERED"
    p.write_csv(status_path, statuses, ["task_id","canonical_plan_key","official_plan_name","discovery_status"])

    conn = psycopg2.connect(dbname="benefit_card_navigator", user=os.environ.get("USER", "albertopaz"), host="localhost")
    final = p.baseline(conn)
    conn.close()
    art = p.read_artifacts()
    tests = (p.ROOT / "PHASE25T_CODEX_TEST_RESULTS.txt").read_text(encoding="utf-8")
    report = p.report(art, final, tests)
    dist = Counter(r["identity_status"] for r in audit)
    identity_section = "\n## Official identity index audit\n\n" + "\n".join(f"- {k}: {v}" for k, v in sorted(dist.items())) + "\n"
    report = report.replace("\n## Database mutations\n", identity_section + "\n## Database mutations\n")
    (p.ROOT / "PHASE25T_CODEX_FINAL_REPORT.md").write_text(report, encoding="utf-8")
    print(dict(dist), flush=True)
    print(report.strip().splitlines()[-1], flush=True)


if __name__ == "__main__":
    main()
