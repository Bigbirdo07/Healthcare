# Provider Directory and Care Request Roadmap

Logged: September 24, 2026

## Product vision

Extend Benefit Card Navigator from a plan-benefit directory into a trustworthy path from “What does my card cover?” to “Who can I contact for care?”

The proposed experience has three provider areas (the original note said two tabs, but named three):

1. Find a doctor
2. Find a dentist
3. Find an eye doctor

Start with Rhode Island, then expand only after the data-import and verification process works reliably.

## Clarified system flow: routed inquiry, local practice record

The intended product is a straight-line workflow with multiple stops, not a centrally hosted medical-record system:

```text
Benefit marketplace
  → Patient builds a Care list
  → Patient sends an inquiry to the selected practice
  → Inquiry is delivered to that practice's portal
  → Practice staff review demand and call the patient
  → Staff record the outreach result
  → A limited status event returns to the owner's private analytics view
  → Identifiable working records and notes remain on the practice's local computer
```

### Exact stops

1. **Marketplace:** The user chooses benefits/services and a doctor, dentist, or eye-care professional.
2. **Inquiry review:** The user sees a summary and submits a request. This is an inquiry, not a confirmed appointment, medical order, or insurance claim.
3. **Routing:** The system delivers the inquiry only to the selected practice's portal.
4. **Practice queue:** Staff see incoming inquiries ordered by date, urgency rules, and demand. They decide whom to call and when.
5. **Outreach:** Staff call the user using the submitted contact preference.
6. **Status entry:** Staff record the outcome:
   - Red: new inquiry / practice still needs to call
   - Yellow: call attempted / patient did not answer
   - Green: patient reached and inquiry handled
   - Blue: appointment made because of the inquiry
7. **Analytics return:** The system sends a minimal event back to a private owner-only dashboard or analytics table, containing the event date, practice identifier, inquiry identifier, previous status, new status, and timestamps.
8. **Local record:** Patient notes and the practice's detailed activity log are saved locally at the practice and are not copied into the owner's analytics system.

Status must include text and an icon in addition to color. Blue is an outcome layered on top of outreach: the system should preserve that a patient was contacted before an appointment was made rather than overwriting the earlier events.

### Central versus local data boundary

| Data | Transit/routing service | Practice's local system | Owner analytics |
| --- | --- | --- | --- |
| Inquiry identifier | Temporarily, for reliable delivery | Yes | Yes, pseudonymous |
| Patient name and phone number | Temporarily, encrypted, until delivery/expiry | Yes | No |
| Requested provider/service | Temporarily, until delivery/expiry | Yes | Prefer category/code only |
| Date of birth | Temporarily, encrypted, until delivery/expiry | Yes | No |
| Clinical or free-text notes | No | Yes | No |
| Contact attempts | Delivery/status events only | Full local log | Counts/timestamps/status only |
| Appointment details | No detailed appointment data | Yes | `appointment_made: yes/no` and event date only |
| Status history | Minimal delivery window | Full history | Minimal pseudonymous event history |

The routing service still needs a short-lived encrypted delivery queue, delivery acknowledgement, retry handling, and an expiry/deletion rule. Otherwise an inquiry can disappear if the practice computer is offline. After the practice portal acknowledges and safely writes the inquiry locally, the routing copy should be deleted on the documented schedule.

The patient-facing inquiry form will collect the patient's name, date of birth, and phone number with an explicit explanation that these fields will be sent to the selected practice so its staff can identify and call the patient. Those three fields appear in the practice portal and are saved in the practice's local record. They do not appear in the owner's analytics dashboard, Google Sheet, reporting export, or status-event payload.

### Owner-only analytics pipeline

Google Sheets can be used for a prototype only if it receives no names, phone numbers, dates of birth, medical notes, exact appointment details, or free text. A safer event row would be:

```text
event_id,anonymous_inquiry_id,practice_id,provider_category,service_category,submitted_date,previous_status,new_status,event_timestamp,appointment_made
```

Use an unguessable random inquiry ID, not an encoded name, phone number, or birth date. The owner dashboard can then show daily counts and colors without exposing patient identity:

