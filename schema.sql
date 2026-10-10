-- PostgreSQL Database Schema for Benefit Card Navigator (Phase 22)
-- Database: benefit_card_navigator

CREATE TABLE IF NOT EXISTS insurers (
    id SERIAL PRIMARY KEY,
    canonical_insurer_key VARCHAR UNIQUE NOT NULL,
    official_name VARCHAR NOT NULL,
    display_name VARCHAR NOT NULL,
    state_scope VARCHAR,
    website_url VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS plans (
    id SERIAL PRIMARY KEY,
    canonical_plan_key VARCHAR UNIQUE NOT NULL,
    repository_plan_id VARCHAR UNIQUE NOT NULL,
    insurer_id INTEGER REFERENCES insurers(id) ON DELETE CASCADE,
    official_plan_name VARCHAR NOT NULL,
    display_name VARCHAR NOT NULL,
    state VARCHAR NOT NULL,
    market_segment VARCHAR NOT NULL,
    coverage_type VARCHAR,
    contract_id VARCHAR,
    external_plan_id VARCHAR,
    segment_id VARCHAR,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS plan_years (
    id SERIAL PRIMARY KEY,
    plan_id INTEGER REFERENCES plans(id) ON DELETE CASCADE,
    year INTEGER NOT NULL,
    effective_date DATE,
    termination_date DATE,
    plan_identity_status VARCHAR DEFAULT 'VERIFIED_PRODUCTION',
    verification_status VARCHAR DEFAULT 'VERIFIED_EXACT',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_plan_year UNIQUE (plan_id, year)
);

CREATE TABLE IF NOT EXISTS plan_aliases (
    id SERIAL PRIMARY KEY,
    plan_id INTEGER REFERENCES plans(id) ON DELETE CASCADE,
    alias_type VARCHAR NOT NULL,
    alias_value VARCHAR NOT NULL,
    source VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    canonical_product_key VARCHAR UNIQUE NOT NULL,
    name VARCHAR NOT NULL,
    description TEXT,
    department VARCHAR,
    category VARCHAR,
    subcategory VARCHAR,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS product_variants (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
    canonical_variant_key VARCHAR UNIQUE NOT NULL,
    name VARCHAR NOT NULL,
    strength VARCHAR,
    size VARCHAR,
    form VARCHAR,
    attributes JSONB,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS services (
    id SERIAL PRIMARY KEY,
    canonical_service_key VARCHAR UNIQUE NOT NULL,
    name VARCHAR NOT NULL,
    description TEXT,
    domain VARCHAR,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS benefits (
    id SERIAL PRIMARY KEY,
    canonical_benefit_key VARCHAR UNIQUE NOT NULL,
    name VARCHAR NOT NULL,
    description TEXT,
    benefit_domain VARCHAR NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS source_documents (
    id SERIAL PRIMARY KEY,
    source_key VARCHAR NOT NULL,
    publisher VARCHAR NOT NULL,
    publisher_domain VARCHAR,
    document_title VARCHAR NOT NULL,
    source_type VARCHAR,
    source_url TEXT,
    final_url TEXT,
    plan_year INTEGER,
    effective_date DATE,
    retrieved_at TIMESTAMP,
    sha256 VARCHAR UNIQUE NOT NULL,
    local_archive_reference TEXT,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS source_plan_applicability (
    id SERIAL PRIMARY KEY,
    source_document_id INTEGER REFERENCES source_documents(id) ON DELETE CASCADE,
    plan_year_id INTEGER REFERENCES plan_years(id) ON DELETE CASCADE,
    applicability_basis VARCHAR NOT NULL,
    applicability_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS coverage_rules (
    id SERIAL PRIMARY KEY,
    legacy_rule_id VARCHAR UNIQUE NOT NULL,
    plan_year_id INTEGER REFERENCES plan_years(id) ON DELETE CASCADE,
    target_type VARCHAR NOT NULL CHECK (target_type IN ('PRODUCT', 'PRODUCT_VARIANT', 'SERVICE', 'BENEFIT')),
    product_id INTEGER REFERENCES products(id),
    product_variant_id INTEGER REFERENCES product_variants(id),
    service_id INTEGER REFERENCES services(id),
    benefit_id INTEGER REFERENCES benefits(id),
    coverage_status VARCHAR NOT NULL CHECK (coverage_status IN ('COVERED', 'CONDITIONAL', 'OTC_ELIGIBLE', 'NOT_COVERED', 'UNKNOWN')),
    coverage_pathway VARCHAR,
    member_cost_text TEXT,
    copay_amount NUMERIC(10,2),
    coinsurance_percent NUMERIC(5,2),
    allowance_amount NUMERIC(10,2),
    allowance_frequency VARCHAR,
    deductible_applies BOOLEAN,
    requires_rx BOOLEAN DEFAULT FALSE,
    requires_provider_order BOOLEAN DEFAULT FALSE,
    requires_medical_necessity BOOLEAN DEFAULT FALSE,
    requires_prior_auth BOOLEAN DEFAULT FALSE,
    requires_network_provider BOOLEAN DEFAULT FALSE,
    requires_network_pharmacy BOOLEAN DEFAULT FALSE,
    requires_network_dme_supplier BOOLEAN DEFAULT FALSE,
    diagnosis_requirement TEXT,
    age_requirement TEXT,
    quantity_limit TEXT,
    frequency_limit TEXT,
    other_requirement TEXT,
    rule_priority INTEGER DEFAULT 100,
    verification_status VARCHAR DEFAULT 'VERIFIED_EXACT',
    effective_from DATE,
    effective_to DATE,
    batch_id VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_target_identity CHECK (
        (target_type = 'PRODUCT' AND product_id IS NOT NULL) OR
        (target_type = 'PRODUCT_VARIANT' AND product_variant_id IS NOT NULL) OR
        (target_type = 'SERVICE' AND service_id IS NOT NULL) OR
        (target_type = 'BENEFIT' AND benefit_id IS NOT NULL)
    )
);

CREATE TABLE IF NOT EXISTS rule_evidence (
    id SERIAL PRIMARY KEY,
    coverage_rule_id INTEGER REFERENCES coverage_rules(id) ON DELETE CASCADE,
    source_document_id INTEGER REFERENCES source_documents(id) ON DELETE CASCADE,
    page_reference VARCHAR,
    section_reference VARCHAR,
    evidence_excerpt TEXT,
    verification_method VARCHAR DEFAULT 'INDEPENDENT_VERIFICATION',
    verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS coverage_conditions (
    id SERIAL PRIMARY KEY,
    coverage_rule_id INTEGER REFERENCES coverage_rules(id) ON DELETE CASCADE,
    condition_type VARCHAR NOT NULL,
    operator VARCHAR,
    value_text TEXT,
    value_numeric NUMERIC(10,2),
    unit VARCHAR,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS ingestion_batches (
    id SERIAL PRIMARY KEY,
    batch_key VARCHAR UNIQUE NOT NULL,
    phase VARCHAR NOT NULL,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    status VARCHAR,
    rules_before INTEGER,
    rules_added INTEGER,
    rules_rejected INTEGER,
    rules_removed INTEGER,
    rules_after INTEGER,
    census_sha256 VARCHAR,
    audit_verdict VARCHAR,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS ingestion_tasks (
    id SERIAL PRIMARY KEY,
    task_key VARCHAR UNIQUE NOT NULL,
    plan_year_id INTEGER REFERENCES plan_years(id) ON DELETE CASCADE,
    benefit_domain VARCHAR NOT NULL,
    priority VARCHAR,
    source_status VARCHAR NOT NULL,
    task_status VARCHAR NOT NULL,
    batch_id VARCHAR,
    source_document_id INTEGER REFERENCES source_documents(id),
    last_error TEXT,
    review_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS plan_domain_status (
    id SERIAL PRIMARY KEY,
    plan_year_id INTEGER REFERENCES plan_years(id) ON DELETE CASCADE,
    benefit_domain VARCHAR NOT NULL,
    status VARCHAR NOT NULL CHECK (status IN ('COMPLETE', 'PARTIAL', 'NOT_INGESTED', 'NOT_APPLICABLE', 'SOURCE_NOT_FOUND')),
    primary_source_document_id INTEGER REFERENCES source_documents(id),
    completion_reason TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_plan_year_domain UNIQUE (plan_year_id, benefit_domain)
);

CREATE TABLE IF NOT EXISTS plan_readiness (
    id SERIAL PRIMARY KEY,
    plan_year_id INTEGER UNIQUE REFERENCES plan_years(id) ON DELETE CASCADE,
    classification VARCHAR NOT NULL CHECK (classification IN ('NOT_YET_INGESTED', 'MINIMALLY_EVIDENCE_MAPPED', 'PARTIALLY_EVIDENCE_MAPPED', 'FULLY_EVIDENCE_MAPPED')),
    verified_rule_count INTEGER DEFAULT 0,
    domains_complete INTEGER DEFAULT 0,
    domains_partial INTEGER DEFAULT 0,
    domains_not_ingested INTEGER DEFAULT 0,
    domains_not_applicable INTEGER DEFAULT 0,
    last_calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS rule_history (
    id SERIAL PRIMARY KEY,
    coverage_rule_id INTEGER REFERENCES coverage_rules(id) ON DELETE CASCADE,
    event_type VARCHAR NOT NULL,
    previous_value JSONB,
    new_value JSONB,
    batch_id VARCHAR,
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_results (
    id SERIAL PRIMARY KEY,
    audit_type VARCHAR NOT NULL,
    batch_id VARCHAR,
    plan_year_id INTEGER REFERENCES plan_years(id),
    coverage_rule_id INTEGER REFERENCES coverage_rules(id),
    status VARCHAR NOT NULL,
    severity VARCHAR,
    result_code VARCHAR,
    details JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- INDEXES
CREATE INDEX IF NOT EXISTS idx_plans_state ON plans(state);
CREATE INDEX IF NOT EXISTS idx_plans_insurer ON plans(insurer_id);
CREATE INDEX IF NOT EXISTS idx_plans_segment ON plans(market_segment);
CREATE INDEX IF NOT EXISTS idx_plan_years_plan_year ON plan_years(plan_id, year);
CREATE INDEX IF NOT EXISTS idx_coverage_rules_plan_year ON coverage_rules(plan_year_id);
CREATE INDEX IF NOT EXISTS idx_coverage_rules_target ON coverage_rules(target_type, product_id, service_id, benefit_id);
CREATE INDEX IF NOT EXISTS idx_coverage_rules_status ON coverage_rules(coverage_status);
CREATE INDEX IF NOT EXISTS idx_source_documents_sha256 ON source_documents(sha256);
CREATE INDEX IF NOT EXISTS idx_ingestion_tasks_status ON ingestion_tasks(source_status, task_status);
CREATE INDEX IF NOT EXISTS idx_plan_domain_status_plan ON plan_domain_status(plan_year_id);
CREATE INDEX IF NOT EXISTS idx_rule_evidence_rule ON rule_evidence(coverage_rule_id);

-- VIEWS
CREATE OR REPLACE VIEW v_plan_coverage_rules AS
SELECT 
    cr.id AS database_rule_id,
    cr.legacy_rule_id,
    p.canonical_plan_key,
    p.repository_plan_id,
    p.official_plan_name,
    p.state,
    p.market_segment,
    py.year AS plan_year,
    cr.target_type,
    cr.coverage_status,
    cr.coverage_pathway,
    cr.member_cost_text,
    cr.copay_amount,
    cr.coinsurance_percent,
    cr.allowance_amount,
    cr.allowance_frequency,
    cr.requires_rx,
    cr.requires_prior_auth,
    cr.requires_network_provider,
    cr.rule_priority,
    cr.verification_status,
    prod.canonical_product_key,
    prod.name AS product_name,
    svc.canonical_service_key,
    svc.name AS service_name,
    ben.canonical_benefit_key,
    ben.name AS benefit_name,
    sd.source_key,
    sd.publisher,
    sd.document_title,
    sd.sha256 AS source_document_sha256,
    re.page_reference,
    re.section_reference,
    re.evidence_excerpt
FROM coverage_rules cr
JOIN plan_years py ON cr.plan_year_id = py.id
JOIN plans p ON py.plan_id = p.id
LEFT JOIN products prod ON cr.product_id = prod.id
LEFT JOIN services svc ON cr.service_id = svc.id
LEFT JOIN benefits ben ON cr.benefit_id = ben.id
LEFT JOIN rule_evidence re ON re.coverage_rule_id = cr.id
LEFT JOIN source_documents sd ON re.source_document_id = sd.id;

CREATE OR REPLACE VIEW v_plan_readiness AS
SELECT 
    p.canonical_plan_key,
    p.repository_plan_id,
    p.official_plan_name,
    p.state,
    p.market_segment,
    py.year AS plan_year,
    pr.classification,
    pr.verified_rule_count,
    pr.domains_complete,
    pr.domains_partial,
    pr.domains_not_ingested,
    pr.domains_not_applicable,
    pr.last_calculated_at
FROM plan_readiness pr
JOIN plan_years py ON pr.plan_year_id = py.id
JOIN plans p ON py.plan_id = p.id;
