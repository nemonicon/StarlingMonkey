"""Bounded read/hash inventory for a future archive. Never import owner helpers.

No native actions, guest/host execution, archive acceptance or live edits.
Only explicitly indexed source rows, six frozen inventories, Root receipts and
nine terminal evidence roots grant enumeration permission.
"""
from pathlib import Path
import codecs,hashlib,json,os,stat
HERE=Path(__file__).resolve().parent
CLASSIC=HERE.parents[1]
REPO=HERE.parents[4]
EXTERNAL=Path('/tmp/starling-node-compat')
SOURCE=EXTERNAL/'classic-trace-source-v1'
SOURCE_ASSETS=json.loads((REPO/'tests/node-compat/milestone-v12-preparation/pins.json').read_bytes())['requiredSourceBinaryAssets']
rows={};issues=[];links={};manifest_summaries=[];cache={};declared_dependencies=[]
def digest(path):
    s=path.stat();key=(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns)
    if key not in cache:
        h=hashlib.sha256()
        with path.open('rb')as f:
            for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
        after=path.stat();assert key==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns)
        cache[key]=h.hexdigest()
    return cache[key]
def mode(path):
    name=str(path)
    if any(name.endswith('/'+relative)and digest(path)==expected for relative,expected in SOURCE_ASSETS.items()):
        return'repository-native-source-binary-exception-five-paths-only'
    if path.suffix.lower()in{'.a','.so','.dylib','.node','.tar','.gz','.zip','.exe'}:
        return'reference-only-host-sdk-or-dependency-binary'
    if path.suffix.lower()in{'.wasm','.cwasm','.o','.obj'}:
        return'external-binary-preservation-required'
    decoder=codecs.getincrementaldecoder('utf-8')()
    try:
        with path.open('rb')as f:
            for block in iter(lambda:f.read(1024*1024),b''):
                if b'\0'in block:return'reference-only-host-sdk-or-dependency-binary'
                decoder.decode(block,final=False)
        decoder.decode(b'',final=True)
    except UnicodeDecodeError:return'reference-only-host-sdk-or-dependency-binary'
    return'repository-text-source-evidence-copy'
def add(path,role,expected=None,size=None):
    path=Path(path).absolute()
    if not path.exists():issues.append({'path':str(path),'role':role,'issue':'missing-original','expectedSha256':expected});return
    if path.is_symlink():
        record={'path':str(path),'linkText':os.readlink(path),'resolvedTarget':str(path.resolve()),'role':role}
        links[str(path)]=record;return
    if not path.is_file():issues.append({'path':str(path),'role':role,'issue':'not-regular-file'});return
    canonical=str(path.resolve());s=path.stat();actual=digest(path)
    if expected is not None and expected!=actual:issues.append({'path':str(path),'role':role,'issue':'original-hash-differs','expectedSha256':expected,'observedSha256':actual})
    if size is not None and size!=s.st_size:issues.append({'path':str(path),'role':role,'issue':'original-size-differs','expectedBytes':size,'observedBytes':s.st_size})
    if canonical not in rows:
        rows[canonical]={'path':canonical,'declaredPaths':[str(path)],'sha256':actual,'bytes':s.st_size,'allocatedBytes':s.st_blocks*512,'mode':stat.S_IMODE(s.st_mode),'flags':getattr(s,'st_flags',None),'mtimeNs':s.st_mtime_ns,'roles':[role],'proposedPreservation':mode(path)}
    else:
        record=rows[canonical];assert record['sha256']==actual and record['bytes']==s.st_size
        if str(path)not in record['declaredPaths']:record['declaredPaths'].append(str(path))
        if role not in record['roles']:record['roles'].append(role)
    return rows[canonical]
def load(path,role):
    add(path,role);return json.loads(Path(path).read_bytes())
def index(root,role):
    doc=load(root/'index.json',role+'-index');entries=doc['files']
    for row in entries:
        assert not Path(row['path']).is_absolute()and '..'not in Path(row['path']).parts
        add(root/row['path'],role,row['sha256'],row['bytes'])
    manifest_summaries.append({'path':str(root/'index.json'),'sha256':digest(root/'index.json'),'kind':role,'rows':len(entries)})
