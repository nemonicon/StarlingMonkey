"""Private source/build-DATA preparation only. Does not touch actual freeze outputs."""
from pathlib import Path
import ast,copy,json,os
import review_io as I
import artifact_model as M
HERE=Path(__file__).resolve().parent;K=HERE.parent
def row(p):return I.descriptor(str(p))
def load(p):return I.read(row(p))
def index(name,sha,size):
    d=dict(path=str(K/name/'index.json'),sha256=sha,bytes=size);v,rows=I.indexed(d,'private source preparation '+name);return d,v,[d,*rows]
def write(name,v):
    with(HERE/name).open('xb')as f:f.write((json.dumps(v,indent=2)+'\n').encode());f.flush();os.fsync(f.fileno())
source,_,source_rows=index('ownership-gc-native-candidate-v2','ed0665046ec293b846069df0c050a388b1d717abbf4a0e56c64d8bd17d9a6d05',4777)
native_peer,_,_=index('independent-ownership-gc-native-v2-source-review-v1','1cc950ddf49925b7b454e8c464cfe3dea1fdfdd9acf6c0d4d66ac58462824e3a',1223)
controller,_,_=index('ownership-gc-freeze-controller-candidate-v1','502027c9e3547a1e42ba1315195463ccc258b195a489ee9e551cae17bbddf218',3425)
controller_peer,_,_=index('independent-ownership-gc-freeze-controller-source-review-v1','22bc75b86704765d857df246a2f94557f4092011c573b82109f3b5fba86682ad',927)
build_index,_,_=index('independent-ownership-gc-v2-native-build-review-v1','fc0c7e3c925df4abc22e3018dcc42e66bea073ae6a1d62d1a764e94c2930c9a7',1945)
contract=load(K/'independent-ownership-gc-v2-native-build-review-v1/result-contract.json');build=I.read(contract['reviewResult'])
for k,v in contract['requiredFixedValues'].items():M.equal(build[k],v,'sealed BUILD-only exact field '+k)
for k,d in contract['requiredExactDescriptors'].items():M.equal(build[k],d,'sealed BUILD-only descriptor '+k);I.verify(d,'actual complete BUILD-only DATA')
m=I.read(build['metadata']);policy=load(Path(M.TOOLS).parent/'policy.json');native,external=M.metadata(m,policy)
# Full normal protection snapshot is read now; actual freeze path is never touched.
normal=load(K/'ownership-gc-native-candidate-v2/normal-protection.json')
I.need(len(normal['originals'])==1387 and len(normal['requiredNormalFreezeMembership'])==1391,'full original normal counts')
for r in normal['originals']:I.verify(r['original'],'initial normal original protection');I.verify(r['frozen'],'initial normal frozen protection')
for r in normal['frozenCopyEntries']:I.verify(r,'initial normal copy protection')
I.verify(normal['freezeReceipt'],'normal immutable receipt');I.exact_tree(I.canonical(normal['freezeReceipt']['path']).parent,normal['requiredNormalFreezeMembership'])
cache=next(r for r in normal['frozenCopyEntries']if r['path'].endswith('/normal-off-CMakeCache.txt'));db=next(r for r in normal['frozenCopyEntries']if r['path'].endswith('/normal-off-compile_commands.json'))
I.need(cache['sha256']=='a2c669f76091a646e85beacef9e80567f378259e0f3f2f5371a5c7dd834426a3'and cache['bytes']==31924,'normal original cache exact protected datum');I.need(db['sha256'].startswith('d88a5f')and db['bytes']==125409,'normal original compile DB exact protected datum')
grammar=[]
for name in ['context.py','guard.py','freeze.py','freezer-body.py']:
    p=K/'ownership-gc-native-candidate-v2'/name;ast.parse(I.verify(row(p)).read_text());grammar.append(str(p))
body=(K/'ownership-gc-native-candidate-v2/freezer-body.py').read_text();guard=(K/'ownership-gc-native-candidate-v2/guard.py').read_text()
I.need("'rootAuthority': context['rootAuthority']"in body and "frame['rootAuthority']==read(frame['captured'][0])['rootAuthority']"in guard,'closed actual frame-field binding preserved')
I.need('validate_plan(plan, receipt_path, output=output_root)'in body and 'execute_plan(plan, output=output_root)'in body,'genuine explicit output API')
I.need("common.OUTPUT==Path('/tmp/starling-node-compat/production-crypto-owner-v2/native-freeze')"in guard and 'common.REPO=='in guard and 'common.HERE=='in guard,'actual donor context asserts preserved')
negatives=[]
for name,mutate in [('gc mode',lambda x:x.update(gcStress=False)),('entropy',lambda x:x.update(entropyPolicy='runtime-only')),('normal source projection',lambda x:x.update(enginePath='/private/tmp/normal.wasm')),('runtime owner proof',lambda x:x['cryptoKeyOwnershipPolicy'].update(runtimeValidation=True)),('missing native row',lambda x:x['sourceManifest'].pop()),('duplicate native row',lambda x:x['sourceManifest'].__setitem__(0,x['sourceManifest'][1])),('backend promoted',lambda x:x['zlibPolicy'].update(runtimeBackendProof=dict(verified=True,version='fake',vernum=1)))]:
    changed=copy.deepcopy(m);mutate(changed)
    try:M.metadata(changed,policy)
    except(AssertionError,KeyError,TypeError):negatives.append(dict(name=name,rejected=True))
    else:raise AssertionError('independent model accepted '+name)
for p in HERE.glob('*.py'):ast.parse(p.read_text());grammar.append(str(p))
I.final_rehash()
write('preparation-inputs.json',dict(schemaVersion=1,files=list(I.ROWS.values()),finalRehash=True,scope='source + already completed build DATA + unchanged normal originals only; no GC freeze output read'))
write('preparation-observations.json',dict(schemaVersion=1,state='SOURCE_READER_PREPARED_ACTUAL_GC_FREEZE_PENDING',sourceIndex=source,sourcePeerIndex=native_peer,controllerSourceIndex=controller,controllerPeerIndex=controller_peer,buildOnlyReviewIndex=build_index,fullNative355SourceModelCheckedOnActualBuildMetadata=True,fullNormalProtectionRehashed=True,normalOriginals=1387,normalFrozenMembers=1391,protectedOriginalCache=cache,protectedOriginalCompileDatabase=db,parsedSources=grammar,independentPureMetadataNegatives=negatives,readHashChecks=I.CHECKS,pureModelChecks=M.CHECKS,uniquePhysicalInputs=len(I.ROWS),actualFreezeOutputRead=False,actualFreezeVerdict=None,verifiedPassed=False,ownerActionsInvoked=False,actionAuthority=None,operationalAdmission=False,runtimeAcceptanceClaim=False,timingAllowed=False))
print(json.dumps(dict(state='PREPARED_ONLY_ACTUAL_FREEZE_PENDING',inputs=len(I.ROWS),checks=I.CHECKS,pureNegatives=len(negatives),actualFreezeOutputRead=False,verdict=None)))
