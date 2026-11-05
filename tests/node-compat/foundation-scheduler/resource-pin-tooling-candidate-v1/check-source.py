"""Preparation read/hash/AST/extracted-pure checks only. Never imports an action/helper."""
from pathlib import Path
import ast,copy,hashlib,json,sys
O=Path(__file__).resolve().parent;R=Path('/Users/dan/dev/StarlingMonkey')
checks=[]
def check(n,v):assert v,n;checks.append(n)
def deny(n,fn):
 try:fn()
 except(AssertionError,KeyError,TypeError,ValueError):check(n,True)
 else:raise AssertionError(n+' accepted')
def h(p):
 d=hashlib.sha256()
 with Path(p).open('rb')as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):d.update(b)
 return d.hexdigest()
def verify(r):
 p=Path(r['path']);check('canonical absolute source',p.is_absolute()and str(p)==r['path']and '..'not in p.parts and '\\'not in r['path']and '\0'not in r['path']);a=p.lstat();check('ordinary exact bytes '+str(p),p.is_file()and not p.is_symlink()and a.st_size==r['bytes']and h(p)==r['sha256']);b=p.lstat();check('stable '+str(p),(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns,b.st_ctime_ns));return p
def family(ix):
 x=json.loads(verify(ix).read_bytes());base=Path(ix['path']).parent;seen=set()
 for d in x['files']:
  n=d['path'];check('unique local member',n and not n.startswith('/')and all(p not in('','.','..')for p in n.split('/'))and n not in seen);seen.add(n);verify(dict(path=str(base/n),sha256=d['sha256'],bytes=d['bytes']))
 check('exact indexed family',not any(p.is_symlink()for p in base.rglob('*'))and{p.relative_to(base).as_posix()for p in base.rglob('*')if p.is_file()}==seen|{'index.json'})
