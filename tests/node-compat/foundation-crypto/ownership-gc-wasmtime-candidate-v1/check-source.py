"""Finite source/data/AST only. Never imports a CLI/preflight/oracle/guest."""
from pathlib import Path
import json,hashlib,ast
O=Path(__file__).resolve().parent;checks=[]
def ck(n,v):assert v,n;checks.append(dict(name=n,passed=True))
def h(p):
 d=hashlib.sha256()
 with Path(p).open('rb')as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):d.update(b)
 return d.hexdigest()
v=json.loads((O/'wasmtime-derivations.json').read_bytes())
for row in v['derived']:
 text=(O/row['file']).read_text()
 for d in reversed(row['changes']):assert text.count(d['after'])==1;text=text.replace(d['after'],d['before'])
 ck('exact normal-source mechanism reversal '+row['file'],text==Path(row['donor']['path']).read_text())
g=(O/'guard.mjs').read_text();r=(O/'run.mjs').read_text();p=(O/'protocol.mjs').read_text()
for n,value in [
 ('literal zero-argument WIT validate()', "return ['run','--invoke','validate()',row.path]"in p),
 ('generic one-argument cost invocation not used','invocation('not in p),
 ('real GC component exacttuple','13118152'in p and'52d99f4e95860b686d896c88f39b2fa5734eabeb433f48545ba814b2e45ce5f1'in p),
 ('strict decoder importedunchanged','parseScalarStringOutput,argvAccounting'in p and'cost-wasmtime-transport-candidate-v1/scalar-transport.mjs'in p),
 ('current GC Jco source5abe/v2 required','INDEPENDENT_CRYPTO_OWNER355_GC_RUNTIME_RESULTS_REVIEW_PASSED_V2'in g and'gc-runtime-candidate-v2/checks.mjs'in p),
 ('actual Jco proof before hostprocess', 'jcoModel(jco.data,refs)'in g and r.index('wasmtimePreflight(descriptor(config))')<r.index('runOwnedCommand(')),
 ('full coverage pressureScope fixed',"c.rawPublicStrings===23"in g and"c.fullWrapperPressureRecords===16"in g and"{retained:48,fresh:16,wrapper:16,total:80}"in g),
 ('private exact actualJco wrapper','crypto-owner355-gc-runtime-v2/index.json'in g and"wrapper/raw/001.json"in g),
 ('whole artifacts contracts hashed','equal(jc.artifacts,ac.artifacts)'in g and"jco.rows.filter(r=>equal(r,jcRow)).length===1"in g),
 ('no normal result approval','INDEPENDENT_CRYPTO_OWNER355_NORMAL_RUNTIME_RESULTS_REVIEW_PASSED_V1'not in g),
 ('all inputdescriptor canonical', 'freeze.files.map(descriptor)'in g),
 ('all input real fullread branches','row.bytes>32*1024*1024' in g and'streamHash(row)'in g),
 ('exact stockNode+Wasmtime pins','await streamHash(refs.wasmtime)'in g and'await streamHash(refs.node)'in g),
 ('no hostenvoverride','WASMTIME_'in g and'DYLD_INSERT_LIBRARIES'in g and'PYTHONPATH'in g),
 ('HOME untouched','env.HOME='not in g and'HOME:'not in r and'CODEX_HOME:'not in r),
 ('owned processes directory before launch',r.index("mkdir(join(out.root,'processes')")<r.index('runOwnedCommand(')),
 ('threefresh invocations', 'ordinal<=3'in r and'new Set(sessions.map(s=>s.pid)).size===3'in r),
 ('raw streams+terminal beforedecode',r.index('checkOwnedTerminal(terminal)')<r.index('parseScalarStringOutput({stdoutBytes:bytes,rawDurablyRetained:true})')),
 ('whole decoded string retained beforeJSONassert',r.index("decodedBeforeSemanticAssertions:true")<r.index('const record=JSON.parse(value)')),
 ('entireactual scalar string exact', 'need(value===frame.jcoWrapper.value' in r),
 ('fulltyped schema2 expected', 'checkWholeRecord(record,frame.oracle,frame.jcoWrapper,frame.expectedRecord)'in r and'validateRecord(value,oracle,gcExpected)'in p),
 ('48 fullpressure records source schedule', 'publicGcPressureRequests:48,fullPressureByteRecords:48,actualNativeGcCountObserved:false'in r),
 ('no freshNodeoracle operation', 'nodeOracle('not in r and'nodeOracleRerun:false'in r),
 ('no generatedJS import path', 'await import('not in r and'generatedJsImported:false'in r),
 ('failedsourcefinalaudit', 'finally{try{await frame.recheck();}finally{await out.close();}}'in r),
 ('finite600s16MiB2400parent gates','v.workerTimeoutMs===600000'in g and'v.maxPipeBytes===16777216'in g and'v.externalParentDeadlineSeconds===2400'in g),
]:ck(n,value)
refs=json.loads((O/'references.json').read_bytes());ck('all actual Jco/host phases NULL',all(refs[k]is None for k in ['jcoGcReview','jcoGcContract','jcoOutputIndex','jcoWrapper','nodeOracle','hostPhaseAuthority']))
f=json.loads((O/'input-freeze.json').read_bytes());seen=set();size=0
for row in f['files']:
 s=row['path'];assert s.startswith('/')and'\0'not in s and'\\'not in s and all(x not in ('','.','..')for x in s.split('/')[1:])
 assert s not in seen;seen.add(s);path=Path(s);assert path.stat().st_size==row['bytes']and h(path)==row['sha256'];size+=row['bytes']
ck('completecanonicalsource bytes',True)
read=json.loads((O/'read-boundary-results.json').read_bytes());ck('real descriptorandfullread boundary',read['actualRowsRead']==read['declaredRows']==len(seen)and read['manifestSha256']==h(O/'input-freeze.json'))
result=dict(schemaVersion=1,state='GC_WT_SOURCE_CLOSURE_CHECKS_PASSED_NO_ACTIONS_V1',checks=checks,count=len(checks),inputRows=len(seen),inputBytes=size,sourceOnly=True,wasmtimeCliInvoked=False,preflightOrOracleOrGuestInvoked=False)
(O/'source-check-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(checks=len(checks),rows=len(seen))))
