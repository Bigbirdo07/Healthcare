# Copy-paste prompt: Rhode Island provider data collection

Paste everything below into a web-enabled research tool. If the tool cannot create downloadable files, have it return the findings in sections and ask it to continue until every source and field has been covered.

---

I am building a Rhode Island healthcare provider directory for a benefit-card website. Research and collect official, current, publicly available data for these three categories:

1. Doctors and other clinicians appropriate for a “Find a doctor” directory
2. Dentists
3. Eye-care professionals, with optometrists and ophthalmologists labeled separately (and opticians kept separate if included)

The directory must help a user determine licensure, specialty, location, Medicare participation, Rhode Island Medicaid participation, exact insurance-plan network participation, whether the practice is accepting new patients, and verified language support.

## Source requirements

Use primary/official sources wherever possible. Prioritize:

- Rhode Island Department of Health active-license lists and real-time professional-license verification
- CMS NPPES/NPI downloadable files or official API
- CMS Medicare Care Compare / Doctors and Clinicians downloadable data and data dictionary
- Rhode Island EOHHS Medicaid Provider Search and downloadable provider information
- Official Rhode Island Medicaid managed-care plan directories
- HealthSource RI provider search
- Official insurer provider directories and machine-readable provider-directory files
- Official practice websites only as supplemental evidence

Do not use data brokers, people-search sites, unofficial directory aggregators, or inferred facts as authoritative evidence. Do not bypass access controls or violate a website’s terms. Prefer downloadable files and APIs over scraping HTML. Record any licensing, attribution, rate-limit, or reuse restrictions.

## Critical accuracy rules

- Do not infer a spoken language from a provider’s surname, name, photo, race, ethnicity, or perceived background.
- Do not infer insurance acceptance from an NPI or active license.
- Keep these facts separate: Medicare enrollment, Medicare assignment, Original Medicare, Medicare Advantage network participation, Rhode Island Medicaid fee-for-service participation, Medicaid managed-care network participation, commercial-plan network participation, and accepting new patients.
- A provider being listed in a directory is not proof that the office is currently accepting new patients. Preserve the source wording and last-updated date.
- Keep individual clinicians (Type 1 NPI) separate from organizations/practices (Type 2 NPI).
- Never collect patient information. This task is provider-directory research only.
- Do not download or reuse provider photographs unless the source explicitly permits reuse. Return a profile-page URL instead.

## Research deliverables

### A. Source inventory

Create `ri_provider_sources.csv` with one row per source and these columns:

```text
source_id,source_name,authority,provider_categories,coverage_fact,source_url,download_or_api_url,file_format,fields_available,geographic_scope,update_frequency,last_updated_date,date_accessed,terms_or_license,reuse_notes,automation_notes,known_limitations
```

For every source, explain exactly what the source proves and what it does not prove. Include direct links to data dictionaries and API documentation.

### B. Provider records

Create UTF-8 `ri_providers.csv` and `ri_providers.json`. Use one row/object for each unique clinician-at-practice-location combination. Use empty values for unknown facts; never guess. Include these fields:

```text
provider_record_id
npi
npi_type
first_name
middle_name
last_name
suffix
credentials
organization_npi
practice_name
provider_category
taxonomy_code
taxonomy_description
specialty
subspecialty
license_number
license_type
license_status
license_expiration_date
address_line_1
address_line_2
city
state
zip
county
latitude
longitude
public_phone
public_website
profile_page_url
telehealth_status
wheelchair_accessible_status
accepting_new_patients_status
accepting_new_patients_last_confirmed
accepting_new_patients_source_id
medicare_enrollment_status
medicare_assignment_status
medicare_source_id
ri_medicaid_ffs_status
ri_medicaid_ffs_source_id
last_verified_at
record_confidence
manual_review_required
manual_review_reason
```

Use controlled values where applicable:

- Status fields: `yes`, `no`, `unknown`, or `source_conflict`
- License status: preserve the official status and also indicate whether it is active
- Confidence: `high`, `medium`, or `low`

### C. Insurance network relationships

Create `ri_provider_networks.csv` with one row per provider/location/network relationship:

```text
npi,provider_record_id,payer_name,plan_name,plan_id,network_name,coverage_type,network_status,accepting_new_patients_status,source_id,source_url,source_last_updated,date_accessed,practice_confirmed,practice_confirmed_date,notes
```

Use these `coverage_type` values where supported:

- `medicare_advantage`
- `ri_medicaid_managed_care`
- `commercial_marketplace`
- `commercial_other`

Do not write only “takes Medicaid” when the source actually identifies a specific managed-care plan. Preserve the exact payer, plan, and network names.

### D. Language and interpreter relationships

Create `ri_provider_languages.csv` with one row per language claim:

```text
npi,provider_record_id,language_bcp47,language_name,spoken_by,proficiency,interpreter_mode,verification_method,source_id,source_url,source_last_updated,date_accessed,notes
```

Use these controlled values:

- `spoken_by`: `clinician`, `office_staff`, or `interpreter`
- `proficiency`: `basic`, `conversational`, `professional_clinical`, `unknown`, or the exact source wording
- `interpreter_mode`: `in_person`, `video`, `phone`, `multiple`, `none`, or `unknown`
- `verification_method`: `provider_attested`, `practice_confirmed`, `insurer_directory`, `official_directory`, or `unknown`

Do not convert a general office-level language listing into a claim that a particular clinician speaks that language.

### E. Match and conflict report

Create `ri_provider_match_review.csv` for possible duplicates, uncertain matches, and conflicting facts:

```text
review_id,record_a_id,record_b_id,issue_type,field_name,value_a,value_b,source_a,source_b,suggested_action,reason
```

Do not merge records based only on similar names. Prefer NPI and license number, supported by name, credentials, taxonomy, and practice location. Flag rather than force uncertain matches.

### F. Research report

Write a concise report that includes:

1. Total records by provider category and profession
2. Total active-license matches
3. Counts with Medicare enrollment and Medicare assignment
4. Counts with Rhode Island Medicaid fee-for-service status
5. Counts by Medicaid managed-care and commercial network
6. Counts with verified accepting-new-patients information
7. Counts with clinician, staff, and interpreter language data
8. Duplicate/conflict/manual-review counts
9. Missing fields and data-quality problems
10. Recommended refresh schedule for each source
11. Exact steps or API requests needed to reproduce each download
12. Sources that could not legally or technically be automated

## Data packaging

Return a ZIP named `ri_provider_directory_research_YYYY-MM-DD.zip` containing:

```text
README.md
ri_provider_sources.csv
ri_providers.csv
ri_providers.json
ri_provider_networks.csv
ri_provider_languages.csv
ri_provider_match_review.csv
research_report.md
raw_source_manifest.csv
```

The raw-source manifest must contain filenames or URLs, cryptographic SHA-256 hashes for downloaded files, retrieval timestamps, and source IDs. Do not place huge original source files in the ZIP if redistribution is not allowed; list their official download URLs and hashes instead.

Before finishing, validate that CSV files parse correctly, JSON is valid, dates use ISO 8601, Rhode Island is represented as `RI`, ZIP codes retain leading zeros, phone numbers are not accidentally converted to numbers, and every factual status has a source ID or is marked `unknown`.

At the end, clearly state which facts still require phone or direct practice confirmation. Do not claim this dataset is a complete list of all currently practicing or available providers unless the official sources support that conclusion.

---

## What to send back with the research

Send the ZIP unchanged. If a ZIP cannot be produced, send the files individually. Also include the research tool's written summary and note the date it completed the research.

