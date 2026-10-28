// Run after: npm install --no-save @microsoft/powerquery-parser@4.0.1
// Syntax validation only: this does not execute Power Query or refresh data.
const fs = require('node:fs');
const path = require('node:path');
const { TaskUtils, DefaultSettings } = require('@microsoft/powerquery-parser');
const root = path.resolve(__dirname, '..');
async function main() {
  const model = JSON.parse(fs.readFileSync(path.join(root, 'powerbi/Wealthsimple.SemanticModel/model.bim'), 'utf8')).model;
  const expressions = [...model.expressions, ...model.tables.flatMap(t => t.partitions.map(p => ({name: t.name, expression: p.source.expression})))];
  for (const filename of fs.readdirSync(path.join(root, 'powerbi/powerquery')).filter(n => n.endsWith('.m'))) {
    expressions.push({name: filename, expression: fs.readFileSync(path.join(root, 'powerbi/powerquery', filename), 'utf8')});
  }
  let failures = 0;
  for (const x of expressions) {
    const result = await TaskUtils.tryLexParse(DefaultSettings, Array.isArray(x.expression) ? x.expression.join('\n') : x.expression);
    console.log(`${x.name}: ${result.resultKind}`);
    if (result.resultKind !== 'Ok') { failures++; console.error(result.error?.innerError || result.error?.message); }
  }
  if (failures) process.exitCode = 1;
}
main().catch(e => { console.error(e.message); process.exitCode = 1; });
