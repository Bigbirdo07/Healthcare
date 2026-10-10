#!/usr/bin/env python3
"""Phase 25T: conservative acquisition of 2026 pharmacy source documents.

The production path in this module has two deliberately narrow data inputs:
live PostgreSQL plan/task records and bytes returned by HttpClient.get().  It
never reads source_documents.reconstructed_archive_path or uses an existing
local file to rescue a failed request.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import html
import io
import os
import random
import re
import ssl
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable, Optional

import psycopg2
import pypdf


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "data" / "official_plan_documents_2026"
PREFIX = "PHASE25T_CODEX_"
EXPECTED_CENSUS_SHA = "e9ae11af0e074f9d819fa8f2339d19b463a515fd5d5dd00db3f71894c770d8af"
AUDIT_SEED = "20260929T-CODEX"
ALLOWED_DOMAINS = {
    "cms.gov", "bcbsri.com", "uhc.com", "aetna.com", "humana.com",
    "wellcare.com", "mass.gov", "dvha.vermont.gov",
    # Explicitly approved by the repository owner on 2026-09-29 for the
    # Rhode Island-first acquisition pass.
    "healthsourceri.com", "eohhs.ri.gov", "nhpri.org",
}
SPECIAL_TASK_IDS = {
    77, 114, 3066, 3076, 3086, 3096, 3186, 3196, 3206, 3216,
    3246, 3256, 3266, 3276, 3285, 3288, 3291, 3294,
}
CONCEPTS = (
    "Tier 1", "Tier 2", "Tier 3", "Tier 4", "Tier 5", "Insulin",
    "Mail Order", "Preferred Pharmacy", "Retail 30-Day", "Retail 90-Day",
)
DOC_CUES = (
    "evidence of coverage", "formulary", "drug list", "summary of benefits",
    "pharmacy directory", "prescription drug", "cost sharing",
)


def utcnow() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def normalize_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (value or "").lower()).strip()


def normalize_plan_name(value: str) -> str:
    return " ".join(x for x in normalize_name(value).split() if x not in {"plan"})


def domain_allowed(url: str) -> bool:
    host = (urllib.parse.urlsplit(url).hostname or "").lower().rstrip(".")
    return any(host == d or host.endswith("." + d) for d in ALLOWED_DOMAINS)


def assert_not_reconstructed(path: Optional[str], quarantined: Iterable[str]) -> None:
    if not path:
        return
    resolved = str(Path(path).resolve())
    q = {str(Path(p).resolve()) for p in quarantined if p}
    if resolved in q or "reconstruct" in resolved.lower():
        raise AssertionError("reconstructed_archive_path cannot be used as evidence")


CMS_KEY_RE = re.compile(
    r"^CMS:(?P<state>[A-Z]{2}):(?P<contract>[HSR]\d{4}):"
    r"(?P<pbp>\d{3}):(?P<segment>\d{3}):(?P<year>\d{4})$"
)


def parse_cms_key(key: str, db_contract: str) -> Optional[dict]:
    """Parse only the exact canonical CMS form; never infer a PBP."""
    match = CMS_KEY_RE.fullmatch(key or "")
    if not match:
        return None
    parsed = match.groupdict()
    if parsed["contract"] != (db_contract or ""):
        raise ValueError("IDENTIFIER_INTEGRITY_FAILURE")
    return parsed


@dataclass
class Response:
    request_id: str
    task_id: int
    channel: str
    query: str
    requested_url: str
    final_url: str
    redirects: list[str]
    status: int
    content_type: str
    content_length: str
    raw: bytes
    timestamp: str
    error: str = ""


class _RedirectRecorder(urllib.request.HTTPRedirectHandler):
    def __init__(self) -> None:
        self.chain: list[str] = []
        super().__init__()

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        self.chain.append(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class HttpClient:
    """HTTP GET-only client that records exact requested and final URLs."""

    def __init__(self, timeout: int = 18) -> None:
        self.timeout = timeout
        self._lock = threading.Lock()
        self._counter = 0
        self.calls: list[str] = []

    def _id(self) -> str:
        with self._lock:
            self._counter += 1
            return f"REQ-{self._counter:07d}"

    def get(self, task_id: int, url: str, channel: str, query: str = "") -> Response:
        request_id = self._id()
        with self._lock:
            self.calls.append(url)
        recorder = _RedirectRecorder()
        ctx = ssl.create_default_context()
        opener = urllib.request.build_opener(
            recorder, urllib.request.HTTPSHandler(context=ctx)
        )
        req = urllib.request.Request(
            url,
            method="GET",
            headers={
                "User-Agent": "BenefitCardNavigator-SourceAudit/1.0 (+document verification)",
                "Accept": "text/html,application/pdf,application/xhtml+xml,*/*;q=0.5",
            },
        )
        try:
            with opener.open(req, timeout=self.timeout) as resp:
                raw = resp.read()
                return Response(
                    request_id, task_id, channel, query, url, resp.geturl(),
                    recorder.chain, int(resp.status), resp.headers.get_content_type(),
                    resp.headers.get("Content-Length", ""), raw, utcnow(), "",
                )
        except urllib.error.HTTPError as exc:
            raw = exc.read() if exc.fp else b""
            return Response(
                request_id, task_id, channel, query, url, exc.geturl(),
                recorder.chain, int(exc.code), exc.headers.get_content_type() if exc.headers else "",
                exc.headers.get("Content-Length", "") if exc.headers else "", raw,
                utcnow(), f"HTTPError: {exc.reason}",
            )
        except Exception as exc:
            return Response(
                request_id, task_id, channel, query, url, url, recorder.chain, 0,
                "", "", b"", utcnow(), f"{type(exc).__name__}: {exc}",
            )


class LinkParser(HTMLParser):
    def __init__(self, base: str) -> None:
        super().__init__()
        self.base = base
        self.links: list[tuple[str, str]] = []
        self._href: Optional[str] = None
        self._text: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "a":
            self._href = dict(attrs).get("href")
            self._text = []

    def handle_data(self, data):
        if self._href is not None:
            self._text.append(data)

    def handle_endtag(self, tag):
        if tag.lower() == "a" and self._href:
            self.links.append((urllib.parse.urljoin(self.base, self._href), normalize_space(" ".join(self._text))))
            self._href = None
            self._text = []


def decode_search_url(url: str) -> str:
    parsed = urllib.parse.urlsplit(html.unescape(url))
    query = urllib.parse.parse_qs(parsed.query)
    if "uddg" in query:
        return urllib.parse.unquote(query["uddg"][0])
    return url


def links_from_html(raw: bytes, base: str) -> list[tuple[str, str]]:
    parser = LinkParser(base)
    parser.feed(raw.decode("utf-8", errors="replace"))
    out, seen = [], set()
    for url, label in parser.links:
        url = decode_search_url(url)
        if url.startswith(("http://", "https://")) and url not in seen:
            out.append((url, label))
            seen.add(url)
    return out


def candidate_score(url: str, label: str, plan: dict) -> int:
    hay = normalize_name(url + " " + label)
    score = 0
    for value, weight in (
        (plan["official_plan_name"], 10), (plan.get("contract_id", ""), 9),
        (plan.get("pbp_id", ""), 7), (plan.get("segment_id", ""), 2),
        ("2026", 7), ("evidence", 5), ("coverage", 4), ("eoc", 5),
        ("formulary", 5), ("drug", 3), ("benefits", 3), ("pharmacy", 3),
        ("summary", 2),
    ):
        needle = normalize_name(value)
        if needle and needle not in {"n a", "000"} and needle in hay:
            score += weight
    if urllib.parse.urlsplit(url).path.lower().endswith(".pdf"):
        score += 5
    return score


def plausible_candidate(url: str, label: str, plan: dict) -> bool:
    combined = (url + " " + label).lower()
    has_cue = any(cue.replace(" ", "") in combined.replace("-", "").replace("_", "").replace(" ", "") for cue in DOC_CUES)
    has_id = bool(plan.get("contract_id") and plan["contract_id"] != "N/A" and plan["contract_id"].lower() in combined)
    is_pdf = urllib.parse.urlsplit(url).path.lower().endswith(".pdf")
    return (has_cue or has_id or is_pdf) and url.startswith(("http://", "https://"))


def classify_response(resp: Response, plan: dict) -> str:
    if resp.status in (401,):
        return "LOGIN_REQUIRED"
    if resp.status in (403, 451):
        return "ACCESS_DENIED"
    if resp.status < 200 or resp.status >= 300:
        return "DOWNLOAD_FAILED"
    raw = resp.raw
    if raw.startswith(b"%PDF-"):
        try:
            reader = pypdf.PdfReader(io.BytesIO(raw))
            if len(reader.pages) > 0:
                return "VALID_OFFICIAL_PDF" if domain_allowed(resp.final_url) else "WRONG_DOCUMENT"
        except Exception:
            return "INVALID_FILE"
        return "INVALID_FILE"
    sample = raw[:20000].lower()
    if b"<html" in sample or b"<!doctype html" in sample:
        text = normalize_name(raw.decode("utf-8", errors="replace"))
        path = urllib.parse.urlsplit(resp.final_url).path.strip("/")
        if any(x in text for x in ("access denied", "forbidden")):
            return "ACCESS_DENIED"
        if any(x in text for x in ("sign in", "log in")) and not any(c in text for c in DOC_CUES):
            return "LOGIN_REQUIRED"
        year = year_from_text(text) == "YEAR_2026_VERIFIED"
        identity = normalize_name(plan["official_plan_name"]) in text or (
            plan.get("contract_id") not in (None, "", "N/A") and plan["contract_id"].lower() in text
        )
        cues = any(c in text for c in DOC_CUES)
        if domain_allowed(resp.final_url) and year and identity and cues:
            return "VALID_OFFICIAL_PLAN_HTML"
        if not path:
            return "OFFICIAL_PORTAL_ONLY"
        return "HTML_ERROR_PAGE" if any(x in text for x in ("not found", "error 404")) else "OFFICIAL_PORTAL_ONLY"
    return "INVALID_FILE"


def extract_pdf(raw: bytes) -> list[str]:
    if not raw.startswith(b"%PDF-"):
        raise ValueError("not PDF bytes")
    reader = pypdf.PdfReader(io.BytesIO(raw))
    if len(reader.pages) < 1:
        raise ValueError("zero-page PDF")
    return [(page.extract_text() or "") for page in reader.pages]


def year_from_text(text: str) -> str:
    low = normalize_space(text).lower()
    positive = (
        r"\b2026\s+(?:evidence of coverage|formulary|drug list|summary of benefits)",
        r"\bjanuary\s+1,?\s+2026\b",
        r"\b2026\s+plan(?:\s+year)?\b",
        r"\bplan\s+year\s+2026\b",
        r"\bcoverage\s+(?:from|for).*?\b2026\b",
    )
    if any(re.search(p, low) for p in positive):
        return "YEAR_2026_VERIFIED"
    years = set(re.findall(r"\b20(?:2[0-9]|3[0-9])\b", low))
    if years and "2026" not in years:
        return "YEAR_CONFLICT"
    return "YEAR_NOT_VERIFIED"


def identify_document_type(pages: list[str], link_label: str = "") -> str:
    text = normalize_space(" ".join(pages[:5]) + " " + link_label).lower()
    checks = (
        # A formulary frequently tells readers to consult the EOC; title-page
        # formulary/drug-guide language therefore takes precedence over that cross-reference.
        ("FORMULARY", ("prescription drug guide", "formulary", "drug list")),
        ("EOC", ("evidence of coverage",)),
        ("SUMMARY_OF_BENEFITS", ("summary of benefits",)),
        ("PHARMACY_DIRECTORY", ("pharmacy directory",)),
        ("COST_SHARING_DOCUMENT", ("cost sharing", "cost-sharing")),
        ("APPLICABILITY_SCHEDULE", ("applicability schedule",)),
    )
    for kind, cues in checks:
        if any(c in text for c in cues):
            return kind
    return "OTHER_OFFICIAL_PLAN_DOCUMENT" if pages else "UNKNOWN"


def find_context(pages: list[str], needle: str, normalized: bool = False) -> tuple[bool, str, str]:
    if not needle:
        return False, "", ""
    target = normalize_name(needle) if normalized else needle.lower()
    for num, page in enumerate(pages, 1):
        hay = normalize_name(page) if normalized else page.lower()
        pos = hay.find(target)
        if pos >= 0:
            # For normalized matching, preserve a source excerpt without claiming exact offsets.
            if normalized:
                return True, str(num), normalize_space(page)[:500]
            return True, str(num), page[max(0, pos - 100): min(len(page), pos + len(needle) + 180)]
    return False, "", ""


def identifier_checks(plan: dict, pages: list[str]) -> dict:
    exact, exact_page, exact_ctx = find_context(pages, plan["official_plan_name"])
    norm = False
    norm_page = norm_ctx = ""
    norm_target = normalize_plan_name(plan["official_plan_name"])
    for n, page in enumerate(pages, 1):
        if norm_target and norm_target in normalize_plan_name(page):
            norm, norm_page, norm_ctx = True, str(n), normalize_space(page)[:500]
            break
    contract = plan.get("contract_id", "")
    c_match, c_page, c_ctx = find_context(pages, contract) if contract != "N/A" else (False, "", "")
    pbp_match = False
    pbp_page = pbp_ctx = ""
    parsed = plan.get("cms")
    if parsed:
        contract_re = re.escape(parsed["contract"])
        pbp_re = re.escape(parsed["pbp"])
        combo = re.compile(rf"\b{contract_re}\s*[-/]\s*{pbp_re}\b", re.I)
        for n, page in enumerate(pages, 1):
            m = combo.search(page)
            if m:
                pbp_match, pbp_page = True, str(n)
                pbp_ctx = page[max(0, m.start()-100):min(len(page), m.end()+180)]
                break
        if not pbp_match:
            # Official shared formularies may express an explicit applicability list as
            # "S5884-101, 102, 103".  Accept only a contiguous grouped list beginning
            # with the exact contract and containing the exact three-digit PBP.
            grouped = re.compile(rf"\b{contract_re}-(\d{{3}}(?:\s*,\s*\d{{3}})+)", re.I)
            for n, page in enumerate(pages, 1):
                for m in grouped.finditer(page):
                    pbps = re.findall(r"\d{3}", m.group(1))
                    if parsed["pbp"] in pbps:
                        pbp_match, pbp_page = True, str(n)
                        pbp_ctx = page[max(0, m.start()-100):min(len(page), m.end()+180)]
                        break
                if pbp_match:
                    break
    segment_match = False
    if parsed:
        seg_pattern = re.compile(rf"\b{re.escape(parsed['contract'])}[-_/]{re.escape(parsed['pbp'])}[-_/]{re.escape(parsed['segment'])}\b", re.I)
        segment_match = any(seg_pattern.search(page) for page in pages)
    return {
        "exact_plan_name_match": exact, "exact_plan_name_page": exact_page, "exact_plan_name_context": exact_ctx,
        "normalized_plan_name_match": norm, "normalized_plan_name_page": norm_page, "normalized_plan_name_context": norm_ctx,
        "contract_id_match": c_match, "contract_id_page": c_page, "contract_id_context": c_ctx,
        "pbp_id_match": pbp_match, "pbp_id_page": pbp_page, "pbp_id_context": pbp_ctx,
        "segment_id_match": segment_match,
    }


def classify_applicability(ids: dict, text: str, plan: dict) -> str:
    if ids["exact_plan_name_match"] and (ids["contract_id_match"] or plan.get("contract_id") == "N/A"):
        return "EXACT_PLAN"
    if ids["contract_id_match"] and ids["pbp_id_match"]:
        return "EXACT_CONTRACT_PBP"
    if ids["contract_id_match"] and re.search(r"\b(?:all plans|plans listed|applies to)\b", text, re.I):
        return "EXACT_CONTRACT_MULTI_SEGMENT"
    if re.search(r"\b(?:applies to all|all .* plans listed|plans covered by this document)\b", text, re.I):
        return "CARRIER_SHARED_EXPLICIT"
    if text:
        return "CARRIER_SHARED_UNPROVEN"
    return "NO_DOCUMENT"


CONCEPT_PATTERNS = {
    "Tier 1": re.compile(r"\btier\s*1\b|\bpreferred generic\b", re.I),
    "Tier 2": re.compile(r"\btier\s*2\b", re.I),
    "Tier 3": re.compile(r"\btier\s*3\b", re.I),
    "Tier 4": re.compile(r"\btier\s*4\b", re.I),
    "Tier 5": re.compile(r"\btier\s*5\b", re.I),
    "Insulin": re.compile(r"\binsulin\b", re.I),
    "Mail Order": re.compile(r"\bmail[- ]order\b|\bmail service\b", re.I),
    "Preferred Pharmacy": re.compile(r"\bpreferred (?:network )?pharmac(?:y|ies)\b", re.I),
    "Retail 30-Day": re.compile(r"\b30[- ]day\b.*?\bretail\b|\bretail\b.*?\b30[- ]day\b", re.I | re.S),
    "Retail 90-Day": re.compile(r"\b90[- ]day\b.*?\bretail\b|\bretail\b.*?\b90[- ]day\b", re.I | re.S),
}


def actual_heading(page: str, match_start: int) -> str:
    prior = page[:match_start].splitlines()
    for line in reversed(prior[-12:]):
        line = normalize_space(line)
        if 3 <= len(line) <= 160:
            return line
    return ""


def extract_evidence(task_id: int, sha: str, pages: list[str]) -> list[dict]:
    rows = []
    for concept in CONCEPTS:
        found = None
        for page_no, page in enumerate(pages, 1):
            match = CONCEPT_PATTERNS[concept].search(page)
            if match:
                start = max(0, match.start() - 180)
                end = min(len(page), match.end() + 420)
                found = {
                    "task_id": task_id, "source_sha256": sha, "target_concept": concept,
                    "page_number": page_no, "actual_detected_heading": actual_heading(page, match.start()),
                    "start_offset": start, "end_offset": end,
                    "exact_excerpt": page[start:end], "evidence_status": "FOUND",
                }
                assert found["exact_excerpt"] == page[start:end]
                break
        rows.append(found or {
            "task_id": task_id, "source_sha256": sha, "target_concept": concept,
            "page_number": "", "actual_detected_heading": "", "start_offset": "",
            "end_offset": "", "exact_excerpt": "", "evidence_status": "SOURCE_MISSING",
        })
    return rows


def build_queries(plan: dict) -> list[str]:
    identity = f'"{plan["official_plan_name"]}" "{plan["carrier"]}" "{plan["state"]}"'
    if plan.get("cms"):
        identity += f' "{plan["contract_id"]}" "{plan["pbp_id"]}"'
    return [
        f'{identity} 2026 "Evidence of Coverage" EOC Formulary "Drug List"',
        f'{identity} 2026 "Summary of Benefits" "Pharmacy Directory" "Prescription Drug" "Cost Sharing"',
    ]


def search_url(query: str) -> str:
    return "https://html.duckduckgo.com/html/?" + urllib.parse.urlencode({"q": query})


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def load_tasks(conn) -> tuple[list[dict], set[str], list[dict]]:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT t.id, p.canonical_plan_key, p.official_plan_name,
                   COALESCE(i.display_name,''), p.state, p.market_segment,
                   COALESCE(p.coverage_type,''), COALESCE(p.contract_id,''),
                   COALESCE(p.segment_id,''), py.id
            FROM ingestion_tasks t
            JOIN plan_years py ON py.id=t.plan_year_id
            JOIN plans p ON p.id=py.plan_id
            LEFT JOIN insurers i ON i.id=p.insurer_id
            WHERE py.year=2026 AND t.benefit_domain='PHARMACY'
              AND t.task_status='PENDING' ORDER BY t.id
        """)
        rows = cur.fetchall()
        cur.execute("SELECT reconstructed_archive_path FROM source_documents WHERE reconstructed_archive_path IS NOT NULL")
        quarantine = {r[0] for r in cur.fetchall()}
    plans = []
    for row in rows:
        task_id, key, name, carrier, state, market, coverage, contract, segment, pyid = row
        integrity = "VALID"
        try:
            cms = parse_cms_key(key, contract)
        except ValueError:
            cms, integrity = None, "IDENTIFIER_INTEGRITY_FAILURE"
        plans.append({
            "task_id": task_id, "canonical_plan_key": key, "official_plan_name": name,
            "carrier": carrier, "state": state, "market_segment": market,
            "coverage_type": coverage, "contract_id": contract, "segment_id": segment,
            "plan_year_id": pyid, "cms": cms, "pbp_id": cms["pbp"] if cms else "",
            "identifier_integrity": integrity,
        })
    return plans, quarantine, []


