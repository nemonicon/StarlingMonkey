"""Data-only actual source-bundle verifier. Never imports JS/providers/codecs.

Run only after Root63317 terminal outcome was supplied: raw0/PID24635.
"""
from pathlib import Path
import hashlib,json,os,re,stat
H=Path(__file__).resolve().parent;Z=H.parent;OUT=Path('/private/tmp/starling-node-compat/zlib-cost-bundles-v1');PUB=Path('/private/tmp/starling-node-compat/zlib-cost-source-v3')
TOOLING='ff208e72d0b87933aa75cdeb7c1ae16f29aa6ae94c357318a9d6676af04b36b8';GUEST='ebe8fa901a3516358539c0458b09cad822308f9a3b0c76db33015ff378a8eae8';PUBLICATION='4621f7e72b4fb0555a5df630b1aedd4d2a04743b0db9188fc50099779f07387b';ACTION='367e7960fb2382238c2cfa15320d1c57acc153837c5d0080419d33ad3417ce7c'
ROOT_RECEIPT='194d8ec80c70c72339ef00aa1216f7b988c80ff594037a7d43255a0a4b417a8b';AUTH='0776fdf9c1d7c7d793359b9e5c357206f44190535e87f6264407e7d24de70572';CONFIG='779a5f0e1b61206d6ff510dd2bdfb0bef46b9cbf8bc3f05543c893dcb92ec497'
NAMES=['batch','checkpoint','identity','observe','setup','stage','validate'];ARMS=['native-on','fflate-on','fflate-off'];refs={}
def digest(raw):return hashlib.sha256(raw).hexdigest()
def local(value):assert isinstance(value,str)and value and not Path(value).is_absolute()and'\\'not in value and'\0'not in value and all(p not in ['','.','..']for p in value.split('/'));return value
def read(path,expected=None,size=None,collect=True,role='ACTUAL_SOURCE_OR_PROOF_DATA'):
 p=Path(path);before=p.lstat();assert stat.S_ISREG(before.st_mode)and not p.is_symlink(),p
 h=hashlib.sha256();count=0;chunks=[]
 with p.open('rb')as stream:
  for chunk in iter(lambda:stream.read(1024*1024),b''):
   h.update(chunk);count+=len(chunk)
   if collect:chunks.append(chunk)
 after=p.lstat();assert(before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns),p
 sha=h.hexdigest();assert expected is None or sha==expected,p;assert size is None or count==size,p
 key=str(p.absolute());row={'path':key,'realPath':str(p.resolve()),'sha256':sha,'bytes':count,'mode':stat.S_IMODE(after.st_mode),'links':after.st_nlink,'role':role}
 if key in refs:assert all(refs[key][k]==row[k]for k in ['realPath','sha256','bytes','mode','links'])
 else:refs[key]=row
 return b''.join(chunks)if collect else row
def descriptor(path):
 p=Path(path);raw=read(p);return{'path':str(p.resolve()),'sha256':digest(raw),'bytes':len(raw)}
def supplied(row,collect=True,role='BOUND_EXTERNAL_DESCRIPTOR'):return read(row['path'],row['sha256'],row['bytes'],collect,role)
def put(path,value):
 p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x')as stream:json.dump(value,stream,indent=2);stream.write('\n')
def proof(value,state):
 ix=json.loads(supplied(value['index']));seen=set();found=[]
 for row in ix['files']:
  local(row['path']);assert row['path']not in seen;seen.add(row['path']);path=Path(value['index']['path']).parent/row['path'];raw=read(path,row['sha256'],row['bytes'])
  if str(path)==value['result']['path']:assert row['sha256']==value['result']['sha256']and row['bytes']==value['result']['bytes'];found.append(json.loads(raw))
 assert len(found)==1 and found[0]['state']==state;return found[0]

