# Benefit Card Navigator — provider system implementation prompt

You are working inside this exact project:

`/Users/albertopaz/Downloads/Benefit-Card-Navigator-source`

## Primary goal

Expand Benefit Card Navigator with a separate, route-based provider marketplace and inquiry workflow while preserving the existing homepage exactly as it is. The result should feel like multiple sections/windows of one website—for example, a main site at `/` and a separate product at `/find-care/`—rather than adding the provider directory to the homepage.

The long-term product flow is:

```text
Benefit marketplace
→ separate provider marketplace
→ Find a Doctor / Find a Dentist / Find an Eye Doctor
→ select insurance and apply source-backed filters
→ select a provider and add care requests to a Care List
→ review the inquiry summary
→ securely send the inquiry to the selected practice
→ practice staff call the patient
→ staff record outreach and appointment outcomes
→ a minimal, pseudonymous status event reaches an owner-only dashboard
```

## Absolute homepage freeze

Do not modify, reformat, regenerate, rename, or add provider content to any of these files:

- `/Users/albertopaz/Downloads/Benefit-Card-Navigator-source/dist/index.html`
- `/Users/albertopaz/Downloads/Benefit-Card-Navigator-source/dist/app.js`
- `/Users/albertopaz/Downloads/Benefit-Card-Navigator-source/dist/styles.css`
- `/Users/albertopaz/Downloads/Benefit-Card-Navigator-source/dist/data.json`

These files are deliberately read-only. Do not change their permissions. The authoritative recovery archive is:

`/Users/albertopaz/Downloads/Benefit-Card-Navigator-source/Benefit-Card-Navigator-source (1).zip`

Do not extract over, modify, rename, or delete that archive. The homepage freeze rules and fingerprints are recorded at:

`/Users/albertopaz/Downloads/Benefit-Card-Navigator-source/docs/HOMEPAGE_FREEZE.md`

Before and after implementation, verify these SHA-256 fingerprints:

```text
969484506d008572ea7e338855955d2fde205fd43bb9051cb537ee86ab73be16  dist/index.html
41a2b66dead00a3a2edece5bfacd13369a50f1b31e36494745477abf22eba790  dist/app.js
07b3846a48b6d7cc7b523c7843bbca3466a677521145248b40f190412babd272  dist/styles.css
cd454858723855bc10d139adf48495448047cd0a0f2fbb877cb84373d68fe758  dist/data.json
5cde3e830b4aabe9129cd0e0bd2272803d3d0f5f2c72c3a8b338336b57240bc1  Benefit-Card-Navigator-source (1).zip
```

If a requested change appears to require touching a frozen file, stop and ask for explicit approval. Do not work around the freeze.

## Hosting and routing context

The hosting configuration is:

`/Users/albertopaz/Downloads/Benefit-Card-Navigator-source/.openai/hosting.json`

It publishes the `dist` directory as a static website. New public pages must therefore exist under `dist` and work when opened directly by URL—not only after navigating from another page.

Use this intended route architecture:

```text
/                              frozen original homepage
/find-care/                    provider marketplace landing/search
/find-care/doctors/            doctor results and filters
/find-care/dentists/           dentist results and filters
/find-care/eye-doctors/        eye-care results and filters
/practice/                     future private authenticated practice application
/operations/                   future private owner-only reporting application
```

Do not place provider search, provider marketing copy, a Care List, or provider navigation inside the frozen homepage. The provider section may have its own navigation and a link back to `/`.

## Existing provider work to preserve and refine

Do not delete the existing provider code or research. Inspect it before implementing:

```text
dist/find-care/index.html
dist/doctor/index.html
dist/dentist/index.html
dist/eye-doctor/index.html
dist/provider-page.js
dist/provider-directory.css
dist/practice.html
dist/practice.js
dist/operations.html
dist/portal.css
```

Existing provider datasets:

