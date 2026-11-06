"""Source/data assertions only. Never imports operational code or executes probes."""
import ast, hashlib, json, re
from pathlib import Path
HERE=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text())
def row(p):
    p=Path(p);h=hashlib.sha256();n=0
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b);n+=len(b)
    return dict(path=str(p),sha256=h.hexdigest(),bytes=n)
def verify(ref):assert row(ref['path'])==ref,ref['path']
p=read(HERE/'plan.json');checked=[]
for key in ['node','wasmtime','monitor','engine','nativeMetadata','adapter','nodeOracleSource','probeEntry']:
    verify(p[key]);checked.append(p[key])
families=[]
for ref in p['sourceFamilies']:
    verify(ref);root=Path(ref['path']).parent;files=read(ref['path'])['files'];names=[r['path']for r in files]
    assert len(names)==len(set(names));assert set(names)|{'index.json'}=={x.relative_to(root).as_posix()for x in root.rglob('*')if x.is_file()};assert not any(x.is_symlink()for x in root.rglob('*'))
    for r in files:
        rel=Path(r['path']);assert not rel.is_absolute()and '..'not in rel.parts;verify(dict(r,path=str(root/rel)))
    families.append(dict(index=ref,members=len(files)))
source=(HERE/'collect.mjs').read_text();derivation=read(HERE/'helper-derivation.json');verify(derivation['donor']);donor=Path(derivation['donor']['path']).read_text();fragment=(HERE/'helpers-fragment.txt').read_text()
assert hashlib.sha256(fragment.encode()).hexdigest()==derivation['fragmentSha256']
for name in derivation['functions']:
    line=next(x for x in fragment.splitlines()if x.startswith('async function '+name+'('));assert line in source.splitlines()and line in donor.splitlines()
c=read(HERE/'case-contract.json');verify(c['source']);raw=Path(c['source']['path']).read_text();literal=raw.split('export const cases=Object.freeze(',1)[1].split('\n]);',1)[0]+ '\n]'
literal=re.sub(r'(?<=[{,])([a-zA-Z]+):',r"'\1':",literal)
assert ast.literal_eval(literal)==c['cases'];assert len(c['cases'])==12
assert len(p['expectedPropertyGapCases'])==7 and set(p['expectedPropertyGapCases'])<={x['id']for x in c['cases']}
assert source.index('allThreeCaptureAttemptsComplete=true')<source.index('const oracleBytes=')<source.index('result.comparisons=[]')
assert "'--dir'"not in source and "--preopen"not in source
assert "'32'"in source and "'60s'"in source and '180,authority' in (HERE/'run-owned.py').read_text()
ast.parse((HERE/'run-owned.py').read_text());ast.parse(Path(__file__).read_text())
assert all(p[k]is None for k in ['actualRootAuthority','actualComponent','actualNodeOracle','actualResults'])
a=read(HERE/'root-authority-template.json');assert a['runId']is None and a['sourceIndex']is None and a['nodeOracleTerminal']is None
print(json.dumps(dict(state='REGEXP_COLLECTOR_SOURCE_DATA_CHECKS_PASSED_V1',directPins=checked,families=families,caseCount=12,expectedPropertyGapCases=7,derivedHelpers=6,pythonAstFiles=2,operationalActionsInvoked=False),indent=2))
