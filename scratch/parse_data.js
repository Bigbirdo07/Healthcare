const fs = require('fs');

const jsContent = fs.readFileSync('dist/marketplace/marketplace.js', 'utf8');

function extractVar(varName) {
  const startStr = `const ${varName} = [`;
  const idx = jsContent.indexOf(startStr);
  if (idx === -1) return [];
  const start = idx + startStr.length - 1;
  let bracketCount = 0;
  let end = start;
  for (let i = start; i < jsContent.length; i++) {
    if (jsContent[i] === '[') bracketCount++;
    else if (jsContent[i] === ']') {
      bracketCount--;
      if (bracketCount === 0) {
        end = i + 1;
        break;
      }
    }
  }
  const code = jsContent.substring(start, end);
  return eval(code);
}

const PRODUCTS = extractVar('PRODUCTS');
const SERVICES = extractVar('SERVICES');
const BENEFITS = extractVar('BENEFITS');
const COVERAGE_RULES = extractVar('COVERAGE_RULES');
const PLANS = extractVar('PLANS');

console.log('PRODUCTS count:', PRODUCTS.length);
console.log('SERVICES count:', SERVICES.length);
console.log('BENEFITS count:', BENEFITS.length);
console.log('COVERAGE_RULES count:', COVERAGE_RULES.length);
console.log('PLANS count:', PLANS.length);

fs.writeFileSync('scratch/marketplace_dump.json', JSON.stringify({ PRODUCTS, SERVICES, BENEFITS, COVERAGE_RULES, PLANS }, null, 2), 'utf8');