refs=json.loads((O/'references.json').read_bytes());deriv=json.loads((O/'derivations.json').read_bytes());source=verify(deriv['donor']).read_text();nodes={n.name:ast.get_source_segment(source,n)for n in ast.parse(source).body if isinstance(n,ast.FunctionDef)}
parts=[]
for r in deriv['functions']:check('exact data-I/O extraction '+r['name'],r['text']==nodes[r['name']]);parts.append(r['text'])
check('whole data-I/O reconstruction',deriv['header']+'\n\n'.join(parts)+'\n'==(O/'data_io.py').read_text())
guard=(O/'guard.py').read_text();guard_nodes={n.name:ast.get_source_segment(guard,n)for n in ast.parse(guard).body if isinstance(n,ast.FunctionDef)}
check('guard same four genuine data functions',all(guard_nodes[r['name']]==r['text']for r in deriv['functions']))
for row in(refs['resourceSourceIndex'],refs['freezerIndex'],refs['freezerSourceReview']['index'],refs['actualArtifactReview']['index']):family(row)
for key in('node','python','actualArtifactContract','actualFreezeRootObservation','freezeReceipt','metadata','actualStageResult','frozenVerifier','metadataModel','resourcePolicy'):verify(refs[key])
artifact=json.loads(Path(refs['actualArtifactReview']['result']['path']).read_bytes());receipt=json.loads(Path(refs['freezeReceipt']['path']).read_bytes());metadata=json.loads(Path(refs['metadata']['path']).read_bytes());check('actual frozen666 unchanged',len(receipt['copies'])==666)
model_source=Path(refs['metadataModel']['path']).read_bytes();model_env={};exec(compile(ast.Module(body=[n for n in ast.parse(model_source).body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'extracted-genuine-resource342-metadata-DATA-model','exec'),model_env)
policy=json.loads(Path(refs['resourcePolicy']['path']).read_bytes())
def classify(raw):return model_env['validate_metadata'](raw,policy,refs['policySha256'],refs['helperSha256'],refs['recipeSha256'],refs['externalSourceManifest'],'normal-off')
check('actual51fb genuine extracted classifier342 seam',classify(metadata)['nativeFiles']==342)
for label,mutate in [('GC metadata',lambda x:x.__setitem__('gcStress',True)),('edited manifest',lambda x:x['sourceManifest'].pop()),('wrong recipe',lambda x:x.__setitem__('buildRecipeSha256','0'*64)),('invented runtime proof',lambda x:x['resourceOwnershipPolicy'].__setitem__('nativeRuntimeValidation',{})),('wrong external3',lambda x:x['componentizeSourceManifest'].pop()),('disabled web timer',lambda x:x['observedCMakeOptions'].__setitem__('ENABLE_BUILTIN_WEB_TIMERS','OFF'))]:
 z=copy.deepcopy(metadata);mutate(z);deny('genuine extracted classifier rejects '+label,lambda z=z:classify(z))
for row in receipt['copies']:verify({k:row[k]for k in('path','sha256','bytes')})
stage=json.loads(Path(refs['actualStageResult']['path']).read_bytes());check('configured501 distinct role',stage['destination']==refs['configuredSourceRoot']and len(stage['copies'])==501)
for item in stage['copies']:verify(dict(item['original'],path=item['path']))
# Execute only definitions/constant literals from the pure model, never its module.
t=ast.parse((O/'pin_model.py').read_bytes());env={'copy':copy};exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,(ast.Assign,ast.FunctionDef))],type_ignores=[]),'extracted-pin-DATA-model','exec'),env)
ix=dict(path=str(O/'index.json'),sha256='0'*64,bytes=1);pin=env['candidate'](receipt,metadata,refs,ix);document=env['unreviewed_document'](pin)
check('actual whole raw manifest342/fresh3/selected9',pin['sourceManifest']==metadata['sourceManifest']and pin['componentizeSourceManifest']==metadata['componentizeSourceManifest']and pin['selectedModuleManifests']==metadata['selectedModuleManifests'])
check('all666 frozen descriptors preserved',pin['frozenFiles']==[{k:r[k]for k in('path','sha256','bytes')}for r in receipt['copies']])
check('unreviewed and otherthreeNULL',pin['reviewRequired']is True and all(document['variants'][n]is None for n in('normal-runtime','gc-off','disabled-off')))
check('logical state does not rewrite full metadata',pin['resourceOwnershipPolicy']==metadata['resourceOwnershipPolicy']and pin['resourceOwnershipPolicy']['nativeRuntimeValidation']is None)
saved=copy.deepcopy(pin);pin['sourceManifest'][0]['sha256']='0'*64;check('candidate deeply owns output, raw metadata immutable',metadata['sourceManifest'][0]['sha256']!=pin['sourceManifest'][0]['sha256']);pin=saved
reviewed=copy.deepcopy(document);reviewed.update(state='ROOT_REVIEWED_SCHEDULER_RESOURCE342_NORMAL_OFF_VALIDATION_PINS_V1',reviewRequired=False);reviewed['variants']['normal-off'].update(state='reviewed-scheduler-resource342-normal-off-freeze-v1',reviewRequired=False)
export_row=dict(path='/private/tmp/test-source-only-export.json',sha256='a'*64,bytes=1);export_review=dict(index=dict(path='/private/tmp/model-index.json',sha256='b'*64,bytes=1),result=dict(path='/private/tmp/model-result.json',sha256='c'*64,bytes=1))
rr=json.loads((O/'future-root-pin-review.template.json').read_bytes());rr.update(reviewedPinsSha256='d'*64,toolingIndex=ix,actualExportCandidate=export_row,independentExportReview=export_review)
def selected(doc,review=rr):return env['select_reviewed'](doc,review,pin,'d'*64,export_row,export_review)
check('reviewed pin pure DATA seam only',selected(reviewed)==reviewed['variants']['normal-off'])
for name,mutate in [('wrongengine',lambda x:x['variants']['normal-off'].__setitem__('engineSha256','0'*64)),('wrongmetadata',lambda x:x['variants']['normal-off'].__setitem__('metadataSha256','0'*64)),('wrongcontext',lambda x:x['variants']['normal-off'].__setitem__('sourceRoot','/foreign/source')),('edited342manifest',lambda x:x['variants']['normal-off']['sourceManifest'].pop()),('filledGC',lambda x:x['variants'].__setitem__('gc-off',{})),('runtimegrant',lambda x:x.__setitem__('runtimeAcceptanceClaim',True)),('unreviewedstate',lambda x:x.__setitem__('state',document['state'])),('wrongtooling',lambda x:x.__setitem__('toolingIndex',{}))]:
 z=copy.deepcopy(reviewed);mutate(z);deny('reviewed pin rejects '+name,lambda z=z:selected(z))
