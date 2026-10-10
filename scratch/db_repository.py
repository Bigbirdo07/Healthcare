import os
import psycopg2
from psycopg2.extras import RealDictCursor

DB_URI = os.getenv("DATABASE_URL", "postgresql://albertopaz@localhost:5432/benefit_card_navigator")

def get_db_connection():
    return psycopg2.connect(DB_URI)

def get_states():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT DISTINCT state FROM plans ORDER BY state;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [r["state"] for r in rows]

def get_insurance_types(state=None):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    if state:
        cur.execute("SELECT DISTINCT market_segment FROM plans WHERE state = %s ORDER BY market_segment;", (state,))
    else:
        cur.execute("SELECT DISTINCT market_segment FROM plans ORDER BY market_segment;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [r["market_segment"] for r in rows]

def get_insurers(state=None, insurance_type=None):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    query = "SELECT DISTINCT i.canonical_insurer_key, i.official_name, i.display_name FROM insurers i JOIN plans p ON p.insurer_id = i.id WHERE 1=1"
    params = []
    if state:
        query += " AND p.state = %s"
        params.append(state)
    if insurance_type:
        query += " AND p.market_segment = %s"
        params.append(insurance_type)
    query += " ORDER BY i.official_name;"
    cur.execute(query, tuple(params))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [dict(r) for r in rows]

def get_plans(state=None, insurance_type=None, insurer=None):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    query = """
        SELECT p.id as plan_id, p.canonical_plan_key, p.repository_plan_id, p.official_plan_name,
               p.display_name, p.state, p.market_segment, i.official_name as insurer_name, py.year as plan_year
        FROM plans p
        JOIN insurers i ON p.insurer_id = i.id
        JOIN plan_years py ON py.plan_id = p.id
        WHERE py.year = 2026
    """
    params = []
    if state:
        query += " AND p.state = %s"
        params.append(state)
    if insurance_type:
        query += " AND p.market_segment = %s"
        params.append(insurance_type)
    if insurer:
        query += " AND (i.official_name = %s OR i.canonical_insurer_key = %s)"
        params.extend([insurer, insurer])
    query += " ORDER BY p.official_plan_name;"
    cur.execute(query, tuple(params))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [dict(r) for r in rows]

def get_plan(plan_id, year=2026):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    query = """
        SELECT p.id as plan_id, p.canonical_plan_key, p.repository_plan_id, p.official_plan_name,
               p.display_name, p.state, p.market_segment, i.official_name as insurer_name,
               py.id as plan_year_id, py.year as plan_year, pr.classification as readiness_classification
        FROM plans p
        JOIN insurers i ON p.insurer_id = i.id
        JOIN plan_years py ON py.plan_id = p.id
        LEFT JOIN plan_readiness pr ON pr.plan_year_id = py.id
        WHERE (p.repository_plan_id = %s OR p.canonical_plan_key = %s OR CAST(p.id AS VARCHAR) = %s)
          AND py.year = %s;
    """
    cur.execute(query, (str(plan_id), str(plan_id), str(plan_id), year))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return dict(row) if row else None

def get_plan_coverage(plan_id, year=2026):
    plan_info = get_plan(plan_id, year)
    if not plan_info:
        return []
    py_id = plan_info["plan_year_id"]

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    query = """
        SELECT cr.id as database_rule_id, cr.legacy_rule_id, cr.target_type, cr.coverage_status,
               cr.coverage_pathway, cr.member_cost_text, cr.requires_rx, cr.requires_prior_auth,
               cr.verification_status, cr.batch_id,
               prod.canonical_product_key as product_id, prod.name as product_name,
               svc.canonical_service_key as service_id, svc.name as service_name,
               ben.canonical_benefit_key as benefit_id, ben.name as benefit_name,
               re.evidence_excerpt, sd.source_key, sd.publisher, sd.document_title, sd.source_url
        FROM coverage_rules cr
        LEFT JOIN products prod ON cr.product_id = prod.id
        LEFT JOIN services svc ON cr.service_id = svc.id
        LEFT JOIN benefits ben ON cr.benefit_id = ben.id
        LEFT JOIN rule_evidence re ON re.coverage_rule_id = cr.id
        LEFT JOIN source_documents sd ON re.source_document_id = sd.id
        WHERE cr.plan_year_id = %s
        ORDER BY cr.id;
    """
    cur.execute(query, (py_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    normalized = []
    for r in rows:
        t_name = r["product_name"] or r["service_name"] or r["benefit_name"] or "Coverage Item"
        t_id = r["product_id"] or r["service_id"] or r["benefit_id"] or r["legacy_rule_id"]
        cost_text = r["member_cost_text"] or "$0 Copay"
        
        cost_lower = cost_text.lower()
        path_lower = (r["coverage_pathway"] or "").lower()
        if "otc" in path_lower or "allowance" in cost_lower or "rx" in cost_lower or "prescription" in cost_lower or r["requires_rx"]:
            cta = "ADD_TO_REQUEST"
        else:
            cta = "DIRECT_BENEFIT_ACCESS"

        normalized.append({
            "rule_id": r["legacy_rule_id"],
            "plan_id": plan_info["repository_plan_id"],
            "canonical_plan_key": plan_info["canonical_plan_key"],
            "plan_year": year,
            "target_type": r["target_type"],
            "target_id": t_id,
            "target_name": t_name,
            "coverage_status": r["coverage_status"],
            "coverage_pathway": r["coverage_pathway"],
            "member_cost": cost_text,
            "copay": 0.0,
            "coinsurance": 0.0,
            "allowance_amount": 0.0,
            "allowance_frequency": "QUARTERLY" if "quarterly" in cost_text.lower() else "ANNUAL",
            "requirements": "In-Network Provider Required" if r["requires_prior_auth"] else "Standard Plan Benefit",
            "cta": cta,
            "source": r["document_title"] or "2026 Evidence of Coverage",
            "source_id": r["source_key"],
            "source_url": r["source_url"],
            "verification_status": r["verification_status"]
        })
    return normalized

def get_rule_evidence(rule_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    query = """
        SELECT cr.legacy_rule_id, cr.verification_status, sd.source_key, sd.publisher,
               sd.publisher_domain, sd.document_title, sd.source_url, sd.sha256,
               re.page_reference, re.section_reference, re.evidence_excerpt
        FROM coverage_rules cr
        JOIN rule_evidence re ON re.coverage_rule_id = cr.id
        JOIN source_documents sd ON re.source_document_id = sd.id
        WHERE cr.legacy_rule_id = %s OR cr.legacy_rule_id LIKE %s OR CAST(cr.id AS VARCHAR) = %s;
    """
    cur.execute(query, (str(rule_id), f"{rule_id}%", str(rule_id)))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return dict(row) if row else None

def get_admin_progress():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("SELECT count(*) as total FROM v_plan_verification_status;")
    tot_plans = cur.fetchone()["total"]
    
    cur.execute("SELECT count(*) as verified_count FROM v_plan_verification_status WHERE has_verified_coverage_data = true;")
    verified_plans = cur.fetchone()["verified_count"]
    
    unverified_plans = tot_plans - verified_plans
    
    cur.execute("SELECT count(*) as pending FROM ingestion_tasks WHERE task_status != 'COMPLETED';")
    pending_tasks = cur.fetchone()["pending"]
    
    cur.execute("SELECT readiness_classification, count(*) as count FROM v_plan_verification_status GROUP BY readiness_classification;")
    readiness_rows = cur.fetchall()
    readiness_dist = {r["readiness_classification"]: r["count"] for r in readiness_rows}
    
    cur.execute("""
        SELECT benefit_domain, 
               count(CASE WHEN status = 'COMPLETE' THEN 1 END) as complete_count,
               count(CASE WHEN status = 'PARTIAL' THEN 1 END) as partial_count,
               count(CASE WHEN status = 'NOT_INGESTED' THEN 1 END) as not_ingested_count
        FROM plan_domain_status
        GROUP BY benefit_domain
        ORDER BY benefit_domain;
    """)
    domain_rows = cur.fetchall()
    domain_summary = {r["benefit_domain"]: dict(r) for r in domain_rows}
    
    cur.close()
    conn.close()
    
    return {
        "total_plans": tot_plans,
        "plans_with_verified_coverage_data": verified_plans,
        "plans_without_verified_coverage_data": unverified_plans,
        "pending_tasks": pending_tasks,
        "readiness_distribution": readiness_dist,
        "domain_completion_summary": domain_summary
    }

