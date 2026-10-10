"""Build Rhode Island 2026 coverage rules from verbatim evidence.

Reads data/ri_verified_coverage_2026/evidence_spec.json, checks every source
PDF against its recorded SHA-256, and confirms every excerpt appears in the
PDF text (whitespace-insensitive). Any failure aborts the build, so a rule can
only reach the marketplace if its quote is really in the official document.

Outputs (in data/ri_verified_coverage_2026/):
  RI_VERIFIED_RULES_2026.json   rules + new benefits + new plans for the bundle
  RI_VERIFIED_RULES_AUDIT.csv   one row per rule with page citations

Then run: node scratch/apply_ri_verified_rules.js

Other states use the same builder with their own spec, which sets "state":
  python3 scratch/build_ri_verified_rules.py data/ny_verified_coverage_2026/evidence_spec.json
writes NY_VERIFIED_RULES_2026.json / NY_VERIFIED_RULES_AUDIT.csv next to it.
"""
import csv
import hashlib
import html
import io
import json
import os
import re
import subprocess
import tempfile
import zipfile
import sys
from datetime import date

import pypdf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "data", "ri_verified_coverage_2026")
SPEC_PATH = os.path.join(OUT_DIR, "evidence_spec.json")


def normalize(text):
    text = text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    # Non-breaking hyphens and soft hyphens used in some insurer PDFs.
    text = text.replace("‑", "-").replace("‐", "-").replace("­", "")
    # Footnote daggers that column extraction leaves mid-sentence.
    text = text.replace("— ††", " ").replace("††", " ")
    text = re.sub(r"\s—\s", " ", text)
    text = re.sub(r"\s+", " ", text)
    # PDF line breaks split hyphenated words ("Medicare- covered").
    text = re.sub(r"-\s+(?=[a-z])", "-", text)
    return text.strip()


COST = re.compile(r"\$\d|\d+% coinsurance|copay", re.I)


def squash(text):
    return re.sub(r"\s+", "", normalize(text))


def load_source(src):
    path = os.path.join(ROOT, src["file"])
    with open(path, "rb") as f:
        digest = hashlib.sha256(f.read()).hexdigest()
    if digest != src["sha256"]:
        raise SystemExit(f"SHA-256 mismatch for {src['file']}: expected {src['sha256']}, got {digest}")
    if path.endswith(".html"):
        # A saved official web page counts as one "page" of visible text.
        with open(path, encoding="utf-8", errors="ignore") as f:
            raw = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", f.read(), flags=re.S)
        return [normalize(html.unescape(re.sub(r"<[^>]+>", " ", raw)))]
    if src.get("format") == "csv_rows":
        # A CSV inside a zip (e.g. the CMS State-Based Exchange PUF): each data
        # row becomes one quotable line, "PLAN <id> · <benefit> · Covered: ...".
        # A source may list "fields" as [label, column] pairs; the default is
        # the PUF benefits layout.
        with zipfile.ZipFile(path) as z, z.open(src["zip_member"]) as f:
            rows = csv.DictReader(io.TextIOWrapper(f, encoding="utf-8-sig"))
            if "fields" in src:
                return [normalize(" · ".join([f"PLAN {r['PLAN ID']}"] + [f"{label}: {r[col].strip()}" for label, col in src["fields"]]))
                        for r in rows]
            return [normalize(" · ".join([f"PLAN {r['PLAN ID']}", r["BENEFIT NAME"], f"Covered: {r['IS COVERED']}",
                                           f"Limit: {r['LIMIT QUANTITY']} {r['LIMIT UNIT']}".strip(),
                                           f"Exclusions: {r['EXCLUSIONS']}", f"Explanation: {r['EXPLANATION']}"]))
                    for r in rows]
    if src.get("extractor") == "pdfkit":
        # Some insurer PDFs (e.g. Wellcare) defeat pypdf; macOS PDFKit reads them.
        script = os.path.join(ROOT, "scratch", "pdfkit_text.swift")
        with tempfile.NamedTemporaryFile(suffix=".json") as tmp:
            subprocess.run(["swift", script, path, tmp.name], check=True, capture_output=True)
            return [normalize(p) for p in json.load(open(tmp.name, encoding="utf-8"))]
    reader = pypdf.PdfReader(path)
    if src.get("layout") == "columns":
        return [normalize(column_text(p)) for p in reader.pages]
    if src.get("layout") == "columns3":
        splits = tuple(src.get("splits", (0.455, 0.68)))
        return [normalize(column_text(p, splits)) for p in reader.pages]
    return [normalize(p.extract_text() or "") for p in reader.pages]


