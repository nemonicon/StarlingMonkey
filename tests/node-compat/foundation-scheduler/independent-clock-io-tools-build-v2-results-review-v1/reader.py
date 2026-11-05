"""Independent completed-build DATA audit. No owner imports/tools/actions."""
from pathlib import Path
import ast,hashlib,json,os,re,stat,struct,tarfile
HERE=Path(__file__).resolve().parent;REPO=Path('/Users/dan/dev/StarlingMonkey');S=REPO/'tests/node-compat/foundation-scheduler'
BASE=Path('/private/tmp/starling-node-compat');SOURCE=BASE/'import-abi-clock-io-v1-source';WORK=BASE/'import-abi-clock-io-v1-build';PACKAGE=BASE/'import-abi-clock-io-v1-package';EXTERNAL=BASE/'import-abi-clock-io-v1-build-v2-external-root';OUTER=BASE/'import-abi-clock-io-v1-build-v2-root-observer'
checks=[];rows={};identities={};families=[];trees=[]
def need(v,n):
    assert v,n;checks.append(n)
def write(n,v):(HERE/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def regular(path):
    p=Path(path);a=p.stat();need(p.is_absolute()and p.is_file()and not p.is_symlink(),'regular input '+str(p));h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    z=p.stat();key=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,str(p.resolve()))
    need(key(a)==key(z),'stable hash '+str(p));r=dict(path=str(p),sha256=h.hexdigest(),bytes=z.st_size)
    if str(p)in rows:need(rows[str(p)]==r and identities[str(p)]==key(z),'consistent reread '+str(p))
    rows[str(p)]=r;identities[str(p)]=key(z);return r

def verify(r):
    d={k:r[k]for k in ['path','sha256','bytes']}
    if d['path']in rows:need(rows[d['path']]==d,'exact duplicate descriptor')
    else:need(regular(d['path'])==d,'exact retained descriptor '+d['path'])
    return Path(d['path'])
def decode(raw):
    def unique(pairs):
        result={}
        for k,v in pairs:need(k not in result,'unique JSON key');result[k]=v
        return result
    return json.loads(raw,object_pairs_hook=unique)
def read(r):p=verify(r);need(r['bytes']<=32*1024*1024,'bounded JSON read');return decode(p.read_bytes())
def local(n):need(type(n)is str and n and not n.startswith('/')and '\\'not in n and '\0'not in n and all(x not in ['','.','..']for x in n.split('/')),'confined local path');return n

def family(ix):
    v=read(ix);root=Path(ix['path']).parent;names={'index.json'}
    for r in v['files']:
        name=local(r['path']);need(name not in names,'unique family member');names.add(name);verify(dict(path=str(root/name),sha256=r['sha256'],bytes=r['bytes']))
    need(not any(q.is_symlink()for q in root.rglob('*'))and{q.relative_to(root).as_posix()for q in root.rglob('*')if q.is_file()}==names,'full immutable family membership '+str(root));families.append(dict(index=ix,names=sorted(names)));return v

def clean(t,authority):
    need(type(t['rawExitCode'])is int and t['rawExitCode']==0 and t['authority']==authority,'actual raw zero/authority')
    for k in ['timeout','forcedCleanup']:need(t[k]is False,'no '+k)
    for k in ['parentOwnedGroupGone','allObservedOwnedGroupsGone']:need(t[k]is True,k)
    for k in ['errors','signals','interruptedSignals','remainingObservedPids']:need(t[k]==[],k+' empty')
    need(t['finalGroups']and all(g['alive']is False and g['signalAllowed']is False for g in t['finalGroups']),'all retained final groups gone/non-signalable')
    verify(t['stdout']);verify(t['stderr'])
    pids=[(x['pid'],x['birth'])for x in t['observedProcesses']];need(len(pids)==len(set(pids)),'unique retained observed process identities')
    need(any(p['pid']==t['pid']for p in t['observedProcesses']),'owned root identity witnessed')

def jsonl(r):
    p=verify(r);return[decode(s)for s in p.read_text().splitlines()if s]

