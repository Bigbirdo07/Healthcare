import os
import time
import json
import psycopg2
from psycopg2.extras import RealDictCursor

import db_repository
import legacy_repository

def get_data_source_mode():
    return os.getenv("DATA_SOURCE", "database") # Default after cutover gate, or configured

def resolve_get_states():
    mode = get_data_source_mode()
    if mode == "database":
        try:
            return db_repository.get_states()
        except Exception as e:
            if os.getenv("DB_FAILURE_FALLBACK") == "legacy":
                print(f"[FALLBACK LOG] DB Failure in get_states: {e}. Falling back to legacy.")
                return legacy_repository.get_states()
            raise e
    elif mode == "shadow":
        legacy_res = legacy_repository.get_states()
        try:
            db_res = db_repository.get_states()
            log_shadow_comparison("get_states", None, legacy_res, db_res)
        except Exception as e:
            print(f"[SHADOW MISMATCH LOG] DB Execution error in shadow get_states: {e}")
        return legacy_res
    else:
        return legacy_repository.get_states()

def resolve_get_plans(state=None, insurance_type=None, insurer=None):
    mode = get_data_source_mode()
    if mode == "database":
        try:
            return db_repository.get_plans(state, insurance_type, insurer)
        except Exception as e:
            if os.getenv("DB_FAILURE_FALLBACK") == "legacy":
                print(f"[FALLBACK LOG] DB Failure in get_plans: {e}. Falling back to legacy.")
                return legacy_repository.get_plans(state, insurance_type, insurer)
            raise e
    elif mode == "shadow":
        legacy_res = legacy_repository.get_plans(state, insurance_type, insurer)
        try:
            db_res = db_repository.get_plans(state, insurance_type, insurer)
            log_shadow_comparison("get_plans", None, legacy_res, db_res)
        except Exception as e:
            print(f"[SHADOW MISMATCH LOG] DB Execution error in shadow get_plans: {e}")
        return legacy_res
    else:
        return legacy_repository.get_plans(state, insurance_type, insurer)

def resolve_get_plan(plan_id, year=2026):
    mode = get_data_source_mode()
    if mode == "database":
        try:
            res = db_repository.get_plan(plan_id, year)
            if not res and os.getenv("DB_FAILURE_FALLBACK") == "legacy":
                return legacy_repository.get_plan(plan_id, year)
            return res
        except Exception as e:
            if os.getenv("DB_FAILURE_FALLBACK") == "legacy":
                print(f"[FALLBACK LOG] DB Failure in get_plan: {e}. Falling back to legacy.")
                return legacy_repository.get_plan(plan_id, year)
            raise e
    elif mode == "shadow":
        legacy_res = legacy_repository.get_plan(plan_id, year)
        try:
            db_res = db_repository.get_plan(plan_id, year)
            log_shadow_comparison("get_plan", plan_id, legacy_res, db_res)
        except Exception as e:
            print(f"[SHADOW MISMATCH LOG] DB Execution error in shadow get_plan: {e}")
        return legacy_res
    else:
        return legacy_repository.get_plan(plan_id, year)

def resolve_get_plan_coverage(plan_id, year=2026):
    mode = get_data_source_mode()
    if mode == "database":
        try:
            return db_repository.get_plan_coverage(plan_id, year)
        except Exception as e:
            if os.getenv("DB_FAILURE_FALLBACK") == "legacy":
                print(f"[FALLBACK LOG] DB Failure in get_plan_coverage: {e}. Falling back to legacy.")
                return legacy_repository.get_plan_coverage(plan_id, year)
            raise e
    elif mode == "shadow":
        legacy_res = legacy_repository.get_plan_coverage(plan_id, year)
        try:
            db_res = db_repository.get_plan_coverage(plan_id, year)
            log_shadow_comparison("get_plan_coverage", plan_id, legacy_res, db_res)
        except Exception as e:
            print(f"[SHADOW MISMATCH LOG] DB Execution error in shadow get_plan_coverage: {e}")
        return legacy_res
    else:
        return legacy_repository.get_plan_coverage(plan_id, year)

def resolve_get_rule_evidence(rule_id):
    mode = get_data_source_mode()
    if mode == "database":
        try:
            return db_repository.get_rule_evidence(rule_id)
        except Exception as e:
            if os.getenv("DB_FAILURE_FALLBACK") == "legacy":
                return legacy_repository.get_rule_evidence(rule_id)
            raise e
    elif mode == "shadow":
        legacy_res = legacy_repository.get_rule_evidence(rule_id)
        try:
            db_res = db_repository.get_rule_evidence(rule_id)
            log_shadow_comparison("get_rule_evidence", rule_id, legacy_res, db_res)
        except Exception as e:
            pass
        return legacy_res
    else:
        return legacy_repository.get_rule_evidence(rule_id)

def log_shadow_comparison(req_type, plan_id, leg_res, db_res):
    # Compare legacy vs db results
    mismatches = []
    if isinstance(leg_res, list) and isinstance(db_res, list):
        if len(leg_res) != len(db_res):
            mismatches.append(f"COUNT_MISMATCH: legacy={len(leg_res)}, db={len(db_res)}")
    elif leg_res != db_res:
        mismatches.append("VALUE_MISMATCH")

    try:
        conn = db_repository.get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO audit_results (audit_type, status, severity, result_code, details)
            VALUES ('SHADOW_COMPARISON', %s, %s, %s, %s);
        """, (
            "PASS" if not mismatches else "MISMATCH",
            "INFO" if not mismatches else "WARNING",
            req_type,
            json.dumps({"plan_id": plan_id, "mismatches": mismatches})
        ))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[SHADOW LOG ERROR]: {e}")
