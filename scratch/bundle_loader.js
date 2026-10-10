const fs=require('fs'),vm=require('vm');
module.exports=function(path){
  let src=fs.readFileSync(path,'utf8');
  src=src.replace("if (document.readyState === 'loading')","window.__D={PLANS,RI_OFFICIAL_SELECTOR_PLANS,COVERAGE_RULES,PRODUCTS,SERVICES,BENEFITS,evaluateCoverageRule,getMarketplacePlan,getProductionSelectorPlans};\n  if (document.readyState === 'loading')");
  const window={};
  const ctx={window,document:{readyState:'loading',addEventListener(){},querySelector(){return null},querySelectorAll(){return []},getElementById(){return null}},localStorage:{getItem(){},setItem(){},removeItem(){}},console,URLSearchParams};
  vm.createContext(ctx); vm.runInContext(src,ctx);
  return window;
};