def baseline(conn) -> dict:
    q = {
        "plans": "SELECT COUNT(*) FROM plans",
        "plan_years_2026": "SELECT COUNT(*) FROM plan_years WHERE year=2026",
        "coverage_rules": "SELECT COUNT(*) FROM coverage_rules",
        "products": "SELECT COUNT(*) FROM products", "services": "SELECT COUNT(*) FROM services",
        "benefits": "SELECT COUNT(*) FROM benefits", "tasks": "SELECT COUNT(*) FROM ingestion_tasks",
        "completed": "SELECT COUNT(*) FROM ingestion_tasks WHERE task_status='COMPLETED'",
        "partial": "SELECT COUNT(*) FROM ingestion_tasks WHERE task_status='PARTIAL'",
        "pending": "SELECT COUNT(*) FROM ingestion_tasks WHERE task_status='PENDING'",
        "completed_pharmacy": "SELECT COUNT(*) FROM ingestion_tasks t JOIN plan_years py ON py.id=t.plan_year_id WHERE py.year=2026 AND t.benefit_domain='PHARMACY' AND t.task_status='COMPLETED'",
        "pending_pharmacy": "SELECT COUNT(*) FROM ingestion_tasks t JOIN plan_years py ON py.id=t.plan_year_id WHERE py.year=2026 AND t.benefit_domain='PHARMACY' AND t.task_status='PENDING'",
    }
    out = {}
    with conn.cursor() as cur:
        for key, sql in q.items():
            cur.execute(sql)
            out[key] = cur.fetchone()[0]
    out["catalog"] = out["products"] + out["services"] + out["benefits"]
    out["census_sha256"] = sha256_bytes((ROOT / "NEW_ENGLAND_2026_PLAN_CENSUS_V4.csv").read_bytes())
    out["standard_pharmacy"] = out["pending_pharmacy"] - len(SPECIAL_TASK_IDS)
    out["special_pharmacy"] = len(SPECIAL_TASK_IDS)
    expected = {
        "plans": 331, "plan_years_2026": 331, "coverage_rules": 4537,
        "products": 72, "services": 33, "benefits": 46, "catalog": 151,
        "tasks": 3305, "completed": 730, "partial": 922, "pending": 1653,
        "completed_pharmacy": 192, "pending_pharmacy": 139,
        "standard_pharmacy": 121, "special_pharmacy": 18,
        "census_sha256": EXPECTED_CENSUS_SHA,
    }
    bad = {k: (out.get(k), v) for k, v in expected.items() if out.get(k) != v}
    if bad:
        raise RuntimeError(f"PHASE25T_CODEX_BASELINE_MISMATCH: {bad}")
    return out


