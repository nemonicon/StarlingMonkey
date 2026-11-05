"""Own SOURCE assembly/checks only. Never invokes admission/monitor/host/guest."""
from pathlib import Path
import ast,difflib,hashlib,json,os,re,stat,subprocess,time
P=Path(__file__).resolve().parent;K=P.parent;R=K/'ownership-secret-runtime-candidate-v3';rows={};checks=0
def need(x,label):
 global checks
 checks+=1
 assert x,label
def describe(p):
 p=Path(p);a=p.stat();need(stat.S_ISREG(p.lstat().st_mode),'ordinary source input');h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 z=p.stat();need((a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns),'stable source DATA');return dict(path=str(p),sha256=h.hexdigest(),bytes=a.st_size)
def load(p):return json.loads(Path(p).read_bytes())
def save(n,v):
 q=P/n;assert not q.exists(),q;q.write_text(json.dumps(v,indent=2)+'\n')
def add(r):
 expected={k:r[k]for k in ['path','sha256','bytes']};need(expected==describe(r['path']),'actual external source input')
 if r['path']in rows:need(rows[r['path']]==expected,'consistent repeated source row')
 else:rows[r['path']]=expected
families={}
def family(r):
 if r['path']in families:need(families[r['path']]==r,'same family descriptor');return
 add(r);families[r['path']]=r;root=Path(r['path']).parent;d=load(r['path']);names={'index.json'}
 for x in d['files']:
  n=x['path'];need(not n.startswith('/')and n not in names and all(v not in('','.','..')for v in n.split('/')),'unique confined source family row');names.add(n);add(dict(x,path=str(root/n)))
 need(not any(q.is_symlink()for q in root.rglob('*'))and{q.relative_to(root).as_posix()for q in root.rglob('*')if q.is_file()}==names,'complete source/proof family membership')
refs=load(P/'references.json');base=load(R/'source-inputs.json')
for r in base['files']:add(r)
for r in base['families']:family(r)
for d in [refs['runtimeSourceIndex'],refs['runtimeSourceReview']['index'],refs['actualRuntimeReview']['index'],refs['actualArtifactReview']['index']]:family(d)
actual=load(refs['actualRuntimeReview']['result']['path']);contract=load(refs['actualRuntimeContract']['path']);need(actual['state']==contract['requiredReviewState']=='INDEPENDENT_CRYPTO_OWNER355_SECRET_NORMAL_RUNTIME_RESULTS_REVIEW_PASSED_V1'and actual['verifiedPassed']is True,'genuine completed Jco prerequisite')
for k,v in contract['requiredFixedValues'].items():need(actual[k]==v,'whole actual runtime fixed contract')
for k,v in contract['requiredExactDescriptors'].items():need(actual[k]==v,'whole actual runtime exact descriptors')
need(actual['coverage']==contract['requiredCoverage']and actual['artifacts']==contract['artifacts']==refs['artifacts'],'whole full actual runtime coverage/artifact map')
for r in load(actual['inputHashes']['path'])['files']:add(r)
for r in [refs['node'],refs['wasmtime'],refs['pythonExecutable']]:add(r)
# Full exact ordinary-host donor family is provenance DATA only, not imported guard.
donor_family=K/'ownership-wasmtime-candidate-v1/index.json';donor_root=donor_family.parent;donor_names=[]
for q in sorted(donor_root.rglob('*')):
 need(not q.is_symlink(),'ordinary historical donor DATA tree')
 if q.is_file():add(describe(q));donor_names.append(q.relative_to(donor_root).as_posix())
