"""Independent actual export read/hash/JSON/AST DATA only; never call an action."""
from pathlib import Path
import ast,copy,hashlib,json,os,stat

OWN=Path(__file__).resolve().parent
K=OWN.parent
SOURCE=K/'ownership-secret-artifact-tooling-candidate-v3'
ROOT=K/'ownership-secret-artifact-export-v3-root-results.json'
ROOT_SHA='2295d612fd9cf585077f011090b44de719fb32f4fe5ec77d30a1d012969c621a'
rows={};identities={};trees=[];checks=[]
def need(v,n):assert v,n;checks.append(n)
def write(n,v):(OWN/n).write_text(json.dumps(v,indent=2)+'\n')
def actual(path):
    p=Path(path);a=p.stat();assert p.is_file()and not p.is_symlink();h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    z=p.stat();identity=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,str(p.resolve()))
    assert identity(a)==identity(z)
    return dict(path=str(p),sha256=h.hexdigest(),bytes=z.st_size),identity(z)
def checked(value):
    d={k:value[k]for k in ['path','sha256','bytes']}
    if d['path']in rows:assert rows[d['path']]==d;return d
    r,i=actual(d['path']);assert r==d;rows[d['path']]=r;identities[d['path']]=i;return d
def read(value):checked(value);return json.loads(Path(value['path']).read_bytes())
def local(name):
    assert type(name)is str and name and not name.startswith('/')and '\\'not in name and all(n not in ['','.','..']for n in name.split('/'));return name
def tree(root,names,private=False):
    root=Path(root);assert root.is_dir()and not root.is_symlink();found=set()
    if private:assert stat.S_IMODE(root.stat().st_mode)==0o700
    for p in root.rglob('*'):
        assert not p.is_symlink()
        if p.is_dir():
            if private:assert stat.S_IMODE(p.stat().st_mode)==0o700
        else:
            assert p.is_file();found.add(p.relative_to(root).as_posix())
            if private:assert stat.S_IMODE(p.stat().st_mode)==0o600 and p.stat().st_nlink==1
    assert found==set(names);trees.append((root,set(names),private))
def family(ix):
    v=read(ix);root=Path(ix['path']).parent;names={'index.json'};result=[ix]
    for m in v['files']:
        n=local(m['path']);assert n not in names;names.add(n);r=dict(path=str(root/n),sha256=m['sha256'],bytes=m['bytes']);checked(r);result.append(r)
    tree(root,names);return result
def strict(a,b):
    if type(a)is not type(b):return False
    if type(a)is dict:return set(a)==set(b)and all(strict(a[k],b[k])for k in a)
    if type(a)is list:return len(a)==len(b)and all(strict(x,y)for x,y in zip(a,b))
    return a==b

root_row,i=actual(ROOT);need(root_row['sha256']==ROOT_SHA and root_row['bytes']==5089,'exact Root actual result')
root=read(root_row);source_members=family(root['sourceIndex']);need(root['sourceIndex']['sha256']=='d62b235c0c397ff3b91e098691e3bbe137e761beaf7cd513b132fad7474c52a2','actual Source d62 immutable')
source_peer=family(root['sourceReview']['index']);need(root['sourceReview']['result']in source_peer,'Source522e result once indexed');sp=read(root['sourceReview']['result'])
need(sp['state']=='INDEPENDENT_CRYPTO_OWNER355_SECRET_ARTIFACT_TOOLING_SOURCE_REVIEW_PASSED_V3'and sp['toolingSourceIndexSha256']==root['sourceIndex']['sha256'],'exact current Source review')
refs=json.loads((SOURCE/'references.json').read_bytes());inputs=json.loads((SOURCE/'source-inputs.json').read_bytes())
for r in inputs['files']:checked(r)
need(len(inputs['files'])==241,'all241 own declared inputs')
for ix in refs['families']:family(ix)
protected=read(refs['protectedInputLedger']);need(len(protected['files'])==27729,'all27729 fixed protection rows')
for r in protected['files']:checked(r)
authority=read(root['rootAuthority']);config=read(root['config']);checked(authority['rootOuterController'])
need(authority['schemaVersion']==3 and authority['state']=='ROOT_REVIEWED_SECRET_OWNER355_ARTIFACT_TOOLING_PHASE_V3'and authority['phase']=='export','genuine issued export-only Root state')
need(config==dict(schemaVersion=3,state='SECRET_OWNER355_ARTIFACT_TOOLING_CONFIG_V3',phase='export',toolingIndex=root['sourceIndex'],rootAuthority=root['rootAuthority']),'exact actual export config')
need(authority['exportAllowed']is True and authority['bootstrapAllowed']is False and authority['sourceIndependentReview']==root['sourceReview'],'no bootstrap authority')
for k in ['nativeBuildAllowed','nativeFreezeAllowed','gcReconfigureAllowed','ninjaAllowed','engineExecutionAllowed','guestAllowed','keyOrCryptoAllowed','componentAllowed','runtimeAcceptanceClaim','operationalAdmission','sourcePromotionAllowed','metadataProjectionAllowed','timingAllowed']:need(authority[k]is False,'Root closed '+k)
for k in ['actualExportCandidate','independentExportReview','reviewedPins','rootPinReview','runtimeAuthority','actualBootstrap']:need(authority[k]is None,'unissued Root slot '+k)
for k in ['engine','metadata','freezeReceipt','nativeSourceIndex','verifierSourceIndex','actualVerifierReview','actualArtifactReview','configuredSourceRoot','frozenSourceRoot','frozenRoot']:need(authority[k]==refs[k],'exact original Root role '+k)
need(authority['toolingIndex']==root['sourceIndex']and authority['externalParentDeadlineSeconds']==600 and authority['rootOuterDeadlineSeconds']==1800 and authority['expectedCompleteVerifierCalls']==1,'separate1800/600 and one complete helper')
history=read(root['rootObserverHistory']);need(history['ownerActionResultUnchanged']is True and history['kind']=='READER_VARIANT_LABEL_ASSUMPTION','Root observer-only error retained without operation rerun')

