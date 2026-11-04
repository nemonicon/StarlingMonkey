"""Independent DATA-only generated source reader. No owner module imported."""
from pathlib import Path
import hashlib,json,os,stat
HERE=Path(__file__).parent.resolve();S=HERE.parent;ROOT=S/'release-gates-activated-v1';PARENT=S/'release-gates-candidate-v1'
checked={};checks=[]
def need(v,m):
    if not v:raise AssertionError(m)
    checks.append(m)
def h(raw):return hashlib.sha256(raw).hexdigest()
def file(path,sha=None,size=None):
    p=Path(path);s=p.lstat();need(stat.S_ISREG(s.st_mode)and not p.is_symlink(),'regular '+str(p));key=str(p.resolve());identity=(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
    cache=checked.get(key)
    if cache is None or cache['identity']!=identity:
        digest=hashlib.sha256()
        with p.open('rb')as stream:
            for block in iter(lambda:stream.read(1024*1024),b''):digest.update(block)
        after=p.lstat();need(identity==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns),'stable '+str(p));cache={'path':key,'sha256':digest.hexdigest(),'bytes':s.st_size,'identity':identity};checked[key]=cache
    need(sha is None or cache['sha256']==sha,'SHA '+str(p));need(size is None or cache['bytes']==size,'bytes '+str(p));return cache
def raw(path,sha=None,size=None):file(path,sha,size);return Path(path).read_bytes()
def load(path,sha=None,size=None):return json.loads(raw(path,sha,size))
def safe(root,name):
    need(isinstance(name,str)and name and not Path(name).is_absolute()and '\\'not in name and '\0'not in name and all(p not in('','.','..')for p in name.split('/')),'finite local path')
    p=root
    for part in name.split('/'):
        need(len(part.encode())<=255,'bounded basename');p/=part;need(not p.is_symlink(),'no local symlink')
    return p
def index(root,sha):
    data=load(root/'index.json',sha);names=set()
    for r in data['files']:
        need(r['path']not in names,'unique index');names.add(r['path']);file(safe(root,r['path']),r['sha256'],r['bytes'])
    return data,names
def actual(root):
    files=set();directories=set()
    for folder,dirs,names in os.walk(root,followlinks=False):
        for name in dirs+names:
            p=Path(folder)/name;s=p.lstat();need(not stat.S_ISLNK(s.st_mode),'no source symlink')
            if stat.S_ISREG(s.st_mode):files.add(str(p.relative_to(root)))
            else:need(stat.S_ISDIR(s.st_mode),'ordinary directory');directories.add(str(p.relative_to(root)))
    return files,directories
ix,names=index(ROOT,'10d6df0205a17394343be49864f4ed82847292397732b5f821090ec78d94289b');members,_=actual(ROOT)
need(len(names)==1726 and members==names|{'index.json'},'actual1727 exact indexed1726 plus index')
parent,original_names=index(PARENT,'a74dc603f7e42384892c9f4b69a2ba131a87a80daa38da19e91bbc2c099e5372')
root_receipt=load(S/'release-gates-source-v1-root-results.json','39a90af444eac8320ce0a43c57f1419c7906842e363363ec2b296117bf906e12');need(root_receipt['externalPublisherExitCode']==0 and root_receipt['helperPreflightNativeGuestHostOrTimingInvoked']is False,'actual source-only outer0')
for key in['authority','sourceReceipt','externalTerminal','externalStdout','externalStderr']:
    r=root_receipt[key];file(r['path'],r['sha256'],r['bytes'])