- Number of new/red inquiries by day and practice
- Number of yellow outreach attempts
- Number of green reached/handled inquiries
- Number of blue appointment conversions
- Median time from submission to first call
- Median time from submission to resolution
- Conversion rate from inquiry to appointment

For production, a small protected event database is preferable to Google Sheets because it offers stronger access control, validation, auditability, and reliable automated writes. The same owner dashboard can sit on top of either implementation.

### Local practice delivery

“Download as soon as it hits the doctor's computer” should be implemented as an acknowledged local write:

1. The authenticated practice connector requests pending encrypted inquiries.
2. It decrypts and validates the inquiry on the practice device or local server.
3. It writes the inquiry to the local practice database.
4. It verifies the local write and backup state.
5. It returns a delivery acknowledgement.
6. The routing service marks the message delivered and deletes its payload according to the short retention window.

A browser download alone is not sufficient because it cannot guarantee that staff saved, backed up, or can recover the record. The local practice portal should use an encrypted local database with automatic backup, access controls, and an append-only event log. Local storage changes where the data lives; it does not eliminate the practice's privacy, security, retention, and breach responsibilities.

## Recommendation

This is feasible, but it should be built in phases. Provider discovery can be public and read-only. A patient request workflow, practice portal, messaging, and clinical notes are a separate regulated product surface and require authentication, secure storage, audit logs, written operating policies, and legal/compliance review before real patient data is accepted.

Do not call a medical request a “claim” unless it is actually an insurance claim. In the patient interface, use **Care request** or **Appointment request**. Use **Care list** instead of “cart” so users do not mistake the experience for purchasing guaranteed medical care.

Selecting a doctor in the app also must not be described as officially choosing a primary care physician. The practice has to accept the patient, and the health plan may require a separate PCP designation. The interface should say **Request this doctor as my PCP** and show whether confirmation from the practice and insurer is still pending.

## Phase 1: Rhode Island provider finder

Add the three provider tabs and a shared search experience. Each result should include:

- Provider name and credentials
- Provider type and specialty
- Practice/facility name
- Practice address and verified public phone number
- Active Rhode Island license status and last verification date
- Medicare status
- Rhode Island Medicaid status
- Exact plan/network status when available
- Accepting-new-patients status, with source and last confirmed date
- Accessibility and telehealth information when verified
- Languages, separated into clinician-spoken, staff-spoken, and interpreter services
- Profile photo only when supplied or licensed for reuse
- Every source used, its retrieval date, and a “report incorrect information” action

Recommended filters:

- Distance or city/ZIP
- Provider type and specialty
- Medicare
- Rhode Island Medicaid
- Exact insurance plan/network
- Accepting new patients
- Clinician language
- Office-staff language
- Interpreter availability
- In-person or telehealth
- Accessibility needs

### Important insurance labels

Avoid a single ambiguous “takes Medicare/Medicaid” switch. Use explicit, source-backed states:

- Medicare-enrolled
- Accepts Medicare assignment
- Participates in Rhode Island Medicaid fee-for-service
- Listed in the member’s Medicaid managed-care network
- Listed in the member’s commercial-plan network
- Practice confirmed on `[date]`
- Unknown / call to confirm

Enrollment, network participation, accepting new patients, and accepting a particular plan are different facts. Every result should remind users to confirm with both the practice and insurer before scheduling.

## Rhode Island data plan

Use a layered record rather than treating one source as complete.

