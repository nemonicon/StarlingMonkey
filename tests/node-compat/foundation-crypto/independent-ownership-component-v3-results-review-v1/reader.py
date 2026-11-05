"""Read/hash/decode retained component evidence. No owner action is imported."""
import hashlib,json,os,re,struct
from pathlib import Path

P=Path(__file__).resolve().parent
K=P.parent
OUT=Path('/private/tmp/starling-node-compat/crypto-owner355-component-v3')
S=K/'ownership-component-candidate-v3'
SOURCE='593a0e02239fcc3b66bfc35549b6c574c2aee8cb67a273c2d8aea9c7ce22c492'
COMPONENT='842f82e8ae330580bee2d160880b5a3a35aac7c9baf357938814ecf2237a149d'
seen={};checks=[]
def need(v,m):
 if not v:raise AssertionError(m)
 checks.append(m)
def digest(p):
 p=Path(p);h=hashlib.sha256();n=0
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b);n+=len(b)
 return dict(path=str(p),sha256=h.hexdigest(),bytes=n)
def verify(r,role):
 p=Path(r['path']);a=p.stat();need(p.is_file()and not p.is_symlink(),'ordinary evidence '+str(p));got=digest(p);b=p.stat()
 need(all(got[k]==r[k]for k in ['path','sha256','bytes']),'exact retained bytes '+str(p))
 need((a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns,b.st_ctime_ns),'stable read '+str(p))
 if str(p)in seen:need(all(seen[str(p)][k]==r[k]for k in ['path','sha256','bytes']),'consistent evidence duplicate');seen[str(p)]['roles'].add(role)
 else:seen[str(p)]={**got,'roles':{role}}
 return got
def data(r,role='data'):
 verify(r,role);return json.loads(Path(r['path']).read_bytes())
def local(s):
 need(isinstance(s,str)and s and not s.startswith('/')and '\\'not in s and '\0'not in s and all(x not in ['', '.', '..']for x in s.split('/')),'bounded local member');return s
def index(row,count=None):
 x=data(row,'index');need(x['schemaVersion']==1 and isinstance(x['files'],list),'finite index')
 if count is not None:need(len(x['files'])==count,'exact index count '+str(count))
 rows=[];names=set()
 for r in x['files']:
  n=local(r['path']);need(n not in names,'unique index member');names.add(n);rr=dict(path=str(Path(row['path']).parent/n),sha256=r['sha256'],bytes=r['bytes']);verify(rr,'indexed-member');rows.append(rr)
 return x,rows
def save(name,v):(P/name).write_text(json.dumps(v,indent=2)+'\n')

root_row=dict(path=str(K/'ownership-component-v3-root-results.json'),sha256='f04a91d3efa5cb4fc3ff13b2269e5fc762bcad5957d4232ba2e40cb297d7bcf9',bytes=6097)
root=data(root_row,'Root-completed-result')
for key in ['sourceIndex','rootAction','config','externalTerminal','externalLaunch','started','externalStdout','externalStderr','index','result','completion','component','emittedWit','transpileMetadata','publicSourceAudit','componentizerInterfaceAudit','workerTerminal','nativeEngine','nativeMetadata']:
 verify(root[key],'Root-'+key)
need(root['sourceIndex']['sha256']==SOURCE and root['component']['sha256']==COMPONENT,'exact source/component identity')
peer_ix,peer_rows=index(root['sourceReview']['index'],8)
peer=data(root['sourceReview']['result'],'independent-source-peer')
need(peer['state']=='INDEPENDENT_CRYPTO_OWNER355_COMPONENT_SOURCE_REVIEW_PASSED_V3'and peer['sourceReviewPassed']is True and peer['ownerActionsInvoked']is False,'exact construction-only source peer')
prior_inputs=data(next(r for r in peer_rows if r['path'].endswith('/rehashed-inputs.json')),'prior-complete-source-inputs')
for r in prior_inputs['files']:verify(r,'fresh-source-native-packaging-rehash')
source_ix,source_rows=index(root['sourceIndex'],25)
source_freeze=data(next(r for r in source_rows if r['path'].endswith('/input-freeze.json')),'preparation-seal')
need(len(source_freeze['files'])==6825,'exact 6825 original-context preparation rows')
for r in source_freeze['files']:verify(r,'original-preparation-reference')