terminal=load(root_receipt['externalTerminal']['path']);need(terminal['schemaVersion']==1 and terminal['rawExitCode']==0 and terminal['sourceOnly']is True and terminal['helperPreflightNativeGuestHostOrTimingInvoked']is False and terminal['pid']==root_receipt['pid'],'actual typed source publisher terminal raw0')
argv=terminal['argv'];need(argv[0]=='python3'and argv[1]==str(PARENT/'publish.py')and argv[argv.index('--index-sha256')+1]==root_receipt['proposalIndexSha256']and argv[argv.index('--output')+1]==str(ROOT),'actual source publisher command and exact output family')
authority=load(S/'release-gates-source-v1-root-review.json','a01a8711a582b9d28aa8882dc4b9210209bd7f957f94d4bcc7e7845de057a5cc')
need(authority['sourceActivationApproved']is True and authority['runtimeActionsApproved']is False and authority['sourcePromotionAllowed']is False and authority['operationalAdmission']is False,'source authority does not allow runtime/promotion')
peer=authority['independentSourceReview'];peer_root=Path(peer['index']['path']).parent;index(peer_root,peer['index']['sha256']);file(peer['result']['path'],peer['result']['sha256'],peer['result']['bytes'])
payload=load(PARENT/'payload-files.json')['files'];need(len(payload)==1719 and 'native-preflight.mjs'not in payload,'compiled bridge excluded from original payload')
for name in payload:need(raw(ROOT/name)==raw(PARENT/name),'exact payload '+name)
config=load(ROOT/'activation.json');seal=load(ROOT/'input-freeze.json');receipt=load(ROOT/'source-receipt.json')
need(config['state']=='REVIEWED_CONSUMERS355_RELEASE_SOURCE_ACTIVATED_V1'and config['proposalIndexSha256']==root_receipt['proposalIndexSha256'],'actual activation lineage')
need(config['nativeConfiguredSourceRoot']=='/private/tmp/starling-node-compat/consumers-source-v2'and config['componentToolRoot']==str(ROOT/'snapshot'),'configured vs packaging contexts distinct')
for key in['operationalAdmission','guestExecuted','nativeExecuted']:need(config[key]is False,'no activation execution '+key)
need(config['runtimeActionAuthority']is None and receipt['runtimeActionAuthority']is None,'no runtime authority issued')
for key,name in[('pinsSha256','reviewed-pins.json'),('rootReviewSha256','root-review.json'),('sourceReviewSha256','source-root-review.json'),('lineageSha256','lineage.json')]:file(ROOT/name,config[key])
need(raw(ROOT/'reviewed-pins.json')==raw(authority['reviewedPins']['path'],authority['reviewedPins']['sha256']),'exact reviewed pin copy')
need(raw(ROOT/'root-review.json')==raw(authority['nativeRootReview']['path'],authority['nativeRootReview']['sha256']),'exact native Root review copy')
need(raw(ROOT/'source-root-review.json')==raw(S/'release-gates-source-v1-root-review.json'),'exact source authority copy')
compiled=raw(ROOT/'native-preflight.template.mjs').decode().replace('@CONFIG_SHA@',h(raw(ROOT/'activation.json'))).replace('@INPUTS_SHA@',h(raw(ROOT/'input-freeze.json'))).encode()
need(compiled==raw(ROOT/'native-preflight.mjs'),'exact compiled two-parameter bridge')
expected={}
def add(path,sha,size,local=False):
    key=('L:'if local else'E:')+str(path);value={'path':str(path),'sha256':sha,'bytes':size,'local':local};need(key not in expected or expected[key]==value,'exact duplicate union role');expected[key]=value
for r in load(PARENT/'source-inputs.preparation.json')['files']:add(r['path'],r['sha256'],r['bytes'])
for r in parent['files']:add(str(PARENT/r['path']),r['sha256'],r['bytes'])
add(str(PARENT/'index.json'),root_receipt['proposalIndexSha256'],(PARENT/'index.json').stat().st_size)
for r in[authority['reviewedPins'],authority['nativeRootReview'],root_receipt['authority']]:add(r['path'],r['sha256'],r['bytes'])
boundaries={'activation.json','native-preflight.mjs','input-freeze.json','source-receipt.json','index.json'}
for name in sorted(members-boundaries):r=file(ROOT/name);add(name,r['sha256'],r['bytes'],True)
observed={('L:'if r['local']else'E:')+r['path']:r for r in seal['inputs']};need(len(observed)==len(seal['inputs'])==12544 and observed==expected,'exact original-context plus local12544 union')
for r in seal['inputs']:file(safe(ROOT,r['path'])if r['local']else r['path'],r['sha256'],r['bytes'])
need(seal['oldNestedPreparationRowsFollowed']is False and seal['boundaryOutputs']==['activation.json','native-preflight.mjs','input-freeze.json','source-receipt.json','index.json'],'no relocated nested rows or self-hash cycles')
snap,_=actual(ROOT/'snapshot');need(sorted(snap)==seal['snapshotMembers']and len(snap)==1677,'snapshot exact1677 membership')
edits=load(ROOT/'afterimage-proof.json')['edits'];groups={}
for r in edits:file(ROOT/r['preimage'],r['beforeSha256'],r['beforeBytes']);groups.setdefault(r['path'],[]).append(r)
need(len(edits)==23 and len(groups)==20,'23 host edits/20 paths')
for path,steps in groups.items():
    for before,after in zip(steps,steps[1:]):need(before['afterSha256']==after['beforeSha256'],'sequential host edit chain '+path)
    file(ROOT/'snapshot'/path,steps[-1]['afterSha256'],steps[-1]['afterBytes'])
