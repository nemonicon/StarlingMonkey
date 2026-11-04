#!/usr/bin/env python3
"""Read/hash/AST source inspection only. No owner/helper/stage imports or calls."""
import ast,difflib,hashlib,json,stat
from pathlib import Path
P=Path(__file__).resolve().parent
K=P.parent
C=K/'native-integration-candidate-v1'
B=K.parent/'foundation-stream-consumers/native-integration-candidate-v2'
seen={}
def need(v,m):
 if not v:raise AssertionError(m)
def row(p,e=None):
 p=Path(p);s=p.lstat();need(stat.S_ISREG(s.st_mode),'ordinary final file '+str(p));h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 r=dict(path=str(p),sha256=h.hexdigest(),bytes=s.st_size)
 if e:need(all(r[k]==e[k] for k in ['sha256','bytes']),'exact tuple '+str(p))
 seen[str(p)]=r;return r
def data(p):return json.loads(Path(p).read_text())
def write(n,d):(P/n).write_text(json.dumps(d,indent=2)+'\n')
def indexed(root,pin):
 need(row(root/'index.json')['sha256']==pin,'exact source index');d=data(root/'index.json')
 for x in d['files']:row(root/x['path'],x)
 return d
def main():
 own=indexed(C,'10a87c1d7c1c5b040a164c168c716a8da9fc23cecc1c8eb1f33f898097c426db');need(len(own['files'])==38,'38 new source files')
 prep=data(C/'input-freeze.json');need(len(prep['files'])==1271 and prep['parentPreparationManifestsFollowed'] is False,'1271 finite original prep references only')
 for x in prep['files']:row(x['path'],x)
 parent=indexed(B,'9edf31c16af401ac688a4ab9bfe2a01f0338739a6554fc12caa3b2f8ba03a378')
 owner=indexed(K/'key-owner-candidate-v1','216d0272025145f70c3a1e1c5e4f27cc3cc47ef6f97ae8131467e803db3c47d0')
 guard=indexed(K/'prototype-key-guard-candidate-v1','73fbf4f24e013bfe6f7f87830c95b8690ef1700683d9b9620b09ce839d9da831')
 policy=data(C/'policy.json');old=data(B/'policy.json');before={r['path']:r['sha256'] for r in old['expectedNativeSourceManifest']};after={r['path']:r['sha256'] for r in policy['expectedNativeSourceManifest']};crypto=policy['cryptoKeyOwnershipSourcePolicy']
 changed={p for p in before if before[p]!=after[p]};need(len(before)==len(after)==355 and set(before)==set(after) and len(changed)==5 and len(before)-len(changed)==350,'full distinct355 identity with350 unchanged5 replacements')
 need(changed=={r['path'] for r in crypto['changes']},'exact changed crypto source paths')
 composition=data(K/'prototype-key-guard-candidate-v1/composition.json');need(row(K/'prototype-key-guard-candidate-v1/composition.json')['sha256']==crypto['compositionSha256'],'exact composed source proof')
 for r in crypto['changes']:
  need(before[r['path']]==r['beforeSha256'] and after[r['path']]==r['afterSha256'],'exact crypto355 source preimage/afterimage')
  row(r['afterimage'],dict(sha256=r['afterSha256'],bytes=r['bytes']))
 need(policy['profileVersion']==old['profileVersion']=='sm-node-22.14.0-m0.14','unchanged Node module export profile')
 for n in ['streamConsumersSourcePolicy','zlibSourcePolicy','classicTraceSourcePolicy','strictPolicyVersion','protectedPolicyVersion','embedding']:
  need(policy[n]==old[n],'unchanged parent source/boundary contract '+n)
 need(crypto['runtimeValidation'] is None and crypto['allCopiesErasedClaim'] is False and len(crypto['remainingFollowons'])==3,'runtime/BIGNUM/private-copy/bounds followons remain open')
 der=data(C/'derivations.json')
 for r in der['files']:
  a=''.join(difflib.restore(r['ndiff'],1)).encode();b=''.join(difflib.restore(r['ndiff'],2)).encode();need(a==Path(r['parentPath']).read_bytes() and b==(C/r['path']).read_bytes(),'reversible actual source bytes '+r['path']);need(hashlib.sha256(a).hexdigest()==r['beforeSha256'] and hashlib.sha256(b).hexdigest()==r['afterSha256'],'derivation hash binding')
 for n in der['parentByteIdenticalSourceFiles']:need((C/n).read_bytes()==(B/n).read_bytes(),'parent mechanism byte identity '+n)
 need(len(der['files'])==16 and der['exactFivePayloadsPreserved'] is True and der['composedNativeEdits']==20,'16 mechanism derivations preserve20 composed native edits')
 native=data(C/'native-origins.json')['files'];tools=data(C/'tool-origins.json')['files'];pins=data(C/'artifact-tools/tool-pins.json')
 need(len(native)==355 and len(tools)==921,'native/tool origin counts')
 need({x['path']:(x['sha256'],x['bytes']) for x in tools}=={x['path']:(x['sha256'],x['bytes']) for x in pins['toolDependencies']},'tool origins and authenticated stage tool-pins agree')
 plan={}
 def add(name,original,sha,size):
  need(not Path(name).is_absolute() and all(x not in ('','.','..') and len(x.encode())<=255 for x in name.split('/')),'bounded stage path')
  r=row(original,dict(sha256=sha,bytes=size))
  if name in plan:need(plan[name]['sha256']==sha and plan[name]['bytes']==size,'same-byte overlap')
  else:plan[name]=dict(path=name,original=str(original),sha256=sha,bytes=size)
 for x in native:
  need(after[x['path']]==x['sha256'],'native stage origin actual new identity');b=Path(x['original']).read_bytes();add(x['path'],x['original'],x['sha256'],len(b))
 for x in tools:add(x['path'],x['original'],x['sha256'],x['bytes'])
 prefix='tests/node-compat/foundation-crypto/native-integration-candidate-v1'
 add(prefix+'/index.json',C/'index.json',row(C/'index.json')['sha256'],(C/'index.json').stat().st_size)
 for x in own['files']:add(prefix+'/'+x['path'],C/x['path'],x['sha256'],x['bytes'])
 stage=(C/'stage.py').read_text();need(stage.index('authority(descriptor, expected)  #')<stage.index('plan = collect(expected)')<stage.index("['git', 'clone'"),'Root and indexed peer authority before any stage output/Git action')
 need("INDEPENDENT_CRYPTO_OWNER355_NATIVE_INTEGRATION_SOURCE_REVIEW_PASSED_V1" in stage and "result['sourceReviewPassed'] is True" in stage,'exact independent stage prerequisite, unissued by this HOLD')
 need("'--no-local', '--no-checkout'" in stage and "assert not (DEST / '.git/objects/info/alternates').exists()" in stage,'fresh ordinary clone and no Git alternates')
 need('target.chmod(row[\'sourceMode\'])' in stage and 'after = collect(expected)' in stage,'separate source mode and complete postcopy original recheck')
 need('preparationManifestsInterpreted=False' in stage,'old prep contexts not rebased as stage inputs')
 layer=(C/'layer-policy.py').read_text();admit=(C/'build-admission.mjs').read_text();common=(C/'artifact-tools/artifact_common.py').read_text();bootstrap=(C/'artifact-tools/bootstrap-classifier.py').read_text();js=(C/'artifact-tools/bootstrap-preflight.mjs').read_text();recipe=(C/'proposed/tests/node-compat/build-engine.sh').read_text()
 need("values['ENABLE_BUILTIN_WEB_CRYPTO']=='ON'" in layer and "install_text.count(crypto_namespace)==1" in layer and 'assert len(crypto_changed)==3' in layer,'actual raw cache/install/three CPP build observations required')
 need("assert cache['ENABLE_BUILTIN_WEB_CRYPTO']=='ON'" in common,'frozen raw cache cryptoON check')
 need('metadata.cryptoKeyOwnershipPolicy,policy.cryptoKeyOwnershipSourcePolicy' in admit and "cryptoEvidence.changedNativeCompileCommands" in admit and 'layout.get(row.path)' in admit,'new policy and changed CPP commands tied to full layout')
 need("assert.fail('CryptoOwner355 operational admission CLOSED" in admit and 'export function validateCryptoOwnerBuildSourceAdmission' in admit,'named build-only gate, ordinary operation closed')
 need("crypto-owner-v1-build" in recipe and 'keyowner-v1' in recipe and "foundation-crypto/native-integration-candidate-v1" in recipe,'new bounded recipe/tool namespace')
 need("immutable-crypto-owner-release-engine-frozen" in common,'distinct immutable freeze state')
 # Authenticate the six unchanged launcher lifecycle functions by exact source.
 def funcs(p):
  t=p.read_text();tree=ast.parse(t);return {n.name:ast.get_source_segment(t,n) for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name!='main'}
 oldf=funcs(B/'artifact-tools/build-one.py');newf=funcs(C/'artifact-tools/build-one.py');need(oldf==newf and len(newf)==6,'six unchanged non-main launcher lifecycle definitions')
 for n in ['runtime-pins.json','bootstrap-pins.json']:
  d=data(C/n);need(all(v is None for v in d['variants'].values()),'four NULL checked-in '+n)
 future=data(C/'future-authority.json');need(future['sourceStageAuthority'] is None and future['nativeBuildAuthority'] is None,'future source/build authority null')
 # Actual exposed contexts: inspect the Python result and exact JS return.
 need("'sourceRoot':pin['sourceRoot'],'configuredSourceRoot':str(common.REPO)" in bootstrap,'Python authentic classifier returns both actual roots')
 return_text=js[js.index('return Object.freeze({'):]
 need('sourceRoot:actual.sourceRoot' in return_text and 'configuredSourceRoot' not in return_text,'concrete JS return drops configured root')
 callers=[]
 for p in K.rglob('*.mjs'):
  if 'cryptoOwnerBootstrapPreflight' in p.read_text():callers.append(str(p))
 need(callers==[str(C/'artifact-tools/bootstrap-preflight.mjs')],'no current crypto JS consumer beyond exported definition')
 contract=data(C/'bootstrap-contract.json');need(contract['componentHarnessRoot'] is None and contract['componentHarnessClosureComplete'] is False,'future component harness remains absent/unapproved')
 need('configuredSourceRoot' not in contract['bootstrapApi'] and 'Python bootstrap additionally returns configuredSourceRoot' in contract['configuredVsFrozenSource'],'contract distinguishes narrower JS API from Python')
 finding=dict(id='CRYPTO-OWNER355-CONTEXT-API-M1',state='API_DOCUMENTATION_CLARIFICATION_HOLD',pythonProducer=dict(path=str(C/'artifact-tools/bootstrap-classifier.py'),line=74),jsWrapper=dict(path=str(C/'artifact-tools/bootstrap-preflight.mjs'),line=33),actualPythonFields=['sourceRoot:frozen','configuredSourceRoot:common.REPO'],actualJSFields=['sourceRoot:frozen'],missingJSField='configuredSourceRoot',currentJSCallers=callers,currentComponentHarness=None,stageOrNativeRecipeFailureEstablished=False,claimNotEndorsed='README bootstrap returns both contexts',requiredDisposition='Expose the authenticated classifier configuredSourceRoot through a separately reviewed immutable successor, or qualify the documented JS API and future-consumer requirements. Do not invent/derive configuredRoot from frozen sourceRoot.',stagePeerPassStateIssued=False)
 result=dict(schemaVersion=1,state='INDEPENDENT_CRYPTO_OWNER355_SOURCE_IDENTITY_VERIFIED_CONTEXT_API_HOLD',sourceIndexSha256=row(C/'index.json')['sha256'],sourceOnly=True,sourceIdentityAndDataIntegrityPassed=True,sourceReviewPassed=False,ownerActionsInvoked=False,sourceFilesRehashed=38,preparationRowsRehashed=1271,nativeSources=355,unchangedParentNativeSources=350,changedNativeSources=5,exactComposedNativeEdits=20,reversibleMechanismDerivations=16,byteIdenticalParentMechanismFiles=7,toolRows=921,prospectiveStageUniqueRows=len(plan),prospectiveStageWasExecuted=False,unchangedLauncherLifecycleFunctions=list(newf),actualWebCryptoRawBuildEvidenceRequired=True,ordinarySelectorsRemainClosed=True,metadataProjectionAccepted=False,sourceFinding=finding,nativeRuntimeOrCryptoProofIssued=False,operationalAdmission=False,sourcePromotionAllowed=False,remainingFollowons=crypto['remainingFollowons'],uniqueInputsRehashed=len(seen))
 write('prospective-stage-inputs.json',[plan[k] for k in sorted(plan)]);write('source-findings.json',[finding]);write('rehashed-inputs.json',[seen[k] for k in sorted(seen)]);write('results.json',result);print(json.dumps(dict(state=result['state'],inputs=len(seen),stageRows=len(plan),changedNative=5)))
if __name__=='__main__':main()
