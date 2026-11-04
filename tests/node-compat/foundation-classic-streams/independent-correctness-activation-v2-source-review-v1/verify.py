#!/usr/bin/env python3
"""Independent source/data reader, never an activation or backend import."""
import ast
import difflib
import hashlib
import json
import os
from pathlib import Path
import stat

HERE=Path(__file__).resolve().parent
FAMILY=HERE.parent
OWNER=FAMILY/'measurement-correctness-activation-candidate-v2'
PARENT=FAMILY/'measurement-correctness-activation-candidate-v1'
BASE=FAMILY/'measurement-correctness-candidate-v1'
REPORTING=FAMILY/'measurement-correctness-reporting-amendment-v1'
PERSIST=FAMILY/'measurement-correctness-persistence-amendment-v1'
seen={}
def checked(path,expected=None,size=None):
 path=Path(path);before=path.lstat();assert stat.S_ISREG(before.st_mode),str(path)
 digest=hashlib.sha256()
 with path.open('rb')as stream:
  for chunk in iter(lambda:stream.read(1024*1024),b''):digest.update(chunk)
 after=path.lstat();assert(before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns),str(path)
 value=digest.hexdigest()
 if expected is not None:assert value==expected,str(path)
 if size is not None:assert before.st_size==size,str(path)
 seen[str(path)]={'path':str(path),'sha256':value,'bytes':before.st_size};return value
def load(path):checked(path);return json.loads(Path(path).read_bytes())
def indexed(root,digest,count):
 checked(root/'index.json',digest);document=load(root/'index.json');assert len(document['files'])==count
 for row in document['files']:checked(root/row['path'],row['sha256'],row['bytes'])
 return document
indexed(OWNER,'4ef958e973bddea315c383e22e58e3f2908da874a0796fe738ad69ab3eed79bd',15)
indexed(PARENT,'ce2f254f2cf27d44df5f0d23915ca4e09c98ac15b2f88f762d41f57fb8e6048e',19)
indexed(BASE,'138a4e0bcfe22ef3b48375257a50958f595dcebb607fc9267a30080948d612da',36)
indexed(REPORTING,'0558b50589680f9e1b812c8a62210233a768385bfabeae2f07be47c2e1fe5350',14)
indexed(PERSIST,'60a8687e9b6bfff4c68df2a36e9dd47ad0f5cd327441f8cf32d63caa67518ba8',35)
manifest=load(OWNER/'input-freeze.json');assert len(manifest['inputs'])==6960
for row in manifest['inputs']:
 assert Path(row['path']).is_absolute();checked(row['path'],row['sha256'],row['bytes'])
before=(PARENT/'activate.py').read_text();after=(OWNER/'activate.py').read_text();proof=load(OWNER/'transformation-proof.json')
assert hashlib.sha256(before.encode()).hexdigest()==proof['beforeSha256']
assert hashlib.sha256(after.encode()).hexdigest()==proof['afterSha256']
assert proof['reverseExact']is True and len(proof['edits'])==6
value=before
for edit in proof['edits']:
 assert edit['count']==1 and value.count(edit['old'])==1
 at=value.index(edit['old']);assert edit['afterOffsets']==[at]
 value=value[:at]+edit['new']+value[at+len(edit['old']):]
assert value==after
for edit in reversed(proof['edits']):
 at=edit['afterOffsets'][0];assert value[at:at+len(edit['new'])]==edit['new']
 value=value[:at]+edit['old']+value[at+len(edit['new']):]
assert value==before
patch=''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/activate.py',tofile='b/activate.py'))
assert patch==(OWNER/'activation.UNAPPLIED.patch').read_text()
for name in ['authority.py','future-authority.json']:assert(OWNER/name).read_bytes()==(PARENT/name).read_bytes()
future=load(OWNER/'future-authority.json');assert future['reviewedPins']is None and future['rootReviewReceipt']is None and future['actualONEngineTuple']is None
assert 'UNCONFIGURED'in future['state']
assert after.index('load_authority(pin_path')<after.index('persist_rows=indexed(PERSIST,PERSIST_INDEX)')<after.index("spec_from_file_location('benchmark_common'")
assert "backend.require_source_root(CANONICAL)"in after and "backend.verify_frozen(LABEL)"in after
assert 'assert pin[key]==value' in after
assert "payload['component-driver.mjs']=regular(PERSIST/'proposed/component-driver.mjs')"in after
assert "payload['bounded-comparison.mjs']=regular(AMEND/'bounded-comparison.mjs')"in after
assert "payload['durable-host.mjs']=regular(PERSIST/'durable-host.mjs')"in after
names_start="names=['native-provider.mjs'";names_end='payload={name:regular(BASE/name)'
assert after[after.index(names_start):after.index(names_end)]==before[before.index(names_start):before.index(names_end)]
payload_names=['native-provider.mjs','guest.mjs','workload.mjs','encoding-cases.mjs','activation-contract.mjs','runtime-preflight.template.mjs','consumed.mjs','bundle-diagnostic.mjs','completion.mjs','run.UNEXECUTED.mjs','node-workload-oracle.json','node-encoding-oracle.json']
for name in payload_names:checked(BASE/name)
for marker in ["for root in [BASE,PRODUCER]", "receipt['copies']", "metadata['sourceManifest']",'backend.capture_addons()', 'backend.tool_dependencies(CANONICAL)',"tool_trees==original['toolTrees']and tool_links==original['toolLinks']", "regular(path,sha(raw))==raw", "for row in inputs.values():", "regular(stage/name,sha(raw),len(raw))"]:assert marker in after
assert "'boundary':'.'"in after and "'CONFIG_SHA':sha(payload['activation-template.json'])"in after and "'INPUTS_SHA':sha(payload['input-freeze.json'])"in after
assert "stage.mkdir(exist_ok=False)"in after and "path.open('xb')"in after
assert after.rindex('load_authority(pin_path')>after.index('stage.mkdir(exist_ok=False)')
assert after.rindex('tool_snapshot(roots)==(tool_trees,tool_links)')>after.index('stage.mkdir(exist_ok=False)')
assert "OUTPUT=HERE.parent/'measurement-correctness-activated-v2'"in after
for suffix in ['','\.staging']:
 path=FAMILY/('measurement-correctness-activated-v2'+suffix.replace('\\',''))
 assert not path.exists()and not path.is_symlink()