for key,value in [('reviewedPinsSha256','e'*64),('otherVariantsNull',False),('runtimeAcceptanceClaim',True),('engineSha256','0'*64),('actualExportCandidate',None),('independentExportReview',None)]:
 z=copy.deepcopy(rr);z[key]=value;deny('Root pin review rejects '+key,lambda z=z:selected(reviewed,z))
g={'Path':Path,'SOURCE':Path(refs['configuredSourceRoot']),'FROZEN':Path(refs['freezeRoot']),'EXPORT_FILE':Path('/private/tmp/starling-node-compat/scheduler-resource-v1-pin-tooling/export-normal-off-UNREVIEWED.json'),'RESOURCE_SHA':refs['resourceSourceIndex']['sha256'],'FREEZER_SHA':refs['freezerIndex']['sha256']}
exec(compile(ast.Module(body=[n for n in ast.parse(guard).body if isinstance(n,ast.FunctionDef)and n.name in('descriptor','root_model','source_peer_model','artifact_model')],type_ignores=[]),'extracted-phase-DATA-models','exec'),g)
g['artifact_model'](artifact,refs);check('real80b artifact DATA wire',True)
for key,value in [('nativeSourceFiles',355),('selectedManifestCount',11),('variant','gc-off'),('engineExecuted',True),('bootstrapExecuted',True),('configuredSourceRoot','/wrong/context'),('metadata',dict(refs['metadata'],sha256='0'*64))]:
 z=copy.deepcopy(artifact);z[key]=value;deny('artifact DATA rejects '+key,lambda z=z:g['artifact_model'](z,refs))
peer=json.loads((O/'future-source-peer-contract.json').read_bytes());peer['toolingSourceIndexSha256']=ix['sha256'];g['source_peer_model'](peer,dict(toolingIndex=ix));check('exact future source-peer DATA seam',True)
for key,value in [('toolingSourceIndexSha256','e'*64),('sourceReviewPassed',False),('sourceOnly',False),('ownerActionsInvoked',True),('hostActionsInvoked',True),('exportOrBootstrapActionsInvoked',True)]:
 z=copy.deepcopy(peer);z[key]=value;deny('source-peer DATA rejects '+key,lambda z=z:g['source_peer_model'](z,dict(toolingIndex=ix)))
cfg=dict(toolingIndex=ix);root=json.loads((O/'future-root-authority.template.json').read_bytes());root.update(state='ROOT_REVIEWED_SCHEDULER_RESOURCE342_PIN_TOOLING_PHASE_V1',phase='export',toolingIndex=ix,exportAllowed=True,candidateOutput=str(g['EXPORT_FILE']));g['root_model'](root,cfg,'export');check('export phase synthetic DATA seam only',True)
boot=copy.deepcopy(root);boot.update(phase='bootstrap',exportAllowed=False,bootstrapAllowed=True,candidateOutput=None,actualExportCandidate=export_row,reviewedPins=export_row,rootPinReview=export_row,independentExportReview=export_review);g['root_model'](boot,cfg,'bootstrap');check('bootstrap phase distinct synthetic DATA seam only',True)
deny('export Root cannot bootstrap',lambda:g['root_model'](root,cfg,'bootstrap'));deny('bootstrap Root cannot export',lambda:g['root_model'](boot,cfg,'export'))
for key in('buildAllowed','freezeAllowed','gcReconfigureAllowed','componentAllowed','engineExecutionAllowed','guestAllowed','keyOrCryptoAllowed','runtimeAcceptanceClaim','operationalAdmission','sourcePromotionAllowed','metadataProjectionAllowed','timingAllowed'):
 z=copy.deepcopy(root);z[key]=True;deny('Root rejects unrelated grant '+key,lambda z=z:g['root_model'](z,cfg,'export'))