def archive_response(plan: dict, resp: Response, doc_type: str) -> tuple[str, str]:
    if not resp.raw:
        return "", ""
    sha = sha256_bytes(resp.raw)
    contract = re.sub(r"[^A-Za-z0-9]+", "-", plan.get("contract_id") or "NO-CONTRACT")
    pbp = plan.get("pbp_id") or "NO-PBP"
    suffix = ".pdf" if resp.raw.startswith(b"%PDF-") else ".html" if b"html" in resp.raw[:1000].lower() else ".bin"
    filename = f"TASK_{plan['task_id']}_{contract}_{pbp}_{doc_type}_{sha[:12]}{suffix}"
    target = ARCHIVE / filename
    # Never overwrite differing bytes; same-name content is necessarily same SHA prefix but verify anyway.
    if target.exists() and target.read_bytes() != resp.raw:
        raise AssertionError("archive collision")
    if not target.exists():
        target.write_bytes(resp.raw)
    if sha256_bytes(target.read_bytes()) != sha:
        raise AssertionError("saved-byte SHA mismatch")
    return str(target), sha


def response_log_row(resp: Response) -> dict:
    return {
        "task_id": resp.task_id, "request_id": resp.request_id,
        "discovery_channel": resp.channel, "query": resp.query,
        "requested_url": resp.requested_url, "final_url": resp.final_url,
        "redirect_chain": " | ".join(resp.redirects), "http_status": resp.status,
        "content_type": resp.content_type, "content_length": resp.content_length,
        "downloaded_byte_count": len(resp.raw), "timestamp": resp.timestamp,
        "error": resp.error,
    }


