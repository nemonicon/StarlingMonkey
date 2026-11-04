#!/usr/bin/env python3
"""Source/data-only harness review: no oracle, codec, bootstrap or guest calls."""
import ast
import hashlib
import json
from pathlib import Path
import re
import stat

HERE=Path(__file__).resolve().parent
FAMILY=HERE.parent
BASE=FAMILY/'component-validation-candidate-v1'
AMEND=FAMILY/'component-validation-control-evidence-amendment-v1'
seen={}
def checked(path,pin=None,size=None):
 path=Path(path);before=path.lstat();assert stat.S_ISREG(before.st_mode),str(path)
 digest=hashlib.sha256()
 with path.open('rb')as stream:
  for chunk in iter(lambda:stream.read(1024*1024),b''):digest.update(chunk)
 after=path.lstat();assert(before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns),str(path)
 value=digest.hexdigest()
 if pin is not None:assert value==pin,str(path)
 if size is not None:assert before.st_size==size,str(path)
 seen[str(path)]={'path':str(path),'sha256':value,'bytes':before.st_size};return value
def load(path):checked(path);return json.loads(Path(path).read_bytes())
def indexed(root,pin,count):
 checked(root/'index.json',pin);document=load(root/'index.json');assert len(document['files'])==count
 for row in document['files']:checked(root/row['path'],row['sha256'],row['bytes'])
 return document
indexed(BASE,'a7eca2349282a29649806c327c41ea19f01be9673c0bd7c72201f30672819816',25)
indexed(AMEND,'fd3ec6efb2f5b2aeadc2f673560be951071025b48d084f63bcbd57faa72d5353',8)
for root,count in[(BASE,8414),(AMEND,8423)]:
 manifest=load(root/'input-freeze.json');assert len(manifest['inputs'])==count
 for row in manifest['inputs']:checked((root/row['path']).resolve(),row['sha256'],row['bytes'])
def roundtrip(proof_name,parent_name,new_name,count):
 proof=load(AMEND/proof_name);before=(BASE/parent_name).read_text();after=(AMEND/new_name).read_text()
 assert hashlib.sha256(before.encode()).hexdigest()==proof['beforeSha256']and hashlib.sha256(after.encode()).hexdigest()==proof['afterSha256']
 value=before;positions=[];assert len(proof['edits'])==count
 for edit in proof['edits']:
  assert edit['count']==1 and value.count(edit['old'])==1;at=value.index(edit['old']);positions.append(at);value=value[:at]+edit['new']+value[at+len(edit['old']):]
 assert value==after
 for at,edit in reversed(list(zip(positions,proof['edits']))):
  assert value[at:at+len(edit['new'])]==edit['new'];value=value[:at]+edit['old']+value[at+len(edit['new']):]
 assert value==before
 return after
