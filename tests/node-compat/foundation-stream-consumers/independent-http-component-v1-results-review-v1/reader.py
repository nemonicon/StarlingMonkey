"""Actual component read/hash/JSON/binary decoding. No owner/guest execution."""
from pathlib import Path
import hashlib,json,os,stat
P=Path(__file__).resolve().parent;S=P.parent/'http-construction-candidate-v1';OUT=Path('/private/tmp/starling-node-compat/consumers355-http-component-v1')
SOURCE='dc98f4653eec1719e07d64ecfa8eb93ecfea1748bb3640521e0ac2a7e6aa5487';PUB='37fe3e00e33b195a808362e4119c12fdea9fb36acaeefcaebd8d61601ec8b67e';ENGINE='b227a8d2e6fb6b83da556d3520dceec82d5e1978801ba3c607bc9a31aa28ad60'
seen={};physical={};checks=0
def need(v,m):
 global checks
 if not v:raise AssertionError(m)
 checks+=1
def ident(s):return(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
def row(p):
 p=Path(p);h=hashlib.sha256();n=0
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b);n+=len(b)
 return dict(path=str(p),sha256=h.hexdigest(),bytes=n)
def verify(r,role):
 p=Path(r['path']);need(p.is_file()and not p.is_symlink(),'ordinary input '+str(p));real=str(p.resolve());need(real==str(p)or str(p).startswith('/tmp/')and real=='/private'+str(p),'only system/tmp alias')
 a=p.stat()
 if real not in physical:
  v=row(p);b=p.stat();need(ident(a)==ident(b),'stable streamed source');physical[real]=dict(sha256=v['sha256'],bytes=v['bytes'],identity=ident(b))
 else:need(ident(a)==physical[real]['identity'],'repeated physical input stable')
 need(physical[real]['sha256']==r['sha256']and physical[real]['bytes']==r['bytes'],'exact full bytes '+str(p))
 if str(p)not in seen:seen[str(p)]={k:r[k]for k in ['path','sha256','bytes']};seen[str(p)]['roles']=set()
 seen[str(p)]['roles'].add(role);return r
def data(r,role='data'):verify(r,role);return json.loads(Path(r['path']).read_bytes())
def local(n):need(isinstance(n,str)and n and not n.startswith('/')and '\\'not in n and '\0'not in n and all(x not in ['', '.', '..']for x in n.split('/')),'safe local member');return n
def index(r,count=None):
 x=data(r,'index');need(x['schemaVersion']==1 and isinstance(x['files'],list),'finite index')
 if count is not None:need(len(x['files'])==count,'exact indexed count '+str(count))
 rows=[];names=set()
 for v in x['files']:
  n=local(v['path']);need(n not in names,'unique indexed member');names.add(n);q=dict(path=str(Path(r['path']).parent/n),sha256=v['sha256'],bytes=v['bytes']);verify(q,'indexed-member');rows.append(q)
 return x,rows
def save(n,v):(P/n).write_text(json.dumps(v,indent=2)+'\n')
rootrow=dict(path=str(P.parent/'http-component-v1-root-results.json'),sha256='0c7df8c46538bde66bb7c9fd5e814d192ab3880ea69ead7f29d659700380faf1',bytes=9268)
root=data(rootrow,'actual-Root-result');root_descriptors={k:v for k,v in root.items()if isinstance(v,dict)and all(x in v for x in ['path','sha256','bytes'])}
for k,v in root_descriptors.items():verify(v,'Root-'+k)
need(root['constructionSourceIndex']['sha256']==SOURCE and root['sourcePublicationIndexSha256']==PUB and root['engineSha256']==ENGINE,'exact source/publication/native tuple')
for key,count in [('sourceReview',8),('sourcePublicationReview',7),('bundleReview',25)]:
 proof=root[key];ix,rows=index(proof['index'],count);data(proof['result'],'prior-'+key)
 inputs=data(next(r for r in rows if r['path'].endswith('/rehashed-inputs.json')),'complete-prior-closure')
 for r in inputs['files']:verify(r,'complete-native-source-tool-publication-bundle-input')
