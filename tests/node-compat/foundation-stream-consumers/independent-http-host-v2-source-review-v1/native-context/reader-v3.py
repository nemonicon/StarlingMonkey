#!/usr/bin/env python3
"""Independent DATA-only fixed HTTP-component/native-context rehash. No imports of owner code."""
import collections, hashlib, json, os, pathlib, stat, sys
ROOT=pathlib.Path('/Users/dan/dev/StarlingMonkey')
S=ROOT/'tests/node-compat/foundation-stream-consumers'
OUT=S/'independent-http-host-v2-source-review-v1/native-context'
REVIEW=S/'independent-http-component-v1-results-review-v1'
CAND=S/'http-construction-candidate-v1'
checks=0
physical={}
declared={}
path_components={}
allowed_links={}
def need(ok,message):
 global checks
 checks+=1
 if not ok: raise AssertionError(message)
def ident(st): return [st.st_dev,st.st_ino,st.st_mode,st.st_size,st.st_mtime_ns,st.st_ctime_ns]
def component_id(st): return [st.st_dev,st.st_ino,st.st_mode]
def strict_path(value,allow_final_link=False):
 p=pathlib.Path(value)
 need(p.is_absolute(),'not absolute: '+str(p))
 need('..' not in p.parts,'traversal: '+str(p))
 need('http-host-candidate-v2' not in p.parts,'changing v2 source forbidden')
 cur=pathlib.Path('/')
 for n,part in enumerate(p.parts[1:]):
  cur=cur/part; st=cur.lstat(); key=str(cur)
  record=component_id(st)
  if stat.S_ISLNK(st.st_mode):
   text=os.readlink(cur)
   if key=='/tmp': need(text=='private/tmp' and str(pathlib.Path('/tmp').resolve(strict=True))=='/private/tmp','unexpected /tmp alias')
   else:
    link=allowed_links.get(key)
    need(link is not None,'undeclared symlink: '+key)
    need(text==link['linkText'],'link text differs: '+key)
    need(n==len(p.parts)-2 and allow_final_link,'link not a declared terminal: '+key)
   record += [text]
  if key in path_components: need(path_components[key]==record,'component identity changed: '+key)
  else: path_components[key]=record
 need(str(p.resolve(strict=True))==('/private'+str(p) if str(p)=='/tmp' or str(p).startswith('/tmp/') else str(p)) or (allow_final_link and str(p) in allowed_links),'resolution beyond declared /tmp alias: '+str(p))
 return p.resolve(strict=True)
def read_hash(p):
 q=strict_path(str(p)); before=q.lstat();need(stat.S_ISREG(before.st_mode),'not regular: '+str(q))
 digest=hashlib.sha256(); count=0
 with q.open('rb') as f:
  need(ident(os.fstat(f.fileno()))==ident(before),'open identity mismatch: '+str(q))
  while True:
   b=f.read(1024*1024)
   if not b:break
   digest.update(b);count+=len(b)
  need(ident(os.fstat(f.fileno()))==ident(before),'changed during read: '+str(q))
 after=q.lstat();need(ident(after)==ident(before),'changed after read: '+str(q));need(count==before.st_size,'size mismatch')
 return str(q),{'sha256':digest.hexdigest(),'bytes':count,'identityBefore':ident(before),'identityAfter':ident(after)}
def verify(row,base=None,role='declared-input'):
 p=pathlib.Path(row['path'])
 if not p.is_absolute():
  need(base is not None,'relative descriptor missing base');p=pathlib.Path(base)/p
 key=str(p);q=str(strict_path(key));expected=(row['sha256'],row.get('bytes'))
 if q not in physical:
  actual_q,actual=read_hash(q);need(actual_q==q,'physical resolution mismatch');physical[q]=actual
 actual=physical[q]
 need(actual['sha256']==expected[0],'SHA mismatch: '+key)
 if expected[1] is not None:need(actual['bytes']==expected[1],'byte mismatch: '+key)
 if key in declared:
  need(declared[key]['sha256']==actual['sha256'] and declared[key]['bytes']==actual['bytes'],'conflicting declared descriptor')
 else:declared[key]={'path':key,'realPath':q,'sha256':actual['sha256'],'bytes':actual['bytes'],'roles':[]}
 if role not in declared[key]['roles']:declared[key]['roles'].append(role)
 return p