def input_manifest(path,role):
    doc=load(path,role+'-manifest');inputs=doc['inputs']
    for row in inputs:
        original=Path(row['path']);original=original if original.is_absolute()else path.parent/original
        add(original,role,row['sha256'],row.get('bytes'))
        declared_dependencies.append({'manifest':str(path),'originalPath':str(original.absolute()),'resolvedPath':str(original.resolve()),'sha256':row['sha256'],'bytes':row.get('bytes')})
    for row in doc.get('toolLinks',[]):
        link=Path(row['path']);add(link,role+'-tool-link')
        if link.is_symlink()and os.readlink(link)!=row['linkText']:issues.append({'path':str(link),'issue':'tool-link-text-differs'})
    manifest_summaries.append({'path':str(path),'sha256':digest(path),'kind':role,'rows':len(inputs),'toolTrees':len(doc.get('toolTrees',[])),'toolLinks':len(doc.get('toolLinks',[]))})
def absolute_descriptors(value,role):
    if isinstance(value,dict):
        if isinstance(value.get('path'),str)and Path(value['path']).is_absolute()and isinstance(value.get('sha256'),str)and len(value['sha256'])==64:
            add(value['path'],role,value['sha256'],value.get('bytes'))
        for child in value.values():absolute_descriptors(child,role)
    elif isinstance(value,list):
        for child in value:absolute_descriptors(child,role)
def terminal_tree(root,role):
    assert root.is_dir()and not root.is_symlink(),root
    count=0
    for parent,dirs,names in os.walk(root,followlinks=False):
        for name in dirs:
            path=Path(parent)/name
            if path.is_symlink():add(path,role+'-directory-link')
        dirs[:]=[name for name in sorted(dirs)if name not in['node_modules','.git','target','__pycache__']]
        for name in names:
            path=Path(parent)/name
            if path.is_file()or path.is_symlink():add(path,role);count+=1
        for name in list(dirs):
            path=Path(parent)/name
            if path.is_symlink():add(path,role+'-link');dirs.remove(name)
    module_link=root/'node_modules'
    if module_link.is_symlink():add(module_link,role+'-node-modules-link')
    manifest_summaries.append({'path':str(root),'kind':role,'terminalTreeRegularOrLinkEntries':count,'nodeModulesNotTraversed':True})
def put(name,value):
    with(HERE/name).open('x')as f:json.dump(value,f,indent=2);f.write('\n')
