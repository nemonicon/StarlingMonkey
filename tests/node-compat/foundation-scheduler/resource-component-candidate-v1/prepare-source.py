"""Read/hash only source preparation; writes this new family, invokes no helper."""
from pathlib import Path
import hashlib
import json
import re

OWN=Path(__file__).resolve().parent
REPO=Path('/Users/dan/dev/StarlingMonkey')
assert OWN==REPO/'tests/node-compat/foundation-scheduler/resource-component-candidate-v1'
assert not(OWN/'index.json').exists()
SCHED=OWN.parent
CRYPTO=REPO/'tests/node-compat/foundation-crypto'
inputs={}
def descriptor(path):
    p=Path(path);assert p.is_absolute()and p.is_file()and not p.is_symlink(),p
    a=p.stat();h=hashlib.sha256();count=0
    with p.open('rb')as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b);count+=len(b)
    z=p.stat();assert(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns)
    return dict(path=str(p),sha256=h.hexdigest(),bytes=count)
def capture(row):
    assert descriptor(row['path'])==row,row['path']
    assert inputs.setdefault(row['path'],row)==row
    return row
def family(root,sha):
    ix=capture(descriptor(root/'index.json'));assert ix['sha256']==sha
    index=json.loads((root/'index.json').read_bytes());names={'index.json'}
    for row in index['files']:
        n=row['path'];assert n and not n.startswith('/')and all(p not in('','.','..')for p in n.split('/'))and n not in names;names.add(n)
        capture(dict(row,path=str(root/n)))
    assert not any(p.is_symlink()for p in root.rglob('*'))
    assert{p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}==names
    return dict(index=ix,role='INDEXED_SOURCE_OR_PROOF_DATA_ORIGINAL_CONTEXT_NO_PREPARATION_REBASING')
def write(name,value):
    p=OWN/name;p.parent.mkdir(parents=True,exist_ok=True)
    if isinstance(value,(dict,list)):value=json.dumps(value,indent=2)+'\n'
    p.write_text(value)

families=[
    family(SCHED/'resource-integration-candidate-v1','20e6bab4c34da81c6657341f4ae917e78614e9503d689d4b046fb14b980fc414'),
    family(SCHED/'resource-pin-tooling-candidate-v1','c55fd0fc10854b853dc57eee77c276857399a4e086d7bac23730b95a1ce66238'),
    family(SCHED/'independent-resource-normal-off-bootstrap-review-v1','e9a798cc27adbfae7aaad58bc5275991998b58e20ff9906c7335218807ce3175'),
    family(CRYPTO/'ownership-component-candidate-v1','eb648e19274c055968557227221627e2ced5dd35a2c0fb17af941dbc9a8b5c30'),
]
bootstrap=json.loads((SCHED/'independent-resource-normal-off-bootstrap-review-v1/results.json').read_bytes())
assert bootstrap['verifiedPassed']is True and bootstrap['engineExecuted']is False and bootstrap['componentOrGuestExecuted']is False
assert bootstrap['resourceSourceIndexSha256']==families[0]['index']['sha256']and bootstrap['toolingSourceIndexSha256']==families[1]['index']['sha256']
actualBootstrapReview=dict(index=families[2]['index'],result=capture(descriptor(SCHED/'independent-resource-normal-off-bootstrap-review-v1/results.json')))
for key in('engine','metadata','freezeReceipt','bootstrapConfig','bootstrapRootObservation','reviewedPins','rootPinReview','cliWholeFrame'):
    capture(bootstrap[key])
actual=json.loads(Path(bootstrap['cliWholeFrame']['path']).read_bytes())
assert actual['engine']==bootstrap['engine']and len(actual['metadata']['sourceManifest'])==342 and len(actual['selectedManifests'])==9
native=[]
for row in actual['metadata']['sourceManifest']:
    d=descriptor(Path(actual['sourceRoot'])/row['path']);assert d['sha256']==row['sha256'];capture(d);native.append(d)

