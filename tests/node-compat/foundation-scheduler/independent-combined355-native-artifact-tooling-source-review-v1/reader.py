"""Independent combined355 freeze DATA audit; no producer/verifier/tool execution."""
from pathlib import Path
import ast,copy,hashlib,json,os,re,stat,subprocess,time,tempfile
P=Path(__file__).resolve().parent;S=P.parent;C=S/'combined-native-artifact-tooling-candidate-v1';F=Path('/private/tmp/starling-node-compat/combined-native355-v2-freeze');E=Path(str(F)+'-external-root');checks=0;seen={};identities={};copy_evidence=[];raw_copies=[]
def need(v,label):
 global checks
 checks+=1
 assert v,label
def identity(p):
 s=p.lstat();need(stat.S_ISREG(s.st_mode),'regular actual file');return(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,stat.S_IMODE(s.st_mode),s.st_nlink)
def row(p):
 p=Path(p);a=identity(p)
 if str(p)in seen:need(identities[str(p)]==a,'same captured identity');return seen[str(p)]
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 need(a==identity(p),'stable hash read');r=dict(path=str(p),sha256=h.hexdigest(),bytes=a[2]);seen[str(p)]=r;identities[str(p)]=a;return r
def verify(r):need(row(r['path'])=={k:r[k]for k in['path','sha256','bytes']},'exact actual descriptor');return Path(r['path'])
def read(r):return json.loads(verify(r).read_bytes())
def load(p):return read(row(p))
def same(a,b):
 if type(a)is not type(b):return False
 if isinstance(a,dict):return a.keys()==b.keys()and all(same(a[k],b[k])for k in a)
 if isinstance(a,list):return len(a)==len(b)and all(same(x,y)for x,y in zip(a,b))
 return a==b
def tree(root,names,allowlinks=None):
 root=Path(root);fs=set();links={}
 for q in root.rglob('*'):
  n=q.relative_to(root).as_posix()
  if q.is_symlink():links[n]=os.readlink(q)
  elif q.is_file():fs.add(n)
 need(fs==set(names)and links==(allowlinks or{}),'complete current exact tree')
def family(r):
 ix=read(r);base=Path(r['path']).parent;names={'index.json'};rs=[]
 for m in ix['files']:
  n=m['path'];need(n not in names and n and not n.startswith('/')and all(s not in('','.','..')for s in n.split('/')),'unique confined indexed member');names.add(n);q=dict(m,path=str(base/n));verify(q);rs.append(q)
 tree(base,names);return ix,rs
def proof(pair):
 _,rs=family(pair['index']);need(pair['result']in rs,'result indexed once');return read(pair['result'])
def save(n,v):
 p=P/n;need(not p.exists(),'new reviewer output only');p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n')
source_index=dict(path=str(C/'index.json'),sha256='c365e6089688f62f028580e86b14db80bb434ba7b4ac45ae341e851c11913a7b',bytes=4950);_,members=family(source_index);need(len(members)==31,'whole immutable31 Source members');refs=load(C/'references.json');declared=load(C/'source-inputs.json');need(len(declared['files'])==21,'finite21 direct declared source references')
for r in declared['files']:verify(r)
actual=proof(refs['actualFrozenReview']);fc=read(refs['actualFrozenContract']);need(fc['requiredReviewState']==actual['state']=='INDEPENDENT_COMBINED355_NATIVE_FREEZE_V2_RESULTS_REVIEW_PASSED_V1'and actual['verifiedPassed']is True,'actual e6f9 frozen DATA prerequisite')
for group in ['requiredFixedValues','requiredExactDescriptors']:
 for k,v in fc[group].items():need(same(actual[k],v),'whole actual frozen contract '+k)
