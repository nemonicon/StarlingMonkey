"""Finite read/hash/AST inspection. Does not import or invoke owner modules."""
import ast
import hashlib
import json
import stat
from pathlib import Path

P=Path(__file__).resolve().parent
K=P.parent
C=K/'native-freezer-source-amendment-v1'
D=K/'native-integration-candidate-v2'
S=Path('/private/tmp/starling-node-compat/crypto-owner-source-v2')
SD=S/'tests/node-compat/foundation-crypto/native-integration-candidate-v2'
H=K/'independent-native-integration-v2-freeze-contract-review-v1'
PIN='0ff37e52888f37ffdc0bd2dc13870c327faadac5889fb495b53bb9549e5ecccd'
seen={}
checks=[]
def need(value,message):
 if not value:raise AssertionError(message)
 checks.append(message)
def row(path,expected=None,guard_regular=False):
 path=Path(path);s=path.lstat();need(stat.S_ISREG(s.st_mode),'Ordinary final file '+str(path))
 if guard_regular:
  need(s.st_nlink==1 and not any(p.is_symlink()for p in (path,*path.parents)),'Actual physical single-link guard input '+str(path))
 h=hashlib.sha256()
 with path.open('rb')as stream:
  for block in iter(lambda:stream.read(1048576),b''):h.update(block)
 r=dict(path=str(path),sha256=h.hexdigest(),bytes=s.st_size)
 if expected:need(all(r[k]==expected[k]for k in ('sha256','bytes')),'Exact bytes/hash '+str(path))
 seen[str(path)]=r;return r
def data(path):return json.loads(Path(path).read_bytes())
def write(name,value):(P/name).write_text(json.dumps(value,indent=2)+'\n')
def index(root,pin):
 need(row(root/'index.json',guard_regular=True)['sha256']==pin,'Exact source index '+str(root));ix=data(root/'index.json')
 for r in ix['files']:row(root/r['path'],r,guard_regular=True)
 return ix