bundle_review=data(root['bundleReview']['result'],'actual-whole-entry-bundle-review')
need(bundle_review['state']=='INDEPENDENT_CONSUMERS355_HTTP_BUNDLE_REVIEW_PASSED_V1'and bundle_review['wholeEntryAndFixtureClosureVerified']is True and bundle_review['componentizerInvoked']is False,'separate prior bundle proof scope')
action=data(root['rootAction'],'actual-new-construction-authority');config=data(root['constructionConfig'],'actual-config')
need(action['state']=='ROOT_REVIEWED_CONSUMERS355_HTTP_CONSTRUCTION_V1'and action['action']=='component-build'and action['actionAllowed']is True and action['actualBundleReview']==root['bundleReview'],'new component-only authority and reviewed bundle')
need(action['sourceIndexSha256']==SOURCE and action['publicationIndex']['sha256']==PUB and action['engineSha256']==ENGINE and config['action']=='component-build'and config['rootAction']==root['rootAction'],'caller source/publication/engine identity')
for k in ['ordinaryGuestExportsAllowed','hostRequestsAllowed','wireBodyAdapterAllowed','metadataProjection','operationalAdmission','runtimeAcceptanceClaim']:need(action[k]is False,'no extra action '+k)
terminal=data(root['externalParentTerminal'],'external-parent-terminal');started=data(root['started'],'external-started')
need(terminal['pid']==23572 and terminal['rawExitCode']==0 and terminal['timeout']is False and terminal['parentOwnedGroupGone']is True,'external parent raw0/clean')
for k in ['stdout','stderr']:verify(terminal[k],'external-'+k)
need(terminal['stderr']['bytes']==0 and terminal['argv'][1]=='/private/tmp/starling-node-compat/consumers355-http-source-v1/run.mjs'and json.loads(terminal['argv'][2])==root['constructionConfig']and started['argv']==terminal['argv'],'published caller/config/full streams')
ix,rows=index(root['parentIndex'],34);by={str(Path(r['path']).relative_to(OUT)):r for r in rows}
need({str(p.relative_to(OUT))for p in OUT.rglob('*')if p.is_file()}==set(by)|{'index.json','completion.json'},'complete34-indexed36-actual output')
need(not any(p.is_symlink()for p in OUT.rglob('*'))and all(p.stat().st_nlink==1 for p in OUT.rglob('*')if p.is_file()),'ordinary complete output')
result=data(root['parentResult'],'parent-result');complete=data(root['parentCompletion'],'parent-completion')
for k,r in [('index',root['parentIndex']),('result',root['parentResult'])]:need(complete[k]==dict(r,path=Path(r['path']).name),'parent completion '+k)
need(json.loads(Path(terminal['stdout']['path']).read_bytes())==dict(index=complete['index'],completion=dict(path='completion.json',sha256=root['parentCompletion']['sha256'],bytes=root['parentCompletion']['bytes'])),'whole parent stdout')
wt=data(root['ownedWorkerTerminal'],'owned-worker-terminal')
for k,v in dict(status=0,signal=None,spawnError=None,timedOut=False,externalSignal=None,outputLimitExceeded=False,closed=True,ownedGroupGone=True,terminalExitZeroObserved=True).items():need(wt[k]==v,'owned raw terminal '+k)
need(wt['pid']==23812 and wt['errors']==[]and wt['signals']==[]and wt['timeoutMs']==600000 and wt['maxOutputBytes']==16777216,'whole bounded owned outcome')
for k in ['stdout','stderr']:verify(wt[k],'owned-'+k)
need(wt['stderr']['bytes']==0 and wt['args'][0]=='/private/tmp/starling-node-compat/consumers355-http-source-v1/worker.mjs','actual worker caller/full stderr')
descriptor=json.loads(wt['args'][1]);need(descriptor==by['worker-descriptor.json'],'exact private worker descriptor')
d=data(descriptor,'complete-private-native-frame');frame=d['frame'];p=d['prerequisites'];engine=d['engineRow'];metadata_row=d['metadataRow'];verify(engine,'actual-native-engine');metadata=data(metadata_row,'actual-native-sidecar')
need(engine['sha256']==ENGINE and metadata_row['sha256']==root['engineMetadataSha256']and metadata==frame['metadata']and len(metadata['sourceManifest'])==355,'actual whole355 metadata unprojected')
pins=data(p['reviewedPins'],'actual-four-native-pins');need(frame['pin']==pins['variants']['normal-runtime']and frame['sourceRoot']==p['nativeFrozenSourceRoot']and frame['admissionSourceRoot']==p['nativeConfiguredSourceRoot']and frame['runtimeSourceRoot']==p['nativeFrozenSourceRoot'],'exact full pin and native contexts')
need(metadata['entropyPolicy']=='runtime-only'and metadata['gcStress']is False and metadata['streamConsumersEnabled']is True,'only selected RuntimeOnly355')
manifests=[json.loads((Path(frame['sourceRoot'])/r['path']).read_bytes())for r in metadata['sourceManifest']if '/export-manifest' in r['path']]
need(len(manifests)==len(frame['selectedManifests'])==11 and {json.dumps(v,sort_keys=True)for v in manifests}=={json.dumps(v,sort_keys=True)for v in frame['selectedManifests']},'full eleven actual native manifests')
wc=data(root['workerCompletion'],'worker-completion');wi,wrows=index(root['workerIndex'],26)
for k,r in [('index',root['workerIndex']),('result',by['worker/results.json'])]:need(wc[k]==dict(r,path=Path(r['path']).name),'worker completion '+k)
need(json.loads(Path(wt['stdout']['path']).read_bytes())==dict(index=wc['index'],completion=dict(path='completion.json',sha256=root['workerCompletion']['sha256'],bytes=root['workerCompletion']['bytes'])),'whole worker stdout')
need(Path(root['actualBundle']['path']).read_bytes()==Path(bundle_review['bundle']['path']).read_bytes()and(OUT/'worker/bundle-graph.json').read_bytes()==Path(bundle_review['graph']['path']).read_bytes(),'actual unchanged reviewed bundle/graph consumed; no rebundle')
audit=data(root['componentAudit'],'complete-component-audit');pack=data(root['packagingAudit'],'selected-two-pass-packaging-audit');iface=data(root['interfaceAudit'],'actual-final-interface-audit');graph=data(root['typeGraph'],'actual-retained-typegraph')
need(audit['sourceIndexSha256']==SOURCE and audit['publicationIndexSha256']==PUB and audit['engineSha256']==ENGINE and audit['engineMetadataSha256']==metadata_row['sha256'],'full audit provenance')
need(audit['fullActualNativeMetadata']==metadata and audit['actualSelectedManifests']==frame['selectedManifests']and audit['coreExpectations']==frame['coreExpectations'],'full audit native/manifests/core unchanged')
need(audit['componentSha256']==root['component']['sha256']and audit['componentBytes']==root['component']['bytes']and audit['coreSha256']==root['core']['sha256']and audit['applicationBundleSha256']==root['actualBundle']['sha256'],'actual binary/core/bundle/audit relation')
bundle_graph=json.loads((OUT/'worker/bundle-graph.json').read_bytes());need(audit['foundationOracles']==bundle_graph['foundationOracles']==audit['baselineAndClassic']['foundationOracles'],'all actual fixture/oracle data retained')
need(audit['classicOrdinaryGroups']==19 and audit['consumerRequestFixtureGroups']==2 and audit['wholeBaselineGuestBodyUnchanged']is True and audit['wireBodyAdapter']is False,'bounded baseline/classic/consumer body scope')
for k in ['entropyIntegrationFixture','foundationsIntegrationFixture','expandedFoundationsFixture','utilFoundationsFixture','streamWebFoundationsFixture','protectedAbortFoundationsFixture']:need(audit['baselineAndClassic'][k]is True,'old baseline validator not disabled '+k)
expected=json.loads((S/'expected-interfaces.json').read_bytes());six=expected['outerImports'];exports=expected['outerExports']
need(root['selectedInterfaces']==root['emittedImports']==audit['allowedImports']==audit['emittedImports']==iface['selectedInterfaces']==iface['emittedImports']==six,'actual six standard selected/emitted interfaces')
need(root['emittedExports']==audit['emittedExports']==exports==['wasi:http/incoming-handler@0.2.10'],'sole actual HTTP incoming handler export')
need(iface['componentSha256']==root['component']['sha256']and iface['entropyPolicy']=='runtime-only'and iface['state']=='verified-final-component','actual emitted interface audit binds final binary')
need(pack['name']=='componentize-js-0.23-two-pass-selected-http'and pack['packagingSelection']=='patched-import-i32-clock-v2'and pack['entropyPolicy']=='runtime-only'and pack['initialBindingFeatures']==pack['finalStubFeatures']==['http','random']and pack['firstStubFeatures']==['random','stdio','clocks','fetch-event'],'actual selected two-pass integration values')
pack_root=Path(p['invocation']['componentizeModule']).parent.parent
for r in pack['checkedFiles']:verify(dict(path=str(pack_root/r['path']),sha256=r['sha256'],bytes=(pack_root/r['path']).stat().st_size),'actual selected packaging source/artifact')
closure=json.loads(Path(d['closureRow']['path']).read_bytes());live=closure['liveInputs'];need(len(live)==8,'actual live8 source boundary')
need(audit['computedLiveInputChecks']['beforeCopy']==audit['computedLiveInputChecks']['afterCopy']and audit['computedLiveInputChecks']['beforeCopy']['files']==8,'full live8 checks retained around copy')
for r in live:
 verify(r,'actual-live-WIT-adapter')
 if '/wit/deps/'in r['name']:need((OUT/'worker/wit/deps'/r['name'].split('/wit/deps/')[1]).read_bytes()==Path(r['path']).read_bytes(),'each of seven WIT copies byte exact')