def tree_inventory(root,private=False):
    files=[];links=[];need(root.is_dir()and not root.is_symlink(),'actual output root')
    for p in sorted(root.rglob('*')):
        rel=p.relative_to(root).as_posix();m=p.lstat()
        if p.is_symlink():links.append(dict(path=rel,target=os.readlink(p),resolved=str(p.resolve())));continue
        if p.is_dir():
            if private:need(stat.S_IMODE(m.st_mode)==0o700,'private directory '+str(p))
        else:
            need(p.is_file(),'ordinary output member');r=regular(p)if str(p)not in rows else rows[str(p)]
            files.append(dict(r,relativePath=rel,mode=stat.S_IMODE(m.st_mode),device=m.st_dev,inode=m.st_ino,links=m.st_nlink))
    result=dict(root=str(root),files=files,links=links);trees.append(result);return result

root_row=dict(path=str(OUTER/'root-observation.json'),sha256='6844e920cf356bb356b70a2cf17b927d7746924770d788340a7fcdf1d4cffffe',bytes=4960)
root=read(root_row);need(root['state']=='ROOT_OBSERVED_CLOCK_IO_TOOL_BUILD_PARENT_ZERO_UNREVIEWED_V2','actual Root completed build state')
for key,sha in [('sourceIndex','55338bc0e5e0f47ed473ccd283ed1eae70183f081abb8f6a61e5c8001711945f'),('controllerIndex','41b22225b82628e901a8350f33d3150846e3e0e777aa23e561239e0985a50be9')]:need(root[key]['sha256']==sha,'exact Source subject');family(root[key])
for key,state,subject in [('sourceReview','INDEPENDENT_SCHEDULER_CLOCK_IO_PRUNING_SOURCE_REVIEW_PASSED_V1','sourceIndexSha256'),('controllerReview','INDEPENDENT_CLOCK_IO_BUILD_CONTROLLER_SOURCE_REVIEW_PASSED_V2','controllerSourceIndexSha256')]:
    pair=root[key];v=family(pair['index']);need(pair['result']in[dict(r,path=str(Path(pair['index']['path']).parent/r['path']))for r in v['files']],'peer result indexed');proof=read(pair['result']);need(proof['state']==state and proof['sourceOnly']is proof['sourceReviewPassed']is True and proof['ownerActionsInvoked']is False,'actual independent Source peer');need(proof[subject]==root['sourceIndex'if key=='sourceReview'else'controllerIndex']['sha256'],'peer exact Source hash')
controller=Path(root['controllerIndex']['path']).parent;proposal=Path(root['sourceIndex']['path']).parent;inputs=read(regular(controller/'source-inputs.json'));need(len(inputs['files'])==5667,'full5667 fixed Source inputs')
for r in inputs['files']:verify(r)
for f in inputs['families']:family(f['index'])
for a in inputs['links']:
    p=Path(a['path']);need(p.is_symlink()and os.readlink(p)==a['target']and str(p.resolve())==a['resolved']['path'],'original JS alias unchanged');verify(a['resolved'])
