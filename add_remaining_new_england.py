import json
from pathlib import Path

path=Path('dist/data.json'); d=json.loads(path.read_text())
loaded={'CT','ME','MA','VT'}
d['plans']=[p for p in d['plans'] if p.get('state') not in loaded]
d['extras']=[x for x in d['extras'] if x.get('state') not in loaded]
d['extras']=[x for x in d['extras'] if not x.get('key','').startswith(('RI-BCBS-','AUDIT-'))]

labels=['Preventive care','Primary care','Specialist visit','Urgent care','Emergency room','Inpatient hospital','Mental health visits','Generic prescription']
def benefits(note='See the official plan document for your exact copay or coinsurance.'):
    return {x:{'covered':True,'status':'Covered','copay':note,'coinsurance':'','limit':'','explanation':'','exclusions':''} for x in labels}
def add_plan(state,issuer,name,url,ptype='HMO',network='State network',custom=None):
    i=1+sum(p.get('state')==state for p in d['plans']); bid=f'{state}2026-{i:03d}'
    d['plans'].append({'id':bid,'baseId':bid,'state':state,'issuer':issuer,'name':name,'variant':name,'metal':'','type':ptype,'market':'Individual','hsa':'Yes' if 'HSA' in name or 'HDHP' in name else 'No','deductible':'','moop':'','sbc':url,'score':len(labels),'benefitLabels':labels,'benefits':custom or benefits(),'network':network})
def add_med(state,key,plan,benefit,value,url):
    d['extras'].append({'key':key,'state':state,'plan':plan,'coverage':'Medicaid','category':'Plan coverage','benefit':benefit,'value':value,'requirements':'Eligibility and covered-service rules depend on the Medicaid program shown on the member card.','how':'Open the official program page','url':url})
def add_extra(state,key,plan,category,benefit,value,requirements,url):
    d['extras'].append({'key':key,'state':state,'plan':plan,'coverage':'Commercial','category':category,'benefit':benefit,'value':value,'requirements':requirements,'how':'Open the official source and confirm eligibility for your exact plan','url':url,'evidence':'Official carrier source'})

# Connecticut — official Access Health CT marketplace; carrier plan-document portals.
ct='https://www.accesshealthct.com/'
for name in ['Anthem Pathway Standard Gold','Anthem Pathway Standard Silver','Anthem Pathway Standard Bronze','Anthem Pathway HSA Bronze']:
    add_plan('CT','Anthem Blue Cross and Blue Shield',name,'https://www.anthem.com/ct/individual-and-family/health-insurance')
for name in ['ConnectiCare Choice Gold','ConnectiCare Choice Silver','ConnectiCare Choice Bronze','ConnectiCare Value Gold','ConnectiCare Value Silver','ConnectiCare Value Bronze','ConnectiCare Covered CT']:
    add_plan('CT','ConnectiCare',name,'https://www.connecticare.com/resources/forms/individual/plan-documents')
add_med('CT','CT-MED-HUSKY-A','HUSKY Health','HUSKY A','Medicaid coverage for eligible children, parents, caregivers and pregnant members','https://www.huskyhealthct.org/')
add_med('CT','CT-MED-HUSKY-C','HUSKY Health','HUSKY C','Medicaid coverage for eligible older adults and people with disabilities','https://www.huskyhealthct.org/')
add_med('CT','CT-MED-HUSKY-D','HUSKY Health','HUSKY D','Medicaid coverage for eligible adults','https://www.huskyhealthct.org/')
add_extra('CT','AUDIT-CT-CONN-DISCOUNTS','ConnectiCare','Everyday savings','Healthy Discounts','Member discounts on eligible health and wellness products and services','Offers and eligibility vary by exact plan; sign in to myConnectiCare before purchasing.','https://www.connecticare.com/')
add_extra('CT','AUDIT-CT-CONN-CLASSES','ConnectiCare','Fitness','Free health and wellness classes','ConnectiCare publishes free classes and community events','Schedules, locations and eligibility change; register through the current event listing.','https://www.connecticare.com/')

