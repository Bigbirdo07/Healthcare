import os
import re

JS_MARKETPLACE_PATH = "/Users/albertopaz/Downloads/Benefit-Card-Navigator-source/dist/marketplace/marketplace.js"
JS_APP_PATH = "/Users/albertopaz/Downloads/Benefit-Card-Navigator-source/dist/app.js"

def apply_ri_default_plan_fix():
    print("=== APPLYING RHODE ISLAND ACTIVE PLAN AUTO-SELECTION FIX ===")

    for js_path in [JS_MARKETPLACE_PATH, JS_APP_PATH]:
        if not os.path.exists(js_path):
            continue

        with open(js_path, "r", encoding="utf-8") as f:
            code = f.read()

        # 1. Update onStateChange to auto-select default verified plan for RI
        code = re.sub(
            r"function onStateChange\(newState\)\s*\{\s*activeState = newState;\s*selectedInsurerId = '';\s*activePlanId = null;",
            """function onStateChange(newState) {
    activeState = newState;
    selectedInsurerId = (newState === 'RI') ? 'bcbsri' : '';
    activePlanId = (newState === 'RI') ? 'CMS:RI:H4152:004:000:2026' : null;""",
            code
        )

        # 2. Update onCardTypeChange
        code = re.sub(
            r"function onCardTypeChange\(newCardType\)\s*\{\s*activeCardType = newCardType;",
            """function onCardTypeChange(newCardType) {
    activeCardType = newCardType;
    if (activeState === 'RI' && !activePlanId) {
      selectedInsurerId = 'bcbsri';
      activePlanId = 'CMS:RI:H4152:004:000:2026';
    }""",
            code
        )

        # 3. Update onInsurerChange
        code = re.sub(
            r"function onInsurerChange\(newInsurerId\)\s*\{\s*selectedInsurerId = newInsurerId;",
            """function onInsurerChange(newInsurerId) {
    selectedInsurerId = newInsurerId;
    if (!activePlanId || activePlanId === 'generic_unselected_plan') {
      activePlanId = (activeState === 'RI') ? 'CMS:RI:H4152:004:000:2026' : 'CMS:RI:H4152:004:000:2026';
    }""",
            code
        )

        # 4. In renderGrid, if activePlanId is null and activeState is RI, fallback to CMS:RI:H4152:004:000:2026
        code = code.replace(
            "// Handle Unselected Plan State (activePlanId === null)\n    if (!activePlanId) {",
            "if (!activePlanId && activeState === 'RI') { activePlanId = 'CMS:RI:H4152:004:000:2026'; selectedInsurerId = 'bcbsri'; }\n    // Handle Unselected Plan State (activePlanId === null)\n    if (!activePlanId) {"
        )

        with open(js_path, "w", encoding="utf-8") as f:
            f.write(code)

        print(f"Successfully applied default RI active plan fix to {os.path.basename(js_path)}!")

if __name__ == "__main__":
    apply_ri_default_plan_fix()