need((OUT/'worker/wit/profile.wit').read_bytes()==Path(p['paths']['worldSource']).read_bytes(),'exact profile world source')
options=data(by['worker/component-options.json'],'actual-component-options');adapter=next(r for r in live if r['bytes']==53512)
need(options==dict(engine=engine['path'],witPath=str(OUT/'worker/wit'),worldName='profile',preview2Adapter=adapter['path'],disableFeatures=['stdio','clocks','fetch-event'],selectedInterfaces=six),'actual selected HTTP engine/repository adapter/options')
for n in ['version','typegraph']:
 tr=data(by['worker/wasm-tools-'+n+'.terminal.json'],'retained-parser-'+n+'-terminal');need(tr['status']==0 and tr['signal']is None and tr['error']is None and tr['parserOnly']is True,'retained parser status '+n)
 for k in ['stdout','stderr']:
  r=tr[k];verify(dict(path=str(OUT/'worker'/r['path']),sha256=r['sha256'],bytes=r['bytes']),'retained-parser-stream')
need((OUT/'worker/wasm-tools-typegraph.stdout').read_bytes()==Path(root['typeGraph']['path']).read_bytes(),'typegraph raw bytes retained before parsing')
clock=[v for v in graph['interfaces']if v['name']=='monotonic-clock'and graph['packages'][v['package']]['name']=='wasi:clocks@0.2.10'];need(len(clock)==1 and clock[0]['functions']=={}and list(clock[0]['types'])==['duration']and graph['types'][clock[0]['types']['duration']]['kind']==dict(type='u64'),'actual duration-only u64 clock, no functions')
def interface_name(i):
 v=graph['interfaces'][i];base,version=graph['packages'][v['package']]['name'].split('@');return base+'/'+v['name']+'@'+version
