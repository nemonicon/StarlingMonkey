"""Independent data/source reader. No owner imports, actions, copies or patch apply."""
from pathlib import Path
import codecs
import collections
import difflib
import hashlib
import json
import os
import re
import stat

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CLASSIC = HERE.parent
PLAN = CLASSIC/'production-adoption-v1/artifact-closure-plan-v1'
PLAN_SHA = '96b4536ddb54484d665d93d64b6bc1af794dda977c189f50222238bad73a716e'
TARGETS = [
 'builtins/node-compat/classic-streams/classic-core.generated.mjs',
 'builtins/node-compat/classic-streams/transformation-receipt.json',
 'builtins/node-compat/classic-streams/factories.generated.h',
 'tests/node-compat/build-engine.sh',
 'tests/node-compat/classic-streams-admission.mjs',
]
TARGET_PATHS = {str((REPO/p).resolve()):p for p in TARGETS}
REFERENCES = {}
CACHE = {}

def sha(data): return hashlib.sha256(data).hexdigest()

def record(path, expected=None, size=None):
 path = Path(path).absolute()
 before = path.lstat()
 assert stat.S_ISREG(before.st_mode), str(path)
 key = (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)
 if key not in CACHE:
  h = hashlib.sha256()
  with path.open('rb') as stream:
   for block in iter(lambda:stream.read(1024*1024),b''): h.update(block)
  CACHE[key] = h.hexdigest()
 after = path.lstat()
 assert key == (after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns), str(path)
 actual = CACHE[key]
 if expected is not None: assert actual == expected, (str(path),actual,expected)
 if size is not None: assert before.st_size == size, str(path)
 item = {'path':str(path),'sha256':actual,'bytes':before.st_size}
 old = REFERENCES.setdefault(str(path),item)
 assert old == item
 return item

def raw(path, expected=None, size=None):
 record(path,expected,size)
 return Path(path).read_bytes()

def load(path, expected=None): return json.loads(raw(path,expected))

def put(name,value):
 path = HERE/name
 with path.open('x') as output:
  json.dump(value,output,indent=2); output.write('\n')

def index(root,expected=None):
 doc = load(root/'index.json',expected)
 assert len(doc['files']) == len({row['path'] for row in doc['files']})
 for row in doc['files']:
  relative = Path(row['path'])
  assert not relative.is_absolute() and '..' not in relative.parts
  record(root/relative,row['sha256'],row['bytes'])
 return doc

def tree(root):
 rows=[]
 def visit(current):
  assert current.is_dir() and not current.is_symlink()
  for path in sorted(current.iterdir()):
   info=path.lstat()
   kind='symlink' if stat.S_ISLNK(info.st_mode) else 'directory' if stat.S_ISDIR(info.st_mode) else 'file' if stat.S_ISREG(info.st_mode) else None
   assert kind
   rows.append({'path':str(path.relative_to(root)),'kind':kind})
   if kind=='directory':visit(path)
 visit(root)
 return sorted(rows,key=lambda row:row['path'])

def resolve_row(manifest,row):
 path=Path(row['path'])
 return path if path.is_absolute() else manifest.parent/path

def manifest(path,check_rows=True):
 doc=load(path)
 rows=doc.get('inputs',doc.get('files',[]))
 assert isinstance(rows,list)
 hits=[]
 for number,row in enumerate(rows):
  assert isinstance(row,dict) and isinstance(row.get('path'),str), (str(path),number)
  resolved=resolve_row(path,row)
  if check_rows:record(resolved,row['sha256'],row.get('bytes'))
  canonical=str(resolved.resolve())
  if canonical in TARGET_PATHS:
   hits.append({'row':number,'manifest':str(path),'recordedPath':row['path'],
    'originalPath':str(resolved.absolute()),'canonicalPath':canonical,
    'target':TARGET_PATHS[canonical],'expectedSha256':row['sha256'],
    'bytes':row.get('bytes')})
 return doc,hits

def classification(path,assets):
 name=str(path)
 if any(name.endswith('/'+relative) and record(path)['sha256']==expected for relative,expected in assets.items()):
  return 'repository-native-source-binary-exception-five-paths-only'
 if path.suffix.lower() in {'.a','.so','.dylib','.node','.tar','.gz','.zip','.exe'}:
  return 'reference-only-host-sdk-or-dependency-binary'
 if path.suffix.lower() in {'.wasm','.cwasm','.o','.obj'}:
  return 'external-binary-preservation-required'
 decoder=codecs.getincrementaldecoder('utf-8')()
 try:
  with path.open('rb') as stream:
   for block in iter(lambda:stream.read(1024*1024),b''):
    if b'\0' in block:return 'reference-only-host-sdk-or-dependency-binary'
    decoder.decode(block,final=False)
  decoder.decode(b'',final=True)
 except UnicodeDecodeError:return 'reference-only-host-sdk-or-dependency-binary'
 return 'repository-text-source-evidence-copy'

