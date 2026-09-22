# Benefit Card Navigator

Benefit Card Navigator is a static, browser-based application for exploring publicly available health-plan benefits across the six New England states. It helps users find a plan, review benefit categories, compare selected Marketplace plans, and follow links back to official carrier or government sources.

The project was designed and developed by Alberto Alejandro Paz as a portfolio project in public-data integration, consumer health information, and accessible frontend engineering.

## What it demonstrates

- Integration of heterogeneous public insurance-plan data into a normalized JSON model
- Coverage for Connecticut, Maine, Massachusetts, New Hampshire, Rhode Island, and Vermont
- A searchable benefit explorer for commercial and Medicaid plan information
- Side-by-side Marketplace plan comparison
- State, issuer, plan, and benefit filtering in a dependency-free JavaScript frontend
- Visible evidence links, coverage limitations, and user-facing safety disclaimers
- Python data-transformation scripts and a deployable static site

The included snapshot contains 296 commercial plan records from 15 issuers plus 46 supplemental or Medicaid benefit entries. New Hampshire and Rhode Island contain the most detailed plan-level cost-sharing information; the other states provide carrier and program directory coverage.

## Technology

- Python standard library for CSV/JSON transformation
- JavaScript, HTML5, and CSS3
- Static JSON data delivery
- Responsive, accessible UI components
- OpenAI static-hosting configuration

## Run locally

No JavaScript build step or package installation is required.

```bash
python3 -m http.server 8000 --directory dist
```

Then open `http://localhost:8000`.

## Rebuild the data

The generated `dist/data.json` snapshot is committed so the site works immediately. Raw source CSV files are intentionally excluded.

```bash
python3 build_dashboard_data.py \
  --plans data/raw/nh_2026_commercial_plans.csv \
  --benefits data/raw/nh_2026_commercial_benefits.csv \
  --output dist/data.json
python3 add_rhode_island.py
python3 add_remaining_new_england.py
```

The scripts should be reviewed against current source schemas before producing a new annual release.

## Data sources and limitations

The application uses public plan data and official government or carrier webpages, including Healthcare.gov datasets and state Marketplace or Medicaid resources. Supporting links are included in the interface and generated data.

This application is an informational navigator—not an insurer, broker, healthcare provider, eligibility system, or coverage determination tool. Plan benefits, networks, cost sharing, prior-authorization requirements, and eligibility can change. Users must confirm all information with the applicable insurer, official plan documents, or member portal.

The MIT license applies to the original source code in this repository. It does not grant rights to third-party plan data, company names, trademarks, linked documents, or other externally sourced content.

## Repository structure

```text
.
├── build_dashboard_data.py       # Builds the base New Hampshire dataset
├── add_rhode_island.py           # Adds Rhode Island plan records
├── add_remaining_new_england.py  # Adds CT, ME, MA, and VT directories
├── dist/
│   ├── index.html
│   ├── app.js
│   ├── styles.css
│   └── data.json
└── .openai/hosting.json
```

## Author

Alberto Alejandro Paz

- Portfolio: [pazatlas.org](https://pazatlas.org/)
- GitHub: [Bigbirdo07](https://github.com/Bigbirdo07)