authority=read(root['rootAuthority']);cfg=read(root['config']);verify(root['rootOuterController']);need(root['rootOuterController']['sha256']=='ad6bae37c0caa6494503cf71c5641a73d48d5125a34ea5e480aa3252d5100368','actual outer Root controller bytes')
need(cfg==dict(schemaVersion=1,state='CLOCK_IO_BUILD_CONTROLLER_CONFIG_V2',controllerIndex=root['controllerIndex'],rootAuthority=root['rootAuthority']),'actual config exact original schema/context')
need(authority['controllerIndex']==root['controllerIndex']and authority['sourceIndex']==root['sourceIndex']and authority['sourceReview']==root['sourceReview']and authority['controllerReview']==root['controllerReview']and authority['rootOuterController']==root['rootOuterController'],'Root/Source/proof pairing')
need(authority['state']=='ROOT_REVIEWED_CLOCK_IO_TOOLS_BUILD_V2'and authority['phase']=='build-clock-io-tools'and authority['deadlineSeconds']==authority['rootOuterDeadlineSeconds']==7200,'actual bounded issued build phase')
for key in ['stageAllowed','privateVendorAllowed','downloadThreeLockedArchivesAllowed','rustBuildAndUnitTestsAllowed','jcoToolPackagingAllowed','prunerRefusalUnitTestAllowed']:need(authority[key]is True,'actual permitted '+key)
for key in ['adapterPublicationAllowed','adapterPruningAllowed','validAdapterPruningAllowed','nativeEngineBuildAllowed','applicationComponentAllowed','applicationGuestAllowed','keyOrCryptoAllowed','timingAllowed','sourcePromotionAllowed','operationalAdmission','runtimeAcceptanceClaim']:need(authority[key]is False,'no actual authority '+key)
need(authority['sourceRoot']==str(SOURCE)and authority['workRoot']==str(WORK)and authority['packageRoot']==str(PACKAGE)and authority['externalRoot']==str(EXTERNAL)and authority['rootObserverOutput']==str(OUTER),'actual original output roles')
outer=read(root['terminal']);clean(outer,root['rootAuthority']);need(outer['stderr']['bytes']==0 and root['streams']==dict(stdout=outer['stdout'],stderr=outer['stderr']),'full actual outer streams')
parent_lines=jsonl(outer['stdout']);need(len(parent_lines)==2 and parent_lines[0]['timeoutSeconds']==7200,'exact two outer JSONL records')
parent_row=root['buildObservation']['parentObservation'];parent=read(parent_row);need(parent_lines[-1]==dict(observation=parent_row,completeUnreviewed=True),'outer final exact observation envelope and whole parent descriptor')
need(parent['state']=='CLOCK_IO_BUILD_CONTROLLER_COMPLETE_UNREVIEWED_V2'and parent['rootAuthority']==root['rootAuthority']and parent['protectedInputsRechecked']is True and parent['errors']==[],'actual parent complete Source-protected frame')
inner=read(parent['rawTerminal']);clean(inner,root['rootAuthority']);need(inner['pid']==parent_lines[0]['pid']and inner['stderr']['bytes']==0,'actual worker PID/whole empty stderr')
worker_lines=jsonl(inner['stdout']);need(len(worker_lines)==9,'exact nine worker JSONL records');worker_row=root['buildObservation']['workerResult'];need(worker_lines[-1]==worker_row,'whole actual worker descriptor')
worker=read(worker_row);need(worker['state']=='CLOCK_IO_TOOLS_BUILD_COMPLETE_UNREVIEWED_V2'and worker['rootAuthority']==root['rootAuthority']and worker['error']is worker['finalProtectionError']is None and worker['protectedInputsRechecked']is worker['privatePackageMembershipVerified']is True,'actual worker complete/protected/private state')
need(parent['workerObservation']['workerResult']==worker_row and parent['workerObservation']['rawWorkerStdout']==inner['stdout']and parent['workerObservation']['rawWorkerStderr']==inner['stderr'],'whole parent/worker bindings')
for value in [root,parent,worker]:
    need(value['prunerFunctionInvokedByRefusalUnitTest']is True and value['validAdapterPruningRun']is value['adapterCliPruneCommandInvoked']is value['operationalAdmission']is value['runtimeAcceptanceClaim']is False,'invalid pruner unit distinct from no valid pruning/runtime')

# Independent reconstruction of the four original command plans + four filters.
plan=read(regular(proposal/'future-build-plan.json'));tools=read(regular(proposal/'tool-cut-references.json'));cut=read(regular(proposal/'source-cut.json'));host=read(regular(controller/'host-context.json'))
filters=['adapter_input_guard_refuses_unknown_payloads_before_parse','pure_and_clock_only_keep_distinct_capabilities','stream_profiles_keep_poll_and_stream_transport','explicitly_selected_world_io_is_retained'];commands=[]
for i,p in enumerate(plan['commandPlans']):
    argv=list(p['argv'])
    if i<2:argv+=['--jobs','1']
    else:argv[1]=str(PACKAGE/'node_modules/@bytecodealliance/jco/dist/jco.js')
    commands.append(dict(name=p['role'].lower(),argv=argv,timeout=1800 if i<2 else 600,unit=None))
    if i==0:
        for f in filters:commands.append(dict(name='unit-'+f,argv=[tools['cargo']['path'],'test','--locked','--offline','--release','-p','spidermonkey-embedding-splicer','--lib','--target','aarch64-apple-darwin','--target-dir',str(WORK/'target'),'--jobs','1','clock_io_policy_tests::'+f,'--','--nocapture'],timeout=600,unit=f))
