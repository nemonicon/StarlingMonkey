"""Independent read/hash/source audit. Never imports an owner module or invokes an action."""
from pathlib import Path
import hashlib,json,os,re,stat,sys

HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'ownership-gc-component-candidate-v1'
SOURCE_SHA='6f0faf4b61af8fd8addffbb2948af847d2f772b401629b0fb9213ba4b2ccf0db'
checks=[];seen={};families=[]
def require(name,value):
    if not value:raise AssertionError(name)
    checks.append(name)
def digest(path):
    h=hashlib.sha256()
    with path.open('rb')as f:
        for chunk in iter(lambda:f.read(4*1024*1024),b''):h.update(chunk)
    return h.hexdigest()
def row(path):
    path=Path(path);return dict(path=str(path),sha256=digest(path),bytes=path.stat().st_size)
def verify(r):
    path=Path(r['path']);before=path.lstat()
    require('ordinary file '+str(path),stat.S_ISREG(before.st_mode)and not path.is_symlink())
    require('size '+str(path),before.st_size==r['bytes'])
    require('sha '+str(path),digest(path)==r['sha256'])
    after=path.lstat();require('stable '+str(path),(before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns))
    if str(path)in seen:require('same descriptor '+str(path),seen[str(path)]==r)
    seen[str(path)]={k:r[k]for k in ('path','sha256','bytes')}
    return path
def read(r):return json.loads(verify(r).read_bytes())
def family(r):
    index=read(r);names=set()
    for member in index['files']:
        name=member['path'];require('local unique family member',bool(name)and not name.startswith('/')and '\\'not in name and all(x not in ('','.','..')for x in name.split('/'))and name not in names);names.add(name)
        verify(dict(path=str(Path(r['path']).parent/name),sha256=member['sha256'],bytes=member['bytes']))
    actual=set()
    for p in Path(r['path']).parent.rglob('*'):
        require('no family symlink '+str(p),not p.is_symlink())
        if p.is_file():actual.add(p.relative_to(Path(r['path']).parent).as_posix())
    require('complete family membership '+r['path'],actual==names|{'index.json'})
    families.append(dict(index=r,members=len(names)))
    return index

index=family(dict(path=str(SOURCE/'index.json'),sha256=SOURCE_SHA,bytes=12548))
require('76 source members',len(index['files'])==76)
inputs=json.loads((SOURCE/'input-freeze.json').read_bytes())
require('8171 unique original context inputs',len(inputs['files'])==8171 and len({r['path']for r in inputs['files']})==8171)
for r in inputs['files']:verify(r)
refs=json.loads((SOURCE/'references.json').read_bytes())
for f in refs['families']:family(f['index'])
prereq=json.loads((SOURCE/'prerequisites.json').read_bytes())

# Independently reconstruct both actual construction donors in both directions.
derivations=json.loads((SOURCE/'construction-derivations.json').read_bytes());edit_counts={}
for item in derivations['derived']:
    donor=verify(item['donor']).read_text();after=(SOURCE/item['file']).read_text();value=donor
    for d in item['changes']:
        require('singleton forward '+item['file'],value.count(d['before'])==1);value=value.replace(d['before'],d['after'])
    require('exact forward '+item['file'],value==after)
    for d in reversed(item['changes']):
        require('singleton reverse '+item['file'],value.count(d['after'])==1);value=value.replace(d['after'],d['before'])
    require('exact reverse '+item['file'],value==donor);edit_counts[item['file']]=len(item['changes'])
require('6 parent and 8 worker derivations',edit_counts=={'build.mjs':6,'build-worker.mjs':8})

