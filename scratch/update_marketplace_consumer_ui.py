import re

# 1. UPDATE index.html
with open('dist/marketplace/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Remove topbar checkout button
html = re.sub(r'<button type="button" id="navCheckoutBtn".*?</button>', '', html, flags=re.DOTALL)

# Remove hero checkout button
html = re.sub(r'<button type="button" class="hero-form-btn" id="heroCheckoutBtn">.*?</button>', '', html, flags=re.DOTALL)

# Update radio status filter list in sidebar to include Not Covered
old_status_filter = r'<div class="filter-checkbox-list">\s*<label class="filter-checkbox-label">\s*<input type="radio" name="sideStatus" value="all" checked>.*?</div>'
new_status_filter = """<div class="filter-checkbox-list">
            <label class="filter-checkbox-label">
              <input type="radio" name="sideStatus" value="all" checked>
              <span>All Statuses</span>
            </label>
            <label class="filter-checkbox-label">
              <input type="radio" name="sideStatus" value="Covered">
              <span style="color:#0d6b63;font-weight:700">✓ Covered</span>
            </label>
            <label class="filter-checkbox-label">
              <input type="radio" name="sideStatus" value="Conditional">
              <span style="color:#8a5d00;font-weight:700">⚡ Conditional</span>
            </label>
            <label class="filter-checkbox-label">
              <input type="radio" name="sideStatus" value="Needs Verification">
              <span style="color:#2b5797;font-weight:700">❓ Needs Verification</span>
            </label>
            <label class="filter-checkbox-label">
              <input type="radio" name="sideStatus" value="Not Covered">
              <span style="color:#b91c1c;font-weight:700">✕ Not Covered</span>
            </label>
          </div>"""

html = re.sub(r'<div class="filter-checkbox-list">\s*<label class="filter-checkbox-label">\s*<input type="radio" name="sideStatus".*?</div>\s*</div>', f'{new_status_filter}\n        </div>', html, flags=re.DOTALL)

with open('dist/marketplace/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated dist/marketplace/index.html cleanly.")