def main():
    assert not(HERE/'needed-files.json').exists()
    # Complete immutable classic source/history/review packets; exclude the
    # mutable adoption directory and unrelated zlib/consumer source proposals.
    packets=[p for p in CLASSIC.iterdir()if p.is_dir()and(p/'index.json').is_file()]
    for root in sorted(packets):index(root,'indexed-classic-source-or-proof-packet')
    fixed=[CLASSIC/'trace-integration-candidate-v1/input-freeze.json',CLASSIC/'production-trace-runtime-activated-v1/input-freeze.json',CLASSIC/'measurement-correctness-activated-v2/input-freeze.json',CLASSIC/'measurement-execution-activated-v2/input-freeze.json',CLASSIC/'measurement-stock-composition-candidate-v1/input-freeze.json',CLASSIC/'measurement-composition-timing-admission-amendment-v1/input-freeze.json',SOURCE/'tests/node-compat/foundation-classic-streams/production-trace-regression-activated-v1/input-freeze.json',SOURCE/'tests/node-compat/foundation-classic-streams/production-trace-http-activated-v1/input-freeze.json']
    for path in fixed:input_manifest(path,'actual-critical-family-consumed-input')
    for name in['production-trace-regression-activated-v1','production-trace-http-activated-v1']:
        index(SOURCE/'tests/node-compat/foundation-classic-streams'/name,'staged-corrected-source-family')
    freezes=[]
    for base,labels in[(EXTERNAL/'production-classic-trace-v1/native-freeze',['normal-off','normal-runtime','disabled-off','gc-off']),(EXTERNAL/'classic-benchmark-trace-v3-artifacts/native-freeze',['benchmark-classic-on','benchmark-classic-off'])]:
        for label in labels:
            path=base/(label+'-freeze-receipt.json');doc=load(path,'actual-frozen-receipt')
            for row in doc['copies']:add(row['path'],'actual-frozen-inventory',row['sha256'],row['bytes'])
            freezes.append({'label':label,'receipt':str(path),'receiptSha256':digest(path),'engineSha256':doc['engineSha256'],'copies':len(doc['copies']),'diagnosticOnly':bool(doc.get('diagnosticOnly',False)),'originalPathsAreProvenanceNotCurrentConfigRequirements':True})
    # Root's already-issued immutable raw-terminal/collection receipts provide
    # finite paths to logs, effective host configuration and historical failures.
    adoption=CLASSIC/'production-adoption-v1';root_receipts=[]
    for path in sorted(adoption.iterdir()):
        if path.is_file():
            add(path,'root-issued-adoption-record')
            if path.suffix=='.json':
                doc=json.loads(path.read_bytes());absolute_descriptors(doc,'Root-record-explicit-absolute-evidence')
                root_receipts.append({'path':str(path),'sha256':digest(path),'state':doc.get('state')})
    outputs=['production-classic-corrected-runtime-v1','production-classic-corrected-trace-v1','production-classic-corrected-regression-v1','production-classic-corrected-workload-v2','production-classic-corrected-http-v1','production-common-byte-correctness-v2','production-common-byte-stock-only-v1','production-common-byte-composition-v1','production-common-byte-composed-timing-v1']
    for name in outputs:terminal_tree(EXTERNAL/name,'completed-classic-evidence-root')
    # Latest accepted checkpoint is referenced and remains immutable; never
    # duplicate or relabel its306-source runtime proof as corrected342 proof.
    for name in['index.json','results.json','README.md']:
        add(REPO/'tests/node-compat/milestones/foundations-v12'/name,'latest-accepted-v12-reference')
    targets=['builtins/node-compat/classic-streams/classic-core.generated.mjs','builtins/node-compat/classic-streams/transformation-receipt.json','builtins/node-compat/classic-streams/factories.generated.h','tests/node-compat/build-engine.sh','tests/node-compat/classic-streams-admission.mjs']
    promotion=[]
    for name in targets:
        before=add(REPO/name,'live-Root-beforeimage-must-preserve-before-rollforward')
        after=add(SOURCE/name,'exact-corrected-Root-afterimage-not-applied')
        promotion.append({'path':name,'beforeSha256':before['sha256'],'beforeBytes':before['bytes'],'afterSha256':after['sha256'],'afterBytes':after['bytes'],'afterSource':str(SOURCE/name),'native':name.startswith('builtins/'),'applied':False})
    affected={str((REPO/name).resolve())for name in targets}
    impacts=[row for row in declared_dependencies if row['resolvedPath']in affected]
    modes=sorted({row['proposedPreservation']for row in rows.values()})
    totals={kind:{'files':sum(row['proposedPreservation']==kind for row in rows.values()),'logicalBytes':sum(row['bytes']for row in rows.values()if row['proposedPreservation']==kind),'allocatedBytesObserved':sum(row['allocatedBytes']for row in rows.values()if row['proposedPreservation']==kind)}for kind in modes}
    free=os.statvfs(EXTERNAL).f_bavail*os.statvfs(EXTERNAL).f_frsize
    by_hash={}
    for row in rows.values():by_hash.setdefault(row['sha256'],[]).append(row['path'])
    for issue in issues:
        issue['authenticatedAlternativePaths']=by_hash.get(issue.get('expectedSha256'),[])
    put('needed-files.json',{'schemaVersion':1,'state':'UNREVIEWED_BOUNDED_ARCHIVE_CLOSURE_PLAN_NOT_A_COPY_OR_ACCEPTANCE','files':sorted(rows.values(),key=lambda r:r['path']),'links':sorted(links.values(),key=lambda r:r['path']),'inputManifestAndScopeSummaries':manifest_summaries,'originalPathDependenciesForFivePromotionTargets':impacts,'freezeInventories':freezes,'RootReceiptsAtInspection':root_receipts,'issues':issues,'totalsByProposedPreservation':totals,'availableBytesObserved':free,'sourcesNotMutated':True,'ownerHelpersGuestNativeOrTimingInvoked':False,'archiveCreated':False,'acceptedCheckpoint':'foundations-v12','newAcceptance':False})
    put('rollforward-map.json',{'schemaVersion':1,'state':'UNAPPLIED_FIVE_FILE_PROMOTION_MAP_ONLY','files':promotion,'unchangedSelector':{'path':'tests/node-compat/module-selection.mjs','sha256':digest(REPO/'tests/node-compat/module-selection.mjs'),'afterSha256':digest(SOURCE/'tests/node-compat/module-selection.mjs')},'oldAbsolutePathsCannotHoldTwoGenerations':True,'historicalManifestRewritePermitted':False,'beforePreservationAndIndependentArchiveReviewRequired':True,'newGuestNativeOrTimingActions':False})
    print(json.dumps({'files':len(rows),'links':len(links),'criticalManifests':len(fixed),'classicIndexedPackets':len(packets),'promotionFiles':len(promotion),'affectedManifestRows':len(impacts),'issues':len(issues),'availableBytes':free,'totals':totals}),flush=True)
if __name__=='__main__':main()
