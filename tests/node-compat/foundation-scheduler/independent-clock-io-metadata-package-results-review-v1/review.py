"""Independent actual metadata continuation DATA only; no operational imports."""
from pathlib import Path
import hashlib,json,re,stat,tarfile
REPO=Path('/Users/dan/dev/StarlingMonkey');S=REPO/'tests/node-compat/foundation-scheduler'
SOURCE=S/'clock-io-metadata-package-decoder-candidate-v1'
OUTPUT=Path('/private/tmp/starling-node-compat/clock-io-metadata-package-v1')
EXTERNAL=Path('/private/tmp/starling-node-compat/clock-io-metadata-package-v1-external-root')
OBSERVER=Path('/private/tmp/starling-node-compat/clock-io-metadata-package-v1-root-observer')
OWN=Path(__file__).resolve().parent
checks=0;seen={};aliases={};memberships={}
def check(value,label):
    global checks
    assert value,label;checks+=1
def physical(path):
    p=Path(path);check(p.is_absolute()and '..'not in p.parts,'absolute descriptor')
    return Path('/private'+str(p))if str(p).startswith('/tmp/')else p
def d(p):
    p=Path(p);h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return dict(path=str(p),sha256=h.hexdigest(),bytes=p.stat().st_size)
def verify(row):
    row={k:row[k]for k in ['path','sha256','bytes']};p=physical(row['path'])
    for a in (p,*p.parents):check(not a.is_symlink(),'no symlink '+str(a))
    s=p.stat();check(stat.S_ISREG(s.st_mode)and s.st_size==row['bytes'],'regular size '+str(p))
    identity=(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,stat.S_IMODE(s.st_mode),s.st_nlink)
    if str(p)not in seen:check(d(p)['sha256']==row['sha256'],'full original SHA '+str(p));seen[str(p)]=(row,identity)
    else:
        old,i=seen[str(p)];check((old['sha256'],old['bytes'],i)==(row['sha256'],row['bytes'],identity),'consistent alias/context')
    aliases.setdefault(str(p),set()).add(row['path']);return p
def read(row):return json.loads(verify(row).read_bytes())
def load(p):return read(d(p))
def names(root):
    value=set()
    for p in root.rglob('*'):
        check(not p.is_symlink(),'complete tree links')
        if p.is_file():value.add(p.relative_to(root).as_posix())
    return value
def family(row):
    value=read(row);root=physical(row['path']).parent;expected=set();rows=[row]
    for r in value['files']:
        n=r['path'];check(n and not n.startswith('/')and all(x not in ('','.','..')for x in n.split('/'))and n not in expected,'confined unique member')
        expected.add(n);f=dict(path=str(root/n),sha256=r['sha256'],bytes=r['bytes']);verify(f);rows.append(f)
    check(names(root)==expected|{'index.json'},'complete Source/peer family membership');memberships[str(root)]=expected|{'index.json'};return rows
def proof(pair):
    rows=family(pair['index']);check(sum(r==pair['result']for r in rows[1:])==1,'result indexed once');return read(pair['result'])
def clean_terminal(row,authority):
    t=read(row);check(t['schemaVersion']==1 and t['authority']==authority and t['rawExitCode']==0,'clean actual authorized raw0')
    for k in ['timeout','forcedCleanup']:check(t[k]is False,'actual '+k+' false')
    for k in ['interruptedSignals','remainingObservedPids','signals','errors']:check(t[k]==[],'actual empty '+k)
    check(t['parentOwnedGroupGone']is t['allObservedOwnedGroupsGone']is True and t['finalGroups']and all(g['alive']is False for g in t['finalGroups']),'actual owned groups gone')
    for k in ['stdout','stderr']:verify(t[k])
    check(t['stderr']['bytes']==0,'actual stderr empty');return t