# A finite lexical module audit of these actual emitted files, not a JS engine.
# This bundle shape has no template literals. Strings/comments/regexp literals
# are skipped before import/export/top-level declaration analysis.
def tokens(text):
 out=[];i=0;previous=None;n=len(text);assert '`'not in text
 prefix={'(','[','{','=',':',',',';','?','!','&','|','+','-','*','%','return','throw','case','=>'}
 while i<n:
  c=text[i]
  if c.isspace():i+=1;continue
  if text.startswith('//',i):
   end=text.find('\n',i+2);i=n if end<0 else end+1;continue
  if text.startswith('/*',i):end=text.find('*/',i+2);assert end>=0;i=end+2;continue
  start=i
  if c in ['"',"'"]:
   quote=c;i+=1
   while i<n:
    if text[i]=='\\':i+=2;continue
    if text[i]==quote:i+=1;break
    i+=1
   else:raise AssertionError('Unterminated string')
   value=('string',text[start:i],start,i)
  elif c=='/'and(previous is None or previous in prefix):
   i+=1;bracket=False
   while i<n:
    if text[i]=='\\':i+=2;continue
    if text[i]=='[':bracket=True
    elif text[i]==']':bracket=False
    elif text[i]=='/'and not bracket:i+=1;break
    i+=1
   else:raise AssertionError('Unterminated regexp')
   while i<n and text[i].isalpha():i+=1
   value=('regexp','REGEXP',start,i)
  elif c.isalpha()or c in ['_','$']:
   i+=1
   while i<n and(text[i].isalnum()or text[i]in ['_','$']):i+=1
   value=('word',text[start:i],start,i)
  elif c.isdigit():
   i+=1
   while i<n and(text[i].isalnum()or text[i]in ['.','_']):i+=1
   value=('number','NUMBER',start,i)
  else:i+=1;value=('punct',c,start,i)
  out.append(value);previous=value[1]
 return out
def public_source(raw):
 text=raw.decode('utf-8');ts=tokens(text);depth=0;imports=[];exports=[];functions={};export_statements=0
 for i,token in enumerate(ts):
  kind,value,start,end=token
  if depth==0 and kind=='word'and value=='import':
   stop=next(j for j in range(i+1,len(ts))if ts[j][1]==';');statement=text[start:ts[stop][3]]
   match=re.fullmatch(r'import\s+[^;]+\s+from\s+("[^"]+"|\'[^\']+\');',statement);assert match,statement
   imports.append(match[1][1:-1])
  if depth==0 and kind=='word'and value=='export':
   export_statements+=1;assert ts[i+1][1]=='{';j=i+2
   while ts[j][1]!='}':assert ts[j][0]=='word';exports.append(ts[j][1]);j+=1;assert ts[j][1]in [',','}'];j+=ts[j][1]==','
   assert ts[j+1][1]==';'
  if depth==0 and kind=='word'and value=='function'and ts[i+1][0]=='word'and ts[i+1][1]in NAMES:
   name=ts[i+1][1];assert ts[i+2][1]=='(';j=i+3;params=[]
   while ts[j][1]!=')':assert ts[j][0]=='word';params.append(ts[j][1]);j+=1;assert ts[j][1]in [',',')'];j+=ts[j][1]==','
   functions[name]=params
  if kind=='punct'and value=='{':depth+=1
  elif kind=='punct'and value=='}':depth-=1;assert depth>=0
 assert depth==0 and export_statements==1 and sorted(exports)==NAMES and len(set(exports))==7
 assert {name:len(functions[name])for name in NAMES}=={'batch':2,'checkpoint':0,'identity':0,'observe':1,'setup':1,'stage':1,'validate':1}
 assert '__require'not in text and'jco:node/zlib'not in text
 return{'imports':sorted(imports),'exports':sorted(exports),'publicParameterCounts':{name:len(functions[name])for name in NAMES},'lexicalAuditOnly':True}

