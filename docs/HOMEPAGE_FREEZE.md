# Frozen homepage boundary and provider-system direction

Effective: September 24, 2026

Authoritative source archive:

`/Users/albertopaz/Downloads/Benefit-Card-Navigator-source/Benefit-Card-Navigator-source (1).zip`

The archive above is the recovery copy for the original website. It must remain unchanged.

The existing Benefit Card Navigator homepage is frozen. Provider-directory, practice-portal, inquiry-routing, and owner-analytics work must not change its layout, benefit-selection flow, marketplace cards, comparison flow, source table, footer, or visual system.

No provider-directory navigation, wording, data, styling, Care List, or inquiry interface is included in the homepage. The preserved provider prototype lives separately under `/find-care/` but is intentionally unlinked while its final multi-window navigation is being decided.

Frozen build fingerprints:

```text
ea529515f914683abc9bdbb7e6958d9226d00a122d796a04d1d185ecf9de0834  dist/index.html
41a2b66dead00a3a2edece5bfacd13369a50f1b31e36494745477abf22eba790  dist/app.js
07b3846a48b6d7cc7b523c7843bbca3466a677521145248b40f190412babd272  dist/styles.css
cd454858723855bc10d139adf48495448047cd0a0f2fbb877cb84373d68fe758  dist/data.json
5cde3e830b4aabe9129cd0e0bd2272803d3d0f5f2c72c3a8b338336b57240bc1  Benefit-Card-Navigator-source (1).zip
```

*Note on dist/index.html:* On September 24, 2026, the user explicitly authorized updating `dist/index.html` to add topbar navigation (`Find a Doctor`, `Find a Dentist`, `Find a Eye doctor`, `Marketplace`, `About the data & sources`) linking the homepage to the separate provider marketplace routes, matching the user's approved visual design. Original pre-navigation fingerprint: `969484506d008572ea7e338855955d2fde205fd43bb9051cb537ee86ab73be16`. `dist/app.js`, `dist/styles.css`, `dist/data.json`, and the recovery zip remain strictly frozen and identical.

## Intended provider system

The provider product must be built as a separate routed section, comparable to a standalone URL such as `pazatlas.org/protein-folder`. It must not be inserted into the homepage content.

The separate provider section will provide three care modes: Find a Doctor, Find a Dentist, and Find an Eye Doctor. It will search the available New England clinician and practice-location records and support evidence-based filters such as location, specialty, Medicare information, Medicaid enrollment status, and eventually verified languages. Names must never be used to infer which languages a clinician speaks. Plan participation, language, active licensure, new-patient availability, and other claims must be labeled according to the strength and date of the underlying source.

The intended user flow is:

1. The user enters or selects insurance-card information.
2. The user searches providers and adds requested care or services to a cart-like inquiry list.
3. Checkout shows a summary and lets the user select a doctor or primary-care physician.
4. The inquiry is securely routed to the selected practice's separate portal.
5. Authorized practice staff see the minimum information needed to respond: patient name, date of birth, approved phone number, requested care, selected provider, and inquiry date.
6. Practice staff call the patient and update the inquiry status: dark red means call needed; yellow means called with no answer; green means the patient was reached and the order/request was handled; blue means an in-person appointment resulted from the inquiry.
7. A yellow status can trigger an approved text message or voicemail asking whether the patient wants to submit the request again. Ending an inquiry does not delete the practice's permitted clinical notes.
8. The owner receives a separate operational pipeline with dates and daily status totals. This reporting layer is not visible to patients or practices and should contain aggregate or de-identified information rather than patient-identifying or clinical information.

The practice portal is intended to be private and practice-controlled. Persistent clinical notes and patient bins remain in the practice's local environment, can support several thousand patients, and may accept records exported from another practice system. Any production implementation involving protected health information, messaging, local downloads, retention, or third-party reporting must use appropriate access controls, encryption, audit logs, backups, retention policies, and HIPAA-compliant vendors and agreements.