```text
dist/providers.json
dist/providers/ct.json
dist/providers/ma.json
dist/providers/me.json
dist/providers/nh.json
dist/providers/vt.json
ri_doctor_medicaid_status.csv
data/ri_doctor_medicaid_status.csv
newengland_provider_medicaid_status.csv
medicaid_latest_by_npi.csv
photo_pilot_matched.csv
source_manifest.json
```

Existing import/research code and documentation:

```text
import_provider_research.py
import_new_england_providers.py
docs/provider-directory-and-care-request-roadmap.md
docs/rhode-island-provider-data-research-prompt.md
```

Preserve this work. Refactor or extend only the non-frozen provider files when needed.

## Provider marketplace requirements

Create three clear choices within the separate provider product:

1. Find a Doctor
2. Find a Dentist
3. Find an Eye Doctor

Each directory should support the fields that actually exist in the data, including:

- State
- Provider name
- Credentials
- Provider category and specialty/taxonomy
- Practice or facility name when available
- Public practice address
- Public practice phone when available
- Medicare Care Compare inclusion
- Medicare assignment information when available
- Historical Medicaid enrollment status and effective/source date
- Exact source and last-checked date

Add filters only when the underlying records support them. Desired filters include location, specialty, Medicare, Medicaid, exact insurance network, accepting new patients, clinician language, staff language, interpreter availability, telehealth, and accessibility. Unsupported filters must be disabled or labeled “data pending”; never fabricate a value.

Insurance wording must distinguish among:

- Medicare enrollment or Care Compare inclusion
- Acceptance of Medicare assignment
- Medicaid enrollment
- Membership in a specific managed-care or commercial-plan network
- Acceptance of new patients
- Practice-confirmed participation and its confirmation date

Historical Medicaid enrollment data through December 31, 2024 does not prove current 2026 participation, plan-network participation, or new-patient availability. Display that limitation plainly and tell users to confirm with the practice and health plan.

Never infer language from a person's surname, name, photograph, ethnicity, or perceived background. Language filters may use only provider-attested, practice-confirmed, insurer-directory, or documented interpreter-service information. Keep clinician language, office-staff language, and interpreter availability separate and show the source/date.

## Patient Care List and inquiry flow

Use “Care List” and “care request” or “appointment request,” not “shopping cart,” “order,” or “claim,” unless the action truly is an insurance claim. A submitted inquiry is not a guaranteed appointment, medical order, authorization, coverage decision, or official PCP designation.

The intended flow is:

1. The patient selects or enters relevant insurance-card information.
2. The patient searches providers and selects a practice/provider.
3. The patient adds desired care/services to a Care List.
4. A review screen summarizes the provider, practice, requested services, contact preference, and applicable disclaimers.
5. The patient may choose “Request this doctor as my PCP,” but the interface must explain that the practice and insurer must confirm it.
6. After explicit consent, the inquiry is securely routed only to the selected practice.
7. The patient receives a reference number and a clear explanation of what happens next.

Until a real practice is verified and connected to a compliant backend, submission controls must remain disabled or run only with clearly labeled synthetic demonstration data.

## Practice portal requirements

The practice portal is a separate authenticated product, not a public page or ordinary tab. Authorized practice staff should see only the inquiries routed to their practice. Each delivered inquiry may include the minimum necessary information:

- Patient name
- Date of birth
- Approved phone number
- Selected provider/practice
- Requested care/service
- Inquiry submission date and reference number

The status workflow must preserve history and use text/icons as well as color:

- Dark red: New — call needed
- Yellow: Outreach attempted — no answer
- Green: Patient reached / request handled
- Blue: Appointment made because of the inquiry

Do not overwrite earlier events. Maintain an append-only status history with actor and timestamp. “Reached,” “request/order handled,” and “appointment made” are distinct events even if the visual summary uses the four colors.

When an authorized user marks an inquiry yellow, a future messaging integration may send an approved text or voicemail asking whether the patient wants to resubmit. This requires prior consent, approved templates, opt-out handling, delivery logs, and a compliant vendor. Do not activate real messaging during a static prototype.