root=json.loads(read(Z/'cost-bundle-v1-root-results.json',ROOT_RECEIPT));assert root['externalBundlerExitCode']==0 and root['rootSessionId']==63317 and root['pid']==24635
terminal=json.loads(supplied(root['externalTerminal']));assert terminal['rawExitCode']==0 and terminal['timeout']is False and terminal['pid']==24635
stdout=json.loads(supplied(root['externalStdout']));assert supplied(root['externalStderr'])==b''
config=json.loads(read(Z/'cost-bundle-v1-root-config.json',CONFIG));authority=json.loads(read(Z/'cost-bundle-v1-root-authority.json',AUTH));assert config['rootAction']==root['authority']and authority['bundleActionSourceIndexSha256']==ACTION and authority['permittedArms']==ARMS
assert json.loads(terminal['argv'][2])=={'path':str((Z/'cost-bundle-v1-root-config.json').resolve()),'sha256':CONFIG,'bytes':641}
pair=proof(authority['rootReviewedPair'],'ROOT_REVIEWED_GENUINE_ZLIB350_COST_PAIR_V1');oracle=proof(authority['nodeOracleRenderProof'],'ROOT_REVIEWED_ZLIB_COST_NODE_ORACLE_RENDER_V1');source_peer=proof(authority['sourcePublicationProof'],'INDEPENDENT_FRESH_ZLIB_COST_SOURCE_PUBLICATION_VERIFIED')
assert oracle['toolingSourceIndexSha256']==TOOLING and oracle['guestSourceIndexSha256']==GUEST and oracle['sourcePublicationIndexSha256']==PUBLICATION and oracle['codecCases']==30 and oracle['nodeEncoderStreams']==15
oracle_bytes=supplied(authority['nodeOracleRenderProof']['oracle']);module_bytes=supplied(authority['nodeOracleRenderProof']['module']);module_text=module_bytes.decode();match=re.search(r'export const oracleInputs\s*=\s*',module_text);assert match;oracle_data,end=json.JSONDecoder().raw_decode(module_text[match.end():]);assert module_text[match.end()+end:].strip()==';';assert oracle_data['oracleSha256']==digest(oracle_bytes)

# Full current published physical source/package closure, never original paths.
publication=json.loads(read(PUB/'index.json',PUBLICATION));pmap={row['path']:row for row in publication['files']};assert len(pmap)==len(publication['files']);identity=PUB.stat();assert identity.st_dev==publication['rootIdentity']['device']and identity.st_ino==publication['rootIdentity']['inode']
for row in publication['files']:
 local(row['path']);record=read(PUB/row['path'],row['sha256'],row['bytes'],False,'PUBLISHED_SOURCE_PACKAGE_OR_JOURNAL');assert record['mode']==row['mode']and record['links']==1
links={row['destination']:row for row in publication['links']};actual_files=[];actual_dirs=[];actual_links=[]
for parent,dirs,names in os.walk(PUB,followlinks=False):
 for name in list(dirs)+names:
  path=Path(parent)/name;relative=str(path.relative_to(PUB));info=path.lstat()
  if stat.S_ISLNK(info.st_mode):
   row=links[relative];assert os.readlink(path)==row['newLinkText']and path.resolve()==(PUB/row['mappedTarget']).resolve();actual_links.append(relative)
  elif path.is_dir():assert stat.S_IMODE(info.st_mode)==0o700;actual_dirs.append(relative)
  else:assert path.is_file();actual_files.append(relative)
assert set(actual_files)==set(pmap)|{'index.json','completion.json'}and set(actual_dirs)==set(publication['directories'])and set(actual_links)==set(links)
supplied(authority['sourcePublicationCompletion']);context=json.loads(read(PUB/'context.json'));assert context['guestSourceIndexSha256']==GUEST

# Inherit full native command/API audits by exact reviewed pair; freshly hash all
# immutable copies and selectedSDK references without old mutable origins.
frozen_counts={}
for name in ['nativeOn','nativeOff']:
 item=pair[name];metadata=json.loads(supplied(item['metadata']));freeze=json.loads(supplied(item['freezeReceipt']));supplied(item['engine'],False)
 assert len(metadata['sourceManifest'])==350 and len(metadata['componentizeSourceManifest'])==3 and metadata['zlibPolicy']['runtimeBackendProof']=={'verified':False,'version':None,'vernum':None}
 assert len(freeze['copies'])==1024
 for row in freeze['copies']:read(row['path'],row['sha256'],row['bytes'],False,'IMMUTABLE_NATIVE_FROZEN_COPY')
 frozen_counts[name]=len(freeze['copies'])
for row in pair['selectedSDKReferences']:supplied(row,False,'SELECTED_SDK_HASH_REFERENCE_NO_COMPILER_EXECUTION')