need('source-receipt.json'in donor_names,'explicit historical unindexed receipt DATA')
base={**base,'historicalDonorTrees':[*base['historicalDonorTrees'],dict(root=str(donor_root),names=donor_names)]}
donors={'entry.mjs':R/'entry.mjs','external.py':R/'external.py','run.mjs':K/'ownership-wasmtime-candidate-v1/run.mjs','protocol.mjs':K/'ownership-wasmtime-candidate-v1/protocol.mjs','checks.mjs':R/'checks.mjs','oracle-check.mjs':R/'oracle.mjs'};deriv=[]
for name,donor in donors.items():
 add(describe(donor));before=donor.read_bytes();after=(P/name).read_bytes();a=before.decode();b=after.decode();edits=[]
 for op,i,j,k,l in difflib.SequenceMatcher(None,a,b,autojunk=False).get_opcodes():
  if op!='equal':edits.append(dict(beforeOffset=len(a[:i].encode()),afterOffset=len(b[:k].encode()),before=a[i:j],after=b[k:l]))
 f=before;v=after
 for e in reversed(edits):
  x=e['before'].encode();y=e['after'].encode();i=e['beforeOffset'];need(f[i:i+len(x)]==x,'exact donor edit slice');f=f[:i]+y+f[i+len(x):]
 for e in reversed(edits):
  x=e['before'].encode();y=e['after'].encode();i=e['afterOffset'];need(v[i:i+len(y)]==y,'exact successor edit slice');v=v[:i]+x+v[i+len(y):]
 need(f==after and v==before,'whole exact forward/reverse derivation');deriv.append(dict(output=name,donor=describe(donor),after=describe(P/name),edits=edits,byteIdentical=before==after))
save('derivations.json',dict(schemaVersion=1,files=deriv,originalNativeGuestArtifactsUnchanged=True,metadataOrStateProjected=False))
# Actual static and single dynamic module edges, without importing an owner API.
nodes={};edges=[]
def module(p):
 p=Path(p).resolve()
 if str(p)in nodes:return
 nodes[str(p)]=describe(p)
 if p.parent!=P:add(nodes[str(p)])
 for line in p.read_text().splitlines():
  if not line.startswith(('import ','export '))or'from 'not in line:continue
  m=re.search(r"from ['\"]([^'\"]+)['\"]",line);need(m is not None,'recognized static module syntax')
  target=m.group(1)
  if target.startswith('node:'):continue
  need(target.startswith('.'),'no unreviewed package/global loader');q=(p.parent/target).resolve();edges.append(dict(caller=str(p),kind='static',specifier=target,target=str(q)));module(q)
for n in ['entry.mjs','run.mjs','protocol.mjs','checks.mjs','oracle-check.mjs']:module(P/n)
entry=(P/'entry.mjs').read_text();need("await import(pathToFileURL(join(HERE,'run.mjs')))"in entry,'exact only dynamic body loader');edges.append(dict(caller=str(P/'entry.mjs'),kind='dynamic',expression="await import(pathToFileURL(join(HERE,'run.mjs')))",target=str(P/'run.mjs')))
need('retainedSecretBootstrapPreflight('not in entry and 'loadPackaging('not in entry and 'nodeOracle('not in entry,'host gate never reruns old APIs/oracle/package actions')
external=(P/'external.py').read_text();tree=ast.parse(external);need("OWN=REPO/'tests/node-compat/foundation-crypto/ownership-secret-host-candidate-v1'"in external and 'Path(__file__).resolve().parent==OWN'in external,'actual current OWN literal/context; no namespace replacement')
need("OUTPUT=Path('"+refs['outputRoot']+"')"in external and "OUT=Path('"+refs['externalOutputRoot']+"')"in external,'actual fresh output constants')
need(external.index('recheck()\n        for path')<external.index("monitor=load_actual"),'all source/proof/Root checks before only custom monitor import')
need('finally:recheck()'in external and 'await frame.recheck();'in entry,'initial/final/failure read guards')
for n in ['outputRoot','externalOutputRoot']:need(not Path(refs[n]).exists(),'future operational root still absent')
save('module-closure.json',dict(schemaVersion=1,modules=list(nodes.values()),edges=edges,pythonCustomImport=dict(caller=describe(P/'external.py'),target=refs['monitorEntry'],loader='load_actual after full preimport authentication'),oldOwnerHelperOrGeneratedGuestImported=False))
# All external rows have measured sizes and current modes; own family covers own files.
save('source-inputs.json',dict(schemaVersion=1,role='Complete original secret355/runtime/actual-Jco/native/frozen/physical-package Source protection',files=[rows[k]for k in sorted(rows)],modeRows=[dict(file=rows[k],mode=stat.S_IMODE(Path(k).stat().st_mode))for k in sorted(rows)],families=list(families.values()),historicalDonorTrees=base['historicalDonorTrees'],normalSourceAndFrozenRolesUnchanged=True))
# Source-only parser and pure tests. No runSecretHost/authenticate/monitor/API action.
node=refs['node'];need(describe(node['path'])==node,'pinned Node22 source test executable before use');terminals=[]
for name,args in [('test-pure',[str(P/'test-pure.mjs')]),*[(n+'.syntax',['--check',str(P/n)])for n in ['entry.mjs','run.mjs','protocol.mjs','checks.mjs','oracle-check.mjs','test-pure.mjs']]]:
 t=time.monotonic();cmd=[node['path'],*args];v=subprocess.run(cmd,cwd=P,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=60);elapsed=time.monotonic()-t
 (P/(name+'.stdout.log')).write_bytes(v.stdout);(P/(name+'.stderr.log')).write_bytes(v.stderr);terminal=dict(schemaVersion=1,argv=cmd,executable=node,rawExitCode=v.returncode,stdout=describe(P/(name+'.stdout.log')),stderr=describe(P/(name+'.stderr.log')),operationalSeconds=elapsed,sourceOnly=True,pureDefinitionsOnly=name=='test-pure',syntaxOnly=name!='test-pure',runSecretHostOrMonitorOrWasmtimeOrGuestOrOracleInvoked=False);save(name+'.terminal.json',terminal);terminals.append(terminal);need(v.returncode==0 and v.stderr==b'','genuine finite pure/grammar check')