need(same(actual['coverage'],fc['requiredCoverage']),'whole frozen coverage')
compact=read(refs['compactInputBoundary']);need(len(compact['files'])==2618 and compact['reviewedBuildReferencesRehashed']==20816 and compact['reviewedBuildInputLedger']==refs['reviewedBuildInputLedger']and compact['reviewedInheritedFamilies']==refs['inheritedFamilies']and compact['historicalTreesRecopied']is False,'exact compact/current versus inherited boundary')
for x in compact['files']:verify(x)
base=read(refs['reviewedBuildInputLedger']);need(len(base['files'])==20816,'whole20816 reference expansion')
for x in base['files']:verify(x)
for ix in refs['inheritedFamilies']:family(ix)
need(len(refs['inheritedFamilies'])==15,'exact fifteen inherited family descriptors')
fr=read(refs['frozenCopyInventory']);need(len(fr['files'])==2596 and fr['wholeMembershipFiles']==2597,'full frozen2596/2597')
names={'normal-off-freeze-receipt.json'};inodes=set()
for x in fr['files']:
 a=verify(x['copy']).stat();n=Path(x['copy']['path']).relative_to(F).as_posix();need(n not in names and a.st_nlink==1 and stat.S_IMODE(a.st_mode)==0o600 and(a.st_dev,a.st_ino)not in inodes,'unique private whole frozen copies');names.add(n);inodes.add((a.st_dev,a.st_ino))
 if x['original']is not None:
  b=verify(x['original']).stat();need((a.st_dev,a.st_ino)!=(b.st_dev,b.st_ino),'all original/copy inode independence')
tree(F,names)
protection=read(refs['freezerProtection']);need(len(protection['files'])==20816 and len(protection['modePairs'])==1613,'complete original mode/stage pair boundary')
for x in protection['files']:
 s=verify(x['descriptor']).stat();need(stat.S_IMODE(s.st_mode)==x['mode']and s.st_nlink==x['nlink'],'all original file modes/nlinks')
all_paths={x['path']for x in compact['files']}|{x['path']for x in base['files']}
for x in protection['modePairs']:
 need(x['copy']['path']in all_paths and x['original']['path']in all_paths,'JS mode-pair byte descriptors already in captured ledgers');a=verify(x['copy']).stat();b=verify(x['original']).stat();need(stat.S_IMODE(a.st_mode)==x['copyMode']and stat.S_IMODE(b.st_mode)==x['originalMode']and(a.st_dev,a.st_ino)!=(b.st_dev,b.st_ino),'all1613 stage pair modes and inodes')
