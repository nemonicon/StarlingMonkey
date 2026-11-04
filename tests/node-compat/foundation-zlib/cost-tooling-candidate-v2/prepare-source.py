"""Author preparation: source bytes/physical inventories only, never owner code."""
import hashlib,json,os,re,stat
from pathlib import Path
HERE=Path(__file__).parent.resolve();REPO=Path('/Users/dan/dev/StarlingMonkey')
PROPOSAL=HERE.parent/'cost-comparison-candidate-v1'
STAGE=Path('/tmp/starling-node-compat/zlib-source-v4').resolve()
TOOL=Path('/tmp/starling-node-compat/native-toolchain-lock').resolve()
PACKAGER=Path('/tmp/starling-node-compat/import-abi-clock-v2-build/package').resolve()
records={}
def need(v,m):
    if not v:raise AssertionError(m)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def row(path):
    p=Path(path).resolve(strict=True);s=p.lstat();need(stat.S_ISREG(s.st_mode),'Ordinary input')
    h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    mode=stat.S_IMODE(s.st_mode);need(not mode&0o7000,'No privileged source mode')
    value={'source':str(p),'sha256':h.hexdigest(),'bytes':s.st_size,'mode':mode};records[str(p)]=value;return value
def read(path,expected=None):
    r=row(path);need(expected is None or r['sha256']==expected,'Input hash');return Path(r['source']).read_bytes()
def load(path,h=None):return json.loads(read(path,h))
def write(name,value):
    p=HERE/name;p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x')as f:json.dump(value,f,indent=2);f.write('\n')
def copy_source(source,target,expected=None):
    raw=read(source,expected);p=HERE/'image'/target;p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb')as f:f.write(raw)
    return{**row(source),'destination':target,'imagePath':str(p.relative_to(HERE))}

proposal_index=load(PROPOSAL/'index.json','e29c596df3c809bab8fd3851b224a7ec4e84177d791c5d1f909072985f047ef8')
for r in proposal_index['files']:read(PROPOSAL/r['path'],r['sha256'])
decision=HERE.parent/'cost-source-protocol-amendment-root-decision-v2.json'
read(decision,'0025c7a1083d9291effe0cf51bbfef4e154353db75d433dae07f296d46d61cc6')
snapshot=load(PROPOSAL/'selector-snapshot.json')
overrides={r['snapshotPath'].split('selector-snapshot/',1)[1]:r for r in snapshot['files']}
files={};edges=[];pending=['tests/node-compat/toolchain.mjs','tests/node-compat/componentizer.mjs','tests/node-compat/profile-bundler.mjs','tests/node-compat/foundations/native-scalar-harness.mjs'];visited=set()
def source_for(name):return PROPOSAL/overrides[name]['snapshotPath']if name in overrides else REPO/name
while pending:
    name=pending.pop(0)
    if name in visited:continue
    visited.add(name);source=source_for(name);text=read(source).decode()
    files[name]=copy_source(source,'packaging/'+name)
    for match in re.finditer(r"^\s*import\b[^;]*?\bfrom\s*(['\"])([^'\"]+)\1\s*;",text,re.M):
        request=match.group(2)
        if request.startswith('node:'):continue
        need(request.startswith('.'),'Unknown bare inherited packaging import')
        local=os.path.normpath(str(Path(name).parent/request));need(not local.startswith('../'),'Packaging import escapes source root')
        edges.append({'importer':name,'request':request,'target':local});pending.append(local)
need(len(visited)==11,'Derived actual350 inherited packaging JS count')
for name,r in overrides.items():
    if name not in files:files[name]=copy_source(PROPOSAL/r['snapshotPath'],'packaging/'+name,r['sha256'])
data=['tests/node-compat/wasi-0.2.10-interfaces.json','tests/node-compat/oom/componentize-clock-errno-v2.patch','tests/node-compat/abi-fix/componentize-import-i32-v1.patch','tests/node-compat/abi-fix/splicer-Cargo.v1.lock']
for name in data:
    if name not in files:files[name]=copy_source(REPO/name,'packaging/'+name)
native_facts=load(PROPOSAL/'existing-native-facts.DATA-ONLY.json')
native_hashes={r['path']:r['sha256']for r in native_facts['sourceManifest350']}
for name in ['cli','clocks','filesystem','http','io','random','sockets']:
    target='host-apis/wasi-0.2.10/wit/deps/wasi-'+name+'-0.2.10/package.wit';files[target]=copy_source(REPO/target,'packaging/'+target,native_hashes[target])
adapter=REPO/'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm'
adapter_row=row(adapter);need(adapter_row['sha256']=='988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0'and adapter_row['bytes']==53512,'Actual regular adapter')
# Binary adapter is a private-publication copy row only, not a new repo binary.
binary_rows=[{**adapter_row,'destination':'packaging/host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm','role':'selected-tooling-source-adapter'}]
for name in ['package.json','esm/browser.js','esm/browser.d.ts','LICENSE']:
    copy=copy_source(TOOL/'node_modules/fflate'/name,'comparands/fflate/'+name)
    files['fflate:'+name]=copy

