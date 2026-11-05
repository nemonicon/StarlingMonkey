"""Independent first stock-Wasmtime render DATA audit. No target or helper execution."""
from pathlib import Path
import hashlib,json,os,stat
P=Path(__file__).resolve().parent;S=P.parent;checks=0;seen={};identities={};copies=[]
def need(x,label):
 global checks
 checks+=1
 assert x,label
def ident(p):
 st=p.lstat();need(stat.S_ISREG(st.st_mode),'regular actual input');return(st.st_dev,st.st_ino,st.st_size,st.st_mtime_ns,st.st_ctime_ns)
def row(p,expected=None):
 p=Path(p);a=ident(p)
 if str(p)in seen:
  r=seen[str(p)];need(identities[str(p)]==a,'input identity unchanged')
  if expected is not None:need(r==expected,'repeated exact descriptor')
  return r
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 r=dict(path=str(p),sha256=h.hexdigest(),bytes=a[2]);need(a==ident(p),'stable streamed input hash')
 if expected is not None:need(r==expected,'exact authentic input descriptor')
 seen[str(p)]=r;identities[str(p)]=a;return r
def read(p,expected=None):row(p,expected);return json.loads(Path(p).read_bytes())
def typed(a,b):
 if type(a)is not type(b):return False
 if isinstance(a,dict):return a.keys()==b.keys()and all(typed(a[k],b[k])for k in a)
 if isinstance(a,list):return len(a)==len(b)and all(typed(x,y)for x,y in zip(a,b))
 return a==b
def family(d):
 v=read(d['path'],d);base=Path(d['path']).parent;names={'index.json'}
 for r in v['files']:
  n=r['path'];need(not Path(n).is_absolute()and all(x not in('','.','..')for x in n.split('/')),'confined family path');need(n not in names,'unique indexed member');names.add(n);row(base/n,dict(r,path=str(base/n)))
 actual=set()
 for q in base.rglob('*'):
  need(not q.is_symlink(),'indexed family has no aliases')
  if q.is_file():actual.add(str(q.relative_to(base)))
 need(names==actual,'whole exact indexed family membership');return v
# Strict independent decoder for the actual ASCII WAVE quoted scalar subset.
# It rejects trailing tokens, controls, unknown escapes and unterminated strings.
def wave(raw):
 s=raw.decode('utf-8','strict');need(s.startswith('"'),'single quoted WAVE scalar');out=[];i=1
 while i<len(s):
  c=s[i];i+=1
  if c=='"':need(s[i:]=='\n','exact one WAVE string plus newline');return ''.join(out)
  need(ord(c)>=32,'no unescaped control')
  if c=='\\':
   need(i<len(s),'complete WAVE escape');c=s[i];i+=1;need(c in{'"','\\','n','r','t'},'actual supported WAVE escape');out.append({'"':'"','\\':'\\','n':'\n','r':'\r','t':'\t'}[c])
  else:out.append(c)
 raise AssertionError('unterminated WAVE scalar')
def dump(n,v):
 q=P/n;need(not q.exists(),'new independent file only');q.parent.mkdir(parents=True,exist_ok=True);q.write_text(json.dumps(v,indent=2)+'\n')
def retain(p,n):
 p=Path(p);a=row(p);q=P/'raw-evidence'/n;need(not q.exists(),'fresh review raw copy');q.parent.mkdir(parents=True,exist_ok=True)
 with q.open('xb')as f:f.write(p.read_bytes());f.flush();os.fsync(f.fileno())
 os.chmod(q,0o600);b=row(q);need(a['sha256']==b['sha256']and a['bytes']==b['bytes']and ident(p)[:2]!=ident(q)[:2],'whole raw bytes independently retained');copies.append(dict(original=a,copy=b,distinctInode=True))