ix=json.loads(supplied(root['actualIndex']));report=json.loads(supplied(root['actualResult']));completion=json.loads(supplied(root['actualCompletion']));assert len(ix['files'])==10 and report['state']=='ZLIB_COST_SOURCE_BUNDLES_CAPTURED_UNREVIEWED_V1'and completion['componentizationAllowed']is False
assert stdout['root']==str(OUT)and stdout['index']==completion['index']and stdout['componentizationAllowed']is False
expected={'index.json','completion.json'}
for row in ix['files']:local(row['path']);assert row['path']not in expected;expected.add(row['path']);read(OUT/row['path'],row['sha256'],row['bytes'])
actual=set()
for path in OUT.rglob('*'):
 assert not path.is_symlink();info=path.lstat()
 if path.is_dir():assert stat.S_IMODE(info.st_mode)==0o700
 else:assert path.is_file()and stat.S_IMODE(info.st_mode)==0o600 and info.st_nlink==1;actual.add(str(path.relative_to(OUT)))
assert actual==expected and len(actual)==12

arm_results=[];all_graphs={}
for row in report['arms']:
 arm=row['arm'];assert arm in ARMS;code=read(OUT/row['code']['path'],row['code']['sha256'],row['code']['bytes']);graph=json.loads(read(OUT/row['graph']['path'],row['graph']['sha256'],row['graph']['bytes']));all_graphs[arm]=graph
 assert graph['codeSha256']==digest(code)and graph['codeBytes']==len(code)and graph['arm']==arm and graph['componentizationAllowedByThisResult']is False and graph['guestCompatibilityClaim']is False
 public=public_source(code);expected_imports=['node:buffer','node:zlib']if arm=='native-on'else['node:buffer'];assert public['imports']==sorted(graph['imports'])==expected_imports and public['exports']==sorted(graph['exports'])==NAMES
 assert graph['virtualModuleIds']==row['virtualModuleIds']==[] and graph['virtualSourceReviewRequired']is False
 assert graph['entryPath']==str(PUB/'guest/guest.mjs')and graph['providerPath']==str(PUB/'guest'/('native-provider.mjs'if arm=='native-on'else'fflate-provider.mjs'))and graph['oracleInputsPath']==authority['nodeOracleRenderProof']['module']['path']
 assert row['nativeEngineSha256']==pair['nativeOff'if arm=='fflate-off'else'nativeOn']['engine']['sha256']
 paths=[]
 for source in graph['physicalSources']:
  supplied(source);path=Path(source['path']);paths.append(str(path))
  if source['role']=='reviewed-derived-oracle-inputs':assert source['sha256']==authority['nodeOracleRenderProof']['module']['sha256']
  else:
   relative=str(path.relative_to(PUB));assert pmap[relative]['sha256']==source['sha256']and pmap[relative]['bytes']==source['bytes']
 assert sorted(paths)==sorted(graph['modules'])and len(paths)==len(set(paths))==(11 if arm=='native-on'else 12)
 ff=[source for source in graph['physicalSources']if source['role']=='fflate-browser'];assert len(ff)==(0 if arm=='native-on'else 1)
 if ff:assert ff[0]['sha256']=='b7ca4450b19559a1d50eb381adcee94b82449674be4cd17789d9beba7e6122a1'
 text=code.decode();m=re.search(r'(?:const|var) oracleInputs\s*=\s*',text);assert m;inlined,end=json.JSONDecoder().raw_decode(text[m.end():]);assert inlined==oracle_data and text[m.end()+end:].lstrip().startswith(';')
 # Independently reconstruct finite actual source imports and alias targets.
 alias={'codec:provider':graph['providerPath'],'codec:oracle-inputs':graph['oracleInputsPath'],'codec:fflate-browser':str(PUB/context['fflateBrowser'])};pending=[graph['entryPath']];seen=set();externals=set();resolutions=[]
 while pending:
  name=pending.pop(0)
  if name in seen:continue
  seen.add(name);source=read(name).decode()
  for item in re.finditer(r'^\s*import\b[^\n;]*?\bfrom\s*([\'\"])([^\'\"]+)\1',source,re.M):
   request=item[2]
   if request.startswith('node:'):externals.add(request)
   elif request in alias:target=alias[request];resolutions.append({'request':request,'importer':name,'target':target});pending.append(target)
   else:assert request.startswith('.');pending.append(str((Path(name).parent/request).resolve()))
 assert sorted(seen)==sorted(paths)and sorted(externals)==expected_imports and sorted(resolutions,key=lambda r:json.dumps(r,sort_keys=True))==sorted(graph['resolutions'],key=lambda r:json.dumps(r,sort_keys=True))
 capsule=H/arm;capsule.mkdir(parents=True,exist_ok=False);(capsule/'code.mjs').write_bytes(code);(capsule/'graph.json').write_bytes(read(OUT/row['graph']['path']))
 result={'schemaVersion':1,'state':'INDEPENDENT_ZLIB_COST_BUNDLE_SOURCE_VERIFIED_V1','toolingSourceIndexSha256':TOOLING,'guestSourceIndexSha256':GUEST,'sourcePublicationIndexSha256':PUBLICATION,'bundleActionSourceIndexSha256':ACTION,'rootActionSha256':AUTH,'arm':arm,'nativeEngineSha256':row['nativeEngineSha256'],'oracleSha256':authority['nodeOracleRenderProof']['oracle']['sha256'],'operationalAdmission':False,'ordinaryGuestExportsInvoked':False,'code':descriptor(capsule/'code.mjs'),'graph':descriptor(capsule/'graph.json'),'virtualModuleSources':[],'actualVirtualIds':[],'originalCode':{**row['code'],'path':str(OUT/row['code']['path'])},'originalGraph':{**row['graph'],'path':str(OUT/row['graph']['path'])},'publicSourceAudit':public,'inlinedOracleDataDeepEqual':True,'fullPhysicalModuleGraphReconstructed':True,'externalBundlerExitCode':0,'rootObservedTerminalNotRunByThisReader':True,'componentOrGuestOrPerformanceProof':False,'componentizationApproved':False}
 put(capsule/'results.json',result)
 capsule_rows=[{'path':str(p.relative_to(capsule)),'sha256':digest(p.read_bytes()),'bytes':p.stat().st_size}for p in sorted(capsule.iterdir())if p.is_file()]
 put(capsule/'index.json',{'schemaVersion':1,'state':'INDEXED_INDEPENDENT_ZLIB_COST_BUNDLE_SOURCE_PROOF_V1','files':capsule_rows})
 arm_results.append({'arm':arm,'index':descriptor(capsule/'index.json'),'result':descriptor(capsule/'results.json'),'code':result['code'],'graph':result['graph'],'physicalModules':len(paths),'virtualIds':[]})