world=graph['worlds'][0];need(len(graph['worlds'])==1 and sorted(interface_name(v['interface']['id'])for v in world['imports'].values())==six and [interface_name(v['interface']['id'])for v in world['exports'].values()]==exports,'actual complete typegraph import/export world')

# Static binary sections/imports/producers, without WebAssembly compilation.
def u(buf,pos):
 n=0;s=0
 while True:
  need(pos<len(buf)and s<70,'bounded LEB');b=buf[pos];pos+=1;n|=(b&127)<<s
  if not b&128:return n,pos
  s+=7
def string(buf,pos):n,q=u(buf,pos);need(q+n<=len(buf),'complete binary string');return buf[q:q+n].decode('utf8'),q+n
def sections(buf,header):
 need(buf[:8]==header,'actual binary header');pos=8;result=[]
 while pos<len(buf):
  kind=buf[pos];size,q=u(buf,pos+1);need(q+size<=len(buf),'complete binary section');name=None
  if kind==0:name,z=string(buf,q)
  result.append(dict(id=kind,start=pos,offset=q,bytes=size,name=name,sha256=hashlib.sha256(buf[q:q+size]).hexdigest()));pos=q+size
 need(pos==len(buf),'whole binary consumed');return result
def imports(buf,ss):
 selected=[r for r in ss if r['id']==2]
 if not selected:return []
 need(len(selected)==1,'one core import vector');r=selected[0];count,pos=u(buf,r['offset']);rows=[]
 for _ in range(count):
  module,pos=string(buf,pos);name,pos=string(buf,pos);kind=buf[pos];pos+=1;entry=dict(module=module,name=name)
  if kind==0:idx,pos=u(buf,pos);entry.update(kind='function',typeIndex=idx)
  elif kind in [1,2]:
   entry['kind']='table'if kind==1 else'memory'
   if kind==1:
    valtype=buf[pos];pos+=1;need(valtype in [0x70,0x6f],'ordinary decoded auxiliary reference type');entry['elementTypeByte']=valtype
   flags,pos=u(buf,pos);minimum,pos=u(buf,pos);entry.update(limitsFlags=flags,minimum=minimum)
   if flags&1:maximum,pos=u(buf,pos);entry['maximum']=maximum
  elif kind==3:
   entry.update(kind='global',valueTypeByte=buf[pos],mutable=buf[pos+1]);pos+=2
  elif kind==4:
   attribute=buf[pos];pos+=1;idx,pos=u(buf,pos);entry.update(kind='tag',attribute=attribute,typeIndex=idx)
  else:raise AssertionError('unknown actual core import kind')
  rows.append(entry)
 need(pos==r['offset']+r['bytes'],'whole import vector');return rows