action=data(root['rootAction'],'actual-component-only-Root-action');config=data(root['config'],'actual-Root-config')
need(action['state']=='ROOT_REVIEWED_CRYPTO_OWNER355_COMPONENT_BUILD_V3'and action['componentSourceIndexSha256']==SOURCE and
 action['componentBuildAllowed']is True and action['componentInitializationAllowed']is True,'actual new construction/initialization authority')
need(action['keyExportCallsAllowed']is False and action['keyOrCryptoOperationsAllowed']is False and action['operationalAdmission']is False and
 action['runtimeAcceptanceClaim']is False and action['sourceIndependentReview']==root['sourceReview'],'construction-only scope/source proof')
need(config['componentSourceIndexSha256']==SOURCE and config['rootAction']==root['rootAction'],'actual config/source/Root binding')
terminal=data(root['externalTerminal'],'external-parent-terminal')
need(terminal['rawExitCode']==0 and terminal['timeout']is False and terminal['parentOwnedGroupGone']is True and terminal['pid']==5288,'external parent raw0/clean/no timeout')
for name in ['stdout','stderr']:verify(terminal[name],'external-'+name)
need(terminal['authority']==root['rootAction']and terminal['config']==root['config'],'terminal exact authority/config')
need(terminal['argv'][1]==str(S/'build.mjs')and json.loads(terminal['argv'][2])==root['config'],'external actual own-parent caller')
need(terminal['ordinaryGuestExportsInvoked']is False and terminal['keyOperationsInvoked']is False and terminal['stderr']['bytes']==0,'external scope and full empty stderr')
started=data(root['started'],'external-started');need(started['argv']==terminal['argv']and started['pid']==terminal['pid'],'started/terminal caller identity')
launch=Path(root['externalLaunch']['path']).read_text()
need("k not in ('PYTHONOPTIMIZE','PYTHONPATH','PYTHONHOME','NODE_OPTIONS','NODE_PATH')"in launch and "BINARYEN_CORES='1'"in launch,'authenticated external launch environment policy')
selected_env=started['selectedEnvironment'];need(selected_env['NODE_COMPAT_TOOLCHAIN']=='/private/tmp/starling-node-compat/zlib-cost-source-v3/tools/toolchain'and
 selected_env['NODE_COMPAT_COMPONENTIZE_MODULE']=='/private/tmp/starling-node-compat/zlib-cost-source-v3/tools/packager/src/componentize.js','actual explicit packaging roots')