def cap_tree(root,terminal):
    check(not root.is_symlink()and stat.S_IMODE(root.stat().st_mode)==0o700,'private capture root')
    start=load(root/'started.json');check(start['pid']==terminal['pid']and start['authority']==terminal['authority'],'actual started tuple')
    events=[]
    for p in sorted(root.glob('owned-*.json')):
        v=load(p);check(v['sequence']==len(events),'raw owned sequence');events.append(v)
    check([v['process']for v in events]==terminal['observedProcesses'],'whole raw owned observations equal terminal')
    expected={'started.json','stdout.log','stderr.log','terminal.json'}|{f'owned-{i:04d}.json'for i in range(len(events))}
    check(names(root)==expected,'complete capture membership');memberships[str(root)]=expected;return start,len(events)
def uleb(raw,i):
    value=0;shift=0
    while True:
        check(i<len(raw)and shift<=35,'bounded unsigned LEB');b=raw[i];i+=1;value|=(b&127)<<shift
        if not b&128:return value,i
        shift+=7
def custom_payloads(row):
    raw=verify(row).read_bytes();check(raw[:8]==b'\0asm\1\0\0\0','actual core wasm header')
    i=8;parts=[]
    while i<len(raw):
        section=raw[i];i+=1;size,i=uleb(raw,i);end=i+size;check(end<=len(raw),'section exact boundary')
        if section==0:
            n,k=uleb(raw,i);name=raw[k:k+n].decode('utf8','strict');k+=n;check(k<=end,'custom name boundary')
            if name.startswith('component-type'):parts.append((name,raw[k:end]))
        i=end
    check(i==len(raw),'whole core sections consumed');return parts
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n')

root_row=dict(path=str(S/'clock-io-metadata-package-v1-root-results.json'),sha256='d1ef64f8940abbf5250e96fed056123f4769ee29d77890f51f3edd1ba5682e76',bytes=3010)
root=read(root_row);refs=load(SOURCE/'references.json');manifest=load(SOURCE/'source-inputs.json')
family(root['sourceIndex']);peer=proof(root['sourcePeer'])
check(root['sourceIndex']['sha256']=='28a8cdab6315394f0479e7a3d9988cedcf4b59ed25bb596ee1fdb40df757ce3a','actual Source28a8')
check(peer['state']=='INDEPENDENT_CLOCK_IO_METADATA_PACKAGE_DECODER_SOURCE_REVIEW_PASSED_V1'and peer['sourceIndexSha256']==root['sourceIndex']['sha256']and peer['sourceOnly']is peer['sourceReviewPassed']is True and peer['ownerActionsInvoked']is False,'actual Source peer e216')
check(len(manifest['files'])==24525,'complete declared protected row count')
for row in manifest['files']:verify(row)
for ix in manifest['families']:family(ix)
for t in refs['oldTrees']:
    check(names(Path(t['root']))==set(t['names']),'old failed-phase exact membership');memberships[t['root']]=set(t['names'])
failure=proof(refs['failedPhaseReview']);contract=read(refs['failedPhaseContract'])
for group in ['requiredFixedValues','requiredExactDescriptors','requiredPairs']:
    for k,v in contract.get(group,{}).items():check(failure[k]==v,'original failure finite contract '+k)