candidate=read(root['candidate']);whole=read(root['wholeVerifierFrame']);historical=read(refs['actualVerifierWholeFrame']);metadata=read(refs['metadata']);receipt=read(refs['freezeReceipt'])
need(strict(whole,historical)and root['wholeVerifierFrame']['sha256']==refs['actualVerifierWholeFrame']['sha256'],'entire saved helper frame exact historical bytes and JSON values')
need(len(metadata)==75 and strict(whole['metadata'],metadata),'all75 raw metadata fields and types unchanged')
need(len(metadata['sourceManifest'])==355 and len(metadata['componentizeSourceManifest'])==3 and len(metadata['selectedModuleManifests'])==len(whole['selectedManifests'])==11,'actual355+3/all11')
for r,value in zip(metadata['selectedModuleManifests'],whole['selectedManifests']):
    p=Path(refs['frozenSourceRoot'])/local(r['path']);d,i=actual(p);checked(d);need(d['sha256']==r['sha256']and strict(json.loads(p.read_bytes()),value),'full original manifest '+r['path'])

# Authenticated pure DATA model only, not module import or exporter/helper call.
model_source=(SOURCE/'pin_model.py').read_text();model_tree=ast.parse(model_source);env=dict(copy=copy)
for n in model_tree.body:
    if isinstance(n,ast.Assign):
        for target in n.targets:
            assert isinstance(target,ast.Name);env[target.id]=ast.literal_eval(n.value)
nodes=[n for n in model_tree.body if isinstance(n,ast.FunctionDef)and n.name in ['candidate','unreviewed_document']]
need(len(nodes)==2,'only two pure pin DATA predicates extracted')
exec(compile(ast.Module(body=nodes,type_ignores=[]),'<authenticated pure candidate DATA model only>','exec'),env)
expected=env['unreviewed_document'](env['candidate'](whole,receipt,refs,root['sourceIndex']))
need(strict(candidate,expected),'whole actual candidate equals genuine unreviewed model with strict JSON types')
need(candidate['schemaVersion']==3 and candidate['state']=='UNREVIEWED_SECRET_OWNER355_NORMAL_OFF_PIN_CANDIDATE_V3'and candidate['reviewRequired']is True,'actual unreviewed document remains unreviewed')
need(set(candidate['variants'])=={'normal-off','normal-runtime','gc-off','disabled-off'}and all(candidate['variants'][k]is None for k in candidate['variants']if k!='normal-off'),'exact actual four wire labels/other3NULL')
pin=candidate['variants']['normal-off'];need(pin['state']=='unreviewed-secret-owner355-normal-off-pin-v3'and pin['reviewRequired']is True and strict(pin['verifierFrame'],whole),'normal pin state/complete frame not reviewed or projected')
need(len(pin['frozenFiles'])==1902 and strict(pin['frozenFiles'],[{k:r[k]for k in ['path','sha256','bytes']}for r in receipt['copies']]),'all1902 exact frozen pin entries')
need(pin['enginePath']==refs['engine']['path']and pin['verifierFrame']['metadata']['enginePath']==metadata['enginePath'],'selected frozen engine separate from unchanged raw metadata build path')

