import os

JS_MARKETPLACE_PATH = "/Users/albertopaz/Downloads/Benefit-Card-Navigator-source/dist/marketplace/marketplace.js"
JS_APP_PATH = "/Users/albertopaz/Downloads/Benefit-Card-Navigator-source/dist/app.js"

def apply_final_guard_fix():
    print("=== APPLYING FINAL GETMARKETPLACEFORPLAN GUARD FIX ===")

    for js_path in [JS_MARKETPLACE_PATH, JS_APP_PATH]:
        if not os.path.exists(js_path):
            continue

        with open(js_path, "r", encoding="utf-8") as f:
            code = f.read()

        # Remove || !selectedInsurerId from getMarketplaceForPlan guard check
        code = code.replace(
            "if (targetPlanId === 'generic_unselected_plan' || !selectedInsurerId)",
            "if (targetPlanId === 'generic_unselected_plan')"
        )

        with open(js_path, "w", encoding="utf-8") as f:
            f.write(code)

        print(f"Successfully applied getMarketplaceForPlan guard fix to {os.path.basename(js_path)}!")

if __name__ == "__main__":
    apply_final_guard_fix()
