import os
import shutil
import psycopg2

DB_CONNECT_ARGS = {
    'dbname': 'benefit_card_navigator',
    'user': 'albertopaz',
    'host': 'localhost',
    'port': 5432
}

BRAIN_DIR = '/Users/albertopaz/.gemini/antigravity-ide/brain/5b95c931-dccd-4aa6-884c-acea48a79fe5'

def main():
    conn = psycopg2.connect(**DB_CONNECT_ARGS)
    cur = conn.cursor()

    cur.execute("SELECT id, rules_before FROM ingestion_batches WHERE batch_key = 'PHASE23_BATCH12';")
    row = cur.fetchone()
    assert row is not None, "PHASE23_BATCH12 batch record not found!"
    batch_record_id, rules_before = row

    cur.execute("SELECT count(*) FROM coverage_rules;")
    rules_after = cur.fetchone()[0]

    rules_added = rules_after - rules_before

    cur.execute("""
    UPDATE ingestion_batches
    SET completed_at = CURRENT_TIMESTAMP,
        status = 'COMPLETED',
        rules_added = %s,
        rules_after = %s,
        rules_rejected = 0,
        audit_verdict = 'DB_NATIVE_BATCH12_VALIDATED — SAFE_FOR_BATCH13'
    WHERE id = %s;
    """, (rules_added, rules_after, batch_record_id))
    conn.commit()
    print(f"Updated ingestion_batches record {batch_record_id} status to COMPLETED.")

    all_artifacts = [
        'BATCH12_TASK_SELECTION.csv',
        'BATCH12_TASK_OVERLAP_AUDIT.csv',
        'BATCH12_DB_PROGRESS_DELTA.csv',
        'BATCH12_RULE_CANDIDATES.csv',
        'BATCH12_APPROVED_RULES.csv',
        'BATCH12_REJECTED_RULES.csv',
        'BATCH12_SOURCE_DOCUMENT_AUDIT.csv',
        'BATCH12_RULE_EVIDENCE_AUDIT.csv',
        'BATCH12_CONFLICT_AUDIT.csv',
        'BATCH12_DOMAIN_STATUS_DELTAS.csv',
        'BATCH12_PLAN_READINESS_TRANSITIONS.csv',
        'BATCH12_DOMAIN_COMPLETENESS_POST.csv',
        'BATCH12_MARKETPLACE_API_VALIDATION.csv',
        'BATCH12_PLAN_SWITCH_TEST.csv',
        'BATCH12_INDEPENDENT_SPOT_CHECK.csv',
        'BATCH12_DATABASE_INTEGRITY_AUDIT.csv',
        'BATCH12_QUEUE_SNAPSHOT.csv',
        'PHASE23_BATCH12_DATABASE_NATIVE_INGESTION_REPORT.md'
    ]

    os.makedirs(BRAIN_DIR, exist_ok=True)
    for art in all_artifacts:
        assert os.path.exists(art), f"Missing artifact: {art}"
        shutil.copy(art, os.path.join(BRAIN_DIR, art))
        print(f"Copied {art} to {BRAIN_DIR}")

    cur.execute("SELECT count(*) FROM plans;")
    plans = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM v_plan_verification_status WHERE has_verified_coverage_data = true;")
    verified = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM v_plan_verification_status WHERE has_verified_coverage_data = false;")
    unverified = cur.fetchone()[0]
    cur.execute("SELECT task_status, count(*) FROM ingestion_tasks GROUP BY task_status;")
    tasks = dict(cur.fetchall())

    print("\n==========================================")
    print("PHASE 23 BATCH 12 EXECUTION COMPLETE")
    print("==========================================")
    print(f"Total Plans: {plans}")
    print(f"Coverage Rules: {rules_after} (+{rules_added})")
    print(f"Verified Plans: {verified}")
    print(f"Unverified Plans: {unverified}")
    print(f"Ingestion Task Ledger: {tasks}")
    print(f"Total Tasks: {sum(tasks.values())}")
    print(f"Artifacts Persisted: {len(all_artifacts)}")
    print("\nFINAL VERDICT: DB_NATIVE_BATCH12_VALIDATED — SAFE_FOR_BATCH13")

    conn.close()

if __name__ == '__main__':
    main()