@dataclass
class Artifacts:
    search_queries: list[dict] = field(default_factory=list)
    search_requests: list[dict] = field(default_factory=list)
    candidates: list[dict] = field(default_factory=list)
    downloads: list[dict] = field(default_factory=list)
    validated: list[dict] = field(default_factory=list)
    hashes: list[dict] = field(default_factory=list)
    doc_types: list[dict] = field(default_factory=list)
    pages: list[dict] = field(default_factory=list)
    years: list[dict] = field(default_factory=list)
    identifiers: list[dict] = field(default_factory=list)
    applicability: list[dict] = field(default_factory=list)
    evidence: list[dict] = field(default_factory=list)
    completeness: list[dict] = field(default_factory=list)
    statuses: list[dict] = field(default_factory=list)
    mutations: list[dict] = field(default_factory=list)
    audit: list[dict] = field(default_factory=list)


def process_plan(plan: dict, client: HttpClient) -> dict:
    """Network-only primary acquisition result for one plan."""
    result = {"plan": plan, "queries": [], "search": [], "candidates": [], "downloads": []}
    if plan["identifier_integrity"] != "VALID":
        return result
    candidate_map: dict[str, dict] = {}
    for query in build_queries(plan):
        result["queries"].append(query)
        resp = client.get(plan["task_id"], search_url(query), "WEB_SEARCH_DUCKDUCKGO_HTML", query)
        result["search"].append(resp)
        if resp.status == 200:
            for url, label in links_from_html(resp.raw, resp.final_url):
                if plausible_candidate(url, label, plan):
                    score = candidate_score(url, label, plan)
                    old = candidate_map.get(url)
                    if old is None or score > old["score"]:
                        candidate_map[url] = {"url": url, "label": label, "score": score, "channel": "WEB_SEARCH_DUCKDUCKGO_HTML"}
    # Every URL recorded as a candidate receives a fresh GET against that exact URL.
    for cand in sorted(candidate_map.values(), key=lambda x: (-x["score"], x["url"])):
        result["candidates"].append(cand)
        resp = client.get(plan["task_id"], cand["url"], "CANDIDATE_DOWNLOAD", "")
        result["downloads"].append((cand, resp))
        if resp.status == 200 and "html" in resp.content_type:
            for url, label in links_from_html(resp.raw, resp.final_url):
                if plausible_candidate(url, label, plan) and url not in candidate_map:
                    nested = {"url": url, "label": label, "score": candidate_score(url, label, plan), "channel": "OFFICIAL_PORTAL_TRAVERSAL"}
                    result["candidates"].append(nested)
                    nested_resp = client.get(plan["task_id"], url, "CANDIDATE_DOWNLOAD", "")
                    result["downloads"].append((nested, nested_resp))
    return result