driver=roundtrip('transformation-proof.json','run-validation.mjs','proposed/run-validation.mjs',4)
publisher=roundtrip('activation-proof.json','activate.py','activate.py',6)
component=(BASE/'component.mjs').read_text();corpus=(BASE/'corpus.mjs').read_text()
contract=load(BASE/'profile-contract.json');assert len(contract['exports'])==40 and len(contract['sync'])==6 and len(contract['deferred'])==31
contract_literal=(BASE/'profile-contract.mjs').read_text();assert json.loads(contract_literal[len('export const contract=Object.freeze('):-3])==contract
node=load(BASE/'node-results.json');assert node['node']=='v22.14.0'and len(node['cases'])==61 and len(node['dataFiles'])==28
assert len(node['inventory']['exports'])==40 and len(node['inventory']['constants'])==107
assert node['inventory']['zMaxChunk']=={'type':'number','valueEncoding':'positive-infinity'}
assert node['inventory']['vernum']=={'type':'number','value':4865}
assert [row['index']for row in node['cases']]==list(range(61))
for row in node['dataFiles']:checked(row['path'],row['sha256'],row['bytes'])
oracle=load(BASE/'node-oracle-receipt.json');assert oracle['rawExitCode']==0 and oracle['cases']==61 and oracle['dataFiles']==28
assert oracle['rawStdoutStderrCapturedAsFiles']is False
checked(BASE/'node-oracle.mjs',oracle['generatorSha256']);checked(BASE/'corpus.mjs',oracle['corpusSha256']);checked(BASE/'node-results.json',oracle['oracleSha256']);checked(BASE/'node-fixtures.mjs',oracle['fixturesSha256'])
assert len((BASE/'node-fixtures.mjs').read_text())==204736
checked(oracle['command'][0],oracle['nodeExecutableSha256'])
assert 'MAX_INPUT=1048576,MAX_OUTPUT=16777216'in corpus
assert "phase:'boundary'"in corpus and "phase:'large-output'"in corpus
assert 61+50+50+61+61==283
assert "import zlib,* as namespace from 'node:zlib'"in component and "import {Buffer} from 'node:buffer'"in component
assert re.search(r"module\.exports\s*=\s*require\('node:zlib'\)",(BASE/'canonical-require.cjs').read_text())
assert 'decoded.equals(expected)'in driver and 'assert.deepEqual(bytes,expected)'not in driver
assert 'nodeZlib[decoder](bytes' in driver and 'compressedByteIdentityRequired:false'in driver
assert driver.index("save('calls/'+id+'.raw.txt',raw)")<driver.index('const value=JSON.parse(raw)')
assert driver.index("await progress('wasmtime-terminal'")<driver.index('assert(result.terminalExitZeroObserved&&result.ownedGroupGone)')
assert 'maxOutputBytes:64*1024*1024'in driver and 'timeoutMs:600000'in driver
assert "paths.add(join(output,'package.json'))"in driver and 'outputLinks:[moduleLink]'in driver
assert 'readlink(moduleLink.path),moduleLink.linkText'in driver and 'realpath(moduleLink.path),moduleLink.resolvedTarget'in driver
assert 'directPrivateBackendObserved:false'in driver and 'runtimeBackendMetadataRemainsUnverified:true'in driver
assert "key==='ZLIB_VERNUM'?{type:'number',value:admission.expectedHeader.vernum}:expected"in driver
# The three missing assertions are established without running owner code.
assert 'calls++;'in component and 'const result={calls,'in component
assert 'value.calls'not in driver and 'expectedCalls'not in driver
assert 'fields.errno'not in driver and 'fields.operation.own'not in driver
assert component.count('await import(aliasId)')==1
assert 'sameAliases:names.every(name=>alias[name]===namespace[name])'in component
assert 'aliasCache'not in component and 'canonicalCache'not in component
assert "BOOTSTRAP_INDEX='3ff3a59d4fc1fafa32b2ba1e6ec5a1b8d7787f4e7eca1ee6855d7b38cc7c45db'"in publisher
assert "DECLARED=Path('/tmp/starling-node-compat/zlib-source-v1')"in publisher
assert "assert bootstrap_sha==BOOTSTRAP_INDEX"in publisher
assert publisher.index('boot_rows=indexed(bootstrap,bootstrap_sha)')<publisher.index("spec_from_file_location('actual_zlib350_validation_bootstrap'")
assert 'operationalAdmission' in publisher and "stage.mkdir(exist_ok=False)"in publisher and "open('xb')"in publisher
future=load(BASE/'future-authority.json');assert future['bootstrapSourceIndexSha256']is None and future['reviewedPins']is None and future['rootReview']is None
assert all(value is None for value in future['variants'].values())
for family in['component-validation-activated-v1','component-validation-activated-v2']:
 assert not(FAMILY/family).exists()and not(FAMILY/(family+'.staging')).exists()
tool_seal=load(BASE/'tool-seal.json');assert len(tool_seal['toolTrees'])==2 and len(tool_seal['toolLinks'])==22
source_tests=load(BASE/'evidence/source-tests.json');assert source_tests['passed']==117 and len(source_tests['checks'])==117
syntax=load(BASE/'evidence/syntax-results.json');assert len(syntax['checks'])==13
for row in syntax['checks']:
 checked(BASE/row['path'],row['sha256'])
 if row['kind']=='Node --check':assert row['status']==0 and row['stdout']==row['stderr']==''
python=[]
for root in[BASE,AMEND]:
 for path in root.glob('*.py'):ast.parse(path.read_text());python.append(str(path.relative_to(FAMILY)))