def main():
 own=index(PLAN,PLAN_SHA); assert len(own['files'])==20
 inventory=load(PLAN/'needed-files.json')
 files=inventory['files'];links=inventory['links']
 assert len(files)==17885 and len(links)==47 and not inventory['issues']
 by_path={row['path']:row for row in files};assert len(by_path)==len(files)
 assert all(str(Path(row['path']).resolve())==row['path'] for row in files)
 assets=load(PLAN/'source-binary-whitelist.json')['paths']
 assert assets==load(REPO/'tests/node-compat/milestone-v12-preparation/pins.json')['requiredSourceBinaryAssets']
 assert len(assets)==5
 totals={};inventory_mismatches=[]
 for row in files:
  path=Path(row['path']);actual=record(path)
  if actual['sha256']!=row['sha256'] or actual['bytes']!=row['bytes']:
   alternatives=[candidate['path'] for candidate in files if candidate['sha256']==row['sha256'] and candidate['path']!=row['path']]
   inventory_mismatches.append({'path':str(path),'expectedSha256':row['sha256'],'expectedBytes':row['bytes'],'actualSha256':actual['sha256'],'actualBytes':actual['bytes'],'roles':row['roles'],'inventoryDeclaredAlternativePaths':alternatives})
  assert classification(path,assets)==row['proposedPreservation'],str(path)
  for declared in row['declaredPaths']:assert str(Path(declared).resolve())==row['path']
  category=row['proposedPreservation']
  total=totals.setdefault(category,{'files':0,'logicalBytes':0,'allocatedBytesObserved':0})
  total['files']+=1;total['logicalBytes']+=row['bytes'];total['allocatedBytesObserved']+=row['allocatedBytes']
 assert totals==inventory['totalsByProposedPreservation']
 for row in links:
  path=Path(row['path']);assert path.is_symlink()
  assert os.readlink(path)==row['linkText']
  assert str(path.resolve())==row['resolvedTarget']
 summaries=inventory['inputManifestAndScopeSummaries']
 kinds=collections.Counter(row['kind'] for row in summaries)
 assert kinds=={'indexed-classic-source-or-proof-packet':129,'actual-critical-family-consumed-input':8,'staged-corrected-source-family':2,'completed-classic-evidence-root':9}
 tool_trees={};tool_links={};classic_hits=[]
 for summary in summaries:
  path=Path(summary['path']);kind=summary['kind']
  if kind in {'indexed-classic-source-or-proof-packet','staged-corrected-source-family'}:
   doc=index(path.parent,summary['sha256']);assert len(doc['files'])==summary['rows']
   for item in [path]+[path.parent/row['path'] for row in doc['files']]:assert str(item.resolve()) in by_path
  elif kind=='actual-critical-family-consumed-input':
   doc,hits=manifest(path);classic_hits+=hits
   assert record(path)['sha256']==summary['sha256'] and len(doc['inputs'])==summary['rows']
   for row in doc.get('toolTrees',[]):
    root=Path(row['path']);assert str(root.resolve())==row['realPath']
    assert tree(root)==row['entries'];tool_trees[str(root)]=len(row['entries'])
   for row in doc.get('toolLinks',[]):
    link=Path(row['path']);assert link.is_symlink() and os.readlink(link)==row['linkText']
    assert str(link.resolve())==row['resolvedTarget']
    if row['targetKind']=='file':record(row['resolvedTarget'],row['targetSha256'],row['targetBytes'])
    tool_links[str(link)]=row
  else:
   # Re-enumerate only the nine explicitly recorded terminal roots, never node_modules.
   count=0
   for parent,dirs,names in os.walk(path,followlinks=False):
    dirs[:]=[name for name in sorted(dirs) if name not in ['node_modules','.git','target','__pycache__']]
    dirs[:]=[name for name in dirs if not(Path(parent)/name).is_symlink()]
    for name in names:
     entry=Path(parent)/name
     if entry.is_file() or entry.is_symlink():
      count+=1
      if not entry.is_symlink():assert str(entry.resolve()) in by_path,str(entry)
   assert count==summary['terminalTreeRegularOrLinkEntries'],(str(path),count)
 assert len(classic_hits)==20
 planned={(row['manifest'],row['resolvedPath'],row['sha256']) for row in inventory['originalPathDependenciesForFivePromotionTargets']}
 assert planned=={(row['manifest'],row['canonicalPath'],row['expectedSha256']) for row in classic_hits}
 freeze_rows=[]
 for row in inventory['freezeInventories']:
  doc=load(row['receipt'],row['receiptSha256'])
  assert len(doc['copies'])==row['copies']
  for copy in doc['copies']:
   record(copy['path'],copy['sha256'],copy['bytes']);assert str(Path(copy['path']).resolve()) in by_path
  freeze_rows.append({'label':row['label'],'copies':row['copies'],'receiptSha256':row['receiptSha256'],'engineSha256':row['engineSha256'],'diagnosticOnly':row['diagnosticOnly']})
 assert sorted(row['copies'] for row in freeze_rows)==[474]*4+[525]*2
 capacity=load(PLAN/'capacity.json');assert capacity['byClass']==totals
 selected=sum(total['logicalBytes'] for category,total in totals.items() if category!='reference-only-host-sdk-or-dependency-binary')
 assert selected==4477421192==capacity['copyAllSelectedNonHostSdkBytesUpperBound']
 assert selected*2+1024**3==10028584208==capacity['conservativeReserveTwoCopiesPlus1GiB']
 assert capacity['reserveFitsObservedCapacity']==(capacity['availableBytesObserved']>=selected*2+1024**3)
 fs=os.statvfs('/tmp/starling-node-compat');current_free=fs.f_bavail*fs.f_frsize
 mapping=load(PLAN/'rollforward-map.json');assert {row['path'] for row in mapping['files']}==set(TARGETS)
 expected_patch='';deltas=[]
 for row in mapping['files']:
  before=raw(PLAN/row['beforeStagedPath'],row['beforeSha256'],row['beforeBytes'])
  after=raw(PLAN/row['afterStagedPath'],row['afterSha256'],row['afterBytes'])
  assert raw(REPO/row['path'])==before and raw(row['afterSource'])==after
  expected_patch+=''.join(difflib.unified_diff(before.decode().splitlines(True),after.decode().splitlines(True),fromfile='a/'+row['path'],tofile='b/'+row['path']))
  deltas.append({'path':row['path'],'beforeSha256':sha(before),'afterSha256':sha(after),'native':row['native']})
 assert raw(PLAN/'rollforward.UNAPPLIED.patch').decode()==expected_patch
 selector=mapping['unchangedSelector'];record(REPO/selector['path'],selector['sha256'])
 record(Path(mapping['files'][0]['afterSource']).parents[3]/selector['path'],selector['afterSha256'])
 policy=load(CLASSIC/'trace-integration-candidate-v1/policy.json')
 source=Path('/tmp/starling-node-compat/classic-trace-source-v1')
 changed={row['path']:row for row in mapping['files'] if row['native']}
 native=[]
 for row in policy['expectedNativeSourceManifest']:
  after=record(source/row['path'],row['sha256'])
  before=record(REPO/row['path'],changed[row['path']]['beforeSha256'] if row['path'] in changed else row['sha256'])
  native.append({'path':row['path'],'beforeSha256':before['sha256'],'afterSha256':after['sha256']})
 assert len(native)==342 and sum(row['beforeSha256']==row['afterSha256'] for row in native)==339
 # Discovery is bounded to regular manifests under tests/node-compat; owner code is never imported.
 discovered=[];schema_skips=[]
 for parent,dirs,names in os.walk(REPO/'tests/node-compat',followlinks=False):
  dirs[:]=[name for name in dirs if name not in ['node_modules','.git','__pycache__','history','milestones'] and not(Path(parent)/name).is_symlink()]
  for name in ['input-freeze.json','source-inputs.json']:
   if name not in names:continue
   path=Path(parent)/name;doc=load(path)
   rows=doc.get('inputs',doc.get('files',[]))
   if not isinstance(rows,list) or any(not isinstance(row,dict) or not isinstance(row.get('path'),str) for row in rows):
    schema_skips.append({'path':str(path),'reason':'not path-descriptor-list; not silently treated as checked'});continue
   hits=[]
   for number,row in enumerate(rows):
    item=resolve_row(path,row)
    if str(item.resolve()) in TARGET_PATHS:
     record(item,row['sha256'],row.get('bytes'))
     hits.append({'row':number,'recordedPath':row['path'],'target':TARGET_PATHS[str(item.resolve())],'expectedSha256':row['sha256'],'bytes':row.get('bytes')})
   if hits:discovered.append({'manifest':str(path),'sha256':record(path)['sha256'],'rows':len(rows),'directOldRootRows':hits})
 nonclassic=[row for row in discovered if '/foundation-classic-streams/' not in row['manifest']]
 current=[]
 configs=[('zlib-current-runtime','foundation-zlib/component-validation-activated-v8','input-freeze.json'),('zlib-disabled-validation','foundation-zlib/disabled-validation-candidate-v1','input-freeze.json'),('zlib-current-source-publisher','foundation-zlib/component-validation-buffer-input-amendment-v1','input-freeze.json'),('zlib-native-producer','foundation-zlib/native-integration-candidate-v4','input-freeze.json'),('consumers-current-source','foundation-stream-consumers/production-text-json-candidate-v2','source-inputs.json')]
 for role,relative,name in configs:
  root=REPO/'tests/node-compat'/relative;doc=index(root)
  data,hits=manifest(root/name)
  current.append({'role':role,'root':str(root),'indexSha256':record(root/'index.json')['sha256'],'indexedFiles':len(doc['files']),'manifest':str(root/name),'manifestSha256':record(root/name)['sha256'],'manifestRows':len(data.get('inputs',data.get('files',[]))),'directOldRootRows':hits})
 future=REPO/'tests/node-compat/foundation-stream-consumers/native-integration-candidate-v1'
 future_pins=load(future/'artifact-tools/tool-pins.json')
 assert len(future_pins['toolDependencies'])==767
 future_targets=[row for row in future_pins['toolDependencies'] if row['path'] in TARGETS]
 for row in future_targets:assert row['sha256']!=record(REPO/row['path'])['sha256']
 future_context={'root':str(future),'sealedIndexPresent':(future/'index.json').exists(),'toolPinsSha256':record(future/'artifact-tools/tool-pins.json')['sha256'],'toolRows':767,'stageRelativeTargetRows':future_targets,'originMapPresent':(future/'tool-origins.json').exists(),'classification':'Unsealed draft snapshot; relative build/admission rows select consumer afterimages, not live old Root5. A sealed origin/preparation manifest still needs review before use.'}
 # Authenticate source flow for the decisive current-runtime consequence and negative classifications.
 source_paths=[REPO/'tests/node-compat/foundation-zlib/component-validation-activated-v8'/name for name in ['runtime-preflight.mjs','consumed.mjs']]
 source_paths+=[REPO/'tests/node-compat/foundation-zlib/native-integration-candidate-v4'/name for name in ['layer-policy.py','artifact-tools/artifact_common.py','artifact-tools/bootstrap-classifier.py']]
 source_paths+=[REPO/'tests/node-compat/foundation-stream-consumers/production-text-json-candidate-v2'/name for name in ['prepare-host.py','prepare-native.py','layer-policy.py','seal-source.py']]
 source_paths+=[future/'prepare-source.py']
 for path in source_paths:record(path)
 preflight=raw(source_paths[0]).decode();consumed=raw(source_paths[1]).decode()
 assert preflight.index('await verifyConsumedSeal(here')<preflight.index("await import(pathToFileURL(join(config.bootstrapRoot")
 assert 'const path = resolve(here, row.path);' in consumed and 'await ordinary(path, row.sha256, row.bytes)' in consumed
 assert 'assert.equal(hash(data), expected, path)' in consumed
 # The author may continue this unsealed draft. These are observation hashes,
 # deliberately not stable final-review inputs or approved executable bytes.
 draft_snapshots=[REFERENCES.pop(str((future/name).absolute())) for name in ['artifact-tools/tool-pins.json','prepare-source.py']]
 future_context['snapshotOnlyDescriptors']=draft_snapshots
 future_context['draftIsApprovedStableInput']=False
 # Late proofs remain a supplement, never silently changed initial inventory.
 late=load(PLAN/'late-proof-supplement.json')
 for row in late['independentTimingIntegrity']['files']:record(row['path'],row['sha256'],row['bytes'])
 numeric=Path('docs/node-compat/classic-stream-measurement-v1')
 numeric_doc=index(REPO/numeric,'dcd7542d07980c3559a39f3b4af3d14eee327663bc5b07275772c968a36222ad')
 result={'schemaVersion':1,'state':'SOURCE_REVIEW_HOLD_CURRENT_CONTEXT_AND_MUTABLE_SNAPSHOT_GAPS',
  'planIndexSha256':PLAN_SHA,'planIndexedFiles':20,'inventoryFiles':17885,'inventoryLinks':47,'scopeKinds':dict(kinds),'toolTrees':tool_trees,'distinctToolLinks':len(tool_links),'freezes':freeze_rows,'totals':totals,
  'capacity':{'selectedNonHostBytes':selected,'twoCopiesPlus1GiB':selected*2+1024**3,'observedAtPlan':capacity['availableBytesObserved'],'observedByThisReader':current_free,'futureCopyMustRecheckFreeSpace':True,'actualCopyOrArchiveCreated':False},
  'fiveExactDeltas':deltas,'fullNativeRows':342,'nativeChanged':3,'nativeUnchanged':339,'moduleSelectionUnchanged':selector,
  'classicPlannedImpactRows':20,'nonclassicDirectManifests':len(nonclassic),'nonclassicDirectRows':sum(len(row['directOldRootRows']) for row in nonclassic),'inventoryRehashMismatches':inventory_mismatches,
  'currentOwnerFrames':current,'futureConsumerProducerDraft':future_context,'schemaSkips':schema_skips,
  'blockers':[{'id':'ART-CLOSURE-M1','severity':'BEFORE_ANY_LIVE_ROLLFORWARD','finding':'The plan audits only20 direct oldRoot rows in four classic manifests. Current zlib v8 runtime, disabled validation and current publisher preparation each directly authenticate all five live preimages. Promotion invalidates their unchanged consumed seals. The current nonclassic disposition/migration map must be explicit before applying the five files.',
   'requiredResolution':'Preserve current owner source and actual outputs with exact original-context mappings; explicitly hold/retire existing source programs or derive new current source families/tool contexts. Do not claim a data-only archive reader reruns old preflight, rewrite old descriptors, or project350/355 native metadata.'}]+([{'id':'ART-CLOSURE-M2','severity':'BEFORE_ARCHIVE_COPY_OR_ZERO_MISMATCH_CLAIM','finding':'The sealed inventory includes mutable adoption text whose current bytes differ from its snapshot. See exact inventoryRehashMismatches.','requiredResolution':'Preserve an authentic old-byte witness if the original snapshot is to be copied, or issue an explicit new immutable supplement with current descriptor/context and explain superseded mutable text. Never overwrite the old plan or claim every old descriptor rehashed exact.'}] if inventory_mismatches else []),
  'sourceOnlyPlanLimits':['No archive assembler/originalPath mapping reader is implemented or reviewed by this plan.','Capacity is a point-in-time estimate; external Wasm and host/SDK references are not repository byte copies.','Original historical preflight code can reject changed live paths; archival integrity alone does not repair rerunnability.','Native3502261 and consumer source506 have zero direct oldRoot5 rows in their own manifests; referencing an immutable parent manifest file does not recursively follow its rows.','The unsealed future767 producer needs its final origin/preparation closure reviewed, not an inferred pass.','Numerical report dcd754 is a later separate sealed supplement, not part of the original17885 inventory.'],
  'numericLateSupplement':{'indexSha256':record(REPO/numeric/'index.json')['sha256'],'indexedFiles':len(numeric_doc['files'])},
  'noOwnerImportsOrActions':True,'noLiveOrHistoricalEdits':True,'oldPreflightRerunClaim':False,'acceptanceOrPerformanceClaim':False,'rootTerminalObservedByThisReader':False}
 put('results.json',result)
 put('all-discovered-direct-dependencies.json',{'manifests':discovered,'nonclassic':nonclassic,'scope':'regular input-freeze/source-inputs lists under tests/node-compat; histories, accepted milestones, symlinked trees and owner code execution excluded','schemaSkips':schema_skips})
 put('current-owner-dependencies.json',{'currentOwnerFrames':current,'futureDraft':future_context})
 put('five-file-native-ledger.json',{'nativeSources':native,'promotion':deltas})
 put('external-references.json',{'files':sorted(REFERENCES.values(),key=lambda row:row['path']),'binaryCopiesInsideReview':False})
 print(json.dumps({'state':result['state'],'inventoryFiles':len(files),'links':len(links),'currentOwnerFrames':len(current),'nonclassicDirectManifests':len(nonclassic),'externalReferencePaths':len(REFERENCES),'inventoryRehashMismatches':len(inventory_mismatches),'blockers':[row['id'] for row in result['blockers']]}))

if __name__=='__main__':main()