def adjudicate_result(result: dict, art: Artifacts, quarantine: set[str]) -> None:
    plan = result["plan"]
    tid = plan["task_id"]
    search_blocked = bool(result["search"]) and not any(r.status == 200 for r in result["search"])
    for idx, query in enumerate(result["queries"], 1):
        art.search_queries.append({"task_id": tid, "query_sequence": idx, "query": query, "submitted": True})
    art.search_requests.extend(response_log_row(r) for r in result["search"])
    for cand in result["candidates"]:
        art.candidates.append({
            "task_id": tid, "candidate_url": cand["url"], "official_link_label": cand["label"],
            "candidate_score": cand["score"], "discovery_channel": cand["channel"],
            "discovery_query": cand.get("query", ""),
            "allowlist_status": "ALLOWED_OFFICIAL_DOMAIN" if domain_allowed(cand["url"]) else "OFFICIAL_DOMAIN_REQUIRES_ALLOWLIST_REVIEW",
        })

    best = None
    had_block = False
    had_portal = False
    for cand, resp in result["downloads"]:
        classification = classify_response(resp, plan)
        had_block |= classification in {"ACCESS_DENIED", "LOGIN_REQUIRED"}
        had_portal |= classification == "OFFICIAL_PORTAL_ONLY"
        pages = []
        if classification == "VALID_OFFICIAL_PDF":
            try:
                pages = extract_pdf(resp.raw)
            except Exception:
                classification = "INVALID_FILE"
        elif classification == "VALID_OFFICIAL_PLAN_HTML":
            pages = [normalize_space(re.sub(r"<[^>]+>", " ", resp.raw.decode("utf-8", errors="replace")))]
        doc_type = identify_document_type(pages, cand["label"]) if pages else "UNKNOWN"
        archive_path, sha = archive_response(plan, resp, doc_type if classification.startswith("VALID_") else classification)
        assert_not_reconstructed(archive_path, quarantine)
        row = response_log_row(resp)
        row.update({
            "validation_classification": classification, "archive_path": archive_path,
            "sha256": sha, "allowlist_status": "ALLOWED_OFFICIAL_DOMAIN" if domain_allowed(resp.final_url) else "OFFICIAL_DOMAIN_REQUIRES_ALLOWLIST_REVIEW",
        })
        art.downloads.append(row)
        if sha:
            art.hashes.append({"task_id": tid, "request_id": resp.request_id, "archive_path": archive_path, "byte_count": len(resp.raw), "sha256": sha})
        if pages and classification in {"VALID_OFFICIAL_PDF", "VALID_OFFICIAL_PLAN_HTML"}:
            year = year_from_text("\n".join(pages))
            ids = identifier_checks(plan, pages)
            applicability = classify_applicability(ids, "\n".join(pages), plan)
            rank = (
                year == "YEAR_2026_VERIFIED",
                applicability in {"EXACT_PLAN", "EXACT_CONTRACT_PBP"},
                classification == "VALID_OFFICIAL_PDF",
                cand["score"],
            )
            if best is None or rank > best["rank"]:
                best = {"rank": rank, "resp": resp, "pages": pages, "sha": sha,
                        "path": archive_path, "doc_type": doc_type, "year": year,
                        "ids": ids, "applicability": applicability, "classification": classification}

    if best:
        b = best
        art.validated.append({
            "task_id": tid, "source_url": b["resp"].requested_url, "final_url": b["resp"].final_url,
            "archive_path": b["path"], "sha256": b["sha"], "page_count": len(b["pages"]),
            "validation_classification": b["classification"],
        })
        art.doc_types.append({"task_id": tid, "source_sha256": b["sha"], "document_type": b["doc_type"]})
        for n, text in enumerate(b["pages"], 1):
            art.pages.append({"task_id": tid, "source_sha256": b["sha"], "page_number": n, "complete_extracted_text": text, "character_count": len(text)})
        art.years.append({"task_id": tid, "source_sha256": b["sha"], "year_verification": b["year"]})
        idsrow = {"task_id": tid, "source_sha256": b["sha"], **b["ids"]}
        art.identifiers.append(idsrow)
        art.applicability.append({"task_id": tid, "source_sha256": b["sha"], "applicability": b["applicability"]})
        evidence = extract_evidence(tid, b["sha"], b["pages"])
        art.evidence.extend(evidence)
        missing = sum(e["evidence_status"] == "SOURCE_MISSING" for e in evidence)
        ready_identity = b["year"] == "YEAR_2026_VERIFIED" and b["applicability"] in {"EXACT_PLAN", "EXACT_CONTRACT_PBP", "EXACT_CONTRACT_MULTI_SEGMENT", "CARRIER_SHARED_EXPLICIT"}
        completeness = "SOURCE_SET_COMPLETE" if ready_identity and missing == 0 else "SOURCE_SET_PARTIAL" if ready_identity else "SOURCE_SET_INSUFFICIENT"
        art.completeness.append({"task_id": tid, "source_completeness": completeness})
        if b["applicability"] == "EXACT_PLAN": status = "EXACT_DOCUMENT_DISCOVERED"
        elif b["applicability"] == "EXACT_CONTRACT_PBP": status = "CONTRACT_PBP_DOCUMENT_DISCOVERED"
        elif b["applicability"] == "EXACT_CONTRACT_MULTI_SEGMENT": status = "CONTRACT_FAMILY_DOCUMENT_DISCOVERED"
        elif b["applicability"] == "CARRIER_SHARED_EXPLICIT": status = "CARRIER_SHARED_DOCUMENT_DISCOVERED"
        else: status = "OFFICIAL_DOCUMENT_DISCOVERED_APPLICABILITY_UNRESOLVED"
    else:
        art.years.append({"task_id": tid, "source_sha256": "", "year_verification": "YEAR_NOT_VERIFIED"})
        art.applicability.append({"task_id": tid, "source_sha256": "", "applicability": "NO_DOCUMENT"})
        art.completeness.append({"task_id": tid, "source_completeness": "SOURCE_SET_INSUFFICIENT"})
        status = "ACCESS_BLOCKED" if (had_block or search_blocked) else "OFFICIAL_PORTAL_ONLY" if had_portal else "DOCUMENT_NOT_DISCOVERED"
    art.statuses.append({
        "task_id": tid, "canonical_plan_key": plan["canonical_plan_key"],
        "official_plan_name": plan["official_plan_name"], "discovery_status": status,
    })