if 'requiredCoverage'in contract:check(failure['coverage']==contract['requiredCoverage'],'original failure full coverage')
check(failure['phasePassed']is failure['adapterAccepted']is failure['metadataDecoded']is False,'old phase remains failed')
check(failure['coreDataAuditPassed']is True and failure['actualWorkerExitCode']==1 and failure['prunerExitCode']==failure['nodeCoreValidationExitCode']==0 and failure['metadataExitCode']==1,'old retained statuses preserved')
for key in ['normalizedAdapter','prunedAdapter','metadataPayload','coreValidation','structuralAudit']:check(failure[key]==refs[key],'old actual tuple '+key);verify(refs[key])
oldroot=read(refs['failedRootObservation']);check(oldroot['state']=='ROOT_OBSERVED_CLOCK_IO_VALID_ADAPTER_FAILED_AT_METADATA_V1','old Root failure state')
authority=read(root['rootAuthority']);config=read(root['rootConfig']);invocation=read(root['invocation'])
check(authority['state']=='ROOT_REVIEWED_CLOCK_IO_METADATA_PACKAGE_PHASE_V1'and authority['phase']=='decode-retained-wit-package-once'and authority['metadataPackageDecodeAllowed']is True,'real metadata-only Root phase')
check(authority['sourceIndex']==root['sourceIndex']==config['sourceIndex'] and config['rootAuthority']==root['rootAuthority']==invocation['authority'],'literal Source/config/Root identities')
check(authority['sourceIndependentReview']==root['sourcePeer']and authority['failedPhaseReview']==refs['failedPhaseReview'],'actual Source/failure proof roles')
for k in ['normalizationAllowed','pruningAllowed','nodeValidationAllowed','adapterPromotionAllowed','defaultPackagerReplacementAllowed','componentAllowed','engineExecutionAllowed','guestAllowed','keyOrCryptoAllowed','nativeBuildAllowed','runtimeAcceptanceClaim','operationalAdmission','timingAllowed']:check(authority[k]is False,'actual phase closed '+k)
check(root['state']=='ROOT_OBSERVED_CLOCK_IO_METADATA_PACKAGE_ZERO_UNREVIEWED_V1'and root['rawExitCode']==0 and root['error']is root['finalProtectionError']is None,'whole Root raw0 report')
check(verify(dict(path=str(OBSERVER/'root-observation.json'),sha256=root_row['sha256'],bytes=root_row['bytes'])).read_bytes()==verify(root_row).read_bytes(),'Root report byte-copy equal')
result=read(root['actualResult']);ix=d(OUTPUT/'index.json');index=read(ix);completion_row=d(OUTPUT/'completion.json');completion=read(completion_row)
expected=set()
for r in index['files']:
    n=r['path'];check(n not in expected and n in {'external-inventory.json','metadata-raw-observed.json','result.json','wit-observations.json'},'finite output member')
    expected.add(n);verify(dict(path=str(OUTPUT/n),sha256=r['sha256'],bytes=r['bytes']))
check(len(expected)==4 and names(OUTPUT)==expected|{'index.json','completion.json'},'producer index4 plus separate completion exact membership')
memberships[str(OUTPUT)]=expected|{'index.json','completion.json'}
check(completion==dict(schemaVersion=1,state='COMPLETE_UNREVIEWED',index=ix,result=root['actualResult'],metadataDecoded=True,operationalAdmission=False),'whole completion actual index/result equality')
check(stat.S_IMODE(OUTPUT.stat().st_mode)==0o700,'private output root')
output_ids=[]
for n in names(OUTPUT):
    p=OUTPUT/n;t=p.stat();check(stat.S_IMODE(t.st_mode)==0o600 and t.st_nlink==1,'private single-link actual output');output_ids.append((t.st_dev,t.st_ino))