def load(p):
 # Every JSON loaded here is also directly hashed; it is parsed as data only.
 q,actual=read_hash(p)
 if q not in physical:physical[q]=actual
 else:need(physical[q]==actual,'JSON re-read identity changed: '+q)
 with pathlib.Path(q).open('rb') as f:return json.load(f)
def fixed(p,sha,n,role):verify({'path':str(p),'sha256':sha,'bytes':n},role=role);return load(p)
def verify_index(p,role):
 data=load(p);names=[]
 for row in data['files']:
  need(not pathlib.Path(row['path']).is_absolute() and '..' not in pathlib.Path(row['path']).parts,'index traversal');verify(row,pathlib.Path(p).parent,role);names.append(row['path'])
 need(len(names)==len(set(names)),'duplicate index paths');return data

def walk(root,include_dirs=True):
 root=strict_path(str(root));found=[]
 for current,dirs,files in os.walk(root,followlinks=False):
  for name in sorted(dirs+files):
   p=pathlib.Path(current)/name;st=p.lstat()
   kind='symlink' if stat.S_ISLNK(st.st_mode) else 'directory' if stat.S_ISDIR(st.st_mode) else 'file' if stat.S_ISREG(st.st_mode) else 'other'
   need(kind!='other','special tree member')
   if include_dirs or kind!='directory':found.append({'path':str(p.relative_to(root)),'kind':kind})
 return sorted(found,key=lambda x:x['path'])

idx=fixed(REVIEW/'index.json','da7a8d7937eec6a30eacf123312311313cae7d5affe7a1aa5ecff0460a496bad',2549,'fixed-component-review-index')
res=fixed(REVIEW/'results.json','368c3d5a3070dda8a11dda2e61034b23e2909733526defa67e626319fd50bf61',19212,'fixed-component-review-result')
contract=fixed(REVIEW/'result-contract.json','f371f4d6f6ac900d0832ccdb4dd49a7105d36942fa0cebc2b9dda21b121771c7',19755,'fixed-component-review-contract')
closure=fixed(CAND/'closure.json','b7d998c521d74ce78a3405a357efec25a8d1b7e1c7226cb129cf966407d8a93b',8384899,'fixed-original-finite-closure')
need(len(closure['toolLinks'])==22,'tool link count')
for link in closure['toolLinks']:
 for p in (link['path'],link['path'].replace('/tmp/','/private/tmp/',1)):
  allowed_links[p]=link
verify_index(REVIEW/'index.json','authenticated-component-review-member')
for k,v in contract['requiredFixedValues'].items():need(k in res and res[k]==v,'contract fixed field mismatch: '+k)
for k,v in contract['requiredExactDescriptors'].items():need(res[k]==v,'contract exact descriptor: '+k);verify(v,role='component-contract-exact-artifact')
need(contract['grantsHostActionAuthority'] is False and contract['constructionProofOnly'] is True and contract['nextRootAction'] is None,'contract scope changed')
for row in closure['files']:
 verify(row,role='original-finite-physical-closure')
 for alias in row.get('declaredPaths',[]):verify({'path':alias,'sha256':row['sha256'],'bytes':row['bytes']},role='original-closure-declared-alias')
need(len(closure['files'])==12667,'finite regular rows count')
for tree in closure['toolTrees']:
 need(str(strict_path(tree['path']))==tree['realPath'],'tool realpath mismatch')
 need(walk(tree['path'])==sorted(tree['entries'],key=lambda x:x['path']),'exact tool membership mismatch')
for link in closure['toolLinks']:
 p=pathlib.Path(link['path']);st=p.lstat();need(stat.S_ISLNK(st.st_mode),'declared link missing');strict_path(str(p),True)
 need(os.readlink(p)==link['linkText'],'tool link text changed')
 need(str(p.resolve(strict=True))==link['resolvedTarget'],'tool target changed')
 if link['targetKind']=='file':
  verify({'path':link['resolvedTarget'],'sha256':link['targetSha256'],'bytes':link['targetBytes']},role='explicit-tool-link-target')
 else:
  need(link['targetKind']=='directory' and stat.S_ISDIR(pathlib.Path(link['resolvedTarget']).lstat().st_mode),'declared directory tool target differs')
  need(link['resolvedTarget']=='/private/tmp/starling-node-compat/native-toolchain-lock/node_modules','unexpected directory target')