Clinical notes, imported records, detailed contact logs, and patient bins remain in the practice-controlled local environment. The design must scale to several thousand patients. A browser download is not sufficient for production; use an encrypted local database or local service with authenticated access, verified writes, backups, recovery, and an audit log.

## Routing and retention boundary

The long-term system is a straight-line delivery pipeline, not a centrally hosted medical-record repository:

```text
Patient inquiry
→ short-lived encrypted delivery queue
→ authenticated practice connector
→ verified write to the practice's local system
→ delivery acknowledgement
→ central payload deletion under a documented retention rule
```

The routing service needs delivery acknowledgement, retries, failure handling, expiration, and an audit trail. It may temporarily hold the minimum encrypted information necessary for reliable delivery. Do not promise that information is never stored; describe the short-lived routing copy accurately.

## Owner-only operations reporting

The owner needs daily operational visibility without access to patient identity or clinical notes. The private reporting pipeline may contain:

```text
event_id
anonymous_inquiry_id
practice_id
provider_category
service_category
submitted_date
previous_status
new_status
event_timestamp
appointment_made
```

It must not contain patient names, phone numbers, dates of birth, medical notes, free text, exact appointment details, or identifiers derived from those fields. Google Sheets may be used only for a non-PHI prototype with pseudonymous events. A protected database with authentication, role-based access, validation, and audit logging is preferred for production.

The owner dashboard should eventually show daily red/yellow/green/blue counts, response time, resolution time, and appointment-conversion rates by practice and date. Patients and practices must not see this owner-only dashboard.

## Security and compliance constraints

The current site is static and is not sufficient for handling real patient data. Do not place patient information in URLs, static JSON, source control, browser local storage, analytics, console logs, or mock datasets. Do not accept real patient information until there is an approved backend and architecture covering authentication, authorization, encryption in transit and at rest, minimum-necessary access, audit logging, backup/recovery, retention/deletion, incident response, consent, vendor agreements, and HIPAA/legal review.

Use synthetic data for prototypes. Do not claim HIPAA compliance merely because data is stored locally.

## Implementation order

1. Verify and preserve the homepage fingerprints.
2. Audit the existing provider pages, scripts, styles, and datasets.
3. Normalize the separate route structure under `/find-care/` without touching `/`.
4. Build/refine the public read-only New England provider search using only source-supported claims.
5. Add the Care List and inquiry-review interface with submission disabled unless using synthetic demo data or a verified connected practice.
6. Build a synthetic-data practice-portal prototype as a separate application surface.
7. Build a synthetic/pseudonymous owner-operations prototype.
8. Design and review the compliant backend, delivery connector, authentication, messaging, retention, and auditing before enabling real inquiries.
9. Re-run homepage hashes and route-level tests.

## Acceptance criteria

- The four frozen homepage files and recovery ZIP retain their exact hashes.
- Opening `/` shows the original Benefit Card Navigator with no provider-directory content added.
- `/find-care/` opens directly as a complete separate provider experience.
- Doctor, dentist, and eye-doctor choices work as distinct routes or clearly routed views within `/find-care/`.
- Provider results never present enrollment as proof of current network participation or new-patient acceptance.
- Every material provider claim shows its source status and date where available.
- Unsupported language, network, license, accessibility, telehealth, or availability claims are not guessed.
- The Care List clearly describes submission as an inquiry, not a guaranteed appointment, claim, order, authorization, or PCP selection.
- No real patient information is collected by the static prototype.
- Practice and owner prototypes use synthetic data and remain separate from the public provider directory.
- Statuses have text/icons in addition to colors and retain event history.
- The layout works on desktop and mobile and supports keyboard navigation and accessible labels.
- Existing provider research and code are preserved.

Before making changes, summarize which non-frozen files you intend to change. After implementation, report every changed file, tests performed, route tested, remaining data limitations, and confirmation that the frozen hashes still match.