authority_path=S/'clock-v13-wasmtime-first-render-v1-root-authority.json';observation_path=S/'clock-v13-wasmtime-first-render-v1-root-results.json';comparison_path=S/'clock-v13-wasmtime-first-render-v1-comparison.json'
A=read(authority_path);R=read(observation_path);C=read(comparison_path)
need(A['state']=='ROOT_APPROVED_CLOCK_V13_SINGLE_WASMTIME_RENDER_PROBE_V1'and A['phase']=='single-stock-host-render'and A['ordinaryRunAllowed']is A['engineInitializationAllowed']is A['fullUnchangedRealReactDomWorkload']is True,'actual bounded Root phase')
for k in ['generatedModuleImportAllowed','packageOrWizerAllowed','keyOrCryptoWorkloadsAllowed','hostServersAllowed','timingAllowed','fullClockProfileAcceptance','operationalAdmission','runtimeAcceptanceClaim']:need(A[k]is False,'closed scope '+k)
need(A['allSevenResourceCasesRemainRequired']is A['fullRetainedFreshJcoSuiteStillRequired']is True,'future full profile remains required')
for k in ['host','component','nativeEngine','nativeMetadata','expectedNodeReport','monitor']:row(A[k]['path'],A[k])
need(A['host']['sha256']=='a85dec9fcbbad23d0e038e5a99604114dbe9aa77bc784e4bce0f33013eb33c1c'and A['host']['bytes']==50820352,'exact pinned stock Wasmtime42.0.1 binary')
need(A['component']['sha256']=='5c002f8da675016fd7061d245074965413d6914e4f40eb2a32a8141c1f3b7460','actual reviewed component')
need(A['actualArgv']==[A['host']['path'],'run','--invoke','run()',A['component']['path']]and R['actualArgv']==A['actualArgv']and A['timeoutSeconds']==60,'whole literal run() argv and deadline')
need(R['authority']==str(authority_path)and R['error']is R['postProtectionError']is None and R['protectedPaths']==11935,'Root-reported pre/final protection count and clean result')
need(R['wholeReturnDecoded']is R['wholeReturnComparedToNode']is False,'initial observation retained before separate comparison')
root=Path(A['outputRoot']);need(root==Path('/private/tmp/starling-node-compat/clock-v13-wasmtime-first-render-v1'),'actual fresh probe namespace')
actual={str(q.relative_to(root))for q in root.rglob('*')if q.is_file()};need(actual=={'wasmtime.string.txt','comparison.json','root-observation.json','invoke/stderr.log','invoke/stdout.log','invoke/started.json','invoke/terminal.json','invoke/owned-0000.json'},'exact actual eight output files; no invented producer index')
need((root/'root-observation.json').read_bytes()==observation_path.read_bytes()and(root/'comparison.json').read_bytes()==comparison_path.read_bytes(),'whole Root output/repository copies exact')
T=read(root/'invoke/terminal.json');started=read(root/'invoke/started.json');owned=read(root/'invoke/owned-0000.json')
need(T['pid']==started['pid']==22455 and T['rawExitCode']==0 and T['timeout']is T['forcedCleanup']is False and T['parentOwnedGroupGone']is T['allObservedOwnedGroupsGone']is True,'one owned fresh process raw0 clean')
for k in ['interruptedSignals','remainingObservedPids','signals','errors']:need(T[k]==[],'no process failure '+k)
need(T['finalGroups']==[dict(pgid=22455,alive=False,signalAllowed=False)]and len(T['observedProcesses'])==1 and T['observedProcesses'][0]['pid']==T['observedProcesses'][0]['pgid']==22455,'actual exact process/group singleton')
need(owned['sequence']==0 and owned['process']==T['observedProcesses'][0],'complete durable owned record')
need(started['argv']==A['actualArgv']and started['authority']==A==T['authority']and started['timeoutSeconds']==60,'whole started argv/authority/cap')
need(all(typed(R['terminal'][k],v)for k,v in T.items()),'Root entire durable terminal fields retained')
root_terminal_additions=sorted(set(R['terminal'])-set(T))
need(root_terminal_additions==['acceptanceRequiresRawZeroNoSignalsNoTimeoutAndIndependentResultReview','operationalElapsedSeconds'],'Root terminal additions explicitly operational/acceptance only')
for k in ['stdout','stderr']:row(T[k]['path'],T[k])
need(T['stdout']['bytes']==120 and T['stderr']['bytes']==0 and R['rawStdout']==T['stdout']['path']and R['rawStderr']==T['stderr']['path'],'full raw streams descriptors')
raw=Path(T['stdout']['path']).read_bytes();decoded=wave(raw);need(decoded==json.loads(raw),'independent WAVE subset decoder equals standard JSON quoted-string reader for these actual bytes')
need((root/'wasmtime.string.txt').read_bytes()==decoded.encode(),'whole retained public string bytes')
N=read(A['expectedNodeReport']['path'],A['expectedNodeReport']);cases=[x for x in N['cases']if x['id']=='react-dom-edge'];need(len(cases)==1,'exact retained Node oracle case');case=cases[0];oracle=case['nodeControl'];need(oracle['status']=='passed'and type(oracle['value'])is str,'actual successful retained Node control')
nodecommands=[x for x in N['commands']if x['name']=='node-react-dom-edge'];need(len(nodecommands)==1,'one actual retained Node control command');NC=nodecommands[0]
need(NC['status']==0 and NC['signal']is NC['spawnError']is None and NC['timedOut']is NC['outputLimitExceeded']is False and NC['ownedGroupGone']is NC['closed']is True and NC['signals']==NC['errors']==[],'retained Node raw clean0')
for k in ['stdout','stderr']:row(NC[k]['path'],NC[k])
need(NC['stderr']['bytes']==0 and typed(json.loads(Path(NC['stdout']['path']).read_bytes()),oracle),'whole retained Node raw result frame equals report control')
need(decoded==oracle['value']==A['expectedNodeReturn']==R['expectedNodeReturn']==C['wholeWasmtimeReturn']==C['wholeNodeReturn'],'entire public WAVE string exact retained Node string; no value projection')
value=json.loads(decoded);expected=dict(library='react-dom/server.edge',html='<p id="wasm-ssr">Hello from real ReactDOM</p>',bytes=45);need(typed(value,expected)and len(value['html'].encode())==value['bytes'],'all exact typed values and full UTF8 HTML bytes')
need(C['wholeReturnEqual']is True and typed(C['parsedReturn'],value)and C['component']==A['component']and C['rawStdoutSha256']==T['stdout']['sha256']and C['rawExitCode']==0 and C['allObservedOwnedGroupsGone']is True,'whole separately retained comparison authentic')
for k in ['freshNodeOracleExecuted','jcoRuntimeExecuted','retainedInstanceBehaviorProved','fullClockProfileAcceptance','operationalAdmission']:need(C[k]is False,'comparison finite limit '+k)
family(A['actualArtifactReview']['index']);AR=read(A['actualArtifactReview']['result']['path'],A['actualArtifactReview']['result'])
need(AR['state']=='INDEPENDENT_CLOCK_V13_COMPONENT_ARTIFACT_REVIEW_PASSED_V1'and AR['verifiedPassed']is True and AR['artifacts']['component']==A['component']and AR['nativeEngine']==A['nativeEngine']and AR['nativeMetadata']==A['nativeMetadata'],'genuine b073 artifact binding; unchanged native342')
caps=['wasi:clocks/monotonic-clock@0.2.10','wasi:clocks/wall-clock@0.2.10','wasi:io/poll@0.2.10'];need(A['selectedInterfaces']==AR['selectedInterfaces']==AR['emittedImports']==C['selectedInterfaces']==caps,'exact three accepted versioned capability imports from existing graph review')
need(AR['nativeSourceFiles']==342 and AR['externalEmbeddingSources']==3 and AR['selectedManifestCount']==9 and AR['fullMetadataFields']==64,'real v13 native context; no355 projection')
need(AR['publicAbiFunctions']==['run']and AR['allRootImportsCallable']is AR['pollableResourceSharedByPollAndMonotonicClock']is AR['canonicalPollableDrop']is True and AR['externalStderrStreamsErrorImports']is False,'reviewed callable import graph/pollable scope')
for x in list(AR['artifacts'].values())+[AR['typeGraph'],AR['callableCoreGraph']]:row(x['path'],x)
need(case['worker']['originalSource']['sha256']==AR['artifacts']['guest']['sha256']and case['worker']['bundle']['sha256']==AR['artifacts']['bundle']['sha256'],'same complete ReactDOM source/bundle against retained Node suite')
row(case['worker']['originalSource']['path'],case['worker']['originalSource']);row(case['worker']['bundle']['path'],case['worker']['bundle'])
family(AR['sourceIndex']);family(AR['sourcePeer']['index']);family(AR['loaderSourceIndex']);family(AR['loaderSourcePeer']['index'])
source=Path(AR['sourceIndex']['path']).parent;I=read(source/'source-inputs.json');need(len(I['files'])==11581 and len(I['families'])==11,'entire declared current Source11581/11 scope')
for x in I['files']:row(x['path'],x)
for x in I['families']:family(x)
# Negative DATA cases check the actual independent decoder's refusal boundary.
negatives=0
for bad in [b'',b'"unterminated',b'"a"\ntrailing',b'"a" "b"\n',b'"bad\\q"\n',b'"control\x00"\n']:
 try:wave(bad)
 except(AssertionError,UnicodeDecodeError):negatives+=1
 else:raise AssertionError('invalid WAVE accepted')