snapshot_initial=walk(closure['familySnapshotRoot'],False)
need([x['path'] for x in snapshot_initial]==sorted(closure['familySnapshotMembers']),'snapshot membership mismatch')
need(len(snapshot_initial)==1678 and all(x['kind']=='file' for x in snapshot_initial),'snapshot count or type')
for row in closure['liveInputs']:
 verify(row,role='sealed-live-WIT-adapter-input');verify({'path':str(ROOT/row['name']),'sha256':row['sha256'],'bytes':row['bytes']},role='current-live-WIT-adapter-input')
need(len(closure['liveInputs'])==8,'live input count')
ledger=load(REVIEW/'rehashed-inputs.json')
for row in ledger['files']:verify(row,role='authenticated-prior-finite-reference-rehashed-as-DATA')
need(len(ledger['files'])==14157,'prior reference row count')
source_index=verify(res['constructionSourceIndex'],role='original-source-index');source=verify_index(source_index,'original-source-index-member')
freeze=load(CAND/'input-freeze.json')
for row in freeze['files']:verify(row,role='original-finite-input-freeze-member')

actual={k:load(res[k]['path']) for k in ('componentAudit','metadata','packagingAudit','interfaceAudit','constructionConfig','rootAction','parentIndex','workerIndex','parentResult','parentCompletion','workerCompletion','externalParentTerminal','ownedWorkerTerminal')}
m=actual['metadata'];a=actual['componentAudit'];data=load(REVIEW/'data-results.json')
need(a['fullActualNativeMetadata']==m,'whole actual metadata differs from audit')
need(data['fullActualNativeMetadata']==m,'whole actual metadata differs from retained data')
need(len(m)==71,'metadata complete key count')
need(m['engineSha256']==res['engineSha256'] and m['engineBytes']==res['engine']['bytes'],'engine binding')
for k,v in {'entropyPolicy':'runtime-only','gcStress':False,'oomTesting':False,'strictInitialization':True,'profileEnabled':True,'streamConsumersEnabled':True,'hostApi':'wasi-0.2.10'}.items():need(m[k]==v,'normal-runtime metadata field: '+k)
need(len(m['sourceManifest'])==355 and len(m['componentizeSourceManifest'])==3,'source manifest lengths')
contexts=[closure['nativeConfiguredSourceRoot'],closure['nativeFrozenSourceRoot'],closure['packagingRoot']]
for row in m['sourceManifest']:
 for context in contexts:verify({'path':str(pathlib.Path(context)/row['path']),'sha256':row['sha256']},role='native355-full-source-context')
external=pathlib.Path(closure['nativeFrozenSourceRoot']).parent/'componentize-source'
for row in m['componentizeSourceManifest']:verify({'path':str(external/row['path']),'sha256':row['sha256']},role='external3-frozen-componentize-source')
selected=[]
for row in m['selectedModuleManifests']:
 p=verify({'path':str(pathlib.Path(closure['packagingRoot'])/row['path']),'sha256':row['sha256']},role='actual-selected-module-manifest')
 manifest=load(p);need(manifest['profileVersion']==row['profileVersion'],'selected manifest profile');selected.append(manifest)
