import re
from pathlib import Path

print("Adding 'Verified for my plan' toggle to marketplace HTML and JS...")

# 1. Update index.html
html_path = Path('dist/marketplace/index.html')
html = html_path.read_text(encoding='utf-8')

OLD_CB_HTML = """            <label class="filter-checkbox-label">
              <input type="checkbox" id="chkZeroCost">
              <span>$0 Member Cost Only</span>
            </label>"""

NEW_CB_HTML = """            <label class="filter-checkbox-label" style="font-weight:700;color:var(--green-dark)">
              <input type="checkbox" id="chkVerifiedOnly">
              <span>✓ Verified for my plan</span>
            </label>
            <label class="filter-checkbox-label">
              <input type="checkbox" id="chkZeroCost">
              <span>$0 Member Cost Only</span>
            </label>"""

if OLD_CB_HTML in html:
    html = html.replace(OLD_CB_HTML, NEW_CB_HTML)
    html_path.write_text(html, encoding='utf-8')
    print("Successfully added chkVerifiedOnly checkbox to index.html.")

# 2. Update marketplace.js
js_path = Path('dist/marketplace/marketplace.js')
js_code = js_path.read_text(encoding='utf-8')

# Add chkVerifiedOnly state variable
if 'let chkVerifiedOnly = false;' not in js_code:
    js_code = js_code.replace('let chkZeroCostOnly = false;', 'let chkVerifiedOnly = false;\n  let chkZeroCostOnly = false;')

# Wire listener
OLD_LISTENER = "$('#chkZeroCost')?.addEventListener('change', (e) => { chkZeroCostOnly = e.target.checked; renderGrid(); });"
NEW_LISTENER = "$('#chkVerifiedOnly')?.addEventListener('change', (e) => { chkVerifiedOnly = e.target.checked; renderGrid(); });\n    $('#chkZeroCost')?.addEventListener('change', (e) => { chkZeroCostOnly = e.target.checked; renderGrid(); });"

if OLD_LISTENER in js_code:
    js_code = js_code.replace(OLD_LISTENER, NEW_LISTENER)

# Wire filtering logic inside renderGrid
OLD_FILTER_IN_GRID = "if (countLabel) {"
NEW_FILTER_IN_GRID = """if (chkVerifiedOnly) {
      displayItems = displayItems.filter(item => item.is_mapped && item.rule && item.rule.coverage_status_code !== 'NEEDS_VERIFICATION' && item.rule.coverage_status !== 'Unknown / needs verification');
    }

    if (countLabel) {"""

if OLD_FILTER_IN_GRID in js_code and 'if (chkVerifiedOnly) {' not in js_code:
    js_code = js_code.replace(OLD_FILTER_IN_GRID, NEW_FILTER_IN_GRID)

js_path.write_text(js_code, encoding='utf-8')
print("Successfully wired chkVerifiedOnly in marketplace.js.")