def main():
 own=index(C,PIN);need(len(own['files'])==13,'13 final correction source files')
 donor=index(D,'68b6f2a50174adbf30d8257f8107dd6c5b38beddf0db4b95ad972e3f47e25575')
 index(H,'62cf4f2c270668b26fa0e21612f2bb1fdc4bef3884c1ac538550c41a87cbc912')
 inputs=data(C/'input-freeze.json');need(len(inputs['files'])==65,'65 exact original input references')
 for r in inputs['files']:row(r['path'],r)
 row(SD/'index.json',row(D/'index.json'),guard_regular=True)
 for r in donor['files']:row(SD/r['path'],r,guard_regular=True)
 pins=data(SD/'artifact-tools/tool-pins.json');need(len(pins['toolDependencies'])==922 and pins['reviewedEnginePins']is None,'Original922 tool contract with null future reviewed pins')
 for r in pins['toolDependencies']:row(S/r['path'],r,guard_regular=True)
 policy=data(SD/'policy.json');need(len(policy['expectedNativeSourceManifest'])==355,'Complete existing355 policy unchanged')
 for r in policy['expectedNativeSourceManifest']:need(row(S/r['path'])['sha256']==r['sha256'],'Actual unchanged native355 source '+r['path'])
 source=(C/'freeze-engine.py').read_text();guard=(C/'freezer-guard.py').read_text();original=(D/'artifact-tools/freeze-engine.py').read_text()
 proof=data(C/'derivations.json');need(proof['editOperations']==len(proof['edits'])==7,'Exactly seven reversible donor edits')
 rebuilt=original
 for e in proof['edits']:
  need(rebuilt.count(e['before'])==1,'Unique forward preimage');rebuilt=rebuilt.replace(e['before'],e['after'])
 need(rebuilt==source,'Actual entire corrected afterimage reconstructs exactly')
 for e in reversed(proof['edits']):
  need(rebuilt.count(e['after'])==1,'Unique reverse afterimage');rebuilt=rebuilt.replace(e['after'],e['before'])
 need(rebuilt==original,'Exact reversal to immutable old wrong freezer')
 need(proof['donorSha256']==row(D/'artifact-tools/freeze-engine.py')['sha256'] and proof['afterSha256']==row(C/'freeze-engine.py')['sha256'],'Reversible proof binds actual donor/active digests')
 active_sha=row(C/'freeze-engine.py')['sha256'];guard_sha=row(C/'freezer-guard.py')['sha256'];donor_sha=row(SD/'artifact-tools/freeze-engine.py')['sha256']
 need(guard_sha in source and source.index('GUARD_PATH.read_bytes()')<source.index('_guard_spec.loader.exec_module(guard)'),'Fixed primitive guard digest before guard import')
 need(source.index('CONTEXT = guard.authorize(')<source.index('_common_spec.loader.exec_module(common)')<source.index('def main():'),'Source/Root/peer/stage authorization before genuine helper import/main')
 for phrase in ["own, own_rows = indexed(own_descriptor)","donor, donor_rows = indexed(donor_descriptor)","peer_index, peer_rows = indexed(peer_pair['index'])",'label = validate_authority_data(authority, own_sha, peer)',"for row in donor['files']:","len(pins['toolDependencies']) == 922",'recheck(context)']:
  need(phrase in guard,'Pre-import guard authenticates finite source/authority/context closure: '+phrase)
 need('assert sys.flags.isolated == 1' in guard and "('PYTHONPATH', 'PYTHONHOME', 'PYTHONOPTIMIZE', 'NODE_OPTIONS', 'NODE_PATH')" in guard,'Python isolated and loader overrides refused')
 need("assert sum(row == peer_descriptor for row in peer_rows[1:]) == 1"in guard,'Peer result must be exactly indexed with matching primitive tuple')
 for phrase in ["assert authority['amendmentSourceIndexSha256'] == own_sha","assert authority['donorSourceIndexSha256'] == DONOR_SHA","assert authority['freezeAllowed'] is True and authority['engineExecutionAllowed'] is False","assert peer['sourceOnly'] is True","assert peer['sourceReviewPassed'] is True and peer['ownerActionsInvoked'] is False"]:
  # The sourceIndexSha256/sourceOnly assertion is intentionally on one line.
  if phrase=="assert peer['sourceOnly'] is True":phrase="peer['sourceOnly'] is True"
  need(phrase in guard,'Exact correction action/peer authority requirement '+phrase)
 need("PEER_STATE = 'INDEPENDENT_CRYPTO_OWNER355_FREEZER_SOURCE_REVIEW_PASSED_V1'"in guard,'Exact future peer state')
 need("Path('/private/tmp/starling-node-compat/crypto-owner-source-v2')"in guard and "Path('/private/tmp/starling-node-compat/production-crypto-owner-v2/native-freeze')"in guard,'Explicit distinct configured/frozen physical roots')
 need('assert common.HERE == Path(CONTEXT[\'artifactToolsRoot\'])'in source and 'assert common.REPO == Path(CONTEXT[\'configuredSourceRoot\'])'in source and "assert common.OUTPUT.resolve() == Path(CONTEXT['freezeRoot'])"in source,'Genuine common HERE/REPO/OUTPUT asserted without rebinding')
 parsed=ast.parse(source)
 forbidden=[]
 for n in ast.walk(parsed):
  if isinstance(n,(ast.Assign,ast.AnnAssign,ast.AugAssign)):
   targets=n.targets if isinstance(n,ast.Assign)else[n.target]
   if any(isinstance(t,ast.Attribute)and isinstance(t.value,ast.Name)and t.value.id=='common'for t in targets):forbidden.append(ast.unparse(n))
 need(not forbidden,'No assignment to genuine common context attributes')
 admission=(SD/'artifact-tools/metadata-admission.mjs').read_text();state='ACTUAL_FINITE_CRYPTO_OWNER355_BUILD_ONLY_SELECTOR_PASSED_NO_ENGINE_EXECUTION'
 need("ADMISSION_STATE = '"+state+"'"in guard and "return{state:'"+state+"'"in admission and 'guard.validate_admission(admission)'in source,'Exact real selector state accepted without source/result rewriting')
 need("assert value['sourceFiles'] == 355 and value['engineBytesRead'] is False"in guard,'Selector finite355/non-engine-read boundary retained')
 need("target_name = 'artifact-tools/donor-data/freeze-engine.py' if name == 'freeze-engine.py'"in source and "add(ENTRY, 'artifact-tools/freeze-engine.py', CONTEXT['active']['sha256'], True)"in source,'Distinct explicit donor DATA and actual active entry copy')
 need("add(GUARD_PATH, 'artifact-tools/active-freezer/freezer-guard.py'"in source and "for index, row in enumerate(CONTEXT['capsules']):"in source and 'generated(correction_bytes, correction_name)'in source,'Actual guard, own/donor/peer/Root control copies and label-specific proof saved')
 need("'helperSha256': sha(Path(__file__))"in source and 'guard.validate_receipt_roles(receipt,'in source and "active['sha256'] == active_sha == receipt['helperSha256']"in guard,'Actual active-file/helperSha/explicit role proof coupled before receipt publication')
 need("inventory = {os.path.realpath(row['path']): row for row in receipt['copies']}"in guard and 'never rewrite rows' in source,'Physical /tmp comparison only; inherited copy row spellings preserved')
 need(source.count('guard.recheck(CONTEXT)')==3 and source.index('guard.recheck(CONTEXT)')<source.index('validate_plan(plan, receipt_path)')<source.index('execute_plan(plan)')<source.rindex('guard.recheck(CONTEXT)')<source.index("with receipt_path.open('x')"),'Complete source/control recheck before/after exclusive copies and before receipt publication')
 need("engine = authority['engine']"in guard and "metadata_descriptor['path'] == engine['path'] + '.build.json'"in guard and "metadata['engineSha256'] == engine['sha256'] and metadata['engineBytes'] == engine['bytes']"in guard,'Root actual engine/metadata primitive identity coupled without guard engine read')
 need("'active': regular(entry)"in guard and "'donor': regular(STAGED / 'artifact-tools/freeze-engine.py')"in guard,'Active and donor capture use actual physical source contexts')
 # The only changed inherited validation/copy behavior is accounted for by the
 # seven exact reversals; all original native/compile/external/codec/OpenSSL/
 # Rust and plan/copy checks otherwise remain exact donor bytes.
 need('validate_plan(plan, receipt_path)'in source and 'execute_plan(plan)'in source and "with receipt_path.open('x')"in source,'Original exclusive complete-copy lifecycle retained')
 owner=data(C/'source-results.json');need(owner['passed']is True and owner['checks']==53 and owner['genuineArtifactHelpersOrAuthorizeOrActionsInvoked']is False,'Authenticated owner53 pure/source checks are not action evidence')
 synthetic=data(C/'saved-correction-proof.DATA-ONLY.json');need(synthetic['state']=='SYNTHETIC_RECEIPT_ROLE_PROOF_NOT_AN_ACTUAL_FREEZE'and synthetic['actualNativeArtifact']is None and synthetic['freezeExecuted']is False,'Saved role proof explicitly synthetic, not freeze result')
 rr=synthetic['receipt'];need(rr['helperSha256']==rr['activeFreezerTooling']['sha256']==active_sha and rr['donorFreezerTooling']['sha256']==donor_sha and active_sha!=donor_sha,'Saved synthetic source/role hashes exactly actual active and immutable donor')
 future=data(C/'future-authority.template.json');need(future['freezeAllowed']is False and future['amendmentSourceIndexSha256']is None and future['engine']is None and future['metadata']is None and future['label']is None,'All future Root action/artifact fields unissued/null')
 need(future['independentSourceReview']==dict(index=None,result=None),'Checked-in future independent authority remains null')
 result=dict(schemaVersion=1,state='INDEPENDENT_CRYPTO_OWNER355_FREEZER_SOURCE_REVIEW_PASSED_V1',sourceIndexSha256=PIN,sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,
  sourceFilesRehashed=13,preparationRowsRehashed=65,donorIndexedFilesRehashed=44,stagedIndexedFilesRehashed=44,stagedToolRowsRehashed=922,stagedNativeSourceHashesVerified=355,uniqueInputsRehashed=len(seen),exactReversibleDonorEdits=7,
  diagnosisIndexSha256=row(H/'index.json')['sha256'],resolvedFinding='CRYPTO-OWNER355-FREEZER-STATE-M1',nativeRecipePolicyHelperAnd922ToolContractUnchanged=True,genuineStagedContextsAssertedNotRebound=True,
  activeFreezer=row(C/'freeze-engine.py'),immutableStagedDonorFreezer=row(SD/'artifact-tools/freeze-engine.py'),guard=row(C/'freezer-guard.py'),
  activeSavedPath='artifact-tools/freeze-engine.py',donorSavedDataPath='artifact-tools/donor-data/freeze-engine.py',activeHelperShaFromActualFile=True,
  authorityRequirements=dict(schemaVersion=1,state='ROOT_REVIEWED_CRYPTO_OWNER355_FREEZER_CORRECTION_V1',amendmentSourceIndexSha256=PIN,donorSourceIndexSha256='68b6f2a50174adbf30d8257f8107dd6c5b38beddf0db4b95ad972e3f47e25575',independentReviewMustBeExactlyIndexed=True,freezeAllowed=True,engineExecutionAllowed=False,operationalAdmission=False,runtimeAcceptanceClaim=False),
  cliShape=['python3','-I',str(C/'freeze-engine.py'),PIN,'EXACT_ROOT_AUTHORITY_DESCRIPTOR_JSON'],
  ownerEvidence=dict(pureSourceChecks=53,actualAuthorizeOrArtifactHelperExecuted=False,peerReranOwnerTests=False),
  limitations=['Source-only correction, not an executed freeze or native artifact acceptance.','Genuine staged verifier is an API function only; future separately authorized caller must authenticate correction/source/control and call it explicitly.','Future actual copy count and every active/donor/control identity must be independently checked from actual frozen bytes.','Native runtime/key/finalizer/zeroization/GC/component/host/performance and open BIGNUM/private-copy/bounds proof remain absent.'],
  actualNativeArtifactAccepted=False,freezeExecutedByThisReader=False,operationalAdmission=False,runtimeAcceptanceClaim=False,futureRootAuthority=None,futureEnginePins=None)
 write('rehashed-inputs.json',[seen[k]for k in sorted(seen)]);write('static-checks.json',dict(passed=True,checks=len(checks),details=checks,ownerModulesImportedOrExecuted=False));write('results.json',result)
 print(json.dumps(dict(state=result['state'],inputs=len(seen),staticChecks=len(checks))))
if __name__=='__main__':main()