need(len(selected)==11 and selected==a['actualSelectedManifests']==data['actualSelectedManifests'],'whole eleven actual manifests differ')
need('selectedInterfaces' not in a,'original componentAudit unexpectedly projected')
interfaces=['wasi:clocks/monotonic-clock@0.2.10','wasi:http/types@0.2.10','wasi:io/error@0.2.10','wasi:io/poll@0.2.10','wasi:io/streams@0.2.10','wasi:random/random@0.2.10']
need(a['allowedImports']==a['emittedImports']==actual['interfaceAudit']['selectedInterfaces']==actual['interfaceAudit']['emittedImports']==interfaces,'retained six interfaces')
need(a['emittedExports']==['wasi:http/incoming-handler@0.2.10'],'retained export')
clock=a['clockDependency'];need(clock['typeOnly'] is True and clock['types']==['duration'] and clock['durationRepresentation']=='u64' and clock['callableImports']==clock['coreClockImports']==[],'retained type-only clock')
need(a['componentSha256']==res['component']['sha256'] and a['coreSha256']==res['core']['sha256'] and a['engineMetadataSha256']==res['metadata']['sha256'],'actual audit artifact binding')
for k in ('hostRequestsInvoked','ordinaryGuestExportsInvoked','operationalAdmission','runtimeAcceptanceClaim','wireBodyAdapter'):need(a[k] is False,'component audit scope changed: '+k)
need(a['guestInitializationExecutedByComponentization'] is True,'initialization disclosure missing')
parent=pathlib.Path(res['parentIndex']['path']).parent;worker=pathlib.Path(res['workerIndex']['path']).parent
pidx=verify_index(res['parentIndex']['path'],'actual-parent-index-member');widx=verify_index(res['workerIndex']['path'],'actual-worker-index-member')
parent_members=walk(parent,False);worker_members=walk(worker,False)
need(all(x['kind']=='file' for x in parent_members),'actual parent contains non-regular member')
need(len(pidx['files'])==34 and len(parent_members)==36,'actual parent 34/36')
need({x['path'] for x in parent_members}=={x['path'] for x in pidx['files']}|{'index.json','completion.json'},'parent membership')
need({x['path'] for x in worker_members}=={x['path'] for x in widx['files']}|{'index.json','completion.json'},'worker membership')
need(len(widx['files'])==26 and len(worker_members)==28,'worker 26/28')
for name,indexname,resultname in (('parentCompletion','parentIndex','parentResult'),('workerCompletion','workerIndex',None)):
 completion=actual[name]
 verify(completion['index'],pathlib.Path(res[name]['path']).parent,'actual-completion-index')
 verify(completion['result'],pathlib.Path(res[name]['path']).parent,'actual-completion-result')
 need(completion['index']['sha256']==res[indexname]['sha256'],'completion index binding')
 if resultname:need(completion['result']['sha256']==res[resultname]['sha256'],'completion result binding')
et=actual['externalParentTerminal'];wt=actual['ownedWorkerTerminal'];pr=actual['parentResult']
need(et['rawExitCode']==0 and et['timeout'] is False and et['parentOwnedGroupGone'] is True,'external parent completion')
need(wt['status']==0 and wt['closed'] is True and wt['ownedGroupGone'] is True and wt['timedOut'] is False and wt['signal'] is None and wt['spawnError'] is None and wt['errors']==[] and wt['signals']==[] and wt['outputLimitExceeded'] is False,'worker raw completion')
need(pr['rawWorkerExitCode']==0 and pr['ownedGroupGone'] is True,'parent worker status')
config=actual['constructionConfig'];authority=actual['rootAction'];source_sha=res['constructionSourceIndexSha256'];pub_sha=res['sourcePublicationIndexSha256']
need(config['sourceIndexSha256']==source_sha and config['action']=='component-build' and config['rootAction']==res['rootAction'],'config original source/action binding')
need(json.loads(et['argv'][2])==res['constructionConfig'],'external exact config argument')
need(et['authority']==res['rootAction'] and et['config']==res['constructionConfig'],'external authority/config descriptors')
need(authority['sourceIndexSha256']==source_sha and authority['publicationIndex']['sha256']==pub_sha and authority['action']=='component-build' and authority['hostRequestsAllowed'] is False and authority['ordinaryGuestExportsAllowed'] is False and authority['wireBodyAdapterAllowed'] is False and authority['metadataProjection'] is False,'original authority source/publication/scope binding')
for obj in (a,pr):need(obj['sourceIndexSha256']==source_sha and obj['publicationIndexSha256']==pub_sha,'actual source/publication binding')
publication=verify(authority['publicationIndex'],role='original-published-source-index');published=verify_index(publication,'original-published-source-member')
common=0
source_rows={row['path']:row for row in source['files']}
for row in published['files']:
 if row['path'] in source_rows:need((row['sha256'],row['bytes'])==(source_rows[row['path']]['sha256'],source_rows[row['path']]['bytes']),'published common source differs: '+row['path']);common+=1
need(common>20,'too few original publication source bindings')
# Re-read all physical bytes and identities after semantic data comparisons.
for q,old in sorted(physical.items()):
 _,fresh=read_hash(q);need(fresh==old,'final physical file rehash/identity changed: '+q)