check(len(set(output_ids))==6,'distinct output inodes')
check(result['state']=='CLOCK_IO_METADATA_PACKAGE_COMPLETE_UNREVIEWED_V1'and result['sourceIndex']==root['sourceIndex']and result['rootAuthority']==root['rootAuthority']and result['config']==root['rootConfig'],'whole actual result phase identity')
for k in ['normalizedAdapter','prunedAdapter','metadataPayload','wasmTools','failedRootObservation','failedPhaseReview']:check(result[k]==refs[k],'result immutable actual '+k)
for k in ['normalizerOrPrunerRerun','nodeValidationRerun','applicationEngineOrGuestExecuted','adapterPromoted','defaultPackagerReplaced','operationalAdmission','runtimeAcceptanceClaim','previousPhasePassed']:check(result[k]is False,'result closed '+k)
check(result['previousPhaseRemainsFailed']is result['metadataDecoded']is result['wholeGraphRenderRequired']is result['nativeMetadataDecoderAttempted']is True and result['sourceBoundedMaximumDecoderCalls']==1 and result['error']is result['finalProtectionError']is None,'metadata-only actual success bounds')
outer=clean_terminal(root['ownedParentTerminal'],root['rootAuthority']);outer_start,outer_count=cap_tree(OBSERVER/'parent',outer)
inner=clean_terminal(result['command']['terminal'],root['rootAuthority']);inner_start,inner_count=cap_tree(EXTERNAL/'metadata-wit',inner)
check(outer_start['timeoutSeconds']==300 and outer_start['argv']==invocation['argv'],'actual enclosing300s argv')
check(inner_start['timeoutSeconds']==60 and inner_start['argv']==[refs['wasmTools']['path'],'component','wit',refs['metadataPayload']['path']],'sole retained native decode60s exact argv')
check(inner['pid']in[r['pid']for r in outer['observedProcesses']]and inner['observedProcesses'][0]['ppid']==outer['pid'],'nested owned lineage retained')
check(result['command']==load(OUTPUT/'metadata-raw-observed.json')==dict(terminal=d(EXTERNAL/'metadata-wit/terminal.json'),stdout=inner['stdout'],stderr=inner['stderr'],rawExitCode=0),'whole primitive native return observation')
check(root['stdout']==outer['stdout']and root['stderr']==outer['stderr'],'Root whole outer stream descriptors')
outer_rows=[json.loads(s)for s in verify(outer['stdout']).read_bytes().splitlines()]
check(outer_rows==[dict(pid=inner['pid'],timeoutSeconds=60),root['actualResult']],'whole native-launch prefix plus returned parent output descriptor')
inventory=load(OUTPUT/'external-inventory.json');check(len(inventory['files'])==5,'all five native external files')
for r in inventory['files']:verify(r)
check({str(physical(r['path']).relative_to(EXTERNAL))for r in inventory['files']}==names(EXTERNAL),'complete external native inventory')
memberships[str(EXTERNAL)]=names(EXTERNAL);memberships[str(OBSERVER)]=names(OBSERVER)
raw=verify(result['fullWit']).read_bytes();check(result['fullWit']==inner['stdout']and len(raw)==15184 and hashlib.sha256(raw).hexdigest()=='6d4b608e27df232ced75558a37088500e39b1cfb0362b12929b7b1d854b8fda7','whole exact WIT stdout')
text=raw.decode('utf8','strict');check('\x00'not in text and '\x1b'not in text,'plain complete strict UTF8 render')
# Independent finite text observations, not a fresh WIT semantic parser.
package=None;packages=[];declarations={};bodies={}
for line in text.splitlines():
    p=re.fullmatch(r'package (wasi:[a-z-]+@0\.2\.0)\s*[;{]',line)
    if p:package=p.group(1);packages.append(package)
    q=re.fullmatch(r'\s*(interface|world) ([a-z][a-z0-9-]*) \{',line)
    if q:
        check(package is not None,'package-qualified declaration');ns,version=package.split('@');key=ns+'/'+q.group(2)+'@'+version
        check(key not in declarations,'unique whole declaration');declarations[key]=q.group(1)
        start=text.index(line)+len(line);i=start;depth=1
        while i<len(text)and depth:
            if text[i]=='{':depth+=1
            elif text[i]=='}':depth-=1
            i+=1
        check(depth==0,'complete declaration body');bodies[key]=text[start:i-1]
observations=read(result['witObservations']);check(sorted(packages)==observations['packages']==refs['expectedWitDeclarations']['packages'],'six exact package identities0.2.0')
check(declarations==observations['declarations']and sorted(declarations)==refs['expectedWitDeclarations']['declarations']and len(declarations)==28,'all28 whole qualified declarations')
check(sum(v=='interface'for v in declarations.values())==27 and declarations['wasi:cli/imports@0.2.0']=='world','27interfaces+one imports world')
check(len(observations['observedResourceAliasClauses'])==10,'ten actual resource/alias clauses')
for r in observations['observedResourceAliasClauses']:check(re.sub(r'\s+','',r['clause'])in re.sub(r'\s+','',bodies[r['declaration']]),'raw declaration exact resource alias')
payload=verify(refs['metadataPayload']).read_bytes();check(payload[:8]==b'\0asm\x0d\0\1\0','encoded WIT component header')
normal=custom_payloads(refs['normalizedAdapter']);pruned=custom_payloads(refs['prunedAdapter'])
check(len(normal)==len(pruned)==1 and normal==pruned and normal[0][1]==payload,'one unchanged whole component-type payload in actual normalized and pruned cores')
archive=verify(refs['wasmToolsArchive']);verify(refs['wasmTools'])
with tarfile.open(archive,'r:gz')as tar:
    candidates=[m for m in tar.getmembers()if m.isfile()and m.name.split('/')[-1]=='wasm-tools'];check(len(candidates)==1,'one native wasm-tools archive member')
    h=hashlib.sha256();size=0
    with tar.extractfile(candidates[0])as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block);size+=len(block)
    check((h.hexdigest(),size)==(refs['wasmTools']['sha256'],refs['wasmTools']['bytes']),'actual native tool byte-equals pinned release archive member')
