"""Read/hash/static and abstract-data checks only. No owner module is imported."""
from pathlib import Path
import ast, hashlib, itertools, json, os, re, shlex, stat

HERE = Path(__file__).resolve().parent
K = HERE.parent
C = K/'ownership-secret-failure-candidate-v2'
OLD = K/'ownership-secret-failure-candidate-v1'
SHA = '26eddb871e6538277e4b98f3c3912bb4f1c86e9e59640488fb06d457930cce54'
hashed, assertions = {}, 0

def need(ok, why):
    global assertions
    assertions += 1
    if not ok: raise AssertionError(why)

def row(p):
    p = Path(p); a=p.lstat(); need(stat.S_ISREG(a.st_mode),'regular leaf '+str(p))
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    z=p.lstat()
    need((a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==
         (z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns),'stable data read')
    return dict(path=str(p),sha256=h.hexdigest(),bytes=z.st_size)

def verify(d,base=None):
    p=Path(d['path'])
    if not p.is_absolute():
        need(base is not None and '..'not in p.parts,'declared relative context');p=base/p
    need(p.is_absolute(),'absolute descriptor')
    v=hashed.get(str(p))
    if v is None:v=row(p);hashed[str(p)]=v
    need((v['sha256'],v['bytes'])==(d['sha256'],d['bytes']),'exact hash/bytes '+str(p))
    return p

def load(p):
    p=Path(p);d=row(p);hashed[str(p)]=d;return json.loads(p.read_text())

def family(p,sha):
    need(row(p)['sha256']==sha,'expected immutable family')
    ix=load(p);names=[d['path']for d in ix['files']]
    need(len(names)==len(set(names)),'unique indexed names')
    for d in ix['files']:verify(d,p.parent)
    need({q.relative_to(p.parent).as_posix()for q in p.parent.rglob('*')if q.is_file()}==set(names)|{'index.json'},'exact family membership')
    return ix

ix=family(C/'index.json',SHA);need(len(ix['files'])==30,'candidate30 members')
refs=load(C/'references.json')
family(Path(refs['parentSourceIndex']['path']),refs['parentSourceIndex']['sha256'])
family(Path(refs['parentHoldReview']['index']['path']),refs['parentHoldReview']['index']['sha256'])
for d in [refs['parentMandatoryHistoryErratum'],refs['parentHoldReview']['result'],refs['requiredCorrectionContract'],refs['finalSourceContract']]:verify(d)
need(refs['parentMandatoryHistoryErratum']['sha256']=='0cad60adee41138aaa395585b3a9e60b2000d9634763c8667998049bf8766656','mandatory history erratum')
for name,count in [('parent-inputs.json',37),('syntax-input-hashes.json',2225),('final-input-hashes.json',5428)]:
    v=load(C/name);need(len(v['files'])==count,'finite '+name)
    need(len({d['path']for d in v['files']})==count,'unique original-context '+name)
    for d in v['files']:verify(d)
der=load(C/'derivations.json');old_der=load(OLD/'derivations.json')
need(len(der['newEdits'])==2 and len(old_der['edits'])==11 and der['composedReversibleEdits']==13,'two new/thirteen composed')
changed={}
for f in der['files']:
    parent=verify(f['parentAfterimage']).read_text();after=verify(f['after']).read_text();current=parent
    for e in [e for e in der['newEdits']if e['file']==f['path']]:
        need(current.count(e['before'])==e['occurrences']==1,'unique new forward edit');current=current.replace(e['before'],e['after'])
    need(current==after,'whole afterimage exact parent derivation')
    for e in reversed([e for e in der['newEdits']if e['file']==f['path']]):
        need(current.count(e['after'])==1,'unique new reverse');current=current.replace(e['after'],e['before'])
    need(current==parent,'whole parent reverse')
    genuine=(OLD/'before'/f['path']).read_text();composed=genuine
    for e in old_der['edits']+der['newEdits']:
        if e['file']==f['path']:
            need(composed.count(e['before'])==1,'composed unique edit');composed=composed.replace(e['before'],e['after'])
    need(composed==after,'genuine355→v2 complete composition')
    changed[f['path']]=f['after']['sha256']
    if f['path'].endswith(('crypto-key.cpp','crypto-raii.h')):need(after==parent,'unchanged key/RAII owner lifetime bytes')
meta=load(Path('/private/tmp/starling-node-compat/crypto-owner355-gc-v2-freeze/gc-off.engine.wasm.build.json'))
base={r['path']:r['sha256']for r in meta['sourceManifest']};need(len(base)==355,'genuine355')
final_contract=load(C/'source-contract.json')
need({d['path']:d['sha256']for d in final_contract['expectedNativeSourceManifest']}=={**base,**changed},'full355 actual three-file afterimage contract')
need(sum(base[p]!=changed.get(p,base[p])for p in base)==3,'three changed352 unchanged')
need(final_contract['parentHoldReview']==refs['parentHoldReview'] and final_contract['parentRequiredCorrectionContract']==refs['requiredCorrectionContract'],'final HOLD binding not pending derivation snapshot')
need(final_contract['mandatoryParentHistoryErratum']==refs['parentMandatoryHistoryErratum'],'final erratum binding')
for k in ['sourceIndependentReview','rootActivation','nativeBuild','runtimeProof']:need(final_contract[k]is None,'closed '+k)

algorithm_path=C/'afterimages/builtins/web/crypto/crypto-algorithm.cpp';text=algorithm_path.read_text()
calls=list(re.finditer(r'auto \[(\w+), (\w+)\] = to_bytes_expand\(cx, ([^;]+)\);',text))
need(len(calls)==17,'all actual helper call sites')
groups=[('ECDSA sign',0,2),('EC private',2,5),('EC public',5,7),('RSA private',7,10),('RSA CRT',10,15),('RSA public',15,17)]
inventory=[]
for group,start,end in groups:
    subset=calls[start:end]
    for m in subset:
        owner,length=m.group(1,2)
        first_get=text.index(owner+'.get()',m.end())
        length_match=re.search(r'\b'+re.escape(length)+r'\b',text[m.end():]);need(length_match is not None,'actual length consumed')
        guard=text.index('if (!'+(owner if group=='ECDSA sign'else subset[0].group(1)),m.end()if group=='ECDSA sign'else subset[-1].end())
        ret=text.index('return nullptr;',guard)
        need(guard<first_get and guard<m.end()+length_match.start(),'owner guard before pointer and returned length use')
        need('JS_ReportOutOfMemory(cx);'in text[guard:ret],'existing explicit OOM report')
        if group=='ECDSA sign':
            exact='\n  if (!'+owner+') {\n    JS_ReportOutOfMemory(cx);\n    return nullptr;\n  }'
            need(text[m.end():].startswith(exact),'immediate complete no-else failure branch')
            next_boundary=calls[1].start()if owner=='r_bytes'else text.index('size_t result_size',m.end())
            need(ret<next_boundary,'no next helper/length/allocation on failure')
        else:
            need(all('!'+s.group(1)in text[guard:ret]for s in subset),'existing collective check covers every group output')
        inventory.append(dict(group=group,owner=owner,callLine=text[:m.start()].count('\n')+1,guardLine=text[:guard].count('\n')+1,
                              checkedBeforePointerOrLengthUse=True,immediateBeforeNextHelperOrResultAllocation=group=='ECDSA sign'))
need(text.count('get_owned_bn_param(pkey.get(),')==15 and text.count('EVP_PKEY_get_bn_param(')==1,'all previous immediate BIGNUM adoptions exact')

# Independently verify every retained abstract case against the source block order.
# Booleans are hypothetical allocator outcomes, never real allocation/fault actions.
models=load(C/'source-check-results.json');need(models['checks']==220 and len(models['cases'])==48,'stored source-model corpus')
case_keys=set();old_continuations=0
for case in models['cases']:
    width=case['width'];r,s,result,ab=(case[k]for k in ['rConversionWouldSucceed','sConversionWouldSucceed','downstreamResultAllocationWouldSucceed','arrayBufferWouldSucceed'])
    need(width in [32,48,66] and all(type(v)is bool for v in [r,s,result,ab]),'pure finite input domain')
    case_keys.add((width,r,s,result,ab));events=case['actualSyntheticEvents']
    if not r:
        need(events==['convert-r'] and case['returned']=='nullptr' and case['oomReports']==1,'r failure returns before s/helper/result operations')
    elif not s:
        need(events==['convert-r','convert-s'] and case['returned']=='nullptr' and case['oomReports']==1 and case['freedOwners']==['r'],'s failure retires r before result')
    elif not result:
        need(events==['convert-r','convert-s','use-lengths','allocate-result'] and case['returned']=='nullptr' and case['oomReports']==1,'downstream allocation branch unchanged')
    else:
        need(events==['convert-r','convert-s','use-lengths','allocate-result','copy-r','copy-s','create-ArrayBuffer'],'successful conversion order unchanged')
        need(case['returned']==('ArrayBuffer'if ab else'nullptr'),'ArrayBuffer success/failure branch')
        need(set(case['freedOwners'])==({'s','r'}if ab else{'s','r','result'}),'owner transfer only on successful ArrayBuffer')
    if not(r and s):
        need(not any(e in events for e in ['use-lengths','allocate-result','copy-r','copy-s','create-ArrayBuffer']),'no downstream continuation')
        if result:old_continuations+=1
    need(len(case['freedOwners'])==len(set(case['freedOwners'])) and case['actualNativeFaultInvoked']is False,'abstract once-only local cleanup')
need(case_keys=={(w,*v)for w in [32,48,66]for v in itertools.product([False,True],repeat=4)},'complete48-case Cartesian model')
need(old_continuations==18,'eighteen held-source continuation models')

overlay=load(C/'syntax-overlay.json');vfs=load(verify(overlay['overlay']));mapping={}
need(len(overlay['sourceCopies'])==359 and sum(r['insideNative355Manifest']for r in overlay['sourceCopies'])==355,'complete355+4 real VFS')
vfs_expected=[]
for d in overlay['sourceCopies']:
    verify(d['original']);verify(d['syntaxBytes']);rel=d['relativePath']
    need(d['syntaxBytes']['sha256']==changed.get(rel,d['original']['sha256']),'only three actual afterimages in VFS')
    need(d['afterimage']==(rel in changed),'truthful actual afterimage')
    mapping[d['original']['path']]=d['syntaxBytes'];vfs_expected.append(dict(type='file',name=d['original']['path'],**{'external-contents':d['syntaxBytes']['path']}))
need(vfs['roots']==vfs_expected and vfs['case-sensitive']is True and vfs['use-external-names']is False,'exact359 overlay roots/no header stubs')
private=Path(overlay['privateRoot'])
need({str(p)for p in private.rglob('*')if p.is_file()}=={r['syntaxBytes']['path']for r in overlay['sourceCopies']}|{overlay['overlay']['path']},'no generated private object/link output')
syntax=load(C/'syntax-results.json');terminal=load(verify(syntax['freshTerminal']));command=load(verify(terminal['command']))
need(terminal['rawExitCode']==0 and terminal['timedOut']is False and terminal['timeoutSeconds']==60,'actual retained fresh syntax terminal0')
for key in ['stdout','stderr']:
    need(verify(terminal[key]).read_bytes()==b'','full empty syntax '+key)
db=load(verify(command['originalCompileDb']));need(command['originalCompileDbRow']in db,'genuine compileDB input row')
for key in ['originalWrapper','actualCompilerLeaf','overlay']:verify(command[key])
words=shlex.split(command['originalCompileDbRow']['command']);kept=[];removed=[];i=1
while i<len(words):
    if words[i]in ['-o','-c']:removed.append(words[i:i+2]);i+=2
    else:kept.append(words[i]);i+=1
need(removed==command['removedCompileOutputAndAction'],'only object/output compile pairs removed')
expected_argv=[command['actualCompilerAlias']]+kept+['-ivfsoverlay',overlay['overlay']['path'],'-fsyntax-only','-MD','-MF',str(C/'evidence/crypto-algorithm/headers.d'),'-MT','crypto-algorithm',command['originalCompileDbRow']['file']]
need(command['actualCommand']==expected_argv and '-o'not in expected_argv and '-c'not in expected_argv,'complete genuine flag→syntax argv')
target,sep,rest=verify(syntax['freshDependencyFile']).read_text().replace('\\\n',' ').partition(':');need(target=='crypto-algorithm'and sep==':','actual depfile target')
dependencies=[]
for logical in shlex.split(rest):
    canonical=os.path.normpath(logical);physical=mapping.get(canonical)
    if physical is None:physical=row(Path(logical).resolve(strict=True))
    dependencies.append(dict(logicalPath=logical,canonicalLogicalPath=canonical,physical=physical,mappedOverlaySource=canonical in mapping))
headers=load(C/'header-dependencies.json')
need(dependencies==headers['files'] and len(dependencies)==1103,'exact fresh1103 dependencies')
need(sum(r['logicalPath'].endswith('.cpp')for r in dependencies)==1,'oneCPP1102headers')
for d in dependencies:verify(d['physical'])
parent_syntax=load(verify(refs['unchangedParentSyntax']))
verify(parent_syntax['sdkArchive']);verify(parent_syntax['compilerLeaf']);verify(parent_syntax['sdkVersionData'])
for d in parent_syntax['sdkAliases']:
    p=Path(d['path']);need(p.is_symlink()and os.readlink(p)==d['linkText']and str(p.resolve())==d['resolvedTarget'],'same declared SDK alias chain')
old_key=load(verify(syntax['unchangedKeySyntaxTerminal']));need(old_key['rawExitCode']==0 and old_key['timedOut']is False,'unchanged key syntax authentic reuse')
for key in ['command','stdout','stderr']:verify(old_key[key])
prior_audit=load(K/'independent-ownership-secret-failure-source-review-v1/source-audit.json')
for witness in prior_audit['apiWitnesses']:verify(witness['file'])
for d in prior_audit['sdkArchiveComparisons']:
    if 'sha256'in d:verify(d)
normal=load(K/'ownership-gc-native-candidate-v2/normal-protection.json')
for d in normal['originals']:verify(d['original']);verify(d['frozen'])
verify(normal['freezeReceipt']);nroot=Path(normal['freezeReceipt']['path']).parent
need(len(normal['originals'])==1387 and len(normal['requiredNormalFreezeMembership'])==1391,'normal protection counts')
need({p.relative_to(nroot).as_posix()for p in nroot.rglob('*')if p.is_file()}==set(normal['requiredNormalFreezeMembership']),'normal strict membership')
for p in C.glob('*.py'):ast.parse(p.read_text())

report=dict(schemaVersion=1,state='INDEPENDENT_SECRET_FAILURE_V2_DATA_AND_SOURCE_BOUNDARIES_VERIFIED_V1',
    sourceIndexSha256=SHA,assertions=assertions,distinctHashedFiles=len(hashed),distinctHashedBytes=sum(d['bytes']for d in hashed.values()),
    candidateMembers=30,finalInputRows=5428,syntaxInputRows=2225,parentInputRows=37,nativeSourceFiles=355,
    originalChangedFiles=3,originalUnchangedFiles=352,newParentChanges=1,newReversals=2,composedReversals=13,
    helperCalls=17,callerGroups=6,allReturnedOwnersCheckedBeforeConsumption=True,immediateEcdsaFailureGuards=2,
    callerInventory=inventory,retainedSyntheticCases=48,heldContinuationModelCounterexamples=18,
    freshStoredSdkSyntaxCalls=1,freshStoredRawExitCodes=[0],freshDependencies=1103,freshTranslationUnits=1,freshHeaders=1102,
    unchangedKeySyntaxReusedByExactBytes=True,mirroredNativeFiles=355,additionalConfiguredHeaders=4,
    normalFrozenMembers=1391,normalOriginalReferences=1387,
    ownerActionsInvoked=False,runtimeActionsInvoked=False,compilerInvokedByReader=False)
with(HERE/'data-audit.json').open('x')as f:json.dump(report,f,indent=2);f.write('\n')
print(json.dumps(dict(audit=row(HERE/'data-audit.json'),assertions=assertions,files=len(hashed),sourceOnly=True)))