for t in protection['trees']:need(stat.S_IMODE(Path(t['root']).stat().st_mode)==t['mode'],'protected root mode');tree(t['root'],t['files'],t['links'])
aliases=read(refs['referenceAliasWitness'])
for a in aliases['symlinks']:need(Path(a['path']).is_symlink()and os.readlink(a['path'])==a['linkText']and str(Path(a['path']).resolve())==a['resolved'],'original31 aliases')
for a in aliases['archiveHardlinks']:need(os.path.samefile(a['path'],a['target']),'original archive hardlink')
# Authenticate actual verifier/monitor APIs as Source; never import/invoke them.
_,vrows=family(refs['freezerSourceIndex']);need(refs['activeVerifier']in vrows,'actual original5230 verifier identity');_,mrows=family(refs['monitorIndex']);need(refs['monitorEntry']in mrows,'original0af monitor identity')
vt=ast.parse(verify(refs['activeVerifier']).read_text());vf=next(n for n in vt.body if isinstance(n,ast.FunctionDef)and n.name=='verify_frozen');need([a.arg for a in vf.args.args]==['receipt_row','expected_source'],'real two-argument verifier signature');va=next(n for n in vt.body if isinstance(n,ast.Assign)and any(isinstance(a,ast.Name)and a.id=='FREEZE'for a in n.targets));need(ast.literal_eval(va.value.args[0])==refs['frozenRoot'],'real unmodified FREEZE constant')
mt=ast.parse(verify(refs['monitorEntry']).read_text());mf=next(n for n in mt.body if isinstance(n,ast.FunctionDef)and n.name=='monitor');need([a.arg for a in mf.args.args]==['argv','cwd','environment','output','timeout_seconds','authority'],'real six-argument original monitor signature')
py=(C/'artifact_tooling.py').read_text();js=(C/'bootstrap.mjs').read_text();pt=ast.parse(py);pintext=(C/'pin_model.py').read_text();ast.parse(pintext)
need("Path(__file__).resolve().parent==OWN"in py and "OWN=REPO/'tests/node-compat/foundation-scheduler/combined-native-artifact-tooling-candidate-v1'"in py and "ORIGINAL='"+str(C)+"'"in js,'actual module OWN/__file__/JS ORIGINAL paths, not injected context')
need("helper.verify_frozen(f['refs']['freezeReceipt'],f['refs']['freezerSourceIndex']['sha256'])"in py and 'helper.FREEZE==Path' in py and 'Path(helper.__file__).resolve()'in py,'actual unchanged verifier direct call/context')
need('helper.HERE'not in py and 'helper.FROZEN'not in py and 'setattr('not in py,'no foreign helper global/path rebinding')
worker=next(n for n in pt.body if isinstance(n,ast.FunctionDef)and n.name=='worker');calls=[n for n in ast.walk(worker)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=='verify_frozen'];need(len(calls)==1 and len(calls[0].args)==2,'one operational verifier call per worker')
parent=next(n for n in pt.body if isinstance(n,ast.FunctionDef)and n.name=='parent');calls=[n for n in ast.walk(parent)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=='monitor'];need(len(calls)==1 and len(calls[0].args)==6,'actual monitor call arity')
need(py.index('write(out/\'raw-terminal-observed.json\'')<py.index("clean_terminal(terminal,f['rootRow'])")<py.index("value=json.loads(Path(terminal['stdout']['path']).read_bytes())"),'whole raw status/streams retained before clean/parse assertions')
need("finally:f['capture'].recheck()"in py and 'finally:c.recheck()'in py and 'finally{try{await c.recheck();}'in js,'full final/failure guards around action/model and JS API')
need('child_process'not in '\n'.join(x for x in js.splitlines()if x.startswith('import '))and 'import('not in js and 'execFile('not in js and 'spawn('not in js and 'writeFile('not in js,'retained API has no helper/process/write import/call')
need("proof.bootstrapFrame"in js and 'const recheck=async()=>{await c.recheck();'in js and 'return Object.freeze({'in js,'full retained actual bootstrap plus fresh own recheck')
# Generic mechanism donor provenance: exact segment and only two declared hooks.
prov=load(C/'mechanism-provenance.json');donor=verify(prov['donor']).read_text();segment=donor[donor.index('def descriptor('):donor.index('def outputs(')];need(hashlib.sha256(segment.encode()).hexdigest()==prov['segmentSha256']and len(segment.encode())==prov['segmentBytes'],'exact generic Source donor segment');expected=segment.replace('def __init__(self):self.rows={};self.families=[]','def __init__(self):self.rows={};self.families=[];self.checks=[]').replace('for root,names,private in self.families:exact_tree(root,names,private)','for root,names,private in self.families:exact_tree(root,names,private)\n        for check in self.checks:check()');need(expected in py,'exact two declared generic IO/Capture additions; no old authorizer/frame reuse')
# Execute only extracted pure definitions against GENUINE frozen DATA.
pure=ast.parse(pintext);need(all(not isinstance(n,(ast.Import,ast.ImportFrom))or isinstance(n,ast.Import)and[n.name for n in n.names]==['copy']for n in pure.body),'pin model has only pure copy import');ns={};exec(compile(pure,str(C/'pin_model.py'),'exec'),ns)
receipt=read(refs['freezeReceipt']);metadata=read(refs['metadata']);capsule=read(refs['historicalVerifierCapsule']);manifests=[]
for r in refs['selectedManifestRows']:p=Path(refs['frozenSourceRoot'])/r['path'];d=row(p);need(d['sha256']==r['sha256'],'actual frozen manifest hash');manifests.append(read(d))
frame=ns['native_frame'](capsule,receipt,metadata,manifests,refs,source_index);candidate=ns['candidate'](frame,receipt,refs,source_index);doc=ns['unreviewed_document'](candidate);reviewed=ns['reviewed_document'](doc);pure_cases=0
need(frame['verificationCapsule']==capsule and frame['verificationCapsule']['state']=='COMBINED355_NORMAL_FREEZE_READ_ONLY_CAPSULE_VERIFIED_NOT_ACCEPTED_V1'and frame['metadata']==metadata and len(metadata)==80 and len(manifests)==11 and frame['enginePath']!=metadata['enginePath'],'genuine full80 frame succeeds preserving unaccepted capsule and original raw paths');pure_cases+=1
need(all(doc['variants'][k]is None for k in ['normal-runtime','gc-off','disabled-off'])and len(candidate['frozenFiles'])==2596,'genuine normal-only full frozen candidate succeeds');pure_cases+=1
def changed(a,b,prefix=''):
 if type(a)is not type(b):return[prefix]
 if isinstance(a,dict):
  out=[]
  for k in a.keys()|b.keys():out+=changed(a.get(k),b.get(k),prefix+'.'+k)
  return out
 if isinstance(a,list):
  if len(a)!=len(b):return[prefix]
  return[x for i,(u,v)in enumerate(zip(a,b))for x in changed(u,v,prefix+'['+str(i)+']')]
 return[]if a==b else[prefix]
