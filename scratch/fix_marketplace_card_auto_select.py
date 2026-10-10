import os
import re

JS_MARKETPLACE_PATH = "/Users/albertopaz/Downloads/Benefit-Card-Navigator-source/dist/marketplace/marketplace.js"
JS_APP_PATH = "/Users/albertopaz/Downloads/Benefit-Card-Navigator-source/dist/app.js"

def apply_auto_select_fix():
    print("=== APPLYING AUTO-SELECT CARD FIX & VANTAGE BLUE SUPPORT ===")

    for js_path in [JS_MARKETPLACE_PATH, JS_APP_PATH]:
        if not os.path.exists(js_path):
            continue

        with open(js_path, "r", encoding="utf-8") as f:
            code = f.read()

        # 1. Update onInsurerChange to auto-select the first plan if available
        old_on_insurer = """  function onInsurerChange(newInsurerId) {
    selectedInsurerId = newInsurerId;
    activePlanId = null;

    renderMarketplaceDropdowns();
    updatePlanStatusBadge();
    renderGrid();
  }"""

        new_on_insurer = """  function onInsurerChange(newInsurerId) {
    selectedInsurerId = newInsurerId;
    const res = window.getInsuranceSelectorOptions({
      state: activeState,
      cardType: activeCardType,
      insurerId: selectedInsurerId
    });
    if (res.plans && res.plans.length > 0) {
      activePlanId = res.plans[0].id;
    } else {
      activePlanId = null;
    }

    renderMarketplaceDropdowns();
    updatePlanStatusBadge();
    renderGrid();
  }"""

        if old_on_insurer in code:
            code = code.replace(old_on_insurer, new_on_insurer)
            print(f"Updated onInsurerChange in {os.path.basename(js_path)}")
        else:
            # Regex replacement fallback
            code = re.sub(
                r"function onInsurerChange\(newInsurerId\)\s*\{\s*selectedInsurerId = newInsurerId;\s*activePlanId = null;",
                """function onInsurerChange(newInsurerId) {
    selectedInsurerId = newInsurerId;
    const res = window.getInsuranceSelectorOptions({ state: activeState, cardType: activeCardType, insurerId: selectedInsurerId });
    activePlanId = (res.plans && res.plans.length > 0) ? res.plans[0].id : null;""",
                code
            )
            print(f"Applied regex onInsurerChange fix in {os.path.basename(js_path)}")

        # 2. Also ensure onCardTypeChange auto-selects insurer & plan if available
        old_on_cardtype = """  function onCardTypeChange(newCardType) {
    activeCardType = newCardType;
    selectedInsurerId = '';
    activePlanId = null;

    renderMarketplaceDropdowns();
    updatePlanStatusBadge();
    renderGrid();
  }"""

        new_on_cardtype = """  function onCardTypeChange(newCardType) {
    activeCardType = newCardType;
    const res = window.getInsuranceSelectorOptions({
      state: activeState,
      cardType: activeCardType,
      insurerId: ''
    });
    if (res.insurers && res.insurers.length > 0) {
      selectedInsurerId = res.insurers[0].id;
      const planRes = window.getInsuranceSelectorOptions({
        state: activeState,
        cardType: activeCardType,
        insurerId: selectedInsurerId
      });
      activePlanId = (planRes.plans && planRes.plans.length > 0) ? planRes.plans[0].id : null;
    } else {
      selectedInsurerId = '';
      activePlanId = null;
    }

    renderMarketplaceDropdowns();
    updatePlanStatusBadge();
    renderGrid();
  }"""

        if old_on_cardtype in code:
            code = code.replace(old_on_cardtype, new_on_cardtype)
            print(f"Updated onCardTypeChange in {os.path.basename(js_path)}")

        # 3. Add Vantage Blue plan aliases so Vantage Blue is explicitly matched in RI_OFFICIAL_SELECTOR_PLANS and COVERAGE_RULES
        code = code.replace(
            '"official_plan_name": "Blue Cross Dental Direct",',
            '"official_plan_name": "Vantage Blue / Blue Cross Dental Direct",'
        )

        with open(js_path, "w", encoding="utf-8") as f:
            f.write(code)

    print("=== AUTO-SELECT FIX SUCCESSFULLY APPLIED TO MARKETPLACE JS BUNDLES ===")

if __name__ == "__main__":
    apply_auto_select_fix()
