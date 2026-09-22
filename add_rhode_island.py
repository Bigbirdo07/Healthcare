import json
from pathlib import Path

path=Path('dist/data.json')
d=json.loads(path.read_text())
for p in d['plans']: p.setdefault('state','NH')
for x in d['extras']: x.setdefault('state','NH')

source='https://healthsourceri.com/wp-content/uploads/OE2026-IF_English_Web_Final.pdf'
labels=['Preventive care','Primary care','Specialist visit','Urgent care','Emergency room','Inpatient hospital','Mental health visits','Outpatient rehabilitation','Generic prescription']

rows=[
('BCBSRI','VantageBlue Direct Plan 950/1900','PPO','No','National','$0','$20 non-PCMH / $10 PCMH','$30','$50','$100','0%','$20','20%','$10'),
('BCBSRI','VantageBlue Direct Plan 1500/3000','PPO','No','National','$0','$30 non-PCMH / $20 PCMH','$45','$75','$200','20%','$30','20%','$10'),
('BCBSRI','BasicBlue Direct 2500/5000','PPO','No','National','$0','$25 non-PCMH / $15 PCMH','$30','$75','10%','10%','$25','10%','$10'),
('NHPRI','Neighborhood PLUS 2650/5300','HMO','No','Rhode Island','$0','First 2 sick visits free; then $30','$65','$65','$400','0%','First 2 visits free; then $30','$65','$5'),
('BCBSRI','BlueSolutions for HSA Direct 1900/3800','PPO','No','National','$0','$35 non-PCMH / $15 PCMH','$40','$75','$300','$300 per admission','$35','$40','$10'),
('BCBSRI','BlueCHiP Direct 2300/4600','POS','Yes','Rhode Island','$0','$35 non-PCMH / $15 PCMH','$45','$75','10%','10%','$35','10%','$7'),
('BCBSRI','BlueCHiP Direct Advance 2300/4600','POS','Yes','RI narrow network','$0','$35 non-PCMH / $15 PCMH','$45','$75','10%','10%','$35','10%','$7'),
('NHPRI','Neighborhood PLUS 1375/2750','HMO','No','Rhode Island','$0','First 2 sick visits free; then $25','$50','$50','$400','20%','First 2 visits free; then $25','$50','$5'),
('BCBSRI','VantageBlue Direct Plan 6000/12000','PPO','No','National','$0','First sick visit free; then $60 non-PCMH / $40 PCMH','$65','$75','$475','30%','$60','30%','$10'),
('BCBSRI','BlueCHiP Direct 5000/10000','POS','Yes','Rhode Island','$0','$30 non-PCMH / $20 PCMH','$60','$75','10%','10%','$30','10%','$7'),
('BCBSRI','BlueSolutions for HSA Direct 4100/8200','PPO','No','National','$0','20%','20%','20%','20%','20%','20%','20%','$10'),
('BCBSRI','BlueCHiP Direct Advance 4950/9900','POS','Yes','RI narrow network','$0','$45 non-PCMH / $25 PCMH','$60','$75','10%','10%','$45','10%','$7'),
('NHPRI','Neighborhood PRIMARY 4750/9500','HMO','No','Rhode Island','$0','First 2 sick visits free; then $35','$75','$75','40%','40%','First 2 visits free; then $35','$75','$5'),
('NHPRI','Neighborhood PRIMARY 3850/7700 HSA','HMO','No','Rhode Island','$0','15%','15%','15%','15%','15%','15%','15%','$5'),
('BCBSRI','BlueCHiP Direct 7000/14000','POS','Yes','Rhode Island','$0','$45 non-PCMH / $35 PCMH','30%','$75','30%','30%','$0','30%','$5'),
('BCBSRI','BlueSolutions for HSA Direct 6300/12600','PPO','No','National','$0','10%','10%','10%','10%','10%','10%','10%','$10'),
('NHPRI','Neighborhood SELECT 6900/13800 HSA','HMO','No','Rhode Island','$0','0%','0%','0%','0%','0%','0%','0%','$5'),
('NHPRI','Neighborhood SELECT 7100/14200 HSA','HMO','No','Rhode Island','$0','$25','30%','30%','30%','30%','$25','30%','$5'),
]
issuer={'BCBSRI':'Blue Cross & Blue Shield of Rhode Island','NHPRI':'Neighborhood Health Plan of Rhode Island'}
for i,r in enumerate(rows,1):
    code,name,ptype,referral,network,*costs=r
    benefits={label:{'covered':True,'status':'Covered','copay':cost,'coinsurance':'','limit':'','explanation':'','exclusions':''} for label,cost in zip(labels,costs)}
    d['plans'].append({'id':f'RI2026-{i:03d}','baseId':f'RI2026-{i:03d}','state':'RI','issuer':issuer[code],'name':name,'variant':name,'metal':'','type':ptype,'market':'Individual','hsa':'Yes' if 'HSA' in name else 'No','deductible':'','moop':'','sbc':source,'score':len(labels),'benefitLabels':labels,'benefits':benefits,'referral':referral,'network':network})

medicaid=[
('RI-MED-NHPRI-ACCESS','Neighborhood Health Plan of Rhode Island','ACCESS','RIte Care coverage for families, children and pregnant members','https://www.nhpri.org/members/plans-for-medicaid-members/'),
('RI-MED-NHPRI-TRUST','Neighborhood Health Plan of Rhode Island','TRUST','Rhody Health Partners coverage for eligible adults','https://www.nhpri.org/members/plans-for-medicaid-members/'),
('RI-MED-UHC-RITE','UnitedHealthcare Community Plan','RIte Care','Rhode Island Medicaid managed-care benefits','https://www.uhc.com/communityplan/rhode-island/plans'),
('RI-MED-UHC-RHP','UnitedHealthcare Community Plan','Rhody Health Partners','Coverage for eligible adults with disabilities','https://www.uhc.com/communityplan/rhode-island'),
('RI-MED-TUFTS','Tufts Health RITogether','RITogether','Rhode Island Medicaid managed-care benefits','https://staycovered.ri.gov/your-medicaid-benefits/your-medicaid-health-plan'),
]
for key,plan,benefit,value,url in medicaid:
    d['extras'].append({'key':key,'state':'RI','plan':plan,'coverage':'Medicaid','category':'Plan coverage','benefit':benefit,'value':value,'requirements':'Eligibility and covered-service rules depend on the Rhode Island Medicaid program shown on the member card.','how':'Open the official plan page','url':url})

d['meta']['states']=['NH','RI']
d['meta']['rhodeIslandCommercialPlans']=len(rows)
d['meta']['rhodeIslandMedicaidCards']=len(medicaid)
path.write_text(json.dumps(d,separators=(',',':')))
print({'ri_commercial':len(rows),'ri_medicaid':len(medicaid),'total_plans':len(d['plans'])})