frozen_names={'normal-off-freeze-receipt.json'}
for r in receipt['copies']:
    p=Path(r['path']);checked(r);need(p.is_relative_to(Path(refs['frozenRoot']))and p.stat().st_nlink==1,'frozen single-link '+r['path']);frozen_names.add(p.relative_to(refs['frozenRoot']).as_posix())
    if r['original']is not None:
        d=dict(path=r['original'],sha256=r['sha256'],bytes=r['bytes']);checked(d);a=Path(d['path']).stat();b=p.stat();need((a.st_dev,a.st_ino)!=(b.st_dev,b.st_ino),'frozen independent inode '+r['path'])
tree(refs['frozenRoot'],frozen_names,True);need(len(frozen_names)==1903 and sum(r['original']is not None for r in receipt['copies'])==1899,'exact1903 frozen membership/1899 original reference entries')
normal=read(refs['normalProtection']);checked(normal['freezeReceipt'])
for r in normal['frozenCopyEntries']:checked(r)
for r in normal['originals']:checked(r['original']);checked(r['frozen'])
tree(Path(normal['freezeReceipt']['path']).parent,normal['requiredNormalFreezeMembership']);need(len(normal['requiredNormalFreezeMembership'])==1391 and normal['originalReferenceEntries']==1387,'old normal1391/1387 protected')

def terminal(role,timeout,extra):
    t=read(root[role]);folder=Path(root[role]['path']).parent;started=json.loads((folder/'started.json').read_bytes());checked(actual(folder/'started.json')[0])
    need(type(t['rawExitCode'])is int and t['rawExitCode']==0 and t['authority']==root['rootAuthority'],'actual raw-zero authority '+role)
    for k in ['timeout','forcedCleanup']:need(t[k]is False,'no '+k+' '+role)
    for k in ['errors','signals','interruptedSignals','remainingObservedPids']:need(t[k]==[],'empty '+k+' '+role)
    need(t['parentOwnedGroupGone']is t['allObservedOwnedGroupsGone']is True and t['finalGroups']and all(g['alive']is False for g in t['finalGroups']),'all observed owned groups gone '+role)
    for k in ['stdout','stderr']:checked(t[k])
    need(t['stderr']['bytes']==0 and started['pid']==t['pid']and started['timeoutSeconds']==timeout and started['authority']==root['rootAuthority'],'started/raw stream join '+role)
    expected_names={'started.json','terminal.json','stdout.log','stderr.log'}|set(extra)
    seen=[]
    for i,process in enumerate(t['observedProcesses']):
        n='owned-'+str(i).zfill(4)+'.json';r=actual(folder/n)[0];event=read(r);need(event['sequence']==i and event['process']==process,'exact observed process '+role+' '+str(i));expected_names.add(n);seen.append(process)
    need(len({p['pid']for p in seen})==len(seen)and seen[0]['pid']==t['pid']and seen[0]['pgid']==t['pid'],'unique owned PID root '+role)
    tree(folder,expected_names,True)
    return t,started
outer,outer_started=terminal('outerTerminal',1800,['root-observation.json']);inner,inner_started=terminal('innerTerminal',600,[])
need(outer['pid']==86546 and inner['pid']==86731,'actual original parent/worker PIDs')
need(inner['observedProcesses'][0]['ppid']==outer['pid']and any(p==inner['observedProcesses'][0]for p in outer['observedProcesses']),'same inner worker independently observed by outer monitor')
need(len(inner['observedProcesses'])==1 and sum('/Python' in p['command']for p in outer['observedProcesses'])==2,'one real owned helper worker; only two observed Python action processes')
need(all('/Python'in p['command']or p['command']in ['/bin/ps','(ps)']for p in outer['observedProcesses']),'observed process roles Python plus sampler only; no engine/Node role')
for mode,started in [('parent',outer_started),('worker',inner_started)]:
    expected_argv=[refs['python']['path'],'-B','-I',str(SOURCE/'artifact_tooling.py'),mode,'export','--config-descriptor',json.dumps(root['config'],separators=(',',':'))]
    need(started['argv']==expected_argv,'exact original argv/context '+mode)