# Complete physical packaging roles and all explicitly permitted tool links.
pack=read(prereq['packagingMap']);pub=Path(pack['publicationRoot']);publication=read(pack['publicationIndex'])
expected={r['path']:r for r in pack['files']};published={r['path']:r for r in publication['files']};links={r['destination']:r for r in pack['links']}
require('4934 roles and 22 links',len(expected)==4934 and len(links)==22)
require('all packaging and tool publication rows',set(expected)=={n for n in published if n.startswith(('packaging/','tools/'))})
require('whole link provenance',pack['links']==publication['links'])
actual=set();actual_links=set()
for prefix in pack['roleRoots']:
    base=pub/prefix;require('ordinary role root',base.is_dir()and not base.is_symlink())
    for p in base.rglob('*'):
        name=p.relative_to(pub).as_posix();s=p.lstat()
        if stat.S_ISLNK(s.st_mode):
            d=links[name];require('link text '+name,os.readlink(p)==d['newLinkText']);require('link target '+name,p.resolve()==pub/d['mappedTarget']);actual_links.add(name)
        elif stat.S_ISDIR(s.st_mode):require('private role dir '+name,stat.S_IMODE(s.st_mode)==0o700)
        else:
            d=expected[name];require('exact role row '+name,all(d[k]==published[name][k]for k in ('sha256','bytes','mode')))
            require('ordinary role mode and inode '+name,stat.S_ISREG(s.st_mode)and s.st_nlink==1 and stat.S_IMODE(s.st_mode)==d['mode'])
            verify(dict(path=str(p),sha256=d['sha256'],bytes=d['bytes']));actual.add(name)
require('physical role membership',actual==set(expected)and actual_links==set(links))
s=pub.lstat();require('publication identity',s.st_dev==pack['rootIdentity']['device']and s.st_ino==pack['rootIdentity']['inode']and stat.S_IMODE(s.st_mode)==0o700)
adapter=expected['packaging/host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm']
require('release 53512 adapter',adapter['bytes']==53512 and adapter['sha256']=='988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0')