pure=json.loads((P/'test-pure.stdout.log').read_bytes());need(pure['passed']is True and pure['runSecretHostInvoked']is False,'all source-coupled pure cases passed')
# Pure actual Python root_model plus actual literal OWN/OUTPUT/OUT assignments.
selected=[n for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom))or isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id in['REPO','OWN','OUTPUT','OUT']for t in n.targets)or isinstance(n,ast.FunctionDef)and n.name=='root_model'];ns={'__name__':'source_pure_model_only'};exec(compile(ast.Module(body=selected,type_ignores=[]),str(P/'external.py'),'exec'),ns);need(ns['OWN']==P and str(ns['OUTPUT'])==refs['outputRoot']and str(ns['OUT'])==refs['externalOutputRoot'],'actual Python module constants, no injected OWN')
root=load(P/'future-root-authority.template.json');own=dict(path=str(P/'index.json'),sha256='0'*64,bytes=1);root={**root,'sourceIndex':own,'entry':describe(P/'entry.mjs'),'externalController':describe(P/'external.py')};ns['root_model'](root,own,refs);python_cases=1
for k,v in [('wasmtimeValidateAllowed',False),('freshProcesses',2),('guardedPrototypeCase3Allowed',False),('fullMetadataFields',80),('nodeOracleAllowed',True),('operationalAdmission',True),('actualRuntimeReview',None),('outputRoot','/tmp/wrong')]:
 try:ns['root_model']({**root,k:v},own,refs)
 except(AssertionError,KeyError):python_cases+=1
 else:raise AssertionError('pure Python authority mutation accepted')