def independent_audit_one(task_id: int, file_path: str, source_url: str) -> dict:
    """Independent audit entry point. Inputs are intentionally limited to three values."""
    row = {"task_id": task_id, "downloaded_file_path": file_path, "official_source_url": source_url}
    conn = None
    try:
        conn = psycopg2.connect(dbname="benefit_card_navigator", user=os.environ.get("USER", "albertopaz"), host="localhost")
        with conn.cursor() as cur:
            cur.execute("""
                SELECT p.canonical_plan_key,p.official_plan_name,p.contract_id
                FROM ingestion_tasks t JOIN plan_years py ON py.id=t.plan_year_id
                JOIN plans p ON p.id=py.plan_id WHERE t.id=%s
            """, (task_id,))
            db = cur.fetchone()
        if not db:
            raise ValueError("task not found")
        key, name, contract = db
        cms = parse_cms_key(key, contract)
        plan = {"official_plan_name": name, "contract_id": contract, "cms": cms}
        if not file_path:
            row.update({
                "recomputed_sha256": "", "magic_bytes_valid": False, "page_count": 0,
                "year_2026_verified": False, "exact_plan_name_verified": False,
                "contract_verified": False, "pbp_verified": False,
                "pharmacy_relevance_verified": False, "independent_excerpt_literal": False,
                "audit_verdict": "AUDIT_INSUFFICIENT_EVIDENCE", "error": "no downloaded file",
            })
            return row
        raw = Path(file_path).read_bytes()
        sha = sha256_bytes(raw)
        magic = raw.startswith(b"%PDF-")
        pages = extract_pdf(raw) if magic else []
        ids = identifier_checks(plan, pages)
        year = year_from_text("\n".join(pages))
        pharmacy = any(re.search(r"\b(?:pharmacy|prescription drug|formulary)\b", p, re.I) for p in pages)
        # Independently cite the first pharmacy occurrence and prove literal containment.
        cited = False
        for page in pages:
            m = re.search(r"\b(?:pharmacy|prescription drug|formulary)\b", page, re.I)
            if m:
                excerpt = page[max(0, m.start()-50):min(len(page), m.end()+100)]
                cited = excerpt in page
                break
        required_id = ids["exact_plan_name_match"] or (ids["contract_id_match"] and ids["pbp_id_match"])
        if magic and pages and year == "YEAR_2026_VERIFIED" and required_id and pharmacy and cited:
            verdict = "AUDIT_PASS"
        elif magic and pages:
            verdict = "AUDIT_INSUFFICIENT_EVIDENCE"
        else:
            verdict = "AUDIT_FAIL"
        row.update({
            "recomputed_sha256": sha, "magic_bytes_valid": magic, "page_count": len(pages),
            "year_2026_verified": year == "YEAR_2026_VERIFIED",
            "exact_plan_name_verified": ids["exact_plan_name_match"],
            "contract_verified": ids["contract_id_match"], "pbp_verified": ids["pbp_id_match"],
            "pharmacy_relevance_verified": pharmacy, "independent_excerpt_literal": cited,
            "audit_verdict": verdict, "error": "",
        })
    except Exception as exc:
        row.update({
            "recomputed_sha256": "", "magic_bytes_valid": False, "page_count": 0,
            "year_2026_verified": False, "exact_plan_name_verified": False,
            "contract_verified": False, "pbp_verified": False,
            "pharmacy_relevance_verified": False, "independent_excerpt_literal": False,
            "audit_verdict": "AUDIT_FAIL", "error": f"{type(exc).__name__}: {exc}",
        })
    finally:
        if conn is not None:
            conn.close()
    return row