delta=changed(doc,reviewed);need(set(delta)=={'.state','.reviewRequired','.variants.normal-off.state','.variants.normal-off.reviewRequired'},'EXACT four reviewed state/flag changes only');pure_cases+=1
symbolic=lambda n:dict(path='/synthetic/combined355-source-review/'+n,sha256='a'*64,bytes=1)
root=dict(reviewedPins=symbolic('pins.json'),actualExportCandidate=symbolic('candidate.json'),independentExportReview=dict(index=symbolic('export-review/index.json'),result=symbolic('export-review/results.json')),rootPinReview=symbolic('pin-review.json'))
review=dict(schemaVersion=1,state='ROOT_COMBINED355_NORMAL_OFF_VALIDATION_PIN_REVIEW_V1',toolingIndex=source_index,reviewedPins=root['reviewedPins'],actualExportCandidate=root['actualExportCandidate'],independentExportReview=root['independentExportReview'],actualFrozenReview=refs['actualFrozenReview'],engine=refs['engine'],metadata=refs['metadata'],freezeReceipt=refs['freezeReceipt'],nativeSourceFiles=355,externalEmbeddingSources=3,selectedManifestCount=11,fullMetadataFields=80,validationBootstrapOnly=True,otherVariantsNull=True,engineExecuted=False,guestExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False,sourcePromotionAllowed=False)
selected=ns['select_reviewed'](reviewed,review,candidate,root,refs,source_index);pure_cases+=1;boot=ns['bootstrap_frame'](selected,frame,refs,source_index,symbolic('bootstrap-root.json'),symbolic('bootstrap-config.json'),root);need(boot['metadata']==metadata and boot['nativeFrame']['verificationCapsule']==capsule and boot['currentFrozenVerifierCalls']==1 and boot['grantsRuntimeAuthority']is False,'pure bootstrap model accepts actual pinned DATA with symbolic unissued Root slots');pure_cases+=1
# Real actual assignments are evaluated, never replace OWN or __file__.
allowed={'REPO','OWN','BASE','TIMEOUT','SOURCE_PEER_STATE'};nodes=[n for n in pt.body if isinstance(n,ast.ImportFrom)and n.module=='pathlib' or isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id in allowed for t in n.targets)or isinstance(n,ast.FunctionDef)and n.name in ['descriptor','outputs','validate_root','clean_terminal']];g={};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(C/'artifact_tooling.py'),'exec'),g);need(g['OWN']==C and g['TIMEOUT']==600 and g['SOURCE_PEER_STATE']=='INDEPENDENT_COMBINED355_NATIVE_ARTIFACT_TOOLING_SOURCE_REVIEW_PASSED_V1','actual original module constants and finite phase budget');pure_cases+=1
roottemplate=load(C/'future-root-authority.template.json')
for phase in ['export','bootstrap']:
 out,external=g['outputs'](phase);need(not out.exists()and not external.exists(),'future output roots absent; no action');v={**roottemplate,'state':roottemplate['requiredIssuedState'],'phase':phase,'toolingIndex':source_index,'exportAllowed':phase=='export','bootstrapAllowed':phase=='bootstrap','frozenReadOnlyVerifierAllowed':True,'outputRoot':str(out),'externalOutputRoot':str(external)}
 if phase=='bootstrap':v.update(root)
 g['validate_root'](v,source_index,refs,phase);pure_cases+=1
 for key,value in [('fullMetadataFields',75),('nativeSourceFiles',342),('selectedManifestCount',9),('engineExecutionAllowed',True),('expectedFrozenVerifierCalls',2),('externalParentDeadlineSeconds',601),('toolingIndex',symbolic('wrong/index.json'))]:
  try:g['validate_root']({**v,key:value},source_index,refs,phase)
  except(AssertionError,KeyError,TypeError):pure_cases+=1
  else:raise AssertionError('bad pure Root phase accepted '+key)