need(len(commands)==len(worker['commandTerminals'])==8 and sum(c['timeout']for c in commands)==7200,'all eight derived commands and shared budgets')
command_audit=[]
for i,(expected,row)in enumerate(zip(commands,worker['commandTerminals'])):
    summary=read(row);terminal=read(summary['monitorTerminal']);clean(terminal,root['rootAuthority']);need(summary['argv']==expected['argv']and summary['cwd']==str(SOURCE)and summary['timeoutSeconds']==expected['timeout'],'actual exact command argv/cwd/timeout '+expected['name'])
    need(worker_lines[i]==dict(pid=terminal['pid'],timeoutSeconds=expected['timeout']),'actual ordered worker launch record')
    need(summary['rawExitCode']==0 and summary['timeout']is False and summary['streamsClipped']is False and summary['availableStreamsFsynced']is True and summary['rawMonitorCallReturned']is True and summary['callFailure']is None,'actual summary raw-zero/fsync/source-controlflow flags')
    need(summary['streams']==dict(stdout=terminal['stdout'],stderr=terminal['stderr']),'actual complete command streams')
    need(summary['beforeFreeBytes']>=838860800 and summary['afterFreeBytes']>=838860800 and summary['preSpaceObservationError']is summary['postSpaceObservationError']is None and summary['diskFloorCheckedBeforeAndAfter']is True and summary['diskFloorMonitoredDuringCommand']is False and summary['beforeFloorPassed']is summary['afterFloorPassed']is True,'actual boundary disk observations; no continuous monitoring')
    if expected['unit']:
        text=verify(terminal['stdout']).read_text();need(len(re.findall(r'^running 1 test$',text,re.M))==1,'exact one selected test');need(len(re.findall(r'^test stub_wasi::clock_io_policy_tests::'+re.escape(expected['unit'])+r' \.\.\. ok$',text,re.M))==1,'exact intended unit name');need(len(re.findall(r'^test result: ok\. 1 passed; 0 failed; 0 ignored; 0 measured; 3 filtered out;',text,re.M))==1,'one passed/zero failed/not ignored')
    command_audit.append(dict(name=expected['name'],argv=summary['argv'],timeoutSeconds=summary['timeoutSeconds'],summary=row,terminal=summary['monitorTerminal'],stdout=terminal['stdout'],stderr=terminal['stderr'],beforeFreeBytes=summary['beforeFreeBytes'],afterFreeBytes=summary['afterFreeBytes'],unit=expected['unit'],rawExitCode=0,ownedProcessIdentities=len(terminal['observedProcesses']),finalGroups=len(terminal['finalGroups'])))
need(root['beforeFreeBytes']>=2147483648 and root['afterFreeBytes']>=838860800 and root['diskFloorCheckedBeforeAndAfter']is True and root['diskFloorMonitoredDuringCommand']is False and root['preSpaceObservationError']is root['postSpaceObservationError']is None,'actual Root boundary observations')

# Reconstruct all5138 copy targets +118 cached archive copies without owner code.
stage=read(worker['stageReceipt']);need(len(stage['copies'])==5256 and stage['sources']==271 and stage['jsToolFiles']==4862 and stage['jsAliases']==21 and stage['originalSourceOrCacheModified']is False and stage['allOutputsFresh']is True,'actual finite stage counts/qualified Source flags')
modes={r['relativePath']:r['mode']for r in cut['baseline']['files']};expected_copies=[]
for item in cut['files']:
    n=local(item['path']);src=item['baseline']if item['origin']=='UNCHANGED_BASELINE'else dict(path=str(proposal/'after'/n),sha256=item['sha256'],bytes=item['bytes']);expected_copies.append(dict(source=src,destination=dict(path=str(SOURCE/n),sha256=item['sha256'],bytes=item['bytes']),mode=modes[n]))