assert [row['arm']for row in report['arms']]==ARMS
assert read(OUT/'fflate-on/bundle.mjs')==read(OUT/'fflate-off/bundle.mjs')
put(H/'input-references.json',{'schemaVersion':1,'state':'ACTUAL_ORIGINAL_SOURCE_DATA_CONTEXT_ONLY','files':[refs[key]for key in sorted(refs)],'originalMutableNativeCachePathsFollowed':False,'ownerSourceOrRuntimeHelpersExecuted':False})
put(H/'results.json',{'schemaVersion':1,'state':'INDEPENDENT_ACTUAL_ZLIB_COST_SOURCE_BUNDLES_VERIFIED','rootReceiptSha256':ROOT_RECEIPT,'actualOutputIndexSha256':root['actualIndex']['sha256'],'indexedOutputFiles':10,'actualOutputFiles':12,'publicExports':NAMES,'arms':arm_results,'allVirtualIdsEmpty':True,'virtualHelperBytesInvented':False,'fullPublicationRecordsRehashed':len(pmap),'publicationActualRegularFiles':len(actual_files),'publicationLinks':len(actual_links),'publicationDirectories':len(actual_dirs),'nativeFrozenRowsRehashed':frozen_counts,'selectedSDKReferencesRehashed':len(pair['selectedSDKReferences']),'allInlinedOracleDataDeepEqual':True,'fflateOnOffCodeBytesIdentical':True,'externalBundlerExitCode':0,'terminalObservedByThisReader':False,'rootReportedSession':63317,'rootReportedPid':24635,'reviewerReranAnyAction':False,'codecProviderComponentGuestNativeOrTimingActionsRun':False,'operationalAdmission':False,'componentizationApproved':False})
print(json.dumps({'state':'PASS_ACTUAL_SOURCE_ONLY','outputFiles':12,'publicationFiles':len(pmap),'sourceRefs':len(refs),'armProofs':arm_results,'actionsRerun':False}))