# Maine — CoverME.gov and official 2026 Harvard Pilgrim product grid.
hp='https://www.harvardpilgrim.org/public/docs/2026-product-grid-me-ind-on'
hp_rows=[
('Clear Choice HMO Gold 2500','$20 primary care / $50 specialist'),
('Clear Choice HMO Silver 4000','$40 primary care / $60 specialist'),
('Clear Choice HMO Silver 5000','$40 primary care / $60 specialist'),
('Clear Choice HMO Bronze 7500','$45 primary care / $80 specialist'),
('HMO Bronze 8500','$50 primary care; specialist subject to plan terms'),
('Clear Choice HMO HSA Bronze 6300','Deductible, then 50%'),
('Clear Choice HMO HSA Bronze 8000','Deductible, then plan pays in full'),
("Clear Choice Maine's Choice Plus HMO Gold 2500",'Preferred: $20 primary care / $50 specialist'),
("Clear Choice Maine's Choice Plus HMO Silver 4000",'Preferred: $40 primary care / $60 specialist'),
("Clear Choice Maine's Choice Plus HMO Silver 5000",'Preferred: $40 primary care / $60 specialist'),
("Clear Choice Maine's Choice Plus HMO Bronze 7500",'Preferred: $45 primary care / $80 specialist'),
("Clear Choice Maine's Choice Plus HMO HSA Bronze 6300",'Preferred: deductible, then 50%'),
]
for name,office in hp_rows:
    b=benefits(); b['Primary care']['copay']=office.split(' / ')[0]; b['Specialist visit']['copay']=office
    add_plan('ME','Harvard Pilgrim Health Care',name,hp,custom=b)
for issuer,name,url in [
('Anthem Blue Cross and Blue Shield','Anthem Clear Choice HMO','https://www.anthem.com/me/individual-and-family/health-insurance'),
('Anthem Blue Cross and Blue Shield','Anthem Clear Choice PPO','https://www.anthem.com/me/individual-and-family/health-insurance'),
('Community Health Options','Community Health Options Clear Choice','https://www.healthoptions.org/members'),
('Mending','Mending Primary Care Marketplace Plan','https://www.coverme.gov/learn/what-plans-are-available')]:
    add_plan('ME',issuer,name,url)
add_med('ME','ME-MED-MAINECARE','MaineCare','MaineCare','Maine Medicaid coverage and member services','https://www.maine.gov/dhhs/oms/member-resources')
add_extra('ME','AUDIT-ME-CHO-VIRTUAL','Community Health Options','Virtual care','24/7 virtual care','Virtual urgent, primary and behavioral health options are offered across Community Health Options plans','The vendor and member cost depend on the exact plan; sign in to the member portal first.','https://www.healthoptions.org/')
add_extra('ME','AUDIT-ME-CHO-CISP','Community Health Options','Chronic conditions','Chronic Illness Support Program','Additional support and coverage for asthma, diabetes, coronary artery disease, COPD and hypertension','Included on non-HSA plans; condition, service and network requirements apply.','https://www.healthoptions.org/')
add_extra('ME','AUDIT-ME-CHO-RX','Community Health Options','Pharmacy','$5 common generics','Many frequently used generic prescriptions are available for $5','Drug formulary, pharmacy and exact plan rules apply.','https://www.healthoptions.org/')

# Massachusetts — Health Connector carrier/card families. ConnectorCare includes Card to Culture.
ma='https://www.mahealthconnector.org/'
ma_plans=[
('Blue Cross Blue Shield of Massachusetts','Health Connector Standard Plan'),
('Harvard Pilgrim Health Care','Standard Platinum – Flex'),('Harvard Pilgrim Health Care','Standard High Gold'),
('Harvard Pilgrim Health Care','HMO 2000 Value II – Flex'),('Harvard Pilgrim Health Care','Standard Silver II'),
('Harvard Pilgrim Health Care','Standard High Bronze HSA – Flex'),
('Health New England','ConnectorCare'),('Mass General Brigham Health Plan','ConnectorCare'),
('Mass General Brigham Health Plan','Complete HMO'),('Tufts Health Plan','Tufts Health Direct ConnectorCare'),
('WellSense Health Plan','WellSense ConnectorCare')]
for issuer,name in ma_plans:add_plan('MA',issuer,name,ma)
for key,plan in [('MA-MED-WELLSENSE','WellSense MassHealth'),('MA-MED-TUFTS','Tufts Health Together'),('MA-MED-ACO','MassHealth Accountable Care Partnership Plan')]:
    add_med('MA',key,plan,'MassHealth coverage','Massachusetts Medicaid benefits and managed-care services','https://www.mass.gov/masshealth')
d['extras'].append({'key':'MA-CONNECTOR-CULTURE','state':'MA','plan':'ConnectorCare','coverage':'Commercial','category':'Community access','benefit':'ConnectorCare Card to Culture','value':'Free or reduced admission at participating Massachusetts cultural organizations','requirements':'Show a valid ConnectorCare card; each organization sets its own offer and limits.','how':'Check the participating venue offer','url':'https://massculturalcouncil.org/organizations/card-to-culture/connectorcare-card-to-culture/'})