mapRow=capture(descriptor(CRYPTO/'ownership-component-candidate-v1/packaging-context.json'))
pack=json.loads(Path(mapRow['path']).read_bytes());ix=capture(pack['publicationIndex']);index=json.loads(Path(ix['path']).read_bytes())
assert ix['sha256']=='4621f7e72b4fb0555a5df630b1aedd4d2a04743b0db9188fc50099779f07387b'
assert len(pack['files'])==4934 and len(pack['links'])==22
for row in pack['files']:
    candidates=[r for r in index['files']if r['path']==row['path']];assert len(candidates)==1 and candidates[0]['sha256']==row['sha256']and candidates[0]['bytes']==row['bytes']
    capture(dict(path=str(Path(pack['publicationRoot'])/row['path']),sha256=row['sha256'],bytes=row['bytes']))
for link in pack['links']:
    p=Path(pack['publicationRoot'])/link['destination'];assert p.is_symlink()and p.readlink().as_posix()==link['newLinkText']and p.resolve()==Path(pack['publicationRoot'])/link['mappedTarget']
node=capture(dict(path='/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node',sha256='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0',bytes=108619024))
jco=capture(descriptor(Path(pack['toolchainRoot'])/'node_modules/@bytecodealliance/jco/dist/api.js'))
versions={}
for name in('@bytecodealliance/jco','@bytecodealliance/componentize-js','rolldown'):
    p=Path(pack['toolchainRoot'])/'node_modules'/name/'package.json';capture(descriptor(p));versions[name]=json.loads(p.read_bytes())['version']
versions['selectedPackager']=json.loads((Path(pack['packagerRoot'])/'package.json').read_bytes())['version']
assert versions=={'@bytecodealliance/jco':'1.40.0','@bytecodealliance/componentize-js':'0.23.0','rolldown':'1.2.16','selectedPackager':'0.23.0'}

fixtures={};derivation=[]
parent=SCHED/'resource-integration-candidate-v1/runtime'
for name,file in [('resource','guest.UNEXECUTED.mjs'),('pure','pure.UNEXECUTED.mjs'),('fatal','fatal.UNEXECUTED.mjs'),('init-fatal','init-fatal.UNEXECUTED.mjs')]:
    source=capture(descriptor(parent/file));write('fixtures/'+name+'.mjs',Path(source['path']).read_text());dest=descriptor(OWN/'fixtures'/f'{name}.mjs');assert source['sha256']==dest['sha256'];derivation.append(dict(kind='BYTE_EXACT_FIXTURE_COPY',original=source,afterimage='fixtures/'+name+'.mjs'))
    fixtures[name]=dict(code=dest,wit=None)
