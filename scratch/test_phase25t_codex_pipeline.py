import hashlib
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import psycopg2

sys.path.insert(0, str(Path(__file__).resolve().parent))
import phase25t_codex_pipeline as p


class FakeClient:
    def __init__(self, responses=None):
        self.responses = responses or {}
        self.calls = []
    def get(self, task_id, url, channel, query=""):
        self.calls.append(url)
        status, ctype, raw = self.responses.get(url, (404, "text/html", b""))
        return p.Response("R", task_id, channel, query, url, url, [], status, ctype, str(len(raw)), raw, p.utcnow())


def plan():
    cms = {"state":"RI","contract":"H5987","pbp":"001","segment":"000","year":"2026"}
    return {"task_id":1,"canonical_plan_key":"CMS:RI:H5987:001:000:2026","official_plan_name":"Exact Plan",
            "carrier":"Carrier","state":"RI","contract_id":"H5987","pbp_id":"001","segment_id":"000",
            "identifier_integrity":"VALID","cms":cms}


class Phase25TNegativeTests(unittest.TestCase):
    def test_01_reconstructed_path_cannot_be_used(self):
        with self.assertRaises(AssertionError):
            p.assert_not_reconstructed("/tmp/reconstructed.pdf", {"/tmp/reconstructed.pdf"})

    def test_02_failed_download_has_no_local_fallback(self):
        pl = plan(); query_urls = [p.search_url(q) for q in p.build_queries(pl)]
        client = FakeClient({u:(200,"text/html",b'<a href="https://cms.gov/doc.pdf">doc</a>') for u in query_urls})
        result = p.process_plan(pl, client)
        self.assertEqual(result["downloads"][0][1].status, 404)
        self.assertEqual(result["downloads"][0][1].raw, b"")

    def test_03_homepage_html_not_plan_document(self):
        r = p.Response("R",1,"x","","https://cms.gov/","https://cms.gov/",[],200,"text/html","",b"<html>CMS home</html>",p.utcnow())
        self.assertNotEqual(p.classify_response(r, plan()), "VALID_OFFICIAL_PLAN_HTML")

    def test_04_candidate_url_get_is_executed(self):
        pl=plan(); target="https://cms.gov/evidence.pdf"
        responses={p.search_url(q):(200,"text/html",f'<a href="{target}">Evidence of Coverage</a>'.encode()) for q in p.build_queries(pl)}
        client=FakeClient(responses); result=p.process_plan(pl,client)
        self.assertIn(target, client.calls)
        self.assertTrue(result["downloads"])

    def test_05_sha_matches_raw_saved_bytes(self):
        raw=b"remote exact bytes"
        self.assertEqual(p.sha256_bytes(raw), hashlib.sha256(raw).hexdigest())

    def test_06_year_not_inferred_from_filename(self):
        self.assertEqual(p.year_from_text("Evidence of Coverage with no stated plan year"), "YEAR_NOT_VERIFIED")

    def test_07_pbp_requires_canonical_and_source_combo(self):
        self.assertIsNone(p.parse_cms_key("QHP:RI:x", "N/A"))
        ids=p.identifier_checks(plan(), ["H5987 appears here and 001 appears elsewhere without a compound identifier"])
        self.assertFalse(ids["pbp_id_match"])

    def test_grouped_contract_pbp_list_is_explicit(self):
        ids=p.identifier_checks(plan(), ["Complete Contract/PBP list: H5987-002, 001, 017"])
        self.assertTrue(ids["pbp_id_match"])

    def test_formulary_title_beats_eoc_cross_reference(self):
        pages=["2026 Prescription Drug Guide Formulary. Read your Evidence of Coverage for costs."]
        self.assertEqual(p.identify_document_type(pages),"FORMULARY")

    def test_08_carrier_state_not_exact_applicability(self):
        ids={"exact_plan_name_match":False,"contract_id_match":False,"pbp_id_match":False}
        self.assertEqual(p.classify_applicability(ids,"Carrier serves Rhode Island",plan()), "CARRIER_SHARED_UNPROVEN")

    def test_09_excerpt_is_literal_page_slice(self):
        page="Heading\nTier 1 preferred generic has a five dollar copay."
        row=p.extract_evidence(1,"abc",[page])[0]
        self.assertIn(row["exact_excerpt"],page)
        self.assertEqual(row["exact_excerpt"],page[int(row["start_offset"]):int(row["end_offset"])])

    def test_10_auditor_signature_excludes_primary_artifacts(self):
        import inspect
        self.assertEqual(list(inspect.signature(p.independent_audit_one).parameters), ["task_id","file_path","source_url"])

    def test_11_coverage_rules_invariant_expected(self):
        conn=psycopg2.connect(dbname="benefit_card_navigator",user=os.environ.get("USER","albertopaz"),host="localhost")
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM coverage_rules")
                self.assertEqual(cur.fetchone()[0],4537)
        finally:
            conn.close()

    def test_12_ingestion_counts_expected(self):
        conn=psycopg2.connect(dbname="benefit_card_navigator",user=os.environ.get("USER","albertopaz"),host="localhost")
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*),COUNT(*) FILTER (WHERE task_status='COMPLETED'),COUNT(*) FILTER (WHERE task_status='PARTIAL'),COUNT(*) FILTER (WHERE task_status='PENDING') FROM ingestion_tasks")
                self.assertEqual(cur.fetchone(),(3305,730,922,1653))
        finally:
            conn.close()

    def test_negative_identifier_mismatch(self):
        with self.assertRaisesRegex(ValueError,"IDENTIFIER_INTEGRITY_FAILURE"):
            p.parse_cms_key("CMS:RI:H5987:001:000:2026","H0000")

    def test_negative_invalid_pdf(self):
        r=p.Response("R",1,"x","","https://cms.gov/x.pdf","https://cms.gov/x.pdf",[],200,"application/pdf","",b"%PDF-not-real",p.utcnow())
        self.assertEqual(p.classify_response(r,plan()),"INVALID_FILE")

    def test_negative_audit_does_not_default_pass(self):
        class Cur:
            def __enter__(self): return self
            def __exit__(self,*args): pass
            def execute(self,*args): pass
            def fetchone(self): return ("CMS:RI:H5987:001:000:2026","Exact Plan","H5987")
        class C:
            def cursor(self): return Cur()
            def close(self): pass
        with patch.object(p.psycopg2,"connect",return_value=C()):
            row=p.independent_audit_one(1,"/definitely/missing.pdf","https://cms.gov/x.pdf")
        self.assertEqual(row["audit_verdict"],"AUDIT_FAIL")


if __name__ == "__main__":
    unittest.main(verbosity=2)