for key,value in [('variant','gc-off'),('nativeSourceFiles',355),('selectedManifestCount',11),('configuredSourceRoot','/foreign/source'),('frozenSourceRoot','/foreign/frozen'),('candidateOutput','/foreign/export.json')]:
 z=copy.deepcopy(root);z[key]=value;deny('Root rejects wrong role '+key,lambda z=z:g['root_model'](z,cfg,'export'))
for key in('reviewedPins','rootPinReview','actualExportCandidate','independentExportReview'):
 z=copy.deepcopy(boot);z[key]=None;deny('bootstrap refusesNULL '+key,lambda z=z:g['root_model'](z,cfg,'bootstrap'))
action=(O/'action.py').read_text();api=(O/'bootstrap.mjs').read_text()
for name,value in{
 'whole own authentication before guard import':action.index("names|{'index.json'}")<action.index("spec_from_file_location('resource_pin_phase_guard'"),
 'full reviews before genuine verifier helper':guard.index("frame['reviewedPin']=pin_model.select_reviewed")<guard.index("model=load_exact(refs['metadataModel']")<guard.index("verifier=load_exact(refs['frozenVerifier']"),
 'exact full verifier path and context':"assert refs['frozenVerifier']in freezer"in guard and "verifier.FREEZE==FROZEN"in guard,
 'no old selector or globals rebinding':all(x not in guard+action for x in('metadata-admission.mjs','verifyProductionTicks','cryptoOwner','sys.modules[','verifier.FREEZE =','verifier.HERE =','verifier.REPO =','verifier.OUTPUT =')),
 'unchanged whole raw metadata returned':'metadata=frame[\'metadata\']'in action,
 'read-only bootstrap has no output branch':action.index("if phase=='export':")<action.index("g.EXPORT_ROOT.mkdir")and 'open(\'x\')'not in action,
 'export exclusive held dirfd':'os.O_EXCL|os.O_NOFOLLOW' in action and 'dir_fd=directory'in action,
 'source family and proof final failure rechecks':'finally:g.recheck(frame)'in action and 'finally:recheck(frame)'in guard,
 'new Node harnessAPI no embedding hook':'export async function resourceBootstrapPreflight({configDescriptor}={})'in api and 'componentize('not in api,
 'Node captures primitives beforeawait':api.index('const captured=captureDescriptor(configDescriptor)')<api.index('const cfg=deepFreeze(JSON.parse(await regular(captured)))'),
 'Node standard read-only helper and whole frame recheck':"'action.py'),'bootstrap'"in api and 'JSON.stringify(await execute())===stable'in api,
 'Node helper failure also rechecks sources':'finally{await sourceRecheck();}'in api,
 'original/configured/frozen explicit':all(x in action for x in('originalToolingRoot=str(OWN)','configuredSourceRoot=str(g.SOURCE)','frozenSourceRoot=str(g.FROZEN/\'source\')')),
 'all activation templatesNULL':all(refs[k]is None for k in('reviewedPins','rootPinReview','independentExportReview','actualExportCandidate','actualBootstrapResult')),
}.items():check(name,value)
asts=[]
for p in sorted(O.glob('*.py')):ast.parse(p.read_bytes(),filename=str(p));asts.append(p.name)
check('all Python AST parses',True);check('no export output created',not Path('/private/tmp/starling-node-compat/scheduler-resource-v1-pin-tooling').exists())
result=dict(schemaVersion=1,state='RESOURCE342_PIN_TOOLING_SOURCE_DATA_PURE_CHECKS_PASSED_NO_ACTIONS_V1',checks=len(checks),checkNames=checks,pythonAstFiles=asts,sourceOnly=True,sourceRoot=refs['configuredSourceRoot'],frozenSourceRoot=refs['frozenSourceRoot'],actualArtifactReview=refs['actualArtifactReview'],frozenCopiesReadOnlyHashed=666,configuredRowsReadOnlyHashed=501,rawMetadataUnchanged=True,modelOnlyExtracted=True,ownerGuardOrActionOrVerifierImported=False,exportOrBootstrapInvoked=False,engineComponentGuestKeyGcOrHostActionsInvoked=False,actualPinOrAuthorityCreated=False)
if len(sys.argv)==2:
 with Path(sys.argv[1]).open('x')as f:json.dump(result,f,indent=2);f.write('\n')
else:assert len(sys.argv)==1
print(json.dumps(result))