source=capture(descriptor(parent/'profile.wit'));write('fixtures/profile.wit',Path(source['path']).read_text());derivation.append(dict(kind='BYTE_EXACT_PUBLIC_WIT_COPY',original=source,afterimage='fixtures/profile.wit'))
driver=capture(descriptor(parent/'driver.template.mjs'));text=Path(driver['path']).read_text();literals=re.findall(r"const scalarWit='([^']+)';",text);assert len(literals)==1
write('fixtures/scalar.wit',literals[0]+'\n');derivation.append(dict(kind='EXACT_EXISTING_SCALAR_WIT_LITERAL_PLUS_FINAL_NEWLINE',original=driver,literal=literals[0],afterimage='fixtures/scalar.wit'))
for name in fixtures:fixtures[name]['wit']=descriptor(OWN/('fixtures/profile.wit'if name=='resource'else'fixtures/scalar.wit'))
refs=dict(schemaVersion=1,families=families,resourceSourceIndex=families[0]['index'],toolingIndex=families[1]['index'],actualBootstrapReview=actualBootstrapReview,bootstrapEntry=capture(descriptor(SCHED/'resource-pin-tooling-candidate-v1/bootstrap.mjs')),bootstrapConfig=bootstrap['bootstrapConfig'],bootstrapRootObservation=bootstrap['bootstrapRootObservation'],reviewedPins=bootstrap['reviewedPins'],rootPinReview=bootstrap['rootPinReview'],actualBootstrapWholeFrame=bootstrap['cliWholeFrame'],engine=bootstrap['engine'],metadata=bootstrap['metadata'],freezeReceipt=bootstrap['freezeReceipt'],configuredSourceRoot=actual['configuredSourceRoot'],frozenSourceRoot=actual['sourceRoot'],packagingMap=mapRow,packagingRoot=pack['packagingRoot'],toolchainRoot=pack['toolchainRoot'],packagerRoot=pack['packagerRoot'],jcoEntry=jco,node=node,fixtures=fixtures,packageVersions=versions,toolLinks=pack['links'])
write('references.json',refs)
write('fixture-derivations.json',dict(schemaVersion=1,entries=derivation,originalGuestCases=7,ordinaryGuestExportsExecuted=False))
write('native-source-data.json',dict(schemaVersion=1,sourceFiles=342,sourceRoot=actual['sourceRoot'],files=native,metadata=bootstrap['metadata'],allNineManifests=actual['selectedManifests'],actualBootstrapWholeFrame=bootstrap['cliWholeFrame'],nativeAuthorityProjected=False))
write('input-freeze.json',dict(schemaVersion=1,state='ORIGINAL_CONTEXT_RESOURCE_COMPONENT_SOURCE_INPUTS_V1',files=sorted(inputs.values(),key=lambda r:r['path']),allPathsAbsolute=True,toolRegularFiles=4934,toolLinks=pack['links'],originalPreparationContextsNeverRebased=True,nativeOriginalReferenceClosureOwnedByGenuineResourceBootstrap=True))
write('future-config.template.json',dict(schemaVersion=1,sourceIndexSha256=None,rootAuthority=None))
write('future-root-authority.template.json',dict(schemaVersion=1,state=None,sourceIndexSha256=None,phase=None,fixture=None,outputRoot=None,sourceIndependentReview=None,bootstrapConfig=None,bootstrapRootObservation=None,reviewedPins=None,rootPinReview=None,workerTimeoutMs=600000,maxComponentBytes=64*1024*1024,maxBundleBytes=32*1024*1024,componentConstructionAllowed=False,initializationOnly=True,nativeBuildAllowed=False,nativeFreezeAllowed=False,sourcePromotionAllowed=False,ordinaryExportsAllowed=False,timerRuntimeAllowed=False,guestLoadingAllowed=False,hostRequestsAllowed=False,gcAllowed=False,keyOrCryptoAllowed=False,timingAllowed=False,operationalAdmission=False,runtimeAcceptanceClaim=False,metadataProjectionAllowed=False))
write('future-source-peer-contract.json',dict(schemaVersion=1,state='INDEPENDENT_SCHEDULER_RESOURCE342_COMPONENT_SOURCE_REVIEW_PASSED_V1',sourceIndexSha256=None,sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,grantsAnyActionAuthority=False))
write('future-artifact-contract.json',dict(schemaVersion=1,state='NO_ACTUAL_RESOURCE_COMPONENT_ARTIFACT_PROOF_V1',sourceIndexSha256=None,actualConstruction=None,actualArtifactReview=None,actualLoadingSource=None,runtimeAuthority=None,expectedNativeEngineSha256=bootstrap['engine']['sha256'],expectedMetadataSha256=bootstrap['metadata']['sha256'],resourceSourceIndexSha256=families[0]['index']['sha256'],requiredTimerInterfaces=['wasi:clocks/monotonic-clock@0.2.10','wasi:io/poll@0.2.10'],pureExpectedImports=[],actualGeneratedFileNames=None,asyncScalarRuntimeProof=False,initializerRefusalUniqueCauseProof=False,clockTypeGraphRequired=True,ordinaryExportsAllowed=False,timerRuntimeAllowed=False,operationalAdmission=False))
write('preparation-history.json',dict(schemaVersion=1,readAssumptions=['Initial unquoted resource-bootstrap* shell glob matched no path; corrected to rg --files inventory before reading.', 'Initial generic donor lookup assumed references/worker/parent/options filenames in v3; actual v3 uses build/build-worker and v1 generic utilities. No helper ran.'],sourceCheckFailures=[],helperOrBootstrapOrPackagerOrGuestActionsInvoked=False))
print(json.dumps(dict(preparationRows=len(inputs),packageFiles=4934,links=22,nativeSources=342,fixtureCopies=5,scalarLiteral=1,noActions=True)))