by_name={r['path']:r for r in cut['files']}
for n in plan['packageSourceFiles']:
    item=by_name[n];expected_copies.append(dict(source=dict(path=str(SOURCE/n),sha256=item['sha256'],bytes=item['bytes']),destination=dict(path=str(PACKAGE/n),sha256=item['sha256'],bytes=item['bytes']),mode=0o600))
for item in tools['jsToolchain']['files']:
    n=local(item['relativePath']);target=n if n.startswith('node_modules/')else'.toolchain-metadata/'+n;expected_copies.append(dict(source=item['descriptor'],destination=dict(item['descriptor'],path=str(PACKAGE/target)),mode=item['mode']))
need(len(expected_copies)==5138,'271+5+4862 original copy reconstruction')
for item in tools['lockedRegistryArchives']:expected_copies.append(dict(source=item['descriptor'],destination=dict(item['descriptor'],path=str(WORK/'locked-archives'/(item['name']+'-'+item['version']+'.crate'))),mode=0o600))
need(stage['copies']==expected_copies,'all5256 exact original/destination/mode tuples')
for r in stage['copies']:
    a=verify(r['source']).stat();b=verify(r['destination']).stat();need(b.st_nlink==1 and(a.st_dev,a.st_ino)!=(b.st_dev,b.st_ino)and stat.S_IMODE(b.st_mode)==r['mode'],'every independent actual copy inode/mode')
for r in cut['baseline']['files']:need(stat.S_IMODE(Path(r['descriptor']['path']).stat().st_mode)==r['mode'],'protected original source mode')
for r in tools['jsToolchain']['files']:need(stat.S_IMODE(Path(r['descriptor']['path']).stat().st_mode)==r['mode'],'protected original JS mode')
# Every locked archive is compared with actual private bytes and every unpacked
# regular member. This is read/decode only, never tar extraction or crate code.
locked={r['name']+'-'+r['version']:dict(r,sha256=r['descriptor']['sha256'])for r in tools['lockedRegistryArchives']}
for r in tools['missingLockedRegistryArchives']:locked[r['name']+'-'+r['version']]=r
need(len(locked)==121 and len(stage['vendored'])==121,'121 exact locked crates')
vendor_audit=[];vendor_total=0
for item in stage['vendored']:
    name=item['name']+'-'+item['version'];pin=locked[name];archive=verify(item['archive']);need(item['archive']['sha256']==pin['sha256'],'actual locked archive SHA '+name)
    expected_files={};dirs=set();unpacked=0
    with tarfile.open(archive,'r:*')as bundle:
        members=list(bundle);need(len(members)<=16384,'finite archive metadata '+name)
        for m in members:
            if m.isdir()and m.name.rstrip('/')==name:continue
            need(m.name.startswith(name+'/'),'literal archive prefix');n=local(m.name[len(name)+1:].rstrip('/')if m.isdir()else m.name[len(name)+1:]);need(n!='.cargo-checksum.json'and n not in expected_files,'no generated-checksum/duplicate archive file')
            need(not any(q.as_posix()in expected_files for q in Path(n).parents if q.as_posix()!='.'),'no file-as-parent')
            if m.isdir():need(n not in dirs,'unique archive directory');dirs.add(n);continue
            need(m.isfile()and n not in dirs and not any(q.startswith(n+'/')for q in set(expected_files)|dirs),'only independent regular tar files, no links/devices')
            need(0<=m.size<=32*1024*1024,'bounded member');unpacked+=m.size;need(unpacked<=128*1024*1024,'bounded crate');h=hashlib.sha256();count=0
            with bundle.extractfile(m)as stream:
                for b in iter(lambda:stream.read(1024*1024),b''):h.update(b);count+=len(b)
            need(count==m.size,'complete decoded member');expected_files[n]=h.hexdigest();dest=WORK/'vendor'/name/n;actual=regular(dest)if str(dest)not in rows else rows[str(dest)];need(actual['sha256']==h.hexdigest()and actual['bytes']==m.size and stat.S_IMODE(dest.stat().st_mode)==(0o700 if m.mode&0o111 else 0o600),'exact private vendor member bytes/mode')
    checksum=read(regular(WORK/'vendor'/name/'.cargo-checksum.json'));need(checksum==dict(files=expected_files,package=pin['sha256']),'actual Cargo checksum map whole equality '+name)
    actual_names={q.relative_to(WORK/'vendor'/name).as_posix()for q in(WORK/'vendor'/name).rglob('*')if q.is_file()};need(actual_names==set(expected_files)|{'.cargo-checksum.json'}and'Cargo.toml'in expected_files,'exact vendor crate membership')
    need(item['files']==len(expected_files)and item['unpackedBytes']==unpacked,'actual vendor receipt metrics');vendor_total+=unpacked;vendor_audit.append(dict(name=item['name'],version=item['version'],archive=item['archive'],files=len(expected_files),unpackedBytes=unpacked,checksum=regular(WORK/'vendor'/name/'.cargo-checksum.json')))
