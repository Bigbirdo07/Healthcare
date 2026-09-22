"""Build the New Hampshire plan dataset used by the static dashboard.

The input CSV files are not committed to this repository. Download the current
plan and benefit datasets from the official source, then pass their paths on the
command line. The generated JSON can subsequently be extended with the Rhode
Island and remaining New England scripts.
"""

import argparse
import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--plans", type=Path, required=True, help="Marketplace plan CSV")
parser.add_argument("--benefits", type=Path, required=True, help="Marketplace benefit CSV")
parser.add_argument("--output", type=Path, default=Path("dist/data.json"), help="Generated JSON path")
args = parser.parse_args()

TARGETS=[
 ('Acupuncture','Acupuncture'),('Chiropractic Care','Chiropractic'),
 ('Routine Eye Exam (Adult)','Adult eye exam'),('Hearing Aids','Hearing aids'),
 ('Basic Dental Care - Adult','Adult dental'),('Weight Loss Programs','Weight-loss program'),
 ('Nutritional Counseling','Nutrition counseling'),('Bariatric Surgery','Bariatric surgery'),
 ('Preventive Care/Screening/Immunization','Preventive care')]
target_map=dict(TARGETS)

def issuer_name(x):
 return (x or '').replace('Anthem Blue Cross and Blue Sheld','Anthem Blue Cross and Blue Shield')

with args.plans.open(newline='',encoding='utf-8-sig') as f:
 plans=list(csv.DictReader(f))
with args.benefits.open(newline='',encoding='utf-8-sig') as f:
 benefits=list(csv.DictReader(f))

benefit_map=defaultdict(dict)
for r in benefits:
 if r['BenefitName'] in target_map:
  benefit_map[r['PlanId']][target_map[r['BenefitName']]]={
   'covered':r['IsCovered']=='Covered','status':r['IsCovered'] or 'Not stated',
   'copay':r['CopayInnTier1'] or '', 'coinsurance':r['CoinsInnTier1'] or '',
   'limit':(' '.join(x for x in [r['LimitQty'],r['LimitUnit']] if x)).strip(),
   'explanation':r['Explanation'] or '', 'exclusions':r['Exclusions'] or ''}

outplans=[]
for r in plans:
 if r['DentalOnlyPlan']=='Yes': continue
 bm=benefit_map.get(r['PlanId'],{})
 score=sum(1 for x in bm.values() if x['covered'])
 outplans.append({
  'id':r['PlanId'],'baseId':r['StandardComponentId'],'issuer':issuer_name(r['IssuerMarketPlaceMarketingName']),
  'name':r['PlanMarketingName'],'variant':r['PlanVariantMarketingName'],'metal':r['MetalLevel'],
  'type':r['PlanType'],'market':r['MarketCoverage'],'hsa':r['IsHSAEligible'],
  'deductible':r['MEHBDedInnTier1Individual'],'moop':r['MEHBInnTier1IndividualMOOP'],
  'sbc':r['URLForSummaryofBenefitsCoverage'],'score':score,'benefits':bm})

issuers=sorted(set(p['issuer'] for p in outplans))
issuer_coverage=[]
for issuer in issuers:
 ps=[p for p in outplans if p['issuer']==issuer]
 row={'issuer':issuer,'plans':len(ps)}
 for _,label in TARGETS:
  vals=[p['benefits'].get(label,{}).get('covered',False) for p in ps]
  row[label]=round(100*sum(vals)/len(vals)) if vals else 0
 issuer_coverage.append(row)

metal_scores=[]
for metal in ['Catastrophic','Expanded Bronze','Silver','Gold']:
 vals=[p['score'] for p in outplans if p['metal']==metal]
 if vals: metal_scores.append({'metal':metal,'median':statistics.median(vals),'min':min(vals),'max':max(vals),'plans':len(vals)})