need(negatives==6,'all six pure malformed scalar fixtures reject')
for q in sorted(root.rglob('*')):
 if q.is_file():retain(q,Path('actual-output')/q.relative_to(root))
for p in [authority_path,observation_path,comparison_path,Path(A['expectedNodeReport']['path']),Path(NC['stdout']['path']),Path(NC['stderr']['path'])]:retain(p,Path('phase-and-oracle')/p.name)
# Current-review bookend only. Actual invocation's unretained pre/final reports
# remain Root/control-flow evidence, not transplanted from component construction.
for p,i in list(identities.items()):need(ident(Path(p))==i,'final current-review identity bookend')
ledger=[seen[k]for k in sorted(seen)if not Path(k).is_relative_to(P)]
dump('input-hashes.json',dict(schemaVersion=1,files=ledger));dump('raw-copy-map.json',dict(schemaVersion=1,files=copies,wholeBytes=True,distinctInodes=True));dump('decoded-public-return.json',dict(schemaVersion=1,rawStdout=T['stdout'],wholeDecodedString=decoded,parsed=value,wholeRetainedNodeEqual=True))
fixed=dict(schemaVersion=1,state='INDEPENDENT_CLOCK_V13_FIRST_WASMTIME_RENDER_RESULTS_REVIEW_PASSED_V1',verifiedPassed=True,componentSha256=A['component']['sha256'],nativeEngineSha256=A['nativeEngine']['sha256'],nativeSourceFiles=342,selectedInterfaces=caps,stockWasmtimeExecuted=True,ordinaryGuestRunInvoked=True,retainedNodeOracleUsed=True,freshNodeOracleExecuted=False,jcoRuntimeExecuted=False,generatedModuleImported=False,retainedInstanceBehaviorProved=False,wasmCloudExecuted=False,fullClockProfileAcceptance=False,operationalAdmission=False,runtimeAcceptanceClaim=False,reviewerToolOrGuestActionsInvoked=False)
direct=dict(rootAuthority=row(authority_path),rootObservation=row(observation_path),rootComparison=row(comparison_path),actualTerminal=row(root/'invoke/terminal.json'),actualStarted=row(root/'invoke/started.json'),rawStdout=T['stdout'],rawStderr=T['stderr'],nodeReport=A['expectedNodeReport'],nodeRawStdout=NC['stdout'],nodeRawStderr=NC['stderr'],host=A['host'],component=A['component'],nativeEngine=A['nativeEngine'],nativeMetadata=A['nativeMetadata'],actualArtifactReview=A['actualArtifactReview'],typeGraph=AR['typeGraph'],callableCoreGraph=AR['callableCoreGraph'],inputHashes=row(P/'input-hashes.json'),rawCopyMap=row(P/'raw-copy-map.json'))
coverage=dict(freshWasmtimeProcesses=1,ordinaryPublicStrings=1,runRecords=1,retainedNodeControls=1,actualOutputFiles=8,sourceInputRows=11581,sourceFamilies=11,rootReportedProtectedPaths=11935,currentActualInputFiles=len(ledger),rawCopies=len(copies),pureInvalidWaveCases=negatives)
limits=[
 'This proves only one fresh stock-Wasmtime42.0.1 run() returned the exact retained successful Node ReactDOM-edge whole string. No fresh Node, Jco runtime, retained-instance reuse, wasmCloud or full framework/clock-profile acceptance is proved.',
 'Three0.2.10 root capabilities and callable/pollable graph facts come from reauthenticated b073 construction graph review. This review performs no fresh binary decoder/host trace and does not prove which individual clock/poll functions the render called.',
 'The original Root observation retains wholeReturnDecoded:false/wholeReturnComparedToNode:false. Its later separate comparison and this independent raw decoder establish equality without rewriting that historical record.',
 'Root reported11581-ledger/Source/peer/artifact checks before/final invocation, protectedPaths11935 and no error/postProtectionError. No separate before/final report/ledger was persisted. Actual-time bookend stability is therefore Root/control-flow scope, not independent retained time-bookend attestation or global/environment attestation. Earlier construction reports are not transferred. This review independently rehashes current11581 rows and indexed families and checks its own final file identities.',
 'The previous retained suite report remains byte-exact: its original ReactDOM-edge Wasm trap and six other refusal cases remain seven failed/refused baseline observations. The new selected-clock single probe does not relabel those historical results.',
 'All seven resource cases, all nine native manifests/nativeBuffer, Date/monotonic/snapshot/timer order/cancel/self-clear/fatal/fresh+retained/all-invalid task queues/interest teardown and the full retained/fresh Jco/stock-host suite remain required under separate Source and Root authority.',
 'The exact pinned binary descriptor/argv is rehashed, not freshly version-invoked. No environment values or complete host/OS attestation are claimed. Operational3.391s is not a benchmark. No APIs/helpers/Node/Wasmtime/tool/engine/guest were executed by this reviewer.'
]
result={**fixed,**direct,'coverage':coverage,'wholeReturn':decoded,'parsedReturn':value,'wholeReturnEqual':True,'checks':checks,'rootReportedPreFinalScopeQualified':True,'earlierConstructionBookendsTransferred':False,'limitations':limits,'fullSuiteAuthority':None,'adoptionAuthority':None}
dump('results.json',result);dump('result-contract.json',dict(schemaVersion=1,requiredReviewState=fixed['state'],requiredFixedValues=fixed,requiredExactDescriptors=direct,requiredCoverage=coverage,wholeExpectedPublicReturn=decoded,limitationsMustBePreserved=limits,issuesActionAuthority=False))
(P/'README.md').write_text('Independent first v13 selected-clock stock-Wasmtime ReactDOM render review\n\nBounded DATA PASS: the complete120-byte WAVE stdout decodes to the exact retained Node-control string and full45-byte HTML. One fresh owned process22455 exited0 under60s cap with all groups gone, empty stderr and no signals/timeout/errors. Original8 output files and whole Node report/raw control are retained.\n\n'+ '\n\n'.join(limits)+'\n')
dump('receipt.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_FIRST_CLOCK_V13_WASMTIME_RENDER_DATA_REVIEW_V1',result=row(P/'results.json'),contract=row(P/'result-contract.json'),noProducerFilesChanged=True,noReviewerTargetActions=True,operationalAdmission=False))
files=[]
for q in sorted(P.rglob('*')):
 if q.is_file():r=row(q);files.append(dict(r,path=str(q.relative_to(P))))
dump('index.json',dict(schemaVersion=1,files=files))
for n in ['index.json','results.json','result-contract.json','receipt.json','input-hashes.json']:print(json.dumps(row(P/n)))
print(json.dumps(dict(sealed=True,members=len(files),checks=checks,inputFiles=len(ledger),rawCopies=len(copies),actions=False)))