ix,rows=index(root['index'],22);by={str(Path(r['path']).relative_to(OUT)):r for r in rows}
actual={str(p.relative_to(OUT))for p in OUT.rglob('*')if p.is_file()}
need(actual==set(by)|{'index.json','completion.json'}and len(actual)==24,'exact output22 indexed/24 actual')
need(not any(p.is_symlink()for p in OUT.rglob('*'))and all(p.stat().st_nlink==1 for p in OUT.rglob('*')if p.is_file()),'all output ordinary single-link files')
result=data(root['result'],'actual-parent-result');completion=data(root['completion'],'actual-parent-completion')
for key,desc in [('index',root['index']),('result',root['result'])]:need(completion[key]==dict(desc,path=Path(desc['path']).name),'parent completion exact '+key)
parent_stdout=json.loads(Path(terminal['stdout']['path']).read_bytes());need(parent_stdout==dict(root=str(OUT),index=completion['index'],completion=dict(path='completion.json',sha256=root['completion']['sha256'],bytes=root['completion']['bytes'])),'whole parent stdout completion decoded')
need(result['sourceIndexSha256']==SOURCE and result['rootAction']==root['rootAction']and result['nativeEngine']==root['nativeEngine']and result['metadata']==root['nativeMetadata'],'actual parent result/source/native bindings')
wt=data(root['workerTerminal'],'owned-worker-terminal')
for n,v in dict(status=0,signal=None,spawnError=None,timedOut=False,externalSignal=None,outputLimitExceeded=False,closed=True,ownedGroupGone=True,terminalExitZeroObserved=True).items():need(wt[n]==v,'owned worker terminal '+n)
need(wt['errors']==[]and wt['signals']==[]and wt['pid']==5394 and wt['timeoutMs']==600000 and wt['maxOutputBytes']==16777216,'owned worker full bounded clean outcome')
for key in ['stdout','stderr']:verify(wt[key],'owned-worker-'+key)
need(wt['stderr']['bytes']==0 and wt['args'][0]==str(S/'build-worker.mjs'),'actual worker own caller/empty stderr')
descriptor_row=json.loads(wt['args'][1]);need(descriptor_row==by['worker-descriptor.json'],'actual worker private descriptor binding')
d=data(descriptor_row,'private-worker-descriptor')
need(d['componentSourceIndexSha256']==SOURCE and d['rootAction']==root['rootAction']and d['ownIndex']==root['sourceIndex']and
 d['engine']==root['nativeEngine']and d['metadata']==root['nativeMetadata']and len(d['criticalSourceFiles'])==73,'private current source/native critical tuple')
for r in d['criticalSourceFiles']:verify(r,'worker-critical-source')
for key in ['node','engine','metadata','code','wit','mapRow']:verify(d[key],'private-'+key)
worker_completion=data(by['worker/completion.json'],'worker-completion')
worker_index_row=by['worker/index.json'];wi,wrows=index(worker_index_row,14)
for key,desc in [('index',worker_index_row),('result',by['worker/results.json']),('component',root['component'])]:
 need(worker_completion[key]==dict(desc,path=Path(desc['path']).name),'worker completion exact '+key)
worker_stdout=json.loads(Path(wt['stdout']['path']).read_bytes());need(worker_stdout==dict(root=str(OUT/'worker'),index=worker_completion['index'],completion=dict(path='completion.json',sha256=by['worker/completion.json']['sha256'],bytes=by['worker/completion.json']['bytes'])),'whole worker stdout completion decoded')
wr=data(by['worker/results.json'],'actual-worker-result');need(wr['sourceIndexSha256']==SOURCE and wr['nativeEngine']==root['nativeEngine']and wr['metadata']==root['nativeMetadata']and wr['guest']==d['code']and wr['wit']==d['wit'],'actual worker payload/native tuple')
for scope in [root,result,wr,completion,worker_completion]:
 need(scope['ordinaryGuestExportsInvoked']is False and scope['keyOperationsInvoked']is False,'retained no ordinary/key action scope')
need(wr['generatedModuleImported']is False and wr['asyncScalarRuntimeProof']is False,'generated loading and async behavior unproved')

native_meta=data(root['nativeMetadata'],'actual-full-native-metadata')
context=json.loads((S/'bootstrap-context.json').read_bytes());prior_contract=data(context['actualContract'],'actual-bootstrap-stable-contract')
freeze_row=prior_contract['freezeReceipt'];fr=data(freeze_row,'actual-native-freeze')
need(len(fr['copies'])==1390 and fr['engineSha256']==root['nativeEngine']['sha256']and fr['receiptSha256']==root['nativeMetadata']['sha256'],'full genuine native freeze1390 tuple')
for r in fr['copies']:
 verify(r,'actual-native-frozen-copy')
 if r['original']is not None:verify(dict(path=r['original'],sha256=r['sha256'],bytes=r['bytes']),'actual-native-original')
need(sum(r['original']is not None for r in fr['copies'])==1387 and
 {Path(r['path']).name for r in fr['copies']if r['original']is None}=={'normal-off-embedding.after.commands.txt','normal-off-source-admission.json','normal-off-freezer-correction-control.json'},'1387 originals plus three explicitly generated frozen evidence files')