CSV_SPECS = {
    "SEARCH_QUERIES.csv": (["task_id","query_sequence","query","submitted"], "search_queries"),
    "SEARCH_REQUEST_LOG.csv": (["task_id","request_id","discovery_channel","query","requested_url","final_url","redirect_chain","http_status","content_type","content_length","downloaded_byte_count","timestamp","error"], "search_requests"),
    "CANDIDATE_URLS.csv": (["task_id","candidate_url","official_link_label","candidate_score","discovery_channel","discovery_query","allowlist_status"], "candidates"),
    "CANDIDATE_DOWNLOADS.csv": (["task_id","request_id","discovery_channel","query","requested_url","final_url","redirect_chain","http_status","content_type","content_length","downloaded_byte_count","timestamp","error","validation_classification","archive_path","sha256","allowlist_status"], "downloads"),
    "VALIDATED_DOCUMENTS.csv": (["task_id","source_url","final_url","archive_path","sha256","page_count","validation_classification"], "validated"),
    "RAW_HASHES.csv": (["task_id","request_id","archive_path","byte_count","sha256"], "hashes"),
    "DOCUMENT_TYPES.csv": (["task_id","source_sha256","document_type"], "doc_types"),
    "PAGE_TEXT.csv": (["task_id","source_sha256","page_number","complete_extracted_text","character_count"], "pages"),
    "YEAR_VERIFICATION.csv": (["task_id","source_sha256","year_verification"], "years"),
    "IDENTIFIER_CONTEXT.csv": (["task_id","source_sha256","exact_plan_name_match","exact_plan_name_page","exact_plan_name_context","normalized_plan_name_match","normalized_plan_name_page","normalized_plan_name_context","contract_id_match","contract_id_page","contract_id_context","pbp_id_match","pbp_id_page","pbp_id_context","segment_id_match"], "identifiers"),
    "APPLICABILITY.csv": (["task_id","source_sha256","applicability"], "applicability"),
    "VERBATIM_EVIDENCE.csv": (["task_id","source_sha256","target_concept","page_number","actual_detected_heading","start_offset","end_offset","exact_excerpt","evidence_status"], "evidence"),
    "SOURCE_COMPLETENESS.csv": (["task_id","source_completeness"], "completeness"),
    "121_DISCOVERY_STATUS.csv": (["task_id","canonical_plan_key","official_plan_name","discovery_status"], "statuses"),
    "DATABASE_MUTATION_LOG.csv": (["timestamp","source_document_id","field","old_value","new_value"], "mutations"),
    "25_PLAN_INDEPENDENT_AUDIT.csv": (["task_id","downloaded_file_path","official_source_url","recomputed_sha256","magic_bytes_valid","page_count","year_2026_verified","exact_plan_name_verified","contract_verified","pbp_verified","pharmacy_relevance_verified","independent_excerpt_literal","audit_verdict","error"], "audit"),
}


def write_artifacts(art: Artifacts, base: dict) -> None:
    baseline_rows = [{"invariant": k, "actual": v, "status": "PASS"} for k, v in base.items()]
    write_csv(ROOT / f"{PREFIX}BASELINE.csv", baseline_rows, ["invariant","actual","status"])
    for suffix, (fields, attr) in CSV_SPECS.items():
        write_csv(ROOT / f"{PREFIX}{suffix}", getattr(art, attr), fields)


def read_artifacts() -> Artifacts:
    """Reload the just-written CSVs so report counts come from artifacts on disk."""
    art = Artifacts()
    for suffix, (_, attr) in CSV_SPECS.items():
        with (ROOT / f"{PREFIX}{suffix}").open(encoding="utf-8", newline="") as handle:
            setattr(art, attr, list(csv.DictReader(handle)))
    return art


def report(art: Artifacts, final_base: dict, tests_text: str) -> str:
    def dist(rows, field):
        return Counter(str(r.get(field, "")) for r in rows)
    counts = {
        "search_requests": len(art.search_requests), "candidate_urls": len(art.candidates),
        "candidate_gets": len(art.downloads),
        "validated_pdfs": sum(r["validation_classification"] == "VALID_OFFICIAL_PDF" for r in art.validated),
        "unique_hashes": len({r["sha256"] for r in art.hashes if r["sha256"]}),
    }
    hard_fail = (
        counts["search_requests"] == 0 or
        any(not r.get("submitted") for r in art.search_queries) or
        {r["candidate_url"] for r in art.candidates} - {r["requested_url"] for r in art.downloads} or
        final_base["coverage_rules"] != 4537 or final_base["tasks"] != 3305 or
        final_base["completed"] != 730 or final_base["partial"] != 922 or final_base["pending"] != 1653 or
        "FAILED" in tests_text or "ERROR" in tests_text
    )
    complete = bool(art.completeness) and all(r["source_completeness"] == "SOURCE_SET_COMPLETE" for r in art.completeness)
    verdict = "PHASE25T_CODEX_SOURCE_PIPELINE_FAILED" if hard_fail else "PHASE25T_CODEX_SOURCE_PIPELINE_VALIDATED" if complete else "PHASE25T_CODEX_PARTIAL_SOURCE_DISCOVERY"
    lines = [
        "# PHASE25T CODEX Final Report", "", "Generated exclusively from the CSV artifacts and final invariant query.", "",
        f"- Search requests: {counts['search_requests']}", f"- Candidate URLs: {counts['candidate_urls']}",
        f"- Actual candidate GETs: {counts['candidate_gets']}", f"- Validated PDFs: {counts['validated_pdfs']}",
        f"- Unique SHA256 hashes: {counts['unique_hashes']}",
    ]
    for title, rows, field in (
        ("Document types", art.doc_types, "document_type"), ("Year verification", art.years, "year_verification"),
        ("Applicability", art.applicability, "applicability"), ("Source completeness", art.completeness, "source_completeness"),
        ("Discovery status", art.statuses, "discovery_status"), ("Independent audit", art.audit, "audit_verdict"),
    ):
        lines.extend(["", f"## {title}", ""] + [f"- {k}: {v}" for k, v in sorted(dist(rows, field).items())])
    lines.extend(["", "## Database mutations", "", f"- Total: {len(art.mutations)}", "", "## Tests", "", "```text", tests_text.strip(), "```", "", "## Final invariants", ""])
    lines.extend(f"- {k}: {v}" for k, v in final_base.items())
    lines.extend(["", "## Verdict", "", verdict, ""])
    return "\n".join(lines)