# Harvard Pilgrim publishes a standard reimbursement process, but eligibility and amount are plan-specific.
for st in ['ME','MA','NH']:
    add_extra(st,f'AUDIT-{st}-HP-FITNESS','Harvard Pilgrim Health Care','Fitness','Fitness reimbursement','Eligible plans may reimburse qualifying gym, studio and virtual fitness membership expenses','Your plan must include the reimbursement. Generally requires eligible membership and proof of payment for at least four months; the amount varies by plan.','https://www.harvardpilgrim.org/public/docs/standard-fitness-reimbursement-form')

# WellSense public plan information identifies these conveniences across its plan portfolio.
for st in ['MA','NH']:
    add_extra(st,f'AUDIT-{st}-WS-TELE','WellSense Health Plan','Virtual care','Telehealth access','Virtual appointments and member support from home','Availability, provider network and cost sharing depend on the exact plan.','https://www.wellsense.org/')
    add_extra(st,f'AUDIT-{st}-WS-NURSE','WellSense Health Plan','Care support','24/7 nurse advice line','Round-the-clock guidance from a nurse','This is guidance, not emergency care; access rules depend on the exact plan.','https://www.wellsense.org/')

# Rhode Island — BCBSRI individual and family wellness extras.
d['extras'].extend([
    {'key':'RI-BCBS-GYM','state':'RI','plan':'Blue Cross & Blue Shield of Rhode Island','coverage':'Commercial','category':'Fitness','benefit':'Gym membership discounts','value':'Member-only savings on participating gym memberships through BCBSRI wellness offers','requirements':'You must be an eligible BCBSRI member. Participating gyms, prices and offers can change; sign in to BlueCare Connect to see the options available to your exact plan.','how':'Sign in to BlueCare Connect and open Discounts & savings','url':'https://www.bcbsri.com/individual/choose/wellness'},
    {'key':'RI-BCBS-CLASSES','state':'RI','plan':'Blue Cross & Blue Shield of Rhode Island','coverage':'Commercial','category':'Fitness','benefit':'Free local fitness classes','value':'Free yoga, salsa, Zumba and other wellness classes offered through Your Blue Store','requirements':'Class schedules, locations, space and member eligibility vary. Check the current BCBSRI event schedule before attending.','how':'Open the wellness page and view current classes','url':'https://www.bcbsri.com/individual/choose/wellness'}
])

# Vermont — official 2026 plan-design source identifies BCBSVT and MVP.
vt='https://info.healthconnect.vermont.gov/vermont-health-connect-info-center'
for issuer,prefix in [('Blue Cross and Blue Shield of Vermont','BCBSVT'),('MVP Health Care','MVP VT Plus')]:
    for name in [f'{prefix} Gold',f'{prefix} Silver',f'{prefix} Bronze',f'{prefix} Gold HDHP',f'{prefix} Silver HDHP']:
        add_plan('VT',issuer,name,vt)
add_med('VT','VT-MED-MCA','Green Mountain Care','Medicaid for Children and Adults','Vermont Medicaid health coverage','https://info.healthconnect.vermont.gov/medicaid')
add_med('VT','VT-MED-DR-DY','Green Mountain Care','Dr. Dynasaur','Low-cost or free coverage for eligible children, teens and pregnant members','https://info.healthconnect.vermont.gov/dr-dynasaur')
add_extra('VT','AUDIT-VT-MVP-GIA','MVP Health Care','Virtual care','Gia virtual care','24/7 virtual urgent care plus virtual therapy and pediatric options','Services, state availability, providers and normal plan cost sharing vary by exact plan.','https://www.mvphealthcare.com/')
add_extra('VT','AUDIT-VT-MVP-WELLBEING','MVP Health Care','Fitness','Well-being reimbursement','Eligible plans may reimburse approved health and well-being expenses','The program and dollar amount are not included on every plan; verify inside Gia before spending.','https://www.mvphealthcare.com/')

d['meta']['states']=['CT','ME','MA','NH','RI','VT']
d['meta']['stateNames']={'CT':'Connecticut','ME':'Maine','MA':'Massachusetts','NH':'New Hampshire','RI':'Rhode Island','VT':'Vermont'}
path.write_text(json.dumps(d,separators=(',',':')))
for st in d['meta']['states']:
    print(st,len([p for p in d['plans'] if p.get('state')==st]),len({x['key'] for x in d['extras'] if x.get('state')==st and x['coverage']=='Medicaid'}))
