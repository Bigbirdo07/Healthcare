#!/usr/bin/env python3
"""Install the official RI 2026 roster into the consumer selector layer.

The historical PLANS array remains intact for audit/referential integrity, but
all historical Rhode Island rows are quarantined from selection.  Official
roster-only plans intentionally have no coverage rules and therefore render as
Needs Verification until source adjudication is complete.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROSTER = ROOT / "PHASE25T_CODEX_RI_OFFICIAL_PLAN_ROSTER.csv"
TARGETS = [ROOT / "dist" / "marketplace" / "marketplace.js", ROOT / "dist" / "app.js"]
START = "  // --- RI OFFICIAL 2026 SELECTOR ROSTER (GENERATED) ---"
END = "  // --- END RI OFFICIAL 2026 SELECTOR ROSTER ---"


INSURERS = {
    "Blue Cross & Blue Shield of Rhode Island": ("bcbsri", "Blue Cross & Blue Shield of Rhode Island"),
    "Blue MedicareRx": ("blue_medicare_rx", "Blue MedicareRx"),
    "UnitedHealthcare": ("unitedhealthcare", "UnitedHealthcare"),
    "Neighborhood Health Plan of Rhode Island": ("neighborhood", "Neighborhood Health Plan of Rhode Island"),
    "Aetna Medicare": ("aetna_medicare", "Aetna Medicare"),
    "Wellcare": ("wellcare", "Wellcare"),
    "HealthSpring": ("healthspring", "HealthSpring"),
    "Humana": ("humana", "Humana"),
    "15287": ("bcbsri", "Blue Cross & Blue Shield of Rhode Island"),
    "77514": ("neighborhood", "Neighborhood Health Plan of Rhode Island"),
}


def build_plans() -> list[dict]:
    with ROSTER.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    plans = []
    for row in rows:
        insurer_id, insurer_name = INSURERS.get(row["issuer"], (re.sub(r"[^a-z0-9]+", "_", row["issuer"].lower()).strip("_"), row["issuer"]))
        if row["market"] == "MEDICARE":
            market_segment = "MEDICARE_PART_D" if row["plan_type"] == "PDP" else "MEDICARE_ADVANTAGE"
            insurance_category = "Medicare Part D" if row["plan_type"] == "PDP" else "Medicare Advantage"
            category_display = insurance_category
        elif row["market"] == "Individual":
            market_segment = "INDIVIDUAL_ACA"
            insurance_category = "Individual / ACA"
            category_display = "Individual Marketplace"
        else:
            market_segment = "SMALL_GROUP"
            insurance_category = "Small Group"
            category_display = "Small Group / Employer"
        plans.append({
            "id": row["official_plan_key"],
            "canonical_plan_key": row["official_plan_key"],
            "insurer_id": insurer_id,
            "insurer_name": insurer_name,
            "official_plan_name": row["official_plan_name"],
            "display_name": row["official_plan_name"],
            "plan_year": 2026,
            "state": "RI",
            "plan_type": row["plan_type"],
            "insurance_category": insurance_category,
            "category_display": category_display,
            "contract_id": row["contract_id"] or "N/A",
            "plan_id": row["pbp_id"] or "N/A",
            "segment_id": row["segment_id"] or "000",
            "market_segment": market_segment,
            "source_status": "SOURCE_CONFIRMED",
            "plan_identity_status": "OFFICIAL_2026_ROSTER_VERIFIED",
            "coverage_verification_status": "VERIFICATION_PENDING",
            "is_verified": False,
            "production_visibility": True,
            "is_test_fixture": False,
            "environment": "PRODUCTION",
            "roster_only": True,
            "benefits_under_review": True,
            "official_roster_source": row["source"],
        })
    if len(plans) != 73 or len({p["id"] for p in plans}) != 73:
        raise RuntimeError("official RI selector roster must contain 73 unique plans")
    return plans


def generated_block(plans: list[dict]) -> str:
    payload = json.dumps(plans, indent=2, ensure_ascii=False)
    return f"""{START}
  // Historical RI rows in PLANS are retained only for audit and foreign-key
  // stability. They must never be returned to a consumer selector.
  const RI_OFFICIAL_SELECTOR_PLANS = {payload};

  function getProductionSelectorPlans() {{
    return [
      ...PLANS.filter((plan) => plan.state !== 'RI'),
      ...RI_OFFICIAL_SELECTOR_PLANS
    ];
  }}

  function getMarketplacePlan(planId) {{
    return RI_OFFICIAL_SELECTOR_PLANS.find((plan) => plan.id === planId)
      || PLANS.find((plan) => plan.id === planId);
  }}

  function isBenefitsUnderReview(plan) {{
    return Boolean(plan && plan.benefits_under_review === true);
  }}
{END}"""


def transform(code: str, block: str) -> str:
    if START in code:
        code = re.sub(re.escape(START) + r".*?" + re.escape(END), block, code, flags=re.S)
    else:
        marker = "\n  // --- 2B. PLAN IDENTIFIERS & CARD MATCHING STRUCTURE ---"
        if marker not in code:
            raise RuntimeError("PLANS insertion marker not found")
        code = code.replace(marker, "\n\n" + block + marker, 1)

    # Only selection/rendering paths use the official overlay. The legacy card
    # matcher remains isolated because it has not been independently verified.
    code = code.replace("const prodPlans = PLANS.filter(p =>", "const prodPlans = getProductionSelectorPlans().filter(p =>", 1)
    code = code.replace("const plan = PLANS.find((p) => p.id === planId);", "const plan = getMarketplacePlan(planId);", 1)
    for old, new in (
        ("const planObj = PLANS.find(p => p.id === activePlanId);", "const planObj = getMarketplacePlan(activePlanId);"),
        ("if (paramPlanId && PLANS.some(p => p.id === paramPlanId)) {", "if (paramPlanId && getProductionSelectorPlans().some(p => p.id === paramPlanId)) {"),
        ("const targetPlan = PLANS.find(p => p.id === paramPlanId);", "const targetPlan = getMarketplacePlan(paramPlanId);"),
        ("const plan = PLANS.find((p) => p.id === activePlanId);", "const plan = getMarketplacePlan(activePlanId);"),
    ):
        code = code.replace(old, new)

    code = code.replace(
        "statusPill.textContent = `✓ ${activeState} Active Plan`;",
        "statusPill.textContent = isBenefitsUnderReview(planObj)\n        ? `✓ ${activeState} Official 2026 Plan · Benefits under review`\n        : `✓ ${activeState} Active Plan`;",
        1,
    )
    code = code.replace(
        '<span style="background:rgba(255,255,255,0.2);color:#fff;padding:3px 10px;border-radius:12px;font-size:11px;font-weight:700">Catalog reviewed: 100%</span>',
        '<span style="background:rgba(255,255,255,0.2);color:#fff;padding:3px 10px;border-radius:12px;font-size:11px;font-weight:700">${isBenefitsUnderReview(getMarketplacePlan(activePlanId)) ? \'Official identity verified · benefits under review\' : `Catalog reviewed: ${marketData.review_completeness_pct}%`}</span>',
        1,
    )
    code = code.replace(
        'Last reviewed: ${esc(marketData.last_reviewed)} · Active Plan Marketplace Contract',
        '${isBenefitsUnderReview(getMarketplacePlan(activePlanId)) ? \'Coverage details are not yet verified for this plan\' : `Last reviewed: ${esc(marketData.last_reviewed)} · Active Plan Marketplace Contract`}',
        1,
    )
    # D-SNP is a Medicare plan. Medicaid/CHIP remain the only Medicaid-card
    # selector categories.
    code = code.replace(
        "return cat.includes('MEDICAID') || cat.includes('CHIP') || cat.includes('D_SNP') || cat.includes('DUAL');",
        "return cat.includes('MEDICAID') || cat.includes('CHIP');",
        1,
    )
    code = code.replace(
        "(cat.includes('MEDICAID') || cat.includes('CHIP') || cat.includes('D_SNP') ? 'MEDICAID_CARD' : 'INSURANCE_CARD')",
        "(cat.includes('MEDICAID') || cat.includes('CHIP') ? 'MEDICAID_CARD' : 'INSURANCE_CARD')",
        1,
    )
    return code


def main() -> None:
    plans = build_plans()
    block = generated_block(plans)
    outputs = []
    for path in TARGETS:
        original = path.read_text(encoding="utf-8")
        updated = transform(original, block)
        path.write_text(updated, encoding="utf-8")
        outputs.append(updated)
    if outputs[0] != outputs[1]:
        raise RuntimeError("dist/app.js and marketplace.js diverged")
    print(f"Installed {len(plans)} official Rhode Island selector plans into both runtime bundles.")


if __name__ == "__main__":
    main()
