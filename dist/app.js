let DATA,mode='commercial',currentState='',selectedPlan=null,activeCategory='All',marketView='covered';
const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
const esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const cleanIssuer=x=>x.replace(' from NH Healthy Families','').replace(' Blue Cross and Blue Shield',' Blue Cross Blue Shield');
const planLabel=p=>p.state==='NH'?`${p.name} · ${p.id}`:p.name;
fetch('data.json').then(r=>r.json()).then(d=>{DATA=d;init()}).catch(()=>{$('#lookupForm').innerHTML='<p>Benefit data could not be loaded.</p>'});
function init(){
  $('#stateSelect').addEventListener('change',()=>{currentState=$('#stateSelect').value;setMode(mode)});
  $$('.segmented button').forEach(b=>b.addEventListener('click',()=>setMode(b.dataset.cover)));
  $('#issuerSelect').addEventListener('change',fillPlans);$('#lookupForm').addEventListener('submit',lookup);
  $('#planSelect').addEventListener('change',updatePlanHelp);
  $('#benefitSearch').addEventListener('input',renderMarketplace);$('#openCompare').addEventListener('click',openCompare);
  $('#coveredTab').addEventListener('click',()=>setMarketView('covered'));$('#notCoveredTab').addEventListener('click',()=>setMarketView('not'));
  $('#compareIssuer').addEventListener('change',fillComparePlans);$('#runCompare').addEventListener('click',renderComparison);
  setupReveal();setMode('commercial');
}
function commercialIssuers(){return [...new Set(DATA.plans.filter(p=>p.state===currentState).map(p=>p.issuer))].sort()}
function medicaidPlans(){return [...new Map(DATA.extras.filter(x=>x.coverage==='Medicaid'&&x.state===currentState).map(x=>[x.key,x.plan])).entries()]}
function setMode(next){
  mode=next;selectedPlan=null;$$('.segmented button').forEach(b=>b.classList.toggle('active',b.dataset.cover===mode));
  $('#planHelp').hidden=true;$('#lookupButton').querySelector('span:first-child').textContent='Show me my benefits';
  const issuer=$('#issuerSelect'),plan=$('#planSelect'),lookupButton=$('#lookupButton');issuer.innerHTML='';
  if(!currentState){issuer.add(new Option('Choose your state first',''));issuer.disabled=true;plan.innerHTML='';plan.add(new Option('Choose your state first',''));plan.disabled=true;lookupButton.disabled=true;$('#planField').hidden=mode!=='commercial';$('#results').hidden=true;return}
  issuer.disabled=false;plan.disabled=false;lookupButton.disabled=false;
  if(mode==='commercial'){commercialIssuers().forEach(x=>issuer.add(new Option(cleanIssuer(x),x)));issuer.value=commercialIssuers().find(x=>x.includes('Anthem'))||commercialIssuers()[0];$('#planField').hidden=false;fillPlans()}
  else{medicaidPlans().forEach(([k,n])=>issuer.add(new Option(n,k)));$('#planField').hidden=true}
  $('#results').hidden=true;
}
function fillPlans(){
  const issuer=$('#issuerSelect').value,sel=$('#planSelect');sel.innerHTML='';
  const plans=DATA.plans.filter(p=>p.state===currentState&&p.issuer===issuer).sort((a,b)=>a.name.localeCompare(b.name)||a.id.localeCompare(b.id));
  plans.forEach(p=>sel.add(new Option(planLabel(p),p.id)));
  sel.add(new Option('I’m not sure / My plan isn’t listed','__unsure__'));
  updatePlanHelp();
}
function updatePlanHelp(){
  const unsure=mode==='commercial'&&$('#planSelect').value==='__unsure__';
  $('#planHelp').hidden=!unsure;
  $('#lookupButton').querySelector('span:first-child').textContent=unsure?'Help me find my plan':'Show me my benefits';
}
function lookup(e){
  e.preventDefault();
  if(mode==='commercial'&&$('#planSelect').value==='__unsure__'){$('#results').hidden=true;$('#planHelp').scrollIntoView({behavior:'smooth',block:'center'});return}
  selectedPlan=mode==='commercial'?DATA.plans.find(p=>p.id===$('#planSelect').value):{id:$('#issuerSelect').value,name:$('#issuerSelect').selectedOptions[0].text,issuer:$('#issuerSelect').selectedOptions[0].text};
  activeCategory='All';marketView='covered';$('#benefitSearch').value='';$('#results').hidden=false;$('#comparePanel').hidden=true;setMarketView('covered');
  $('.compare-invite').hidden=mode!=='commercial';
  renderHeader();renderSnapshot();renderCategories();renderMarketplace();requestAnimationFrame(()=>{observeNew();$('#results').scrollIntoView({behavior:'smooth',block:'start'})});
}
function selectedListings(){
  if(mode==='medicaid')return DATA.extras.filter(x=>x.key===selectedPlan.id);
  const labels=selectedPlan.benefitLabels||DATA.benefitLabels;
  const core=labels.filter(l=>selectedPlan.benefits[l]?.covered).map(l=>({plan:selectedPlan.name,coverage:'Marketplace',category:categoryFor(l),benefit:l,value:costText(selectedPlan.benefits[l]),requirements:'Confirm network, authorization, exclusions and exact cost sharing in the official plan document.',url:selectedPlan.sbc}));
  return[...core,...commercialExtrasFor(selectedPlan)];
}
function commercialExtrasFor(p){return DATA.extras.filter(x=>x.state===p.state&&x.coverage==='Commercial'&&(p.issuer.startsWith('Ambetter')||p.name.includes(x.plan)||p.issuer.includes(x.plan)))}
function renderHeader(){
  const xs=selectedListings(),state=DATA.meta.stateNames?.[currentState]||currentState,issuer=mode==='commercial'?cleanIssuer(selectedPlan.issuer):state+' Medicaid';
  $('#resultHeader').innerHTML=`<div><span class="eyebrow">${esc(state)} · Your selected card</span><h2>${esc(selectedPlan.name)}</h2><p>${esc(issuer)}</p><div class="selected-badges"><span class="pill">${mode==='commercial'?'Marketplace plan':'Managed Medicaid'}</span><span class="pill">Official sources linked below</span><span class="pill">Exact plan rules still apply</span></div></div><div class="card-score"><strong>${xs.length}</strong><span>publicly verified<br>listings found</span></div>`;
}
function renderSnapshot(){
  const listings=selectedListings(),core=mode==='commercial'?(selectedPlan.benefitLabels||DATA.benefitLabels).map(label=>({label,x:selectedPlan.benefits[label]||{}})):[];
  const group=(label,test,filter)=>{const coreHits=core.filter(({label:l,x})=>x.covered&&test(l)),extraHits=listings.filter(x=>x.coverage!=='Marketplace'&&test(`${x.category} ${x.benefit}`));const total=coreHits.length+extraHits.length;return{label,category:filter,state:total?(extraHits.length&&!coreHits.length?'extra':'covered'):'not',detail:total?`${total} verified ${total===1?'listing':'listings'} found for this area`:'No coverage was found in this plan’s public data'}};
  const medicalTest=s=>/preventive|doctor|primary|specialist|urgent|emergency|hospital|mental|therapy|rehabilitation|pharmacy|prescription|bariatric|chiropractic|acupuncture|hearing|nutrition/i.test(s);
  const extraCount=listings.filter(x=>x.coverage!=='Marketplace').length;
  const rows=[group('Medical care',medicalTest,'All'),group('Dental',s=>/dental/i.test(s),'Dental'),group('Vision',s=>/eye|vision/i.test(s),'Vision'),{label:'Everyday extras',category:'All',state:extraCount?'extra':'not',detail:extraCount?`${extraCount} verified extra ${extraCount===1?'program':'programs'} found`:'No extra programs were verified for this selection'}];
  $('.snapshot-help').textContent='Select a category to jump into the detailed marketplace. Coverage and eligibility rules still depend on the exact plan.';
  $('#snapshotChart').innerHTML=rows.map((x,i)=>`<button class="snapshot-row ${x.state}" type="button" data-cat="${esc(x.category)}" title="${esc(x.label)}: ${esc(x.detail)}" aria-label="${esc(x.label)}. ${esc(x.state==='extra'?'Extra program':x.state==='covered'?'Included':'Not found')}. ${esc(x.detail)}"><span class="snapshot-label">${esc(x.label)}</span><span class="snapshot-track"><i style="transition-delay:${Math.min(i,9)*45}ms"></i></span><span class="snapshot-status">${x.state==='extra'?'Extras':x.state==='covered'?'Included':'Not found'}</span><span class="snapshot-tip">${esc(x.detail)}</span></button>`).join('');
  $$('#snapshotChart .snapshot-row').forEach(b=>b.addEventListener('click',()=>{activeCategory=b.dataset.cat;renderCategories();renderMarketplace();$('.benefits-section').scrollIntoView({behavior:'smooth',block:'start'})}));
}
function setMarketView(view){
  marketView=view;activeCategory='All';
  $$('.market-tab').forEach(b=>{const on=(view==='covered'&&b.id==='coveredTab')||(view==='not'&&b.id==='notCoveredTab');b.classList.toggle('active',on);b.setAttribute('aria-selected',String(on))});
  $('#benefitSearch').placeholder=view==='covered'?'Search dental, rides, vitamins, gym…':'Search items not listed as covered…';
  renderCategories();renderMarketplace();
}
function notCoveredListings(){
  const available=selectedListings(),source=mode==='commercial'?selectedPlan.sbc:(available[0]?.url||'#');
  const rows=mode==='commercial'?(selectedPlan.benefitLabels||DATA.benefitLabels).filter(label=>!selectedPlan.benefits[label]?.covered).map(label=>({plan:selectedPlan.name,coverage:'Not listed',category:categoryFor(label),benefit:label,value:'Not shown as covered in this plan’s public benefit data.',requirements:'Do not assume this service is paid for. Check the official plan document or call the number on your card before scheduling or buying.',url:source})):[];
  const misconceptions=[['Gym membership','Fitness'],['Over-the-counter vitamins','Pharmacy'],['Non-emergency transportation','Transportation'],['Routine adult dental','Dental'],['Routine adult vision','Vision'],['Cosmetic procedures','Medical care']];
  misconceptions.forEach(([benefit,category])=>{const words=benefit.toLowerCase().split(/\W+/).filter(w=>w.length>3),found=available.some(x=>words.some(w=>`${x.category} ${x.benefit}`.toLowerCase().includes(w))),already=rows.some(x=>x.benefit.toLowerCase().includes(benefit.replace('Routine adult ','').toLowerCase()));if(!found&&!already)rows.push({plan:selectedPlan.name,coverage:'Not verified',category,benefit,value:'No verified listing for this benefit was found for your selected card.',requirements:'This does not always mean the service is excluded. It means you should confirm with the insurer before relying on reimbursement or a discount.',url:source})});
  return rows;
}
function categoryFor(x){if(/eye/i.test(x))return'Vision';if(/dental/i.test(x))return'Dental';if(/weight|nutrition|bariatric/i.test(x))return'Nutrition';if(/acupuncture|chiropractic/i.test(x))return'Fitness';if(/hearing/i.test(x))return'Hearing';if(/primary|specialist/i.test(x))return'Doctor visits';if(/urgent|emergency|hospital/i.test(x))return'Urgent & hospital';if(/mental/i.test(x))return'Mental health';if(/rehabilitation/i.test(x))return'Therapy';if(/prescription/i.test(x))return'Pharmacy';return'Preventive'}
function costText(x){return[x.copay,x.coinsurance,x.limit&&`Limit: ${x.limit}`].filter(Boolean).join(' · ')||'Covered; exact member cost is in the official plan document'}
function renderCategories(){
  const source=marketView==='not'?notCoveredListings():selectedListings();
  const cats=['All',...new Set(source.map(x=>x.category))];
  $('#categoryFilters').innerHTML=cats.map(c=>`<button class="chip ${c===activeCategory?'active':''}" data-cat="${esc(c)}">${esc(c)}</button>`).join('');
  $$('#categoryFilters .chip').forEach(b=>b.addEventListener('click',()=>{activeCategory=b.dataset.cat;renderCategories();renderMarketplace()}));
}
function renderMarketplace(){
  if(!selectedPlan)return;const q=$('#benefitSearch').value.trim().toLowerCase();let xs=marketView==='not'?notCoveredListings():selectedListings();
  if(activeCategory!=='All')xs=xs.filter(x=>x.category===activeCategory);
  if(q)xs=xs.filter(x=>[x.category,x.benefit,x.value,x.requirements].join(' ').toLowerCase().includes(q));
  const empty=marketView==='not'?'No items listed as not covered match this search.':'No publicly verified benefits for this card match that search.';
  $('#benefitGrid').innerHTML=xs.length?xs.map((x,i)=>`<article class="benefit-card ${marketView==='not'?'not-covered-card':''}" style="transition-delay:${Math.min(i%6,5)*70}ms"><div class="benefit-top"><span class="coverage-badge">${esc(x.category)}</span><small>${esc(x.evidence||x.coverage)}</small></div><h3>${esc(x.benefit)}</h3><div class="plan-name">${esc(x.plan)}</div><p class="value">${esc(x.value)}</p><div class="requirement"><b>${marketView==='not'?'Before you pay:':'Before you use it:'}</b> ${esc(x.requirements)}</div><a class="card-link" href="${esc(x.url)}" target="_blank" rel="noreferrer">Open official source ↗</a></article>`).join(''):`<div class="empty">${esc(empty)}</div>`;
  requestAnimationFrame(()=>$$('.benefit-card').forEach((x,i)=>setTimeout(()=>x.classList.add('visible'),i*55)));
}
function openCompare(){
  $('#comparePanel').hidden=false;const sel=$('#compareIssuer');sel.innerHTML='';
  if(mode==='medicaid'){$('#comparison').innerHTML='<div class="empty">Standardized side-by-side comparison is currently available for Marketplace cards.</div>';$('#comparePanel').scrollIntoView({behavior:'smooth'});return}
  commercialIssuers().forEach(x=>sel.add(new Option(cleanIssuer(x),x)));sel.value=commercialIssuers().find(x=>x!==selectedPlan.issuer)||commercialIssuers()[0];fillComparePlans();
  $('#comparison').innerHTML='<div class="empty">Choose the other plan, then press “Show comparison.”</div>';$('#comparePanel').scrollIntoView({behavior:'smooth',block:'start'});
}
function fillComparePlans(){
  const issuer=$('#compareIssuer').value,sel=$('#comparePlan');sel.innerHTML='';
  DATA.plans.filter(p=>p.state===currentState&&p.issuer===issuer).sort((a,b)=>a.name.localeCompare(b.name)||a.id.localeCompare(b.id)).forEach(p=>sel.add(new Option(planLabel(p),p.id)));
}
function benefitCell(p,label){
  const x=p.benefits[label]||{covered:false},d=[x.copay,x.coinsurance,x.limit&&`Limit: ${x.limit}`].filter(Boolean).join(' · ');
  return`<div><span class="status ${x.covered?'yes':'no'}">${x.covered?'✓ Covered':'× Not covered'}</span>${d?`<div class="detail">${esc(d)}</div>`:''}</div>`;
}
function renderComparison(){
  if(mode!=='commercial'){return}const other=DATA.plans.find(p=>p.id===$('#comparePlan').value);if(!other)return;
  const labels=[...new Set([...(selectedPlan.benefitLabels||DATA.benefitLabels),...(other.benefitLabels||DATA.benefitLabels),...commercialExtrasFor(selectedPlan).map(x=>x.benefit),...commercialExtrasFor(other).map(x=>x.benefit)])];
  const datum=(p,label)=>{const core=p.benefits[label];if(core)return{covered:!!core.covered,extra:false,detail:core.covered?costText(core):'Not covered'};const extra=commercialExtrasFor(p).find(x=>x.benefit===label);return extra?{covered:true,extra:true,detail:extra.value}:{covered:false,extra:false,detail:'Not listed for this plan'}};
  const slot=(p,label,side)=>{const x=datum(p,label),state=x.covered?(x.extra?'extra':'covered'):'not';return`<div class="compare-chart-slot ${state}" tabindex="0" title="${esc(p.name)} — ${esc(label)}: ${esc(x.detail)}"><span class="compare-bar-track"><i></i></span><b>${x.extra?'Extra':x.covered?'Covered':'Not covered'}</b><small>${esc(x.detail)}</small><span class="compare-hover">${esc(side)}: ${esc(x.detail)}</span></div>`};
  $('#comparison').innerHTML=`<div class="comparison-chart"><div class="comparison-chart-head"><div><span class="eyebrow">Visual comparison</span><h3>Benefits side by side</h3></div><div class="compare-chart-legend"><span><i class="your-swatch"></i>Your card</span><span><i class="other-swatch"></i>Other plan</span></div></div><div class="compare-plan-names"><div>Benefit</div><div><small>Your card</small><strong>${esc(selectedPlan.name)}</strong></div><div><small>Other plan</small><strong>${esc(other.name)}</strong></div></div>${labels.map(l=>`<div class="compare-chart-row"><div class="compare-benefit-label">${esc(l)}</div>${slot(selectedPlan,l,'Your card')}${slot(other,l,'Other plan')}</div>`).join('')}</div>`;
}
function setupReveal(){
  window.revealObserver=new IntersectionObserver(entries=>entries.forEach(e=>{if(e.isIntersecting){e.target.classList.add('visible');revealObserver.unobserve(e.target)}}),{threshold:.12});
  $$('.reveal-group').forEach(x=>revealObserver.observe(x));
}
function observeNew(){$$('#results .reveal-group').forEach(x=>revealObserver.observe(x))}