for row in list(seen.values()):checked(row['path'],row['sha256'],row['bytes'])
findings=[
 {'id':'ZVAL-M1','kind':'missing-call-counter-assertions','locations':['component.mjs:8,19,29,32,41','mandatory amended run-validation.mjs:38,43,47,49-53'],'issue':'Guest returns calls, but namespace/checkCase never read or validate it. Planned record counts do not prove retained/fresh per-instance counters.','correction':'New immutable successor should require retained1..161, freshJco1..61, freshWT1, GC1..3, with moduleContract0 initially/fresh and meaningful post-rotation checkpoints.'},
 {'id':'ZVAL-M2','kind':'missing-native-error-shape-assertions','locations':['mandatory amended run-validation.mjs:43','profile-contract.json nativeCodecErrorFields/facadeErrorFields'],'issue':'Native errno is captured but not checked. Existing checks cover only own string code/module/profile; they do not enforce own finite numeric/integer errno and absent operation for codec errors, or the complementary facade error shape.','correction':'Classify finite codec-origin versus facade-origin error cases from actual source, validate errno/operation ownership/types accordingly, preserve Node/profile deviations.'},
 {'id':'ZVAL-M3','kind':'namespace-cache-probe-absent','locations':['component.mjs:17-19','mandatory amended run-validation.mjs:38'],'issue':'One dynamic bare import and equal binding values do not test repeated same-specifier namespace identity despite the cache claim.','correction':'Repeat per-ID imports under the declared finite bundler contract; require per-ID cache identity plus binding equality, without inventing cross-ID namespace identity.'}
]
report={'schemaVersion':1,'state':'INDEPENDENT_PUBLIC_ZLIB_VALIDATION_SOURCE_REVIEW_HOLD_COVERAGE_AND_PRODUCER_REBIND','baseIndexSha256':checked(BASE/'index.json'),'mandatoryControlEvidenceIndexSha256':checked(AMEND/'index.json'),'baseFiles':25,'amendmentFiles':8,'preparationRows':[8414,8423],'controlEvidenceDriverEdits':4,'controlEvidencePublisherEdits':6,'publicExports':40,'syncMethods':6,'deferredMethods':31,'caughtRefusals':68,'nodeOracleCases':61,'nodeFullByteFilesVerified':28,'typedConstants':107,'fixtureCodeUnits':204736,'plannedNormalCodecCalls':283,'plannedGcCases':3,'maxInputBytes':1048576,'maxOutputBytes':16777216,'compressedByteIdentityRequired':False,'fullByteComparisonAndRawBeforeValidationReviewed':True,'outputPackageAndNodeModulesLinkAmendmentCoherent':True,'publicOnlyImportsAndSourceCoupledVernumInferenceReviewed':True,'rootMetadataBackendNotPromoted':True,'pendingProducerRebind':{'oldIndex':'3ff3a59d4fc1fafa32b2ba1e6ec5a1b8d7787f4e7eca1ee6855d7b38cc7c45db','oldStage':'/tmp/starling-node-compat/zlib-source-v1','oldSourceBlockedByIndependentProducerFindings':True,'currentProducerNotAdmitted':True,'required':'New immutable coherent harness successor must bind the reviewed corrected producer/recipe/policy/helper/stage and future genuine actual bootstrap authority; no source/metadata projection.'},'mandatoryCoverageFindings':findings,'otherConcretePublisherBlockersFound':[],'ownerEvidenceAuthenticatedNotRerun':{'sourceChecks':117,'syntaxChecks':13,'nodeOracleExitZeroRecorded':True,'rawOracleStdoutStderrFilesUnavailable':True},'pythonASTParsed':python,'futurePinsNullAndOutputsAbsent':True,'ownerHelpersOrSourceCliTestsOrNodeOracleOrCodecOrBootstrapOrBundlesOrNativeOrGuestOrHostExecuted':False,'runtimeAcceptanceClaim':False,'operationalAdmission':False,'performanceClaim':False,'limitations':['Unexecuted harness review only; no actual350 build/link/runtime/backend/GC/import/result proof.','Existing claimed source cache/counter/error coverage needs the listed new assertions before activation.','GC plan retains application strong owners and exercises existing publicBuffer hooks, not isolated codec temporary roots or heap ownership.','Source-only600s deadlines/outputcaps do not establish resource or deadline adequacy.'],'verifiedFiles':sorted(seen.values(),key=lambda row:row['path'])}
with(HERE/'results.json').open('x')as stream:json.dump(report,stream,indent=2);stream.write('\n')
print(json.dumps({'state':report['state'],'verifiedPaths':len(seen),'nodeOracleCases':61,'byteFiles':28,'mandatoryCoverageFindings':3,'currentActivationApproved':False}))
