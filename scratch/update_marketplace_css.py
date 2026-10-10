import re

print("Updating Marketplace CSS for full-width grid, state-first controls, and checkout review modal...")

css_additions = """
/* Full Width & High Density Layout Extensions */
.marketplace-page .market-shell {
  max-width: 1560px;
  margin: 0 auto;
  padding: 0 24px;
}

.plan-selector-grid {
  display: grid;
  grid-template-columns: 180px 240px 1fr auto;
  gap: 16px;
  align-items: center;
  background: #fff;
  border-radius: 8px;
  padding: 14px 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  border: 1px solid var(--line);
}

.filter-select-group.highlight-group label {
  color: var(--green-dark);
  font-size: 13px;
  margin-bottom: 4px;
  display: block;
}

.filter-select-group.highlight-group select {
  width: 100%;
  padding: 8px 12px;
  font-size: 14px;
  border: 1.5px solid var(--green-light);
  border-radius: 6px;
  background: #fff;
  color: var(--text-main);
  font-weight: 600;
}

.topbar-checkout-btn, .checkout-review-btn {
  background: var(--amazon-yellow);
  border: 1.5px solid #d0b000;
  color: #111;
  font-size: 14px;
  font-weight: 700;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.15s ease;
}

.topbar-checkout-btn:hover, .checkout-review-btn:hover {
  background: var(--amazon-yellow-hover);
  transform: translateY(-1px);
}

.cart-badge-count {
  background: var(--terracotta);
  color: #fff;
  border-radius: 12px;
  padding: 2px 8px;
  font-size: 12px;
}

/* Modal Overlay & Modal Window */
.checkout-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(10, 30, 24, 0.75);
  backdrop-filter: blur(4px);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.checkout-modal-content {
  background: #fff;
  border-radius: 12px;
  max-width: 1100px;
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 12px 36px rgba(0,0,0,0.3);
  overflow: hidden;
}

.checkout-modal-header {
  background: var(--green-dark);
  color: #fff;
  padding: 18px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.checkout-modal-header h2 {
  margin: 0;
  font-size: 20px;
  font-family: Georgia, serif;
}

.close-modal-btn {
  background: none;
  border: none;
  color: #fff;
  font-size: 28px;
  cursor: pointer;
}

.checkout-modal-body {
  padding: 24px;
  overflow-y: auto;
}

.checkout-grid {
  display: grid;
  grid-template-columns: 1fr 1.2fr;
  gap: 28px;
}

.checkout-items-section {
  background: var(--cream);
  padding: 18px;
  border-radius: 8px;
  border: 1px solid var(--line);
}

.checkout-items-section h3, .checkout-form-section h3 {
  margin-top: 0;
  font-size: 16px;
  color: var(--green-dark);
  border-bottom: 2px solid var(--green-light);
  padding-bottom: 8px;
}

.checkout-plan-summary {
  background: var(--green-tint);
  border: 1px solid var(--green-light);
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 16px;
  font-size: 13px;
  color: var(--green-dark);
}

.form-section-title {
  font-weight: 700;
  font-size: 14px;
  color: var(--green-dark);
  margin: 14px 0 8px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 10px;
}

.form-field label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  margin-bottom: 4px;
}

.form-field input, .form-field select {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid var(--line);
  border-radius: 6px;
  font-size: 13px;
  box-sizing: border-box;
}

.checkout-disclaimers {
  margin: 16px 0;
  display: grid;
  gap: 8px;
}

.consent-checkbox {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 12px;
  line-height: 1.4;
  color: var(--text-muted);
}

.submit-request-btn {
  width: 100%;
  background: var(--green-dark);
  color: #fff;
  padding: 12px;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 700;
  border: none;
  cursor: pointer;
  transition: background 0.15s ease;
}

.submit-request-btn:hover {
  background: var(--green-medium);
}
"""

with open('dist/marketplace/marketplace.css', 'a', encoding='utf-8') as f:
    f.write(css_additions)

print("Updated dist/marketplace/marketplace.css successfully!")