need(vendor_total<=512*1024*1024,'bounded121-crate aggregate')
for pin in tools['missingLockedRegistryArchives']:need(not Path(pin['expectedPath']).exists()and not Path(pin['expectedPath']).is_symlink(),'missing global cached archive still absent '+pin['name'])
config_text='[source.crates-io]\nreplace-with = "private-vendor"\n[source.private-vendor]\ndirectory = '+json.dumps(str(WORK/'vendor'))+'\n[net]\noffline = true\n'
need(verify(stage['stageInventory']['cargoConfig']).read_text()==config_text and stage['privateCargoHome']==str(WORK/'cargo-home'),'exact private offline Cargo replacement config')
for ancestor in [SOURCE,*SOURCE.parents]:
    for n in ['.cargo/config','.cargo/config.toml']:need(not(ancestor/n).exists()and not(ancestor/n).is_symlink(),'no Source ancestor Cargo override')
# Receipt vendor/archive hashes are unchanged since pre-command inventory.
for r in stage['stageInventory']['vendor']['files']:verify(r)
for r in stage['stageInventory']['archives']:verify(r)

private_row=regular(WORK/'private-package-inventory.json');private=read(private_row)
for key,base in [('source',SOURCE),('package',PACKAGE)]:
    inventory=private[key];need(inventory['root']==str(base),'actual final inventory root')
    for r in inventory['files']:verify(r);need(stat.S_IMODE(Path(r['path']).stat().st_mode)==r['mode'],'final actual recorded file mode')
    need({q.relative_to(base).as_posix()for q in base.rglob('*')if q.is_file()and not q.is_symlink()}=={r['relativePath']for r in inventory['files']},'exact final source/package regular membership')
need(len(private['source']['files'])==271 and private['source']['links']==[],'all271 new source files/no source aliases')
expected_package={r['destination']['path']for r in expected_copies if r['destination']['path'].startswith(str(PACKAGE)+'/')};generated=private['generatedFiles'];need(len(generated)==22 and len(private['package']['files'])==4889,'actual generated22/newpackage4889')
need({r['path']for r in private['package']['files']}==expected_package|{r['path']for r in generated},'no undeclared package files or metadata replacement')
need(all(r['relativePath'].startswith('lib/')and re.fullmatch(r'lib/.+\.(js|wasm|ts)',r['relativePath'])for r in generated)and sum(r['bytes']for r in generated)<=256*1024*1024,'bounded generated library namespace')
link_map={r['path']:r for r in private['package']['links']};need(len(link_map)==len(tools['jsToolchain']['symlinks'])==21,'all21 private aliases')
for a in tools['jsToolchain']['symlinks']:
    p=PACKAGE/a['path'];need(p.is_symlink()and os.readlink(p)==a['target']and p.resolve().is_relative_to(PACKAGE),'exact confined private alias');r=link_map[a['path']];need(r['target']==a['target']and r['resolvedPath']==str(p.resolve()),'actual relative alias row and distinct absolute target path');resolved=regular(p.resolve())if str(p.resolve())not in rows else rows[str(p.resolve())];need(resolved['sha256']==a['resolved']['sha256']and resolved['bytes']==a['resolved']['bytes'],'alias actual target bytes match original cut')