for mutate in [lambda v:v.update(gcStress=True),lambda v:v.update(sourceManifest=v['sourceManifest'][:342]),lambda v:v.update(selectedModuleManifests=v['selectedModuleManifests'][:9]),lambda v:v['privateRustupBootstrapPolicy']['settingsAtBuildCompletion'].update(bytes=57),lambda v:v['zlibPolicy']['runtimeBackendProof'].update(verified=True)]:
 bad=copy.deepcopy(metadata);mutate(bad)
 try:ns['native_frame'](capsule,receipt,bad,manifests,refs,source_index)
 except(AssertionError,KeyError,TypeError):pure_cases+=1
 else:raise AssertionError('changed actual native data model accepted')
for path,val in [('fullMetadataFields',75),('nativeSourceFiles',342),('selectedManifestCount',9),('engineExecuted',True)]:
 bad={**review,path:val}
 try:ns['select_reviewed'](reviewed,bad,candidate,root,refs,source_index)
 except(AssertionError,KeyError,TypeError):pure_cases+=1
 else:raise AssertionError('wrong pin Root model accepted')
# No model frame is published as operational evidence. Scratch is explicitly
# synthetic Root-slot DATA for independent JS shape model only.
scratch=Path(tempfile.mkdtemp(prefix='independent-combined355-tooling-pure-',dir='/private/tmp'));fixture=scratch/'unissued-pure-fixture.json';fixture.write_text(json.dumps(dict(syntheticRootSlotsOnly=True,actualBootstrap=False,api=row(C/'bootstrap.mjs'),refs=refs,own=source_index,value=boot)));os.chmod(fixture,0o600)
verify(refs['node']);terminals=[]
for name,args in [('pure-js',[str(P/'pure.mjs'),str(fixture)]),('grammar',['--check',str(C/'bootstrap.mjs')])]:
 cmd=[refs['node']['path'],*args];start=time.monotonic();p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,cwd=P,timeout=60);(P/(name+'.stdout.log')).write_bytes(p.stdout);(P/(name+'.stderr.log')).write_bytes(p.stderr);term=dict(schemaVersion=1,argv=cmd,node=refs['node'],source=row(P/'pure.mjs')if name=='pure-js'else row(C/'bootstrap.mjs'),rawExitCode=p.returncode,stdout=row(P/(name+'.stdout.log')),stderr=row(P/(name+'.stderr.log')),operationalSeconds=time.monotonic()-start,pureDataOnly=name=='pure-js',grammarOnly=name=='grammar',combinedNativeBootstrapPreflightOrAnyHelperPhaseInvoked=False);save(name+'.terminal.json',term);terminals.append(term);need(p.returncode==0 and not p.stderr,'genuine finite pure/grammar check raw0')