# Rehash every external source input after all preparation checks.
for r in rows.values():need(describe(r['path'])==r,'final actual source/proof/native/guest protection')
source_result=dict(schemaVersion=1,state='SECRET355_STOCK_WASMTIME_HOST_SOURCE_PREPARED_V1',sourceOnly=True,sourceIndependentReview=None,rootAuthority=None,actualHostResults=None,actualRuntimeReview=refs['actualRuntimeReview'],actualRuntimeContract=refs['actualRuntimeContract'],component=refs['artifacts']['component'],engine=refs['engine'],metadata=refs['metadata'],nativeSourceFiles=355,externalEmbeddingSources=3,rawMetadataFields=75,selectedWholeManifests=11,allFourGuardedCasesRequired=True,freshFutureWasmtimeProcesses=3,declaredInputs=len(rows),declaredInputBytes=sum(r['bytes']for r in rows.values()),protectedFamilies=len(families),moduleCount=len(nodes),moduleEdges=len(edges),derivationFiles=len(deriv),reversibleEdits=sum(len(r['edits'])for r in deriv),readHashChecks=checks,pureNodeCases=pure['pureCases'],purePythonAuthorityCases=python_cases,actualPinnedNodeGrammarChecks=6,syntaxCheckerUsed=True,inertOwnEntryImportedForPureTests=True,ownerActionsInvoked=False,hostActionsInvoked=False,runtimeActionsInvoked=False,wasmtimeExecuted=False,engineOrKeyGuestOrOracleActionsInvoked=False,currentJcoWasmtimeAllowedRemainsFalse=True,metadataOrGlobalContextProjected=False,operationalAdmission=False,runtimeAcceptanceClaim=False)
save('source-check-results.json',source_result)
# README and final results are written after all checks to keep WIP truthful.
(P/'README.md').write_text('Secret355 guarded stock-Wasmtime host gate — SOURCE only\n\nConcrete dormant original-context Node entry/body and Python0af-owned parent caller. Actual e895/240c/10899 independent Jco DATA proof is bound; c067 component/901 engine and raw75-field355+3/11 native frame remain unchanged. All23/20/45 Jco observations are prerequisites.\n\nFuture schedule:3fresh stock-Wasmtime42 validate() calls, wholeWAVE strings exactly equal actualJco wrapper and Node oracle, all4guarded cases including case3. Each expects4records/2imports/11sign attempts/10verify attempts/9fulltags; totals12/6/33/30/27,15true12false. No fresh oracle, generatedJS import, oldhelper/oneshot/retainedAPI replay, build/freezer/package action, GC/pressure/OOM/fault/reset/oldunsafe artifact. Separate host Root and Source peer are unissuedNULL; existing JcoRoot.wasmtimeAllowed:false remains unchanged.\n\nAll external inputs, source/proof families, modes, exact4934+22 physical package and actualJco whole output inventory are authenticated before the only dynamic body/monitor imports and again finally, including failed paths. Genuine durable-host collector writes complete raw streams and terminal before parser/semantic assertions; all unexpected returns/errors/overflow refuse. Output headroom2GiB is a boundary guard; worker deadline600000ms/16MiB pipes and external2400s are operational bounds. No same-worker timeout is claimed.\n\nHistorical41-field frame/current readonly counters remain DATA and cannot authorize this host phase. No metadata/path/global/state projection or module-selection355→9 cast. The source tests use an inert own entry and pure guards/protocol plus parser-only Node checks; no runSecretHost/authenticate/API, collector, monitor, Wasmtime, engine, guest/key or oracle producer ran.\n\nFailure evidence guarantees only files actually returned/registered/persisted by the genuine collector; writer/launch failures can leave partial raw files. No blanket all-partials-retained claim. Source final checks can also fail; those failures refuse completion. No operational/performance/security/free/wipe/isolated-root/request-reuse/full-algorithm/adoption claim follows.\n')
save('results.json',source_result)
save('source-receipt.json',dict(schemaVersion=1,state='SEALED_SECRET355_STOCK_WASMTIME_HOST_SOURCE_CANDIDATE_V1',result=describe(P/'results.json'),sourceChecks=describe(P/'source-check-results.json'),actualRuntimeReview=refs['actualRuntimeReview'],rootAuthority=None,sourceIndependentReview=None,actualHostResults=None,allProducerArtifactsPreserved=True,operationalAdmission=False))
members=[]
for q in sorted(P.rglob('*')):
 if q.is_file():r=describe(q);members.append(dict(r,path=q.relative_to(P).as_posix()))
save('index.json',dict(schemaVersion=1,files=members))
for n in ['index.json','results.json','source-receipt.json']:print(json.dumps(describe(P/n)))
print(json.dumps(dict(sealed=True,members=len(members),checks=checks,inputs=len(rows),pureNodeCases=pure['pureCases'],pythonCases=python_cases,grammar=6,operationalActions=False)))
