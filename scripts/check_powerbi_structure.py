"""Offline source checks; these do not execute M, DAX or Power BI visuals."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]/'powerbi'
model=json.loads((ROOT/'Wealthsimple.SemanticModel/model.bim').read_text())['model']
tables={t['name']:t for t in model['tables']}
for rel in model['relationships']:
 for side in ['from','to']:
  assert rel[side+'Column'] in {c['name'] for c in tables[rel[side+'Table']]['columns']}
visuals=list((ROOT/'Wealthsimple.Report/definition/pages').rglob('visual.json'))
for p in visuals:
 d=json.loads(p.read_text());pos=d['position'];assert pos['x']>=0 and pos['y']>=0
 assert pos['x']+pos['width']<=1600 and pos['y']+pos['height']<=1100
 for role in d['visual'].get('query',{}).get('queryState',{}).values():
  for proj in role['projections']:
   kind,f=next(iter(proj['field'].items()));t=f['Expression']['SourceRef']['Entity']
   assert f['Property'] in {x['name'] for x in tables[t]['measures' if kind=='Measure' else 'columns']},(p,f)
for page in (ROOT/'Wealthsimple.Report/definition/pages').glob('*/page.json'):
 vs=[json.loads(p.read_text())['position'] for p in (page.parent/'visuals').rglob('visual.json')]
 for i,a in enumerate(vs):
  for b in vs[i+1:]:assert not (a['x']<b['x']+b['width'] and b['x']<a['x']+a['width'] and a['y']<b['y']+b['height'] and b['y']<a['y']+a['height'])
assert len(visuals)==105
print('PASS: 105 visual bindings and bounds, no overlaps, relationship endpoints. Desktop execution remains unverified.')