# Read source contracts, never evaluate guest, helper, bundler or componentizer.
texts={n:(SOURCE/n).read_text()for n in ('guard.mjs','build.mjs','build-worker.mjs','bundle.mjs','artifact-guard.mjs')}
g,b,w,bundle,a=(texts[n]for n in ('guard.mjs','build.mjs','build-worker.mjs','bundle.mjs','artifact-guard.mjs'))
for name,value in {
 'actual bootstrap pair before API import':g.index('const bootstrapPeer=await indexed')<g.index('await import(pathToFileURL(p.bootstrapEntry.path))'),
 'tooling rehash before actual API import':g.index('await tooling.recheck();const {cryptoOwnerGcBootstrapPreflight}')<g.index('const frame=await cryptoOwnerGcBootstrapPreflight'),
 'genuine actual API':"cryptoOwnerGcBootstrapPreflight({configDescriptor:descriptor(root.gcBootstrapConfig)})"in g,
 'actual distinct configured and frozen roots':"frame.nativeConfiguredSourceRoot===CONFIGURED"in g and "frame.frozenSourceRoot===FROZEN+'/source'"in g,
 'exact independent observation and config':"descriptor(bp.bootstrapRootObservation)"in g and "descriptor(bp.bootstrapConfig)"in g,
 'no normal pin authority':"['normal-off','normal-runtime','disabled-off'].every(n=>pins.variants[n]===null)"in g,
 'bootstrap full raw frame recheck retained':'await frame.recheck();await packaging.recheck();'in g,
 'small selected-manifest descriptor transmitted':"output.write('selected-manifests.json',frame.selectedManifests,{json:true})"in b and 'selectedManifests:descriptor({'in b and 'await regular(d.selectedManifests)'in w,
 'actual authenticated adapter handoff':'componentOptions({engine:d.engine,adapter:packaging.adapter},wit)'in w,
 'whole bundle API and native Buffer external':"input:code.path,builtinManifests:selectedManifests"in bundle and "JSON.stringify(value.imports)==='[\"node:buffer\"]'"in bundle,
 'physical graph no virtual modules':'Unknown virtual helper refuses before componentization'in bundle and 'guestFixtureSha256:hash(fixture)'in bundle,
 'raw bundle and graph before componentization':w.index("output.write('bundle-graph.json'")<w.index('selected.componentize(source,options)'),
 'actual zero import gate':'result.interfaceAudit.emittedImports.length===0'in w,
 'four independent ABI surfaces':'parsePublicWit(emitted)'in w and 'checkTranspileMetadata(generated)'in w and 'publicJSExports(toolchain.parseAst(glue'in w and 'parsePublicDts(dts)'in w,
 'process dir before real owned helper':b.index("mkdir(join(output.root,'processes')")<b.index('runOwnedCommand('),
 'raw owned helper result before assert':b.index('runOwnedCommand(')<b.index('checkOwnedTerminal(status)'),
 'parent and worker final failure audits':'finally{try{await frame.recheck();}finally{await output.close();}}'in b and 'finally{try{await recheck();}finally{await output.close();}}'in w,
 'worker critical helper final recheck':'for(const row of d.criticalSourceFiles)await regular(row'in w,
 'no generated module import':'await import(pathToFileURL(join(output'not in w,
 'runtime fails closed':"throw new Error('NEW_GC_RUNTIME_SOURCE_REVIEW_AND_ROOT_ACTION_REQUIRED')"in a,
}.items():require(name,value)
template=json.loads((SOURCE/'future-component-authority.template.json').read_bytes())
require('all actual action and evidence slots null',all(template[n]is None for n in ('state','componentSourceIndexSha256','sourceIndependentReview','reviewedGcPins','gcNativeRootReview','gcBootstrapConfig','actualBootstrapObservation','actualBootstrapReview')))
require('all execution permits false',all(template[n]is False for n in ('componentBuildAllowed','componentInitializationAllowed','keyExportCallsAllowed','keyOrCryptoOperationsAllowed','gcPressureCallsAllowed','ordinaryGuestExportsAllowed','operationalAdmission','runtimeAcceptanceClaim','timingAllowed')))
guest=verify(prereq['guest']).read_text();require('unchanged reviewed Buffer-only guest',guest.count("import {Buffer} from 'node:buffer';")==1 and prereq['guest']['sha256']=='08d5f7f49e253baef92fdcd668349c481554f8245c80a25432b882188bdd8c40')
require('initial no keys and pressure counters',"const pressureRecords=[];let pressureRequests=0;"in guest and 'let rawKey=null,jwkKey=null'in guest)
require('whole prior HMAC output stability preserved',"hex(first)===firstHex"in guest)
collector=json.loads((SOURCE/'collector-contract.json').read_bytes());require('schema2 pressure counts and limits',collector['perRunPressureRequests']==[4,4,8,0]and collector['outerPressureRequests']==16 and collector['actualNativeGcCountObserved']is False and collector['isolatedTemporaryRootsProved']is False and collector['finalizerFreeWipeObserved']is False)
expected_gc=read(collector['completeExpected']);require('whole expected GC record counts',expected_gc['schemaVersion']==2 and len(expected_gc['records'])==4 and [r['gcObservation']['publicGcPressureRequests']for r in expected_gc['records']]==[4,4,8,0]and expected_gc['gcObservation']['publicGcPressureRequests']==16)
models=json.loads((SOURCE/'model-results-final.json').read_bytes());require('61 authenticated pure model receipts',models['count']==61 and len(models['checks'])==61 and all(c['passed']is True for c in models['checks'])and models['ownerModulesImported']is False)
source_results=json.loads((SOURCE/'source-check-results.json').read_bytes());require('67 authenticated source/data checks',source_results['count']==67 and all(c['passed']is True for c in source_results['checks']))
parse=[]
for name in ('syntax-results.json','syntax-results-final.json','syntax-results-bootstrap-peer.json'):
    v=json.loads((SOURCE/name).read_bytes());parse.append(dict(file=name,record=v))

# Read current source again; no writer/helper or operational entrypoint runs.
verify(dict(path=str(SOURCE/'index.json'),sha256=SOURCE_SHA,bytes=12548))
out=dict(schemaVersion=1,state='INDEPENDENT_GC_COMPONENT_SOURCE_READ_HASH_AUDIT_PASSED_V1',sourceIndexSha256=SOURCE_SHA,sourceMembers=76,inputDescriptors=8171,inputDeclaredBytes=sum(r['bytes']for r in inputs['files']),uniquePaths=len(seen),checks=len(checks),families=families,derivationEdits=edit_counts,physicalPackagingFiles=len(actual),toolLinks=len(actual_links),ownerReceiptsAuthenticatedOnly=dict(models=61,sourceData=67,syntax=parse),ownerActionsInvoked=False,ownerModulesImported=False,bootstrapInvoked=False,componentizerInvoked=False,guestInvoked=False,sourceOnly=True)
if len(sys.argv)==2:
    with Path(sys.argv[1]).open('x')as f:f.write(json.dumps(out,indent=2)+'\n')
else:
    require('no unrecognized CLI options',len(sys.argv)==1)
print(json.dumps(out,indent=2))