roots=[('toolchain',TOOL),('packager',PACKAGER)];trees=[];all_tool_files=[];all_links=[]
for label,root in roots:
    entries=[]
    for directory,dirs,names in os.walk(root,followlinks=False):
        for name in sorted(dirs+names):
            p=Path(directory)/name;relative=str(p.relative_to(root));s=p.lstat()
            if stat.S_ISLNK(s.st_mode):
                target=p.resolve(strict=True);matches=[(n,r)for n,r in roots if target==r or target.is_relative_to(r)]
                need(len(matches)==1,'Tool link target must stay in the two exact trees')
                dest_label,dest_root=matches[0];destination='tools/'+label+'/'+relative;new_target='tools/'+dest_label+'/'+str(target.relative_to(dest_root))
                link={'kind':'symlink','source':str(p),'destination':destination,'sourceLinkText':os.readlink(p),'resolvedOriginal':str(target),'newLinkText':os.path.relpath(new_target,str(Path(destination).parent)),'mappedTarget':new_target,'targetKind':'directory'if target.is_dir()else'file'}
                all_links.append(link);entries.append({'path':relative,**link})
            elif stat.S_ISDIR(s.st_mode):entries.append({'path':relative,'kind':'directory'})
            else:
                need(stat.S_ISREG(s.st_mode),'Unknown tool-tree file kind')
                item={**row(p),'destination':'tools/'+label+'/'+relative,'role':'copied-tool-file'};all_tool_files.append(item);entries.append({'path':relative,'kind':'file',**item})
    trees.append({'name':label,'originalRoot':str(root),'publicationRoot':'tools/'+label,'entries':entries})
write('tool-trees.json',{'schemaVersion':1,'state':'FRESH_COMPLETE_PHYSICAL_TOOL_TREE_BYTES_NOT_EXECUTED','trees':trees,'links':all_links,'libraryOrPackageInvoked':False,'linksRebasedOnlyInsideNewPublication':True,'oldPathsOrLinkTextsModified':False})
facts=load(PROPOSAL/'existing-native-facts.DATA-ONLY.json')
for source,target in [(PROPOSAL/'existing-native-facts.DATA-ONLY.json','metadata/native-facts.json'),(decision,'metadata/source-protocol-v2.json'),(PROPOSAL/'protocol.json','metadata/original-protocol.json'),(PROPOSAL/'fixtures.json','metadata/fixtures.json')]:
    files['metadata:'+target]=copy_source(source,target)
write('packaging-source-map.json',{'schemaVersion':1,'state':'ACTUAL350_FRESH_PACKAGING_SNAPSHOT_SOURCE_PLAN','inheritedLocalJsModules':len(visited),'newFiniteBundlerFunctionalModule':'control/bundle.mjs','functionalPackagingModules':12,'inheritedStaticEdges':edges,'files':list(files.values()),'selectedAdapter':binary_rows[0],'selectorOperationalAdmission':'CLOSED','normalRawModelOnly':'validateZlibBuildSourceAdmission','fullPythonAncestryReexecution':False})
objects=list(files.values())+binary_rows+all_tool_files
# All control/image metadata rows are added by the final sealer after source is
# held; no self-append/active-output traversal occurs in a real publisher.
write('publication-plan.base.json',{'schemaVersion':1,'state':'FRESH_ZLIB350_COST_SOURCE_PUBLICATION_BASE_PLAN_NO_AUTHORITY','destination':'/tmp/starling-node-compat/zlib-cost-source-v2','objects':objects,'links':all_links,'logicalCopyBytesBeforeControlAndProofCapsules':sum(r['bytes']for r in objects),'configuredNativeRoot':str(STAGE),'frozenNativeRoot':'/private/tmp/starling-node-compat/production-zlib-v4/native-freeze','packagingRoot':'packaging','toolchainRoot':'tools/toolchain','packagerRoot':'tools/packager','fflateBrowser':'comparands/fflate/esm/browser.js','existingNativeFacts':'metadata/native-facts.json','guestRoot':None,'guestSourceIndexSha256':None,'sourceProtocolDecisionSha256':'0025c7a1083d9291effe0cf51bbfef4e154353db75d433dae07f296d46d61cc6','maxRenderedInputUtf8Bytes':33554432,'maxBundleUtf8Bytes':33554432,'actionsAllowed':False})
write('source-preparation-inputs.json',{'schemaVersion':1,'state':'FRESH_SOURCE_AND_COMPLETE_TOOL_INVENTORY_ONLY','files':list(records.values()),'oldConsumedRowsUsedAsCurrentAuthority':False,'oldOwnerHelpersInvoked':False,'libraryCodecOracleBundleNativeGuestHostOrTimingInvoked':False})
print(json.dumps({'inheritedJs':len(visited),'snapshotFiles':len(files),'toolFiles':len(all_tool_files),'toolLinks':len(all_links),'sourceInputs':len(records),'logicalBaseBytes':sum(r['bytes']for r in objects),'actions':False}))