artifacts=worker['artifacts'];need(len(artifacts)==25 and artifacts[:3]==[regular(WORK/'target/aarch64-apple-darwin/release/splicer'),regular(WORK/'target/wasm32-wasip1/release/splicer_component.wasm'),regular(WORK/'splicer.wasm')],'actual three main built artifacts')
need(artifacts[3:]==[{k:r[k]for k in ['path','sha256','bytes']}for r in generated],'all22 generated artifacts exact list')
for r in artifacts:verify(r)
# Static byte/header audit only: do not execute native binary or generated glue.
host_binary=verify(artifacts[0]).read_bytes();magic,cpu,sub,filetype,ncmds,cmdbytes,flags,reserved=struct.unpack_from('<IiiIIIII',host_binary)
need(magic==0xfeedfacf and cpu==0x100000c and filetype==2 and 32+cmdbytes<=len(host_binary),'actual arm64 Mach-O executable header')
pos=32;symbols=[]
for _ in range(ncmds):
    cmd,size=struct.unpack_from('<II',host_binary,pos);need(size>=8 and pos+size<=32+cmdbytes,'bounded Mach-O load command')
    if cmd==2:
        symoff,nsyms,stroff,strsize=struct.unpack_from('<IIII',host_binary,pos+8);need(symoff+nsyms*16<=len(host_binary)and stroff+strsize<=len(host_binary),'bounded static symbol/string tables')
        for i in range(nsyms):
            name_index=struct.unpack_from('<I',host_binary,symoff+i*16)[0];need(name_index<strsize,'bounded symbol name index');end=host_binary.find(b'\0',stroff+name_index,stroff+strsize);need(end>=0,'terminated symbol name');name=host_binary[stroff+name_index:end].decode('utf8','replace')
            if 'prune_clock_adapter_io'in name:symbols.append(name)
    pos+=size
need(pos==32+cmdbytes,'complete Mach-O load command table')
for r in [artifacts[1],artifacts[2],*[x for x in generated if x['path'].endswith('.wasm')]]:
    data=verify(r).read_bytes();need(data[:4]==b'\0asm'and data[4:8]in[b'\x01\0\0\0',b'\x0d\0\x01\0'],'actual core/component header')
binary_audit=dict(host=artifacts[0],machOArm64Executable=True,prunerCommandLiteralPresent=b'prune-clock-adapter-io'in host_binary,matchingStaticSymbolNames=symbols,nativeBinaryExecutedByReviewer=False,binaryWitDecoderInvokedByReviewer=False)
# Whole finite output inventories include Rust targets/cache metadata and all
# monitor records, not only selected artifacts. Never copy or mutate outputs.
output_inventories=[tree_inventory(q,q in[SOURCE,PACKAGE])for q in[SOURCE,PACKAGE,WORK,EXTERNAL,OUTER]]
for q in[SOURCE,PACKAGE,WORK,EXTERNAL,OUTER]:need(stat.S_IMODE(q.stat().st_mode)==0o700,'actual private owned root mode')
for q in(WORK/'vendor').rglob('*'):
    if q.is_dir():need(stat.S_IMODE(q.stat().st_mode)==0o700,'private vendor directory')
need([len(x['files'])for x in output_inventories]==[271,4889,9446,1221,2796],'complete actual five-root regular inventories')
need([len(x['links'])for x in output_inventories]==[0,21,0,0,0],'exact output alias scope')
for path,identity in identities.items():
    p=Path(path);s=p.stat();need((s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,str(p.resolve()))==identity,'final current physical identity '+path)
for f in families:
    base=Path(f['index']['path']).parent;need({p.relative_to(base).as_posix()for p in base.rglob('*')if p.is_file()}==set(f['names']),'final exact fixed family membership')