def column_text(page, splits=(0.56,)):
    """Page text with benefit-chart columns kept apart ("Covered service" ||
    "What you pay" [|| out-of-network]), for charts that plain extraction
    interleaves mid-sentence. `splits` are column edges as a share of page width."""
    chunks = []

    def visit(text, cm, tm, font, size):
        if text.strip():
            chunks.append((tm[4] * cm[0] + cm[4], tm[5] * cm[3] + cm[5], text))

    page.extract_text(visitor_text=visit)
    edges = [0.0] + [float(page.mediabox.width) * s for s in splits] + [float("inf")]
    ordered = lambda cs: " ".join(t for _, _, t in sorted(cs, key=lambda c: (-round(c[1]), c[0])))
    return " || ".join(ordered([c for c in chunks if lo <= c[0] < hi]) for lo, hi in zip(edges, edges[1:]))


def target_type(target_id):
    return {"P": "PRODUCT", "S": "SERVICE", "B": "BENEFIT"}[target_id[0]]


def main():
    spec_path = sys.argv[1] if len(sys.argv) > 1 else SPEC_PATH
    spec = json.load(open(spec_path, encoding="utf-8"))
    state = spec.get("state", "RI")
    out_dir = os.path.dirname(os.path.abspath(spec_path))
    pages_by_source = {key: load_source(src) for key, src in spec["sources"].items()}
    squashed_pages = {key: [squash(p) for p in pages] for key, pages in pages_by_source.items()}
    groups = spec["groups"]
    templates = spec["templates"]
    today = date.today().isoformat()

    rules, audit, failures, seen = [], [], [], {}
    # "fallback" entries (e.g. statewide Medicaid rules) only fill items a
    # plan-specific entry did not cover, so they are processed last.
    ordered = sorted(enumerate(spec["rules"], 1), key=lambda item: bool(item[1].get("fallback")))
    for n, entry in ordered:
        source_key = entry["source"]
        source = spec["sources"][source_key]

        # An excerpt is a string quoted from the rule's source, or
        # {"source": KEY, "text": ..., "column": N} to cite a second document
        # or one column of a multi-column chart (0 = covered service,
        # 1 = in-network cost, 2 = out-of-network cost).
        cited = []
        for excerpt in entry["excerpts"]:
            ex = excerpt if isinstance(excerpt, dict) else {"text": excerpt}
            ex_source = ex.get("source", source_key)
            text, column = ex["text"], ex.get("column")
            # In/out-of-network charts print both costs on the same page, so a
            # cost quote must name its column or an out-of-network amount
            # could pass as in-network.
            if spec["sources"][ex_source].get("layout") == "columns3" and column is None and COST.search(text):
                failures.append(f"rule #{n} ({entry['plans']} / {entry['targets']}): cost quote from a 3-column chart must set \"column\": {text[:70]!r}")
                continue
            # Compare with all whitespace removed: PDF text extraction splits
            # words ("c overed") and spaces punctuation, but every letter and
            # symbol of the quote must still appear in order.
            needle = squash(text)
            if column is None:
                hits = [i + 1 for i, page in enumerate(squashed_pages[ex_source]) if needle in page]
            else:
                hits = [i + 1 for i, page in enumerate(pages_by_source[ex_source])
                        if needle in squash(page.split(" || ")[column] if page.count(" || ") >= column else "")]
            if not hits:
                failures.append(f"rule #{n} ({entry['plans']} / {entry['targets']}): excerpt not found in {ex_source}: {text[:90]!r}")
            else:
                cited.append((ex_source, hits[0], text))
        if len(cited) != len(entry["excerpts"]):
            continue

        template = templates.get(entry.get("template"), {})
        targets = groups.get(entry["targets"], [entry["targets"]])
        pages_cited = {}
        for key, page, _ in cited:
            pages_cited.setdefault(key, set()).add(page)
        labels = []
        for key, pages in pages_cited.items():
            kind = spec["sources"][key]
            if kind.get("format") == "csv_rows":
                where = "CSV line " + ", ".join(str(p + 1) for p in sorted(pages))  # +1 for the header line
            elif kind["file"].endswith(".html"):
                where = "web page"
            else:
                where = "PDF page " + ", ".join(map(str, sorted(pages)))
            labels.append(where if key == source_key else f"{spec['sources'][key]['title']}, {where}")
        page_label = "; ".join(labels)
        excerpt_text = " … ".join(t for _, _, t in cited)
        extra_sources = sorted({k for k, _, _ in cited if k != source_key})

        for plan_id in spec["plans"][entry["plans"]]:
            for target_id in targets:
                key = (plan_id, target_id)
                if key in seen:
                    if not entry.get("fallback"):
                        failures.append(f"rule #{n}: duplicate rule for {plan_id} / {target_id} (also rule #{seen[key]})")
                    continue
                seen[key] = n
                ttype = target_type(target_id)
                rule = {
                    "rule_id": f"R-{state}26-" + re.sub(r"[^A-Za-z0-9]+", "-", f"{plan_id}-{target_id}").strip("-"),
                    "target_type": ttype,
                    "target_id": target_id,
                    "plan_id": plan_id,
                    "state": state,
                    "plan_year": 2026,
                    "coverage_status": entry["status"],
                    "benefit_pathway": entry.get("pathway", template.get("pathway", "")),
                    "member_cost": entry["member_cost"],
                    "requirements": entry.get("requirements", template.get("requirements", "")),
                    "source_id": f"SRC-{state}26-{source_key}",
                    "official_source_name": source["title"],
                    "official_source_url": source["url"],
                    "source_document_sha256": source["sha256"],
                    "source_page": page_label,
                    "evidence_excerpt": excerpt_text,
                    "additional_sources": [{"title": spec["sources"][k]["title"], "url": spec["sources"][k]["url"]} for k in extra_sources],
                    "notes": entry.get("notes", ""),
                    "verification_status": "EXCERPT_MATCHED_IN_SOURCE_DOCUMENT",
                    "last_verified_date": today,
                }
                rule[{"PRODUCT": "product_id", "SERVICE": "service_id", "BENEFIT": "benefit_id"}[ttype]] = target_id
                rules.append(rule)
                audit.append({
                    "rule_id": rule["rule_id"], "plan_id": plan_id, "target_id": target_id,
                    "coverage_status": rule["coverage_status"], "member_cost": rule["member_cost"],
                    "source": source_key, "source_page": page_label, "evidence_excerpt": rule["evidence_excerpt"],
                })

    if failures:
        print("BUILD FAILED - evidence problems:")
        for f in failures:
            print("  -", f)
        sys.exit(1)

    benefits = [{**b, "benefit_id": b["id"], "rule_only": True, "badge_label": "PLAN BENEFIT"} for b in spec["new_benefits"]]
    rules_path = os.path.join(out_dir, f"{state}_VERIFIED_RULES_2026.json")
    audit_path = os.path.join(out_dir, f"{state}_VERIFIED_RULES_AUDIT.csv")
    out = {
        "generated": today,
        "generator": "scratch/build_ri_verified_rules.py",
        "rules": rules,
        "benefits": benefits,
        "plans": spec["new_plans"],
    }
    with open(rules_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    with open(audit_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(audit[0].keys()))
        writer.writeheader()
        writer.writerows(audit)

    per_plan = {}
    for r in rules:
        per_plan[r["plan_id"]] = per_plan.get(r["plan_id"], 0) + 1
    print(f"OK: {len(rules)} rules from {len(spec['rules'])} evidence entries, every excerpt matched.")
    for plan_id, count in sorted(per_plan.items()):
        print(f"  {plan_id}: {count} rules")


if __name__ == "__main__":
    main()