jsresult=json.loads((P/'pure-js.stdout.log').read_bytes());need(jsresult['passed']is True and jsresult['actualFull80NativeDataUsed']is True and jsresult['retainedApiInvoked']is False,'actual metadata pure JS model passes, no retained API call')
# Exact source before/after identity bookend, no history recopy.
for p,i in list(identities.items()):need(identity(Path(p))==i,'current Source/input final identity stable')
sourcecontract=load(C/'future-source-review-contract.json');fixed=dict(sourcecontract['requiredFixedValues']);fixed.update(state=sourcecontract['requiredState'],toolingSourceIndexSha256=source_index['sha256']);direct=dict(sourceIndex=source_index,sourceResult=row(C/'results.json'),actualFrozenReview=refs['actualFrozenReview'],actualFrozenContract=refs['actualFrozenContract'],compactInputBoundary=refs['compactInputBoundary'],expandedBuildInputLedger=refs['reviewedBuildInputLedger'],activeVerifier=refs['activeVerifier'],freezerSourceIndex=refs['freezerSourceIndex'],nativeSourceIndex=refs['nativeSourceIndex'],engine=refs['engine'],metadata=refs['metadata'],freezeReceipt=refs['freezeReceipt'])
coverage=dict(sourceMembers=31,directDeclaredInputs=21,currentCompactRows=2618,expandedBuildRows=20816,inheritedFamilies=15,frozenCopies=2596,frozenFiles=2597,stageOriginalPairs=1613,failedV1TreeFiles=755,configuredTreeDocumentationLinks=3,originalAliases=31,originalArchiveHardlinks=1,metadataFields=80,nativeSources=355,externalEmbeddingSources=3,selectedWholeManifests=11,actualPurePythonCases=pure_cases,actualPureJsCases=jsresult['cases'],actualGrammarChecks=1,uniqueActualInputsRehashed=len(seen))
save('boundary-and-pure-review.json',dict(schemaVersion=1,passed=True,coverage=coverage,exactReviewedPinChangedPaths=sorted(delta),genuineNativeDataModelsPassed=True,syntheticRootSlotsOnly=True,noOperationalFrameOrPinsPublished=True,helperVerifierMonitorExportBootstrapEngineGuestInvoked=False))
save('static-findings.json',dict(schemaVersion=1,concreteBlockers=[],realOwnAndFileContextsChecked=True,actualVerifierArgs=2,actualMonitorArgs=6,rawCaptureBeforeAssertions=True,fullHistoricalCapsulePreserved=True,retainedApiReadHashOnly=True,templateAuthoritySlotsNull=True,sourceAndFinalFailureProtectionPathsReviewed=True,limitations=['Pure bootstrap/select tests use genuine frozen80/355+3/11 metadata/receipt/manifests/capsule with explicit symbolic future Root slots. They are not operational bootstrap proof or issued pins.','Verifier active originalSource self-auth is distinct from frozen payload/model reads; preserved exactly.','Operational controller failure records do not guarantee every attempted raw byte was writable; only clean0 and complete retained terminal/frame can pass.','Source approval grants no phase. Actual export, independent export DATA, new Root-reviewed pins, actual bootstrap and independent bootstrap DATA remain required before retained read-only API can succeed.']))
# Compact descriptor reuse; no full inherited ledger or tree duplicated here.
save('input-boundary.json',dict(schemaVersion=1,sourceIndex=source_index,directDeclaredInputManifest=row(C/'source-inputs.json'),compactInputBoundary=refs['compactInputBoundary'],expandedBuildInputLedger=refs['reviewedBuildInputLedger'],inheritedFamilies=refs['inheritedFamilies'],frozenCopyInventory=refs['frozenCopyInventory'],freezerProtection=refs['freezerProtection'],uniqueCurrentFilesRehashed=len(seen),currentAllRehashed=True,historicalTreesRecopied=False))
limits=['Bounded SOURCE review only. All operational Source/Root/phase/proof/pin/bootstrap/read-only result slots remain unissued; no producer/verifier/monitor/export/bootstrap/engine/guest action occurred.','Original active5230 verify_frozen retains real __file__/FREEZE and exacttwo-argument signature. No HERE/FROZEN facade, metadata/state/path/global projection or old75/342 classifier substitution. Full80/355+3/11 and original NOT_ACCEPTED capsule stay separate.','Complete compact2618/current +20816original ledgers/15families,2596 frozen copies/2597 membership, modes/stagedpairs and declared aliases were currently checked by read/hash. Existing descriptors are reused; no history trees copied.','Pure models accept genuine actual pinned full80metadata/receipt/manifests/capsule. Only four documented pin state/flag changes occur; allotherfields and threeNULL variants persist. Synthetic future Root slots are model fixtures only; no operational frame/pins were published.','JS retained API consumes future independently reviewed actual bootstrap fullDATA, preserving original action contexts and separate currentVerification/fresh recheck. Zerohelper/process/write scope does not mean whole operational bootstrap never ran.','Future actual phase timeout/raw capture/failure and whole-frame evidence still require operation and independent DATA review. Source/pure/parser success is not engine behavior, runtime/adoption, scheduler/resource/GC/free/wipe/security/performance acceptance.']
save('results.json',{**fixed,**direct,'coverage':coverage,'checks':checks,'sourceOnly':True,'sourceReviewPassed':True,'ownerActionsInvoked':False,'hostActionsInvoked':False,'exportOrBootstrapActionsInvoked':False,'syntaxCheckerUsed':True,'inertSourceApiImportedForPureModelOnly':True,'actualNativeDataModelsExercised':True,'retainedApiInvoked':False,'actualExport':None,'actualPins':None,'actualBootstrap':None,'actualReadOnlyApiResult':None,'rootAuthority':None,'limitations':limits})
save('result-contract.json',dict(schemaVersion=1,requiredReviewState=fixed['state'],requiredFixedValues=fixed,requiredSourceIndex=source_index,requiredExactDescriptors=direct,requiredCoverage=coverage,issuesAnyActionAuthority=False))
(P/'README.md').write_text('Independent combined355 native artifact tooling SOURCE review\n\nBounded SOURCE PASS. Actual twoCLI phases, real5230 verifier context, full80/355+3/11 data/pin model, strict original0af600s monitor call and retained read/hash-only JS API were reviewed. Complete finite boundary rehashed using existing descriptors. Pure models exercised actual native metadata/receipt/capsule/all11manifests without calling any operational function.\n\n'+ '\n\n'.join(limits)+'\n')
save('receipt.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_COMBINED355_NATIVE_ARTIFACT_TOOLING_SOURCE_REVIEW_V1',result=row(P/'results.json'),contract=row(P/'result-contract.json'),sourceIndex=source_index,allSourceBytesUnchanged=True,reviewerOperationalActions=False))
files=[]
for q in sorted(P.rglob('*')):
 if q.is_file():r=row(q);files.append(dict(r,path=q.relative_to(P).as_posix()))
save('index.json',dict(schemaVersion=1,files=files))
for n in ['index.json','results.json','result-contract.json','receipt.json']:print(json.dumps(row(P/n)))
print(json.dumps(dict(sealed=True,members=len(files),checks=checks,coverage=coverage,operationalActions=False)))