def producers(buf,ss):
 r=next(r for r in ss if r['name']=='producers');name,pos=string(buf,r['offset']);count,pos=u(buf,pos);result={}
 for _ in range(count):
  name,pos=string(buf,pos);length,pos=u(buf,pos);values=[]
  for _ in range(length):a,pos=string(buf,pos);b,pos=string(buf,pos);values.append([a,b])
  result[name]=values
 need(pos==r['offset']+r['bytes'],'whole producers data');return result
component=Path(root['component']['path']).read_bytes();core=Path(root['core']['path']).read_bytes();cs=sections(component,b'\0asm\r\0\1\0');ks=sections(core,b'\0asm\1\0\0\0')
nested=[r for r in cs if r['id']==1];need(len(nested)==3,'actual three nested core modules')
app=component[nested[0]['offset']:nested[0]['offset']+nested[0]['bytes']];app_sections=sections(app,b'\0asm\1\0\0\0')
a=[r for r in ks if r['id']!=0];b=[r for r in app_sections if r['id']!=0]
need(len(a)==len(b)==11 and all(x['id']==y['id']and x['bytes']==y['bytes']and x['sha256']==y['sha256']for x,y in zip(a,b)),'all eleven application semantic sections byte-identical')
need({r['name']for r in ks if r['id']==0}=={'name','producers','target_features','component-type'}and {r['name']for r in app_sections if r['id']==0}=={'name','producers','target_features'},'component-type consumed, no unknown application custom section')
for name in ['name','target_features']:need(next(r['sha256']for r in ks if r['name']==name)==next(r['sha256']for r in app_sections if r['name']==name),'application custom data exact '+name)
before=producers(core,ks);after=producers(app,app_sections)
need(all(k in after and all(v in after[k]for v in values)for k,values in before.items()),'original producer metadata retained; only additions')
app_imports=imports(core,ks);need([{k:r[k]for k in ['module','name','kind']}for r in app_imports]==pack['coreImports']and len(app_imports)==87,'all87 actual binary core imports equal packaging audit')
need(sorted({r['module']for r in app_imports})==pack['coreImportModules']and not any(r['module'].startswith('wasi:clocks/')or r['module']=='wasi_snapshot_preview1'or r['module'].startswith('wasi:http/outgoing-handler')for r in app_imports),'no callable core clocks/Preview1/outgoing-handler')
aux=[]
for r in nested[1:]:
 raw=component[r['offset']:r['offset']+r['bytes']];ss=sections(raw,b'\0asm\1\0\0\0');im=imports(raw,ss);need(not any(x['module'].startswith('wasi:clocks/')or x['module']=='wasi_snapshot_preview1'for x in im),'no hidden clock/Preview1 import in canonical binding modules');aux.append(dict(descriptor=r,imports=im,sections=ss))