extras=[
 {'key':'NH-MED-ACNH','plan':'AmeriHealth Caritas New Hampshire','coverage':'Medicaid','category':'Rewards','benefit':'CARE Card rewards','value':'Up to $250 value per member per year','requirements':'Complete eligible health-related activities; qualifying activities and timing apply','how':'Reward card','url':'https://www.amerihealthcaritasnh.com/member/benefits/carecard'},
 {'key':'NH-MED-ACNH','plan':'AmeriHealth Caritas New Hampshire','coverage':'Medicaid','category':'Transportation','benefit':'Transportation services','value':'Transportation support for covered care','requirements':'Member and trip rules apply; arrange through the plan','how':'Call the plan','url':'https://www.amerihealthcaritasnh.com/'},
 {'key':'NH-MED-ACNH','plan':'AmeriHealth Caritas New Hampshire','coverage':'Medicaid','category':'Behavioral health','benefit':'Telehealth behavioral services','value':'Remote behavioral health access','requirements':'Member eligibility and network rules apply','how':'Use plan provider resources','url':'https://www.amerihealthcaritasnh.com/'},
 {'key':'NH-MED-NHHF','plan':'NH Healthy Families','coverage':'Medicaid','category':'Transportation','benefit':'Mileage reimbursement','value':'Gas, parking and toll reimbursement for covered medical and behavioral appointments','requirements':'Schedule before appointment; driver registration is required and a trip log must be maintained','how':'MTM 1-888-597-1192 or MTM Link','url':'https://www.nhhealthyfamilies.com/'},
 {'key':'NH-MED-NHHF','plan':'NH Healthy Families','coverage':'Medicaid','category':'Food resources','benefit':'Food-security navigation','value':'Connections to food pantries, SNAP/WIC and community resources','requirements':'Resource assistance, not an insurance payment benefit','how':'Plan and community links','url':'https://www.nhhealthyfamilies.com/'},
 {'key':'NH-MED-WS','plan':'WellSense New Hampshire Medicaid','coverage':'Medicaid','category':'Vision','benefit':'Routine eye exam','value':'One routine eye exam every 12 months','requirements':'Use participating providers and follow the member handbook','how':'Find a provider','url':'https://www.wellsense.org/plans/medicaid/nh/nh-medicaid'},
 {'key':'NH-MED-WS','plan':'WellSense New Hampshire Medicaid','coverage':'Medicaid','category':'Transportation','benefit':'Nonemergency medical transportation','value':'Transportation to medical appointments','requirements':'Trips may require advance approval','how':'Plan transportation resources','url':'https://www.wellsense.org/members/nh/new-hampshire-medicaid/documents-and-forms'},
 {'key':'NH-MED-WS','plan':'WellSense New Hampshire Medicaid','coverage':'Medicaid','category':'Rewards and OTC','benefit':'OTC rewards card','value':'Funds for eligible drugstore items and some utility bills','requirements':'Complete eligible activities; combined cash/non-cash maximum $250 per state fiscal year','how':'Submit reward forms or use member portal','url':'https://www.wellsense.org/plans/medicaid/nh/nh-medicaid'},
 {'key':'NH-MED-WS','plan':'WellSense New Hampshire Medicaid','coverage':'Medicaid','category':'Fitness','benefit':'Tai Ji Quan balance program','value':'24-week YMCA program once per year, virtual or in person','requirements':'Member must have mobility concerns','how':'Contact the plan','url':'https://www.wellsense.org/plans/medicaid/nh/nh-medicaid'},
 {'key':'NH-MED-WS','plan':'WellSense New Hampshire Medicaid','coverage':'Medicaid','category':'Fitness','benefit':'Tracker or gym reimbursement transition benefit','value':'Fitness tracker OR gym membership/WeightWatchers reimbursement','requirements':'Only members enrolled at least 3 months before Sept. 1, 2026; deadline Mar. 31, 2027; cannot combine tracker and gym','how':'Submit reimbursement form','url':'https://www.wellsense.org/members/nh/new-hampshire-medicaid/your-extras'},
 {'key':'NH-MED-WS','plan':'WellSense New Hampshire Medicaid','coverage':'Medicaid','category':'Pregnancy','benefit':'Prenatal vitamins','value':'$0 copay during pregnancy through three months postpartum','requirements':'Pregnancy timing and formulary rules apply','how':'Prescription and plan pharmacy','url':'https://www.wellsense.org/your-health/pregnancy'},
 {'key':'NH-MED-WS','plan':'WellSense New Hampshire Medicaid','coverage':'Medicaid','category':'Pregnancy rewards','benefit':'Prenatal visit rewards','value':'$10 per prenatal visit, up to $100 on an OTC card','requirements':'Provider-signed form; subject to $250 state fiscal-year rewards maximum','how':'Submit prenatal visit form','url':'https://www.wellsense.org/your-health/pregnancy'},
 {'key':'ISSUER-AMB-NH','plan':'Ambetter from NH Healthy Families','coverage':'Commercial','category':'Rewards','benefit':'My Health Pays','value':'Earn up to $500 for eligible healthy activities','requirements':'Activate account, accept terms and complete qualifying activities; verify eligibility for the exact plan','how':'Online member account','url':'https://www.ambetterhealth.com/en/nh/programs-savings/my-health-pays/'},
 {'key':'ISSUER-AMB-NH','plan':'Ambetter from NH Healthy Families','coverage':'Commercial','category':'Bills and daily needs','benefit':'Reward redemption','value':'Rewards may pay premiums, cost sharing, utilities, rent, transportation, education or childcare','requirements':'Restrictions and qualifying activities apply; verify eligibility for the exact plan','how':'My Health Pays portal','url':'https://www.ambetterhealth.com/en/nh/programs-savings/my-health-pays/'},
 {'key':'ISSUER-AMB-NH','plan':'Ambetter from NH Healthy Families','coverage':'Commercial','category':'Telehealth','benefit':'Virtual 24/7 Care','value':'Video and telephone medical help','requirements':'Availability and cost sharing depend on the exact plan','how':'Member account or app','url':'https://www.ambetterhealth.com/en/nh/'}]

extra_counts=[]
for name in sorted(set(x['plan'] for x in extras)):
 xs=[x for x in extras if x['plan']==name]
 extra_counts.append({'plan':name,'coverage':xs[0]['coverage'],'count':len(xs)})

payload={'meta':{'year':2026,'state':'New Hampshire','commercialPlans':len(outplans),'basePlans':len(set(p['baseId'] for p in outplans)),'commercialIssuers':len(issuers),'medicaidPlans':3,'verified':'2026-09-17'},'benefitLabels':[x[1] for x in TARGETS],'plans':outplans,'issuerCoverage':issuer_coverage,'metalScores':metal_scores,'extras':extras,'extraCounts':extra_counts}
args.output.parent.mkdir(parents=True, exist_ok=True)
with args.output.open('w',encoding='utf-8') as f: json.dump(payload,f,separators=(',',':'))
print(json.dumps({'plans':len(outplans),'bytes':args.output.stat().st_size,'issuers':issuers},indent=2))