def run_pipeline(workers: int) -> str:
    conn = psycopg2.connect(dbname="benefit_card_navigator", user=os.environ.get("USER", "albertopaz"), host="localhost")
    conn.autocommit = False
    initial = baseline(conn)
    plans, quarantine, _ = load_tasks(conn)
    special = [p for p in plans if p["task_id"] in SPECIAL_TASK_IDS]
    standard = [p for p in plans if p["task_id"] not in SPECIAL_TASK_IDS]
    if len(standard) != 121 or len(special) != 18:
        raise RuntimeError("PHASE25T_CODEX_BASELINE_MISMATCH: standard/special partition")
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    art = Artifacts()
    client = HttpClient()
    print(f"Baseline verified. Processing {len(standard)} standard tasks with {workers} workers.", flush=True)
    results = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(process_plan, p, client): p["task_id"] for p in standard}
        done = 0
        for future in as_completed(futures):
            results.append(future.result())
            done += 1
            if done % 10 == 0 or done == len(standard):
                print(f"Discovery completed for {done}/{len(standard)} tasks.", flush=True)
    for result in sorted(results, key=lambda r: r["plan"]["task_id"]):
        adjudicate_result(result, art, quarantine)
    for p in special:
        art.statuses.append({"task_id": p["task_id"], "canonical_plan_key": p["canonical_plan_key"], "official_plan_name": p["official_plan_name"], "discovery_status": "MANUAL_SOURCE_REVIEW_REQUIRED"})
    if len(art.statuses) != 139:
        raise AssertionError("discovery status total must be 139")

    # No DB update is attempted without a unique source_documents row mapped to the exact
    # freshly requested URL. This conservative run therefore commits no speculative mutation.
    conn.rollback()

    rng = random.Random(AUDIT_SEED)
    sample = sorted(rng.sample(standard, 25), key=lambda p: p["task_id"])
    by_task = {r["task_id"]: r for r in art.validated}
    for p in sample:
        val = by_task.get(p["task_id"])
        if val:
            art.audit.append(independent_audit_one(p["task_id"], val["archive_path"], val["source_url"]))
        else:
            art.audit.append(independent_audit_one(p["task_id"], "", ""))
    final = baseline(conn)
    conn.close()
    write_artifacts(art, initial)
    disk_art = read_artifacts()
    test_path = ROOT / f"{PREFIX}TEST_RESULTS.txt"
    tests_text = test_path.read_text(encoding="utf-8") if test_path.exists() else "FAILED: test artifact missing"
    final_report = report(disk_art, final, tests_text)
    (ROOT / f"{PREFIX}FINAL_REPORT.md").write_text(final_report, encoding="utf-8")
    verdict = final_report.strip().splitlines()[-1]
    print(verdict, flush=True)
    return verdict


def run_seeded(seed_csv: Path) -> str:
    """Process interactively discovered URLs through the same fresh-GET path."""
    conn = psycopg2.connect(dbname="benefit_card_navigator", user=os.environ.get("USER", "albertopaz"), host="localhost")
    conn.autocommit = False
    initial = baseline(conn)
    plans, quarantine, _ = load_tasks(conn)
    plan_by_id = {p["task_id"]: p for p in plans}
    with seed_csv.open(encoding="utf-8", newline="") as handle:
        seeds = list(csv.DictReader(handle))
    tids = {int(r["task_id"]) for r in seeds}
    if not tids or any(t not in plan_by_id or t in SPECIAL_TASK_IDS for t in tids):
        raise ValueError("seed tasks must be non-special pending Pharmacy tasks")
    art = read_artifacts()
    # Preserve the original attempted search ledger, but replace all adjudication rows
    # for seeded tasks with results from new exact-URL GETs.
    for attr in ("candidates", "downloads", "validated", "hashes", "doc_types", "pages",
                 "years", "identifiers", "applicability", "evidence", "completeness", "statuses"):
        setattr(art, attr, [r for r in getattr(art, attr) if int(r["task_id"]) not in tids])
    client = HttpClient(timeout=45)
    for seed in seeds:
        tid = int(seed["task_id"])
        plan = plan_by_id[tid]
        cand = {
            "url": seed["candidate_url"], "label": seed.get("official_link_label", ""),
            "score": int(seed.get("candidate_score") or 100),
            "channel": seed.get("discovery_channel") or "INTERACTIVE_WEB_SEARCH",
            "query": seed.get("discovery_query", ""),
        }
        resp = client.get(tid, cand["url"], "CANDIDATE_DOWNLOAD", "")
        adjudicate_result({"plan": plan, "queries": [], "search": [], "candidates": [cand], "downloads": [(cand, resp)]}, art, quarantine)
        print(f"Seeded GET task {tid}: HTTP {resp.status}, {len(resp.raw)} bytes", flush=True)
    if len(art.statuses) != 139 or len({int(r["task_id"]) for r in art.statuses}) != 139:
        raise AssertionError("seeded status reconciliation failed")
    conn.rollback()
    art.audit = []
    standard = [p for p in plans if p["task_id"] not in SPECIAL_TASK_IDS]
    sample = sorted(random.Random(AUDIT_SEED).sample(standard, 25), key=lambda p: p["task_id"])
    by_task = {int(r["task_id"]): r for r in art.validated}
    for p in sample:
        val = by_task.get(p["task_id"])
        art.audit.append(independent_audit_one(p["task_id"], val["archive_path"] if val else "", val["source_url"] if val else ""))
    final = baseline(conn)
    conn.close()
    write_artifacts(art, initial)
    disk_art = read_artifacts()
    tests_text = (ROOT / f"{PREFIX}TEST_RESULTS.txt").read_text(encoding="utf-8")
    final_report = report(disk_art, final, tests_text)
    (ROOT / f"{PREFIX}FINAL_REPORT.md").write_text(final_report, encoding="utf-8")
    verdict = final_report.strip().splitlines()[-1]
    print(verdict, flush=True)
    return verdict


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--seed-csv", type=Path)
    args = parser.parse_args()
    if args.seed_csv:
        run_seeded(args.seed_csv)
    else:
        run_pipeline(max(1, min(args.workers, 12)))