origins=load(ROOT/'snapshot-origins.json')['files'];need(len(origins)==1677,'full snapshot origin count')
for r in origins:
    name=r['relativePath'];file(r['canonicalOriginalPath'],r['sha256'],r['bytes'])
    if name not in groups:file(ROOT/'snapshot'/name,r['sha256'],r['bytes'])
    else:need(groups[name][0]['beforeSha256']==r['sha256'],'host edit exact initial origin '+name)
lineage=load(ROOT/'lineage.json')
for n in[306,342,350,355]:need(len(lineage['native'+str(n)])==n and len({r['path']for r in lineage['native'+str(n)]})==n,'actual unique native'+str(n))
for a,b in[(306,342),(342,350),(350,355)]:
    before={r['path']:r['sha256']for r in lineage['native'+str(a)]};after={r['path']:r['sha256']for r in lineage['native'+str(b)]};changes={r['path']:r for r in lineage['delta'+str(b)]};added=lineage['added'+str(b)];need(len(after)==len(before)+len(added)and set(after)==set(before)|set(added),'exact source additions '+str(b))
    for path,digest in before.items():need(after[path]==(changes[path]['afterSha256']if path in changes else digest),'source transition '+str(b)+' '+path)
    for path,r in changes.items():need(r['beforeSha256']==before[path],'exact before policy '+str(b))
pins=load(ROOT/'reviewed-pins.json');review=load(ROOT/'root-review.json');need(pins['sourceFiles']==355 and pins['externalSources']==3 and pins['operationalAdmission']is False,'genuine355 validation pins only')
for label,pin in pins['variants'].items():
    need(pin['reviewRequired']is False and pin['variant']==label and pin['runtimeAcceptanceClaim']is False and pin['runtimeBackendProof']['verified']is False,'reviewed native facts, no runtime proof rewrite '+label)
    for key in['engineSha256','engineBytes','receiptSha256','freezeReceiptSha256']:need(pin[key]==review['variants'][label][key],'Root tuple '+label+' '+key)
    metadata=load(pin['enginePath']+'.build.json',pin['receiptSha256']);need(metadata['sourceManifest']==lineage['native355'],'all355 unchanged actual metadata '+label)
    need(metadata['streamConsumersEnabled']==(label!='disabled-off')and metadata['entropyPolicy']==('runtime-only'if label=='normal-runtime'else'off')and metadata['gcStress']==(label=='gc-off'),'finite native mode '+label)
    for r in lineage['native355']:file(ROOT/'snapshot'/r['path'],r['sha256'])
tool=load(ROOT/'tool-context.json');need(len(tool['toolTrees'])==2 and len(tool['toolLinks'])==22,'two tools/22 links')
for tree in tool['toolTrees']:
    need(str(Path(tree['path']).resolve())==tree['realPath'],'canonical tool root');found=[]
    for folder,dirs,files in os.walk(tree['path'],followlinks=False):
        for name in dirs+files:
            p=Path(folder)/name;s=p.lstat();kind='symlink'if stat.S_ISLNK(s.st_mode)else'directory'if stat.S_ISDIR(s.st_mode)else'file';found.append({'path':str(p.relative_to(tree['path'])),'kind':kind})
    need(sorted(found,key=lambda r:r['path'])==tree['entries'],'whole actual original tool membership')
for r in tool['toolLinks']:
    p=Path(r['path']);need(p.is_symlink()and os.readlink(p)==r['linkText']and str(p.resolve())==r['resolvedTarget'],'actual known tool link')
    need(any(Path(r['resolvedTarget']).is_relative_to(Path(t['realPath']))for t in tool['toolTrees']),'tool link remains in selected trees')