for r in fr['dependencyReferences']:verify(r,'actual-native-linked-dependency')
need(len(native_meta['sourceManifest'])==355 and native_meta['cryptoKeyOwnershipPolicy']['version']=='sm-webcrypto-key-owner-and-prototype-guard-source-v1'and
 native_meta['gcStress']is False,'genuine owner355 normal source policy')
need(fr['runtimeBackendProof']==dict(verified=False,version=None,vernum=None),'backend proof remains false/null/null')
need(result['sourceRoot']==context['sourceRoot']and result['configuredSourceRoot']==context['configuredSourceRoot'],'actual output preserves both context spellings')

artifacts=dict(component=root['component'],glue=by['worker/transpiled/crypto_owner.js'],core=by['worker/transpiled/crypto_owner.core.wasm'],
 dts=by['worker/transpiled/crypto_owner.d.ts'],wit=root['emittedWit'],transpileMetadata=root['transpileMetadata'],
 packageJson=by['worker/transpiled/package.json'],publicSourceAudit=root['publicSourceAudit'],interfaceAudit=root['componentizerInterfaceAudit'])
need(Path(artifacts['packageJson']['path']).read_bytes()==b'{"type":"module"}\n','exact ESM package classification dependency')
abi={'inspect':'() -> string','run':'(u32) -> string','clear':'() -> string','validate':'() -> string'}
wit=Path(artifacts['wit']['path']).read_text();need(wit.startswith('package root:component;')and 'import 'not in wit,'actual emitted root WIT no imports')
wit_exports={}
for name,params,ret in re.findall(r'export\s+(\w+):\s*func\(([^)]*)\)\s*->\s*(\w+)\s*;',wit):wit_exports[name]='('+('u32'if params else '')+') -> '+ret
need(wit_exports==abi,'retained WIT exact four scalar string functions')
meta=data(artifacts['transpileMetadata'],'actual-transpile-metadata');need(meta==dict(imports=[],exports=[['clear','function'],['inspect','function'],['run','function'],['validate','function']],fileNames=['crypto_owner.core.wasm','crypto_owner.d.ts','crypto_owner.js']),'actual Jco metadata exact four functions/three files')
dts=Path(artifacts['dts']['path']).read_text();decls={}
for name,params,ret in re.findall(r'export function (\w+)\(([^)]*)\): (\w+);',dts):decls[name]='('+('u32'if params=='caseId: number'else params)+') -> '+ret
need(decls==abi,'actual d.ts same four scalar declarations')
audit=data(artifacts['publicSourceAudit'],'actual-generated-source-audit');need(audit['declarations']==abi and audit['glueSha256']==artifacts['glue']['sha256']and audit['dtsSha256']==artifacts['dts']['sha256'],'retained source audit exact artifact/ABI binding')
need(audit['publicExports']['names']==['_util','clear','inspect','run','validate']and audit['publicExports']['helper']==dict(name='_util',kind='empty-ordinary-object',notWitExport=True),'retained exact optional empty helper scope')
iface=data(artifacts['interfaceAudit'],'actual-interface-audit');need(iface['emittedImports']==[]and iface['selectedInterfaces']==[]and iface['componentSha256']==COMPONENT and iface['entropyPolicy']=='off','actual selected final imports[] component bound')
options=data(by['worker/component-options.json'],'actual-component-options')
need(options==dict(engine=root['nativeEngine']['path'],preview2Adapter=peer['actualAdapter']['path'],witWorld=Path(d['wit']['path']).read_text(),worldName='validation',selectedInterfaces=[],disableFeatures=['stdio','random','clocks','http','fetch-event'],enableAot=False,env={}),'actual API options full engine/adapter/source/disabled capability contract')
need(data(by['worker/selected-return-transport.json'])==dict(type='object',componentIsUint8Array=True,componentBytes=13107415),'complete selected byte-return transport')
need(data(by['worker/transpile-return-transport.json'])==dict(type='object',filesType='object',importsIsArray=True,exportsIsArray=True),'complete transpile type transport')