parent_json=[json.loads(line)for line in Path(outer['stdout']['path']).read_bytes().splitlines()if line]
need(len(parent_json)==2 and parent_json[0]==dict(pid=inner['pid'],timeoutSeconds=600),'two raw parent JSONL records keep PID prefix role')
need(parent_json[1]==dict(observation=root['controllerObservation'],completeUnreviewed=True),'final parent descriptor matches actual observed file')
need(strict(json.loads(Path(inner['stdout']['path']).read_bytes()),candidate),'whole raw worker JSON equals actual unreviewed candidate')
observation=read(root['controllerObservation']);outer_observation=read(root['outerRootObservation'])
need(observation['state']=='SECRET_OWNER355_ARTIFACT_PHASE_COMPLETE_UNREVIEWED_V3'and observation['phase']=='export'and observation['sourceAndOriginalProtectionRechecked']is True and observation['errors']==[],'actual complete source/original protection observation')
need(observation['rootAuthority']==root['rootAuthority']and observation['config']==root['config']and observation['toolingIndex']==root['sourceIndex']and observation['completePhaseReturn']==root['candidate']and observation['wholeVerifierFrame']==root['wholeVerifierFrame']and observation['rawTerminal']==root['innerTerminal'],'all actual inner descriptors/roles')
need(outer_observation['rawTerminal']==root['outerTerminal']and outer_observation['rawParentExitCode']==0 and outer_observation['config']==root['config']and outer_observation['cleanOwnedCleanup']is True,'actual outer observed clean-zero tuple')
out=Path(root['candidate']['path']).parent;raw_observed=read(actual(out/'raw-terminal-observed.json')[0])
need(raw_observed['terminal']==root['innerTerminal']and raw_observed['stdout']==root['innerRawStdout']and raw_observed['stderr']==root['innerRawStderr'],'raw terminal observation retains original stream roles')
tree(out,['candidate-UNREVIEWED.json','whole-verifier-frame.json','controller-observation.json','raw-terminal-observed.json'],True)
need(Path(root['wholeVerifierFrame']['path']).stat().st_ino!=Path(refs['actualVerifierWholeFrame']['path']).stat().st_ino,'new helper frame is independent file despite identical bytes')
for k in ['candidate','wholeVerifierFrame','controllerObservation','outerRootObservation','outerTerminal','innerTerminal','outerRawStdout','outerRawStderr','innerRawStdout','innerRawStderr']:checked(root[k])
driver=Path(authority['rootOuterController']['path']).read_text();ast.parse(driver)
need('monitor.monitor(argv,str(REPO)'in driver.replace(' ','')and '1800' in driver,'Root outer controller genuine explicit monitor call inspected')
source_py=(SOURCE/'artifact_tooling.py').read_text();ast.parse(source_py)
need(source_py.count("helper.verify_frozen(frame['contract'])")==1 and 'sys.modules'not in source_py and 'helper.HERE==VERIFIER'in source_py,'one source-supported original helper call; no context registry projection')
need(root['rawOuterRootControllerExitCode']==0 and root['rootToolSession']==4382,'enclosing Root exit is recorded Root/tool observation only')
for key in ['engineExecuted','guestExecuted','operationalAdmission','runtimeAcceptanceClaim']:need(root[key]is False,'actual scope closed '+key)
for key in ['independentExportReview','reviewedPins','actualBootstrap']:need(root[key]is None,'no later phase adoption '+key)

for path,identity in identities.items():
    p=Path(path);s=p.stat();need((s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,str(p.resolve()))==identity,'final stable '+path)
for base,names,private in list(trees):tree(base,names,private)
write('input-hashes.json',dict(schemaVersion=1,files=list(rows.values()),readHashJsonAstDataOnly=True))
coverage=dict(nativeSources=355,externalEmbeddingSources=3,selectedFullManifests=11,metadataFields=75,frozenCopies=1902,frozenFiles=1903,originalReferenceEntries=1899,oldNormalFrozenFiles=1391,oldNormalOriginalEntries=1387,actualExportOutputFiles=4,actualInnerMonitorFiles=len(inner['observedProcesses'])+4,actualOuterMonitorFiles=len(outer['observedProcesses'])+5,actualInnerOwnedWorkers=1,actualOuterObservedProcesses=len(outer['observedProcesses']),rawParentJsonlRecords=2,unreviewedCandidateVariants=4,otherVariantsNull=3)
write('checks.json',dict(schemaVersion=1,checks=len(checks),names=checks,ownerActionsInvoked=False,pureCandidateModelExtractedForDataOnly=True,operationalEntryHelperMonitorOrNodeRerun=False))
write('audit-results.json',dict(schemaVersion=1,rootObservation=root_row,coverage=coverage,checks=len(checks),rehashedLexicalPaths=len(rows),logicalBytes=sum(r['bytes']for r in rows.values()),typedWholeCandidateMatch=True,wholeHelperFrameUnchanged=True,allSourceOriginalAndFrozenInputsCurrent=True,allObservedOwnedGroupsGone=True,noConcreteActualEvidenceBlockerFound=True,engineOrRuntimeAcceptance=False))
print(json.dumps(dict(state='INDEPENDENT_ACTUAL_EXPORT_DATA_AUDIT_PASSED',checks=len(checks),paths=len(rows),coverage=coverage)))