| Purpose | Primary source | What it establishes | Limitation |
| --- | --- | --- | --- |
| Active professional license | [RIDOH active licensee list](https://datahealth.ri.gov/lists/licensees/index.php) and [real-time verification](https://healthri.mylicense.com/verification/) | Current Rhode Island license status | Does not prove insurance participation, office availability, or that the provider is accepting patients |
| Provider identity, taxonomy, and public practice locations | [CMS NPPES files](https://download.cms.gov/nppes/NPI_Files.html) | NPI, taxonomy, and public practice-location data | CMS explicitly says an NPI does not validate licensure or credentials; records may be stale |
| Medicare | [CMS Doctors and Clinicians data](https://data.cms.gov/provider-data/topics/doctors-clinicians) | Clinicians/groups listed in Medicare Care Compare; the data dictionary includes Medicare-assignment information | Does not prove an appointment is available or that a Medicare Advantage network includes the provider |
| Rhode Island Medicaid | [RI EOHHS Provider Search](https://eohhs.ri.gov/consumer/provider-search) | Physicians, dentists, and other professionals listed as Medicaid providers | The state warns that the list does not guarantee acceptance of new patients; managed-care members must confirm with their plan |
| Marketplace plan networks | [HealthSource RI Provider Search](https://healthyrhode.ri.gov/HIXWebI3/SearchProvider.action) and carrier directories | Provider-to-plan directory relationships | Directories can change and HealthSource RI tells users to confirm with the provider |

### Import and matching rules

- Use NPI as the principal provider identifier, but never as proof of an active license.
- Keep individual clinicians (Type 1 NPI) distinct from organizations/practices (Type 2 NPI).
- Match RIDOH licenses to NPI records conservatively using license number where available, then name, credential, taxonomy, and location. Send uncertain matches to manual review.
- Store source-specific facts rather than overwriting them with a single yes/no value.
- Preserve `source_url`, `source_name`, `retrieved_at`, `effective_at`, and confidence/verification method for every material fact.
- Refresh active-license data at least daily if the source permits it, CMS data on its publication cadence, and insurer directories frequently enough to display a meaningful “last checked” date.
- Give practices a verified claim/update flow and keep their attestations separate from government or insurer facts.
- Never scrape a site whose terms or technical controls prohibit it. Prefer official downloads and APIs.

## Language information

Do **not** infer language from a provider’s name, surname, photo, ethnicity, or perceived background. That is inaccurate, can discriminate, and could send a patient to someone who cannot safely communicate in that language.

Use these evidence levels instead:

1. Provider-attested language and proficiency
2. Practice-confirmed clinician or staff language, with confirmation date
3. Insurer-directory language field, labeled with its source and retrieval date
4. Professional interpreter available in person, by video, or by phone
5. Unknown

Store clinician language, office-staff language, and interpreter support separately. Let users report an incorrect language listing. If proficiency is collected, use a controlled scale such as “basic,” “conversational,” and “professional/clinical,” and label it as self-attested unless independently verified.

## Phase 2: Care list and request summary

Once provider search is dependable, allow a signed-in user to:

1. Add covered benefits/services to a Care list.
2. Choose a provider or request help finding one.
3. Review a plain-language summary.
4. Choose communication preferences and explicitly consent to texts/voicemail.
5. Submit an appointment/care request.
6. Receive a reference number and see request status.

Submission is not an appointment, order, authorization, insurance claim, coverage guarantee, or PCP designation. The confirmation screen must say what will happen next and the expected response time.

Collect only what the receiving practice actually needs. Date of birth and phone number should not appear in the public/static application or be put into URLs, analytics, logs, or browser storage.

## Phase 3: Practice portal

The practice portal should be a separate authenticated application, not merely another tab in the public site. A local/network deployment can reduce exposure, but it does not remove privacy or security duties. If an Internet service sends inquiries into the practice, both sides and the sync mechanism are part of the security boundary.

Suggested request states:

- **New — action required** (red plus text/icon)
- **Outreach attempted — no response** (yellow plus text/icon)
- **Patient reached** (green plus text/icon)
- **Request submitted/ordered**
- **Appointment scheduled**
- **Declined by practice**
- **Cancelled/closed by patient**

Do not rely on color alone. Each state needs text and an icon for accessibility. “Patient reached,” “order placed,” and “in-person appointment scheduled” are separate events and should not be collapsed into one color. Keep an append-only status history with actor and timestamp so conversion and response metrics can be computed without rewriting history.

Recommended practice view:

- Day/week calendar and queue
- Patient name and only the minimum contact/identity information needed
- Request type and submitted time
- Assigned staff member
- Status, next action, attempt count, and due time
- Contact preferences and consent record
- Structured outcome (scheduled, referred elsewhere, unable to reach, declined, patient cancelled)
- Link to the practice’s existing EHR/workflow where integration is approved

## Patient records and notes

Do not design medical notes to “stay forever.” Retention must follow an approved retention schedule based on Rhode Island law, payer/contract requirements, the practice’s policies, and legal advice. The system also needs access/correction/export handling, legal holds, secure deletion, backups, and documented recovery.

Drag-and-drop clinical notes is high risk. For an early version, keep clinical documentation in the practice’s existing EHR and store only the request workflow. If document import is later required, add malware scanning, file-type and size limits, encryption, role-based access, immutable audit logs, patient matching safeguards, and a supported interoperability route such as FHIR where available.

For several thousand patients, model separate records for patient, practice, provider, request, requested service, contact attempt, appointment/outcome, consent, status event, source evidence, and document metadata. Do not create one unstructured “bin” per patient.

## Privacy, security, and communications gate

Before accepting real patient requests:

- Determine whether Pazeratechnologies is acting as a HIPAA business associate for each practice and execute required agreements. HHS says a software vendor that hosts or can access patient information for a covered provider can be a business associate: [HHS software-vendor guidance](https://www.hhs.gov/hipaa/for-professionals/faq/is-software-vendor-business-associate/index.html).
- Complete and document a security risk analysis covering all electronic protected health information, including local workstations and inbound sync: [HHS risk-analysis guidance](https://www.hhs.gov/hipaa/for-professionals/security/guidance/guidance-risk-analysis/index.html).
- Use encryption in transit and at rest, unique user accounts, multifactor authentication, least-privilege roles, automatic session locking, audit logging, encrypted backups, tested recovery, incident response, and vendor/subcontractor review.
- Confirm whether the FTC Health Breach Notification Rule applies if the consumer application is outside HIPAA: [FTC health-app guidance](https://www.ftc.gov/business-guidance/resources/health-breach-notification-rule-basics-business).
- Obtain consent and record communication preferences before texting or leaving voicemail. Keep messages minimal; HHS advises limiting voicemail content to protect privacy: [HHS voicemail guidance](https://www.hhs.gov/hipaa/for-professionals/faq/may-health-care-providers-leave-messages/index.html).
- Do not put medical details in ordinary SMS or voicemail. A safe default is the practice name, callback number, and a request to return the call, subject to the patient’s stated preference and the practice’s policy.
- Never use advertising pixels or general-purpose analytics on authenticated health/request pages without a formal privacy review.

## Reporting and success measures

Use de-identified or appropriately authorized reporting. Useful operational measures include:

- Time from submission to first outreach
- Contact rate
- Requests submitted to a clinician
- Appointment scheduled rate
- In-person visit resulting from a request
- Closed/cancelled/declined reasons
- Directory corrections and stale-record rate
- Percentage of records recently confirmed by a practice

Do not infer that a scheduled visit means blood work or another procedure occurred. Record those outcomes only when the practice deliberately supplies that fact under an approved purpose and privacy policy.

## Immediate build order

1. Add the three Rhode Island provider-search tabs using sample data and no patient information.
2. Define the normalized provider/source schema and import RIDOH, NPPES, CMS Medicare, RI Medicaid, and plan-directory facts.
3. Add source/date/confidence displays, corrections, and practice verification.
4. Validate directory accuracy with a small group of Rhode Island practices.
5. Prototype the Care list and request summary with synthetic data only.
6. Complete legal/privacy/security design and practice agreements.
7. Build the authenticated practice portal and status-event system.
8. Pilot with one or two practices before statewide launch.

## Decisions still needed

- Whether the first release is directory-only or includes a non-clinical callback request
- Which Rhode Island provider types and specialties are included in “doctor”
- Whether “eye doctor” includes optometrists, ophthalmologists, and opticians, and how each is labeled
- Whether results cover Original Medicare, Medicare Advantage, or both
- Which exact Medicaid managed-care and commercial networks launch first
- Who verifies practice data and how often
- Whether the practice portal integrates with an EHR or stays a request-triage system
- The approved record-retention and deletion schedule
- The permitted SMS/voicemail content and consent flow