# Static binary section decoding only, not instantiation or execution.
def uleb(buf,p):
 n=0;s=0
 while True:
  need(p<len(buf)and s<=35,'bounded wasm LEB');b=buf[p];p+=1;n|=(b&127)<<s
  if not b&128:return n,p
  s+=7
def sections(buf,header):
 need(buf[:8]==header,'actual wasm binary header');p=8;out=[]
 while p<len(buf):
  kind=buf[p];n,q=uleb(buf,p+1);need(q+n<=len(buf),'whole static wasm section');out.append(dict(id=kind,offset=q,bytes=n));p=q+n
 need(p==len(buf),'whole binary sections consumed');return out
component=Path(artifacts['component']['path']).read_bytes();core=Path(artifacts['core']['path']).read_bytes()
cs=sections(component,b'\0asm\r\0\1\0');nested=[r for r in cs if r['id']==1]
need(len(nested)==1 and component[nested[0]['offset']:nested[0]['offset']+nested[0]['bytes']]==core,'one nested actual core byte-identical to Jco core')
need(all(r['id']!=10 for r in cs),'actual component has no binary import section')
ks=sections(core,b'\0asm\1\0\0\0');kis=[r for r in ks if r['id']==2];need(len(kis)==1,'one actual core import vector')
imports,end=uleb(core,kis[0]['offset']);need(imports==0 and end==kis[0]['offset']+kis[0]['bytes'],'actual core import vector is exactly empty')
need(all(r['id']!=8 for r in ks),'actual core has no binary start section')
save('binary-relation.json',dict(schemaVersion=1,component=artifacts['component'],core=artifacts['core'],componentSections=cs,coreSections=ks,
 oneNestedCoreFullBytesEqual=True,componentImportSectionAbsent=True,coreImportCount=0,coreImportVectorIsExactlyEmpty=True,coreStartSectionAbsent=True,readBytesOnly=True,instantiated=False))
save('rehashed-inputs.json',dict(schemaVersion=1,files=[dict(r,roles=sorted(r['roles']))for r in sorted(seen.values(),key=lambda r:r['path'])],ownerActionsInvoked=False))
save('data-results.json',dict(schemaVersion=1,dataReviewPassed=True,rootResult=root_row,sourceIndex=root['sourceIndex'],sourceReview=root['sourceReview'],
 rootAction=root['rootAction'],config=root['config'],actualIndex=root['index'],actualResult=root['result'],actualCompletion=root['completion'],
 externalParentTerminal=root['externalTerminal'],ownedWorkerTerminal=root['workerTerminal'],externalParentExitCode=0,ownedWorkerExitCode=0,ownedCleanup=True,
 artifacts=artifacts,engine=root['nativeEngine'],metadata=root['nativeMetadata'],nativeFreeze=freeze_row,
 sourceIndexSha256=SOURCE,componentSourceIndexSha256=SOURCE,componentSha256=COMPONENT,nativeSourceFiles=355,sourceMembers=25,preparationRows=6825,
 packagingFiles=4934,packagingLinks=22,nativeFrozenCopies=1390,nativeOriginalReferenceEntries=1387,actualIndexedFiles=22,actualRegularFiles=24,uniqueInputsRehashed=len(seen),
 publicAbiFunctions=abi,helper=dict(name='_util',kind='empty-ordinary-object',notWitExport=True),emittedImports=[],
 generatedModuleImported=False,ordinaryGuestExportsInvoked=False,keyOperationsInvoked=False,guestInitializationExecutedByComponentization=True,
 asyncScalarRuntimeProof=False,runtimeBackendProof=fr['runtimeBackendProof'],operationalAdmission=False,runtimeAcceptanceClaim=False,timingAllowed=False,
 reviewerReadHashDecodeOnly=True,ownerActionsInvoked=False,checks=len(checks)))
print(json.dumps(dict(dataReviewPassed=True,uniqueInputs=len(seen),actualIndexedFiles=22,actualRegularFiles=24,checks=len(checks))))