raw_copies=[];evidence=S/'clock-io-metadata-package-v1-root-evidence'
mapping={'output':OUTPUT,'monitor':EXTERNAL,'root':OBSERVER}
for p in sorted(evidence.rglob('*')):
    check(not p.is_symlink(),'retained raw copies links')
    if not p.is_file():continue
    name=p.relative_to(evidence);source=mapping[name.parts[0]]/Path(*name.parts[1:]);a=verify(d(source));b=verify(d(p))
    check(a.read_bytes()==b.read_bytes()and(a.stat().st_dev,a.stat().st_ino)!=(b.stat().st_dev,b.stat().st_ino),'whole independent retained raw copy')
    raw_copies.append(name.as_posix())
check(len(raw_copies)==18,'all18 retained raw text files');memberships[str(evidence)]=set(raw_copies)
# Final complete physical protection bookend after all raw interpretation.
for path,(r,i)in seen.items():
    p=Path(path);s=p.stat();check((s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,stat.S_IMODE(s.st_mode),s.st_nlink)==i,'final original identity/mode/link')
    check(d(p)['sha256']==r['sha256'],'final whole original hash')
for path,expected in memberships.items():check(names(Path(path))==expected,'final full membership')
write(OWN/'input-hashes.json',dict(schemaVersion=1,files=[dict(**r,physicalPath=p,originalDescriptorPaths=sorted(aliases[p]),mode=i[-2],links=i[-1])for p,(r,i)in sorted(seen.items())]))
write(OWN/'whole-wit-observations.json',dict(schemaVersion=1,packages=sorted(packages),declarations=declarations,resourceAliasClauses=observations['observedResourceAliasClauses'],fullWit=result['fullWit'],finiteTextObservationsOnly=True,nativeSemanticTypeDecodeFromRetainedActualCall=True,reviewerDecoderOrParserCommandInvoked=False,applicationImportFootprintInferred=False))
write(OWN/'audit-data.json',dict(schemaVersion=1,state='INDEPENDENT_CLOCK_METADATA_PACKAGE_ACTUAL_DATA_AUDIT_PASSED',checks=checks,uniqueInputFiles=len(seen),inputBytes=sum(r['bytes']for r,i in seen.values()),protectedDeclaredRows=24525,fixedFamilies=12,sourceIndex=root['sourceIndex'],sourcePeer=root['sourcePeer'],actualResult=root['actualResult'],actualIndex=ix,actualCompletion=completion_row,rootObservation=root_row,rootAuthority=root['rootAuthority'],rootConfig=root['rootConfig'],rootInvocation=root['invocation'],outerTerminal=root['ownedParentTerminal'],nativeTerminal=result['command']['terminal'],nativeTool=refs['wasmTools'],normalizedAdapter=refs['normalizedAdapter'],prunedAdapter=refs['prunedAdapter'],metadataPayload=refs['metadataPayload'],fullWit=result['fullWit'],packages=6,declarations=28,resourceAliasClauses=10,outerObservedProcesses=outer_count,nativeObservedProcesses=inner_count,retainedRawCopies=18,outputIndexedFiles=4,outputActualFiles=6,previousPhasePassed=False,normalizerOrPrunerOrNodeValidatorRerun=False,reviewerOperationalActionsInvoked=False))
print((OWN/'audit-data.json').read_text())
