"""Independent source/data reader. Never imports/runs the wrapper or its guards."""
from pathlib import Path
import hashlib,json,re
H=Path(__file__).resolve().parent;OWNER=H.parent/'cost-bundle-action-candidate-v1';EXPECTED='367e7960fb2382238c2cfa15320d1c57acc153837c5d0080419d33ad3417ce7c'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def raw(path,digest=None,size=None):
 p=Path(path);assert p.is_file()and not p.is_symlink(),p;value=p.read_bytes();assert digest is None or sha(value)==digest,p;assert size is None or len(value)==size,p;return value
def put(name,value):(H/name).write_text(json.dumps(value,indent=2)+'\n')
index=json.loads(raw(OWNER/'index.json',EXPECTED));assert len(index['files'])==7
for row in index['files']:raw(OWNER/row['path'],row['sha256'],row['bytes'])
inputs=json.loads(raw(OWNER/'source-inputs.json'));assert len(inputs['files'])==12
for row in inputs['files']:raw(row['path'],row['sha256'],row['bytes'])
publication_ref=next(row for row in inputs['files']if row['path']=='/private/tmp/starling-node-compat/zlib-cost-source-v3/index.json');publication=json.loads(raw(publication_ref['path'],publication_ref['sha256'],publication_ref['bytes']));root=Path(publication_ref['path']).parent
expected_names={'authority.mjs','context.mjs','native.mjs','preflight.mjs','bundle.mjs','environment.mjs','durable.mjs'}
texts={};edges=[];pending=['preflight.mjs','bundle.mjs','durable.mjs'];visited=set()
while pending:
 name=pending.pop(0)
 if name in visited:continue
 assert name in expected_names;visited.add(name);row=next(row for row in publication['files']if row['path']=='control/'+name);text=raw(root/'control'/name,row['sha256'],row['bytes']).decode();texts[name]=text
 for match in re.finditer(r'^\s*import\b[^\n;]*?\bfrom\s*([\'\"])([^\'\"]+)\1',text,re.M):
  request=match[2]
  if request.startswith('node:'):continue
  assert request.startswith('./')and'/'not in request[2:],request;target=request[2:];edges.append({'importer':name,'request':request,'target':target});pending.append(target)
assert visited==expected_names
action=raw(OWNER/'action.mjs').decode()
assert not any(not match[2].startswith('node:')for match in re.finditer(r'^import\b[^\n;]*?\bfrom\s*([\'\"])([^\'\"]+)\1',action,re.M))
first_dynamic=action.index("await import(pathToFileURL(join(root,'control/preflight.mjs')))")
assert action.index('await own();await nodeExecutable();')<action.index('const authority=')<first_dynamic
assert action.index("for(const file of ['authority.mjs','context.mjs','native.mjs','preflight.mjs','bundle.mjs','environment.mjs','durable.mjs'])")<first_dynamic
for token in ["authority.action,'bundle-source'","authority.actionAllowed,true","authority.outputRoot,OUTPUT","authority.permittedArms,arms","authority.componentGuestNativeBuildPilotOrTimingAllowed,false","authority.sourcePromotionAllowed,false","authority.operationalAdmission,false"]:assert token in action,token
assert "const OUTPUT='/private/tmp/starling-node-compat/zlib-cost-bundles-v1'"in action
assert "['native-on','fflate-on','fflate-off']"in action
assert "costPreflight({...config,arm,action:'bundle-source'})"in action
assert "providerPath:join(admitted.guestRoot,arm==='native-on'?'native-provider.mjs':'fflate-provider.mjs')"in action
assert 'oracleInputsPath:admitted.oracleInputsPath'in action
assert action.index('costPreflight(')<action.index('DurableOutput.create(OUTPUT)')<action.index('await bundleCost(')
bundle=texts['bundle.mjs'];assert bundle.index('assertPackagingEnvironment(admitted)')<bundle.index("await import(pathToFileURL(join(admitted.packagingRoot,'tests/node-compat/toolchain.mjs')))")<bundle.index('await loadToolchain()')
for key in ['NAPI_RS_NATIVE_LIBRARY_PATH','NAPI_RS_FORCE_WASI','NAPI_RS_WASI_FLAVOR','NAPI_RS_ENFORCE_VERSION_CHECK']:assert key in texts['environment.mjs']
for token in ['loadOracleRender(authority.authority.nodeOracleRenderProof','admitNativePair({authority,context,arm})','loadPublication(publicationIndex,authority)']:assert token in texts['preflight.mjs']
assert 'IMPLEMENTED_ACTIONS=Object.freeze([\'source-publication\',\'node-oracle\',\'bundle-source\'])'in texts['authority.mjs']
assert "codecProviderOrComponentOrGuestExecuted:false"in action and"independentSourceAndVirtualHelperReviewRequired:true"in action
assert action.count('componentizationAllowed:false')==2 and 'timingAllowed:false'in action
assert 'await admitted.recheck();await own();'in action
assert 'propertiesRead:false,partialOutputsRetained:true'in action
for token in ['O_EXCL','O_NOFOLLOW','await fd.sync()','Exact collected file membership','Retained output changed']:assert token in texts['durable.mjs']
config=json.loads(raw(OWNER/'future-config.template.json'));assert config['sourceIndexSha256']is None and config['rootAction']is None and config['actionsAllowed']is False
parse=json.loads(raw(OWNER/'parse-terminal.json'));assert parse['rawExitCode']==0 and parse['parseOnly']is True and parse['wrapperBodyExecuted']is False;assert parse['source']['sha256']==sha(raw(OWNER/'action.mjs'))
put('results.json',{'schemaVersion':1,'state':'PASS_BOUNDED_COST_BUNDLE_WRAPPER_SOURCE_REVIEW_NO_ACTION_AUTHORITY','candidateIndexSha256':EXPECTED,'indexedFiles':7,'sourceReferences':12,'guardModules':sorted(visited),'guardStaticEdges':edges,'primitiveFirstWrapperAuthentication':True,'exactThreeArmOutputRouting':True,'nativePairPublicationOracleRenderForwardedToExistingPreflight':True,'existingNapiGuardBeforeToolPackageLoad':True,'unreviewedDurableSourceCaptureOnly':True,'ownOrGuardModuleImported':False,'preflightOrWrapperOrBundlerExecuted':False,'codecProviderComponentGuestNativeOrTimingExecuted':False,'originalParseTerminalObservedByThisReader':False,'storedParseOnlyExitCode':0,'newRootBundleAuthorityAvailableInCandidate':False,'operationalAdmission':False,'componentizationApproved':False,'candidateChanged':False})
print(json.dumps({'state':'PASS_SOURCE_ONLY','files':7,'references':12,'guardModules':len(visited),'staticEdges':len(edges),'ownerOrLibraryActionsRun':False}))