graph=load(ROOT/'selected-closure.json');need(len(graph['localModulesAndData'])==102 and len(graph['localEdges'])==194,'actual102 modules/data and194 edges')
for r in graph['localModulesAndData']:file(ROOT/r['path'],r['sha256'],r['bytes'])
for r in graph['localEdges']:need(os.path.normpath(str((ROOT/r['importer']).parent/r['request']))==str(ROOT/r['target']),'exact selected local edge')
need(graph['compiledBoundaryModules']==['native-preflight.mjs'],'explicit compiled boundary')
for r in load(ROOT/'package-endpoints.json')['packages']:
    d=load(r['path'],r['sha256'],r['bytes']);need(d['version']==r['version'],'actual package version '+r['name'])
packages=load(ROOT/'package-endpoints.json')
for r in packages['endpoints']:
    file(r['path'],r['sha256'],r['bytes']);need(str(Path(r['path']).resolve())==r['realPath'],'actual physical selected endpoint '+r['request'])
for r in packages['packageData']:file(r['path'],r['sha256'],r['bytes'])
prerequisite=load(ROOT/'reviewed-consumer-validation.json','36964b2dff52497ed43ce89ec34dbec1610d03d180a477510189150907ded65b')
need(prerequisite['state']=='ROOT_REVIEWED_CONSUMERS355_BOUNDED_COMPONENT_VALIDATION_V1'and prerequisite['nativeSourceFiles']==355 and prerequisite['totalReturnedStrings']==207,'exact separately reviewed prior bounded consumer validation')
need(prerequisite['scope']['operationalAdmission']is False and prerequisite['scope']['productionAcceptanceIssued']is False and prerequisite['scope']['fullNodeOrFullBufferOrFullConsumersSupportClaim']is False,'no prior validation broadened into operational/full support')
bindings=load(ROOT/'integration-bindings.json');need(bindings['nativeSourceFiles']==355 and bindings['httpSourceImplemented']is False and len(bindings['releaseJobs'])==8 and len(bindings['followons'])==5,'eight release stages/five future followons, HTTP unimplemented')
for job in bindings['releaseJobs']:need(job['futureRunnerRelativePath']in names and job['actualReportSha256']is None and job['outerRawExit']is None,'fresh future stage, no report reuse')
for path in bindings['followons'].values():need(path in names,'future followon entry indexed')
body=load(ROOT/'inherited-body-audit.json')
need(body['snapshotFiles']==1677 and body['unchangedFiles']==1657 and body['nativeSourcesModified']is False and body['sourceResultsAdopted']is False,'body/source results remain source-only')
for r in body['unchangedCaseOracleFixtureData']:file(ROOT/'snapshot'/r['path'],r['sha256'],r['bytes'])
need(receipt['state']=='SOURCE_ONLY_CONSUMERS355_RELEASE_GATES_PUBLISHED'and receipt['consumedInputs']==12544 and receipt['priorPassReused']is False and receipt['operationalAdmission']is False,'source-only receipt')
for name in['future-actions.template.json','runtime-authority.template.json']:need(raw(ROOT/name)==raw(PARENT/name),'unchanged future action template '+name)
result={'schemaVersion':1,'state':'INDEPENDENT_CONSUMERS355_RELEASE_GENERATED_SOURCE_VERIFIED_V1','generatedIndexSha256':'10d6df0205a17394343be49864f4ed82847292397732b5f821090ec78d94289b','proposalIndexSha256':root_receipt['proposalIndexSha256'],'verifiedPassed':True,'sourceOnly':True,'externalPublisherExitCode':0,'indexedFiles':1726,'actualRegularFiles':1727,'inputUnionRows':12544,'snapshotFiles':1677,'unchangedSnapshotBodies':1657,'hostEdits':23,'hostAfterimagePaths':20,'nativeSourceFiles':355,'nativeVariants':4,'policyCounts':[306,342,350,355],'toolTrees':2,'toolLinks':22,'selectedModulesAndData':102,'selectedEdges':194,'checks':len(checks),'ownerHelpersOrPreflightsImported':False,'runtimeAuthorityIssued':False,'operationalAdmission':False,'nativeGuestHostOrTimingExecutedByReviewer':False,'runtimeAcceptanceClaim':False}
(HERE/'results.json').write_text(json.dumps(result,indent=2)+'\n');(HERE/'rehashed-files.json').write_text(json.dumps({'schemaVersion':1,'files':[{k:v for k,v in r.items()if k!='identity'}for r in checked.values()]},indent=2)+'\n');print(json.dumps(result))