base_manifest=load(BASE/'input-freeze.json')
assert manifest['toolTrees']==base_manifest['toolTrees']and manifest['toolLinks']==base_manifest['toolLinks']
assert len(manifest['toolTrees'])==2 and len(manifest['toolLinks'])==22
for row in manifest['toolLinks']:
 path=Path(row['path']);assert path.is_symlink()and os.readlink(path)==row['linkText']
 assert str(path.resolve())==row['resolvedTarget']
 if row['targetKind']=='file':checked(path.resolve(),row['targetSha256'],row['targetBytes'])
adapter_suffix='/host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm'
live=[r for r in manifest['inputs']if r['path']==str(FAMILY.parents[2])+adapter_suffix]
assert len(live)==1 and live[0]['sha256']=='988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0'
pins_path=FAMILY/'production-adoption-v1/reviewed-diagnostic-v3-on-pins.json'
review_path=FAMILY/'production-adoption-v1/diagnostic-v3-on-root-review-receipt.json'
checked(pins_path,'2e9811a54b03733d7d4dde0b42f66831a9b97da2c2f26313f078443dc329165c')
checked(review_path,'9681578ea64c826f72baa1e1bff1533af276ff27d6dda52c5bf1dbe064697001')
pins=load(pins_path);review=load(review_path);on=pins['variants']['benchmark-classic-on']
assert pins['variants']['benchmark-classic-off']is None and on['reviewRequired']is False
assert pins['state']=='ROOT_REVIEWED_CLASSIC_TRACE_BENCHMARK_DIAGNOSTIC_FREEZES_V3'
assert on['sourceIndexSha256']=='46c031d36c1691c3980c51d44102e1a7cc651ff4bf8b9470c9e746697eece8bc'
assert on['recipeSha256']=='d98d1129db0a55abe18c2b96e7fe314ab27d6bc9a2ef481abed3f07d996fbba6'
for key in ['engineSha256','engineBytes','metadataSha256','freezeReceiptSha256']:assert review[key]==on[key]
assert on['engineSha256']=='12a8f7dc79e12e8bc3519b3fe72e898b226bbabde6930e63d3a6c30706b88274'
stored=load(OWNER/'evidence/source-tests.json');assert stored['passed']==31 and len(stored['checks'])==31
assert stored['actionMainOrGenuineVerifierOrPreflightOrGuestOrNativeOrTargetHostInvoked']is False
python=[]
for path in OWNER.glob('*.py'):ast.parse(path.read_text());python.append(path.name)
for row in list(seen.values()):checked(row['path'],row['sha256'],row['bytes'])
report={'schemaVersion':1,'state':'INDEPENDENT_CORRECTNESS_ACTIVATOR_V2_SOURCE_REVIEW_PASSED_NO_ACTIONS','ownerIndexSha256':checked(OWNER/'index.json'),'ownerFiles':15,'inputRows':6960,'exactForwardReverseEdits':6,'oldSourcePacketsUnchanged':True,'nativeAuthorityAndFutureNullTemplateByteIdentical':True,'sameActualOnPinsSha256':checked(pins_path),'sameActualRootReviewSha256':checked(review_path),'actualAuthorityJSONComparedDataOnly':True,'actualFrozenVerifierInvoked':False,'mandatoryPersistenceDriverAndHelper':True,'mandatoryOriginalBoundedComparison':True,'originalPayloadFiles':payload_names,'guestWorkloadOraclesProviderQueueBundleCompletionChanged':False,'fullActualSourceFrozenToolClosureMechanismPreserved':True,'toolTrees':2,'toolLinksVerified':22,'liveAdapter988Sealed':True,'privateRuntimePrecheckAndRecheckMechanismUnchanged':True,'beforeAndAfterPublicationAuthoritySourceToolChecksRetained':True,'exclusiveFreshV2OutputStillAbsent':True,'resumeOrOldObservationReuse':False,'ownerStoredPureChecksAuthenticated':31,'ownerTestsOrActionsRerun':False,'pythonASTParsed':sorted(python),'concreteSourceBlockers':[],'nativeGuestComponentizerHostOrTimingExecuted':False,'fullCorrectnessPassed':False,'runtimeAcceptanceClaim':False,'limitations':['Source mechanism review only; actual activation and full fresh20/14 execution remain Root actions.','No all-case600-second adequacy or performance claim.','No crash, ENOSPC, concurrent-writer, reset, ALS or reuse guarantee.'],'verifiedFiles':sorted(seen.values(),key=lambda r:r['path'])}
with(HERE/'results.json').open('x')as stream:json.dump(report,stream,indent=2);stream.write('\n')
print(json.dumps({'state':report['state'],'verifiedPaths':len(seen),'ownerFiles':15,'inputs':6960,'edits':6,'concreteSourceBlockers':0}))