for tree in closure['toolTrees']:need(walk(tree['path'])==sorted(tree['entries'],key=lambda x:x['path']),'final exact tool tree differs')
need(walk(closure['familySnapshotRoot'],False)==snapshot_initial,'final snapshot membership differs')
need(walk(parent,False)==parent_members and walk(worker,False)==worker_members,'final actual artifact membership differs')
for link in closure['toolLinks']:
 p=pathlib.Path(link['path']);strict_path(str(p),True);need(os.readlink(p)==link['linkText'] and str(p.resolve(strict=True))==link['resolvedTarget'],'final declared tool link differs')
for p,old in path_components.items():
 st=pathlib.Path(p).lstat();now=component_id(st)
 if stat.S_ISLNK(st.st_mode):now+=[os.readlink(p)]
 need(now==old,'final path component identity differs: '+p)

output={'schemaVersion':1,'scope':'NEW_INDEPENDENT_READ_HASH_DATA_ONLY_NO_HOST_AUTHORITY','files':[dict(row,roles=sorted(row['roles'])) for _,row in sorted(declared.items())],'physicalFiles':[dict(path=q,**v) for q,v in sorted(physical.items())],'counts':{'declaredPaths':len(declared),'physicalFiles':len(physical),'physicalBytesPerHashPass':sum(v['bytes'] for v in physical.values()),'pathComponents':len(path_components)},'allPhysicalFilesRehashedAtEnd':True,'ownerCodeExecuted':False,'hostOrGuestRuntimeInvoked':False,'wasmToolsInvoked':False,'newDecoderClaim':False,'grantsHostActionAuthority':False}
def write_new(name,obj):
 p=OUT/name
 with p.open('x',encoding='utf-8') as f:json.dump(obj,f,indent=2,sort_keys=True);f.write('\n')
 b=p.read_bytes();return {'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
ld=write_new('rehashed-inputs.json',output)
summary={'schemaVersion':1,'state':'INDEPENDENT_NATIVE_CONTEXT_DATA_AUDIT_COMPLETE','evidenceOnly':True,'blockers':[],'checks':checks,'ledger':ld,'componentReviewIndex':{'path':str(REVIEW/'index.json'),'sha256':'da7a8d7937eec6a30eacf123312311313cae7d5affe7a1aa5ecff0460a496bad','bytes':2549},'closure':{'regularRows':12667,'priorFiniteReferences':14157,'inputFreezeRows':len(freeze['files']),'toolTrees':len(closure['toolTrees']),'toolTreeMembers':[len(t['entries']) for t in closure['toolTrees']],'declaredToolSymlinks':22,'snapshotRegularMembers':1678,'liveWitAdapterInputs':8},'actualArtifactMembership':{'parentIndexed':34,'parentRegular':36,'workerIndexed':26,'workerRegular':28},'fullActualMetadata':{'keys':len(m),'nativeSourceManifest':355,'nativeContexts':contexts,'externalFrozenComponentizeSources':3,'selectedActualManifests':11,'wholeMetadataAndManifestsEqualActualAudit':True},'originalSourcePublicationCommonMembersByteEqual':common,'rawCompletions':{'externalExit':0,'workerExit':0,'parentOwnedGroupGone':True,'workerOwnedGroupGone':True},'retainedArtifactAudit':{'sixWasiImports':interfaces,'soleExport':['wasi:http/incoming-handler@0.2.10'],'clockTypeOnly':True,'callableClockImports':[],'coreClockImports':[],'basis':'exact existing component audit plus authenticated prior artifact review; no new binary decoder'},'component':res['component'],'core':res['core'],'engine':res['engine'],'metadata':res['metadata'],'counts':output['counts'],'limitations':['All owner scripts and helpers were treated solely as bytes; none was imported or executed.','Existing artifact review fields are authenticated as DATA, not adopted as a new runtime result. No new decoder ran.','Historical componentization initialized the guest; this reader invoked no host, guest, native, network, GC, Node, componentizer, preflight or wasm-tools action.','Frozen external componentize source manifest has three files; no additional original configured external-source context is inferred.','No HTTP response, host pass, acceptance, timing, backend, request reuse, ALS, isolated GC rooting, Node compatibility or host authority is established.'],'grantsHostActionAuthority':False,'runtimeAcceptanceClaim':False,'operationalAdmission':False}
sd=write_new('summary.json',summary)
print(json.dumps({'summary':sd,'ledger':ld,'counts':output['counts'],'checks':checks}))