save('binary-relations.json',dict(schemaVersion=1,component=root['component'],core=root['core'],componentSections=cs,retainedCoreSections=ks,embeddedApplicationSections=app_sections,
 actualNestedCoreModules=3,applicationNonCustomSectionsExactlyEqual=True,applicationSemanticSectionCount=11,componentTypeMetadataConsumed=True,producerMetadataBefore=before,producerMetadataAfter=after,
 applicationCoreImports=app_imports,canonicalBindingModules=aux,callableCoreClockImports=[],preview1CoreImports=[],instantiated=False,readBytesOnly=True))
for real,v in physical.items():need(ident(Path(real).stat())==v['identity'],'all hashed source inputs stable at final read')
save('rehashed-inputs.json',dict(schemaVersion=1,files=[dict(r,roles=sorted(r['roles']))for r in sorted(seen.values(),key=lambda r:r['path'])],uniquePhysicalFilesHashed=len(physical),ownerActionsInvoked=False))
save('data-results.json',dict(schemaVersion=1,dataReviewPassed=True,rootResult=rootrow,rootArtifactDescriptors=root_descriptors,
 constructionSourceIndexSha256=SOURCE,sourcePublicationIndexSha256=PUB,sourceFiles=355,engineSha256=ENGINE,engineMetadataSha256=metadata_row['sha256'],engine=engine,metadata=metadata_row,
 sourceReview=root['sourceReview'],sourcePublicationReview=root['sourcePublicationReview'],bundleReview=root['bundleReview'],actualSelectedManifests=frame['selectedManifests'],
 fullActualNativeMetadata=metadata,configuredSourceRoot=frame['admissionSourceRoot'],frozenSourceRoot=frame['runtimeSourceRoot'],packagingRoot=p['paths']['packagingRoot'],
 actualIndexedFiles=34,actualRegularFiles=36,externalParentExitCode=0,rawWorkerExitCode=0,ownedGroupGone=True,parentOwnedGroupGone=True,
 selectedInterfaces=six,emittedImports=six,emittedExports=exports,clockTypeOnly=True,callableClockImports=[],coreClockImports=[],applicationCoreImports=87,
 nestedCoreModules=3,applicationCoreSemanticSectionsByteExact=True,wholeReviewedBundleAndGraphBytesEqual=True,liveWitAdapterFiles=8,witCopies=7,
 guestInitializationExecutedByComponentization=True,ordinaryGuestExportsInvoked=False,hostRequestsInvoked=False,wireBodyAdapter=False,
 operationalAdmission=False,runtimeAcceptanceClaim=False,timingAllowed=False,reviewerReadHashJsonBinaryDataOnly=True,reviewerHelpersPackagerGuestHostNativeActionsInvoked=False,
 uniqueDeclaredInputsVerified=len(seen),uniquePhysicalFilesHashed=len(physical),checks=checks))
print(json.dumps(dict(dataReviewPassed=True,outputIndexed=34,actual=36,coreImports=87,nestedCores=3,physicalFilesHashed=len(physical))))