coverage=dict(protectedSourceInputs=5667,completeFixedFamilies=len({f['index']['path']for f in families}),fullFamilyMembershipChecks=len(families),sourceFiles=271,packageSourceFiles=5,jsDependencies=4860,toolRootMetadataFiles=2,materializedRegularCopies=5138,cachedArchiveCopies=118,totalStageCopyRecords=5256,privateAliases=21,lockedVendorCrates=121,privateMissingDownloads=3,vendorFiles=sum(r['files']for r in vendor_audit),vendorUnpackedBytes=vendor_total,commands=8,selectedUnitFilters=4,passedTestsPerSelectedFilter=1,outerParentJsonlRecords=2,innerWorkerJsonlRecords=9,packageRegularFiles=4889,generatedLibraryFiles=22,builtArtifactDescriptors=25,outputRegularFiles=sum(len(x['files'])for x in output_inventories),outputSymlinks=21,outerObservedProcessIdentities=len(outer['observedProcesses']),innerObservedProcessIdentities=len(inner['observedProcesses']))
result=dict(schemaVersion=1,state='INDEPENDENT_CLOCK_IO_TOOLS_BUILD_RESULTS_REVIEW_PASSED_V2',verifiedPassed=True,sourceIndexSha256=root['sourceIndex']['sha256'],controllerSourceIndexSha256=root['controllerIndex']['sha256'],actualRootObservation=root_row,actualParentObservation=parent_row,actualWorkerResult=worker_row,actualStageReceipt=worker['stageReceipt'],actualPrivatePackageInventory=private_row,rootAuthority=root['rootAuthority'],rootConfig=root['config'],rootOuterController=root['rootOuterController'],outerTerminal=root['terminal'],innerTerminal=parent['rawTerminal'],sourceReview=root['sourceReview'],controllerReview=root['controllerReview'],artifacts=artifacts,coverage=coverage,commandAudit=command_audit,actualBuildRawExitCode=0,allRetainedOwnedTerminalsClean=True,sourceAndOriginalProtectionCurrentlyRehashed=True,fullOutputInventoryHashed=True,declaredCachedOriginalsUnchanged=True,threeMissingGlobalArchivesStillAbsent=True,privateOfflineCargoConfigVerified=True,prunerFunctionInvokedByRefusalUnitTest=True,validAdapterPruningRun=False,adapterCliPruneCommandInvoked=False,adapterPublished=False,applicationEngineOrGuestExecuted=False,newGeneratedPackageImportedByReviewer=False,reviewerOwnerActionsInvoked=False,reviewerToolExecutions=False,reviewerReadHashDecodeDataOnly=True,operationalAdmission=False,runtimeAcceptanceClaim=False,grantsValidAdapterActionAuthority=False,binaryDataAudit=binary_audit,limitations=['Actual tool build and four individually selected Rust tests only; no valid adapter was transformed or published','Static native symbols/string/header observations do not execute or prove valid pruner behavior','Source/protected descriptors and bounded output inventories are fully rehashed now; past final stability/argv/environment/fsync claims additionally rely on authenticated source and retained actual collector frames','No process polling/signalling was performed by reviewer; cleanup is the recorded finite observed-identity/group evidence, not proof about unobserved processes','Disk free was observed at reported boundaries, not monitored during commands; operational durations are not performance results','118 declared original cached archives/other protected inputs unchanged and three declared global paths absent; no universal global-cache/OS/SDK/TLS attestation','Tool component/lib WASI imports are not application imports; no generated library, new application or native engine was executed by reviewer','All actual outputs remain unreviewed for a later valid-adapter/application action; a new source-reviewed caller and Root phase are still required'])
write('results.json',result);write('input-hashes.json',dict(schemaVersion=1,files=list(rows.values())));write('output-inventories.json',dict(schemaVersion=1,roots=output_inventories));write('vendor-audit.json',dict(schemaVersion=1,crates=vendor_audit,totalUnpackedBytes=vendor_total));write('checks.json',dict(schemaVersion=1,checks=len(checks),names=checks));print(json.dumps(dict(state=result['state'],checks=len(checks),inputs=len(rows),coverage=coverage),ensure_ascii=False))
