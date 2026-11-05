"""Preparation-only read/hash/AST/extracted-pure checks. No freezer/helper/action calls."""
from pathlib import Path
import ast,copy,hashlib,json,os,re,shlex,stat,sys
O=Path(__file__).resolve().parent;P=O.parent/'resource-integration-candidate-v1'
checks=[]
def check(n,v):assert v,n;checks.append(n)
def deny(n,fn):
 try:fn()
 except(AssertionError,KeyError,ValueError,TypeError):check(n,True)
 else:raise AssertionError(n+' accepted')
def h(p):
 d=hashlib.sha256()
 with Path(p).open('rb')as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):d.update(b)
 return d.hexdigest()
def verify(r):
 p=Path(r['path']);check('canonical original descriptor',p.is_absolute()and str(p)==r['path']and not r['path'].startswith('//')and '\\'not in r['path']and '\0'not in r['path']and '..'not in p.parts);a=p.lstat();check('ordinary expected bytes '+str(p),stat.S_ISREG(a.st_mode)and a.st_size==r['bytes']and h(p)==r['sha256']);b=p.lstat();check('stable '+str(p),(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns,b.st_ctime_ns));return p
def family(r):
 x=json.loads(verify(r).read_bytes());base=Path(r['path']).parent;names=set()
 for d in x['files']:
  n=d['path'];check('finite family member',n and not n.startswith('/')and '\\'not in n and all(p not in('','.','..')for p in n.split('/'))and n not in names);names.add(n);verify(dict(path=str(base/n),sha256=d['sha256'],bytes=d['bytes']))
 check('exact family membership',not any(p.is_symlink()for p in base.rglob('*'))and{p.relative_to(base).as_posix()for p in base.rglob('*')if p.is_file()}==names|{'index.json'})
refs=json.loads((O/'references.json').read_bytes());plan=json.loads((O/'capture-plan.json').read_bytes());proof=json.loads((O/'derivations.json').read_bytes())
for f in refs['families']:family(f['index'])
for r in refs['files']:verify(r)
for r in refs['sdkAliases']:
 p=Path(r['path']);check('SDK alias exact verified-reference provenance',p.is_symlink()and str(p.readlink())==r['link']and str(p.resolve(strict=True))==r['resolvedTarget'])
source=json.loads((O/'future-config.template.json').read_bytes())['resourceSourceIndex'];family(source)
donor=verify(proof['donor']).read_text();nodes={n.name:ast.get_source_segment(donor,n)for n in ast.parse(donor).body if isinstance(n,ast.FunctionDef)};parts=[]
for r in proof['functions']:
 check('exact donor source '+r['name'],r['before']==nodes[r['name']]);s=r['before']
 for edit in r['changes']:check('singleton function edit',s.count(edit['before'])==1);s=s.replace(edit['before'],edit['after'])
 check('exact function afterimage '+r['name'],s==r['after']);parts.append(s)
 for edit in reversed(r['changes']):check('singleton reverse function edit',s.count(edit['after'])==1);s=s.replace(edit['after'],edit['before'])
 check('exact reverse '+r['name'],s==r['before'])
check('whole source extraction reconstruction',proof['header']+'\n\n'.join(parts)+'\n'==(O/'copy_io.py').read_text())
check('no old helper import/context globals',all(x not in(O/'copy_io.py').read_text()for x in('admission-pins','REPO =','HERE =','OUTPUT =','classify(')))
check('monitor unchanged',verify(proof['monitorDonor']).read_bytes()==(O/'monitor.py').read_bytes())
for r in plan['copies']:verify(r['source']);check('finite copy destination',r['destination']and not r['destination'].startswith('/')and all(p not in('','.','..')for p in r['destination'].split('/')))
check('complete unique copy plan',len({r['destination']for r in plan['copies']})==len(plan['copies'])==plan['baseCopies']==623 and sum(r['source']['bytes']for r in plan['copies'])==plan['baseCopyBytes'])
check('342 plus fresh3 plus159 plus29 exact roles',sum(r['role']=='native-source342'for r in plan['copies'])==342 and sum(r['role']=='fresh-external-embedding3'for r in plan['copies'])==3 and sum(r['role']=='configured-nonnative-tool-proof-source'for r in plan['copies'])==159 and sum(r['role']=='selected-static-library'for r in plan['copies'])==29)
check('verified references explicit not copy coverage',len(plan['verifiedReferences'])==plan['verifiedReferenceCount']==7500 and plan['verifiedReferenceByteCoverageNotCopied']is True)
for r in plan['verifiedReferences']:verify(r)
# Execute only genuine pure function definitions extracted from source, no module imports.
model_source=P/'native-admission-model.py';modelnode=next(n for n in ast.parse(model_source.read_bytes()).body if isinstance(n,ast.FunctionDef)and n.name=='validate_metadata');m={};exec(compile(ast.Module(body=[modelnode],type_ignores=[]),'extracted-raw-model','exec'),m)
metadata=json.loads(verify(refs['metadata']).read_bytes());policy=json.loads((P/'policy.json').read_bytes())
def model(v):return m['validate_metadata'](v,policy,refs['policySha256'],refs['helperSha256'],refs['recipeSha256'],refs['externalSourceManifest'],'normal-off')
check('actual whole51fb raw metadata DATA validates without rewrite',model(metadata)['grantsAuthority']is False)
for name,mutate in[
 ('oldrecipe',lambda x:x.__setitem__('buildRecipeSha256','3694c88b7d000f27e11ffcac835fe0b205b2075f5b0038ba1cf3')),
 ('355projection',lambda x:x['sourceManifest'].extend([dict(path='fake'+str(i),sha256='0'*64)for i in range(13)])),
 ('GC',lambda x:x.__setitem__('gcStress',True)),('RuntimeOnly',lambda x:x.__setitem__('entropyPolicy','runtime-only')),('OOM',lambda x:x.__setitem__('oomTesting',True)),('diagnostic',lambda x:x.__setitem__('diagnosticOnly',True)),
 ('synthetic',lambda x:x.__setitem__('syntheticMetadataOnly',True)),('runtimefabrication',lambda x:x['resourceOwnershipPolicy'].__setitem__('nativeRuntimeValidation',True)),('reusefabrication',lambda x:x['resourceOwnershipPolicy'].__setitem__('fullResetOrReuse',True)),('timersOFF',lambda x:x['requestedCMakeOptions'].__setitem__('ENABLE_BUILTIN_WEB_TIMERS','OFF'))]:
 v=copy.deepcopy(metadata);mutate(v);deny('raw metadata rejects '+name,lambda v=v:model(v))
tree=ast.parse((O/'guard.py').read_bytes());env={'Path':Path,'OWN':O,'SOURCE':Path('/private/tmp/starling-node-compat/scheduler-resource-v1-source'),'WORK':Path('/private/tmp/starling-node-compat/scheduler-resource-v1-build'),'FREEZE':Path('/private/tmp/starling-node-compat/scheduler-resource-v1-freeze'),'EXTERNAL':Path('/private/tmp/starling-node-compat/scheduler-resource-v1-freeze-external-root'),'SOURCE_SHA':source['sha256']}
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in('descriptor','root_model','peer_model')],type_ignores=[]),'extracted-pure-guard','exec'),env)
ix=dict(path=str(O/'index.json'),sha256='0'*64,bytes=1);root=json.loads((O/'future-root-authority.template.json').read_bytes());root.update(state='ROOT_REVIEWED_SCHEDULER_RESOURCE342_NORMAL_OFF_FREEZE_V1',freezeAllowed=True,postBuildNinjaCommandsAllowed=True,freezerIndex=ix,freezerEntry=dict(path=str(O/'freeze.py'),sha256='0'*64,bytes=1));env['root_model'](root,ix);check('Root phase DATA positive only',True)
for key in('buildAllowed','gcReconfigureAllowed','exportAllowed','bootstrapAllowed','componentAllowed','engineExecutionAllowed','guestAllowed','keyOrCryptoAllowed','runtimeAcceptanceClaim','operationalAdmission','sourcePromotionAllowed','metadataProjectionAllowed','timingAllowed'):
 v=copy.deepcopy(root);v[key]=True;deny('deny phase '+key,lambda v=v:env['root_model'](v,ix))
for key,value in [('variant','gc-off'),('selectedManifestCount',11),('nativeSourceFiles',355),('freezeRoot','/private/tmp/old355-freeze'),('externalParentDeadlineSeconds',7200),('resourceSourceIndexSha256','0'*64),('gcStress',True),('entropyMode','RUNTIME_ONLY')]:
 v=copy.deepcopy(root);v[key]=value;deny('deny wrong root '+key,lambda v=v:env['root_model'](v,ix))
for path in('relative','/a/../b','/a//b','//a','/a\\b','/a\0b'):
 deny('canonical descriptor refuses '+repr(path),lambda path=path:env['descriptor'](dict(path=path,sha256='0'*64,bytes=1)))
e={'Path':Path,'re':re,'shlex':shlex};pure={'manifest','exact_release','compile_command','embedding_command'};exec(compile(ast.Module(body=[n for n in ast.parse((O/'copy_io.py').read_bytes()).body if isinstance(n,ast.FunctionDef)and n.name in pure],type_ignores=[]),'extracted-pure-command-functions','exec'),e)
database=json.loads(verify(refs['compileCommands']).read_bytes());names={str(env['SOURCE']/r['path']):r['path']for r in policy['expectedNativeSourceManifest']if r['path'].endswith('.cpp')and r['path'].startswith(('builtins/','runtime/'))};count=0
for r in database:
 if r['file']in names:e['compile_command'](r['command'],False,names[r['file']],True,False);count+=1
check('all actual61 policy commands pureparsed',count==61)
embedding=metadata['actualEmbeddingCompileCommands'];check('separate one embedding pureparsed',len(embedding)==1);e['compile_command'](embedding[0],False,'embedding/embedding.cpp',True,False)
fixture=('\n'.join(embedding)+'\n').encode();check('actual command DATA exact extraction',e['embedding_command'](fixture,refs['externalSourceRoot']+'/embedding/embedding.cpp')==embedding)
deny('duplicate embedding DATA refused',lambda:e['embedding_command'](fixture+fixture,refs['externalSourceRoot']+'/embedding/embedding.cpp'));deny('wrong embedding DATA refused',lambda:e['embedding_command'](fixture,'/foreign/embedding.cpp'))
sample=next(r for r in database if r['file']in names)
for flag in('-O0','-DNODE_COMPAT_OOM_TESTING=1','-fsyntax-only'):
 deny('compile DATA refuses '+flag,lambda flag=flag:e['compile_command'](sample['command']+' '+flag,False,names[sample['file']],True,False))
receipt_fn=next(n for n in ast.parse((O/'verify.py').read_bytes()).body if isinstance(n,ast.FunctionDef)and n.name=='receipt_model');ve={'ENGINE':refs['engine']['sha256'],'META':refs['metadata']['sha256']};exec(compile(ast.Module(body=[receipt_fn],type_ignores=[]),'extracted-receipt-data-model','exec'),ve)
receipt=dict(schemaVersion=1,state='SCHEDULER_RESOURCE342_NORMAL_OFF_NATIVE_FREEZE_COMPLETE_UNREVIEWED_V1',variant='normal-off',resourceSourceIndexSha256=source['sha256'],engine=refs['engine'],metadata=refs['metadata'],nativeInputsVerified=342,externalEmbeddingInputsVerified=3,selectedManifestCount=9,compileDatabaseRows=67,policyCppCommands=61,otherConfiguredSourceRows=5,generatedNullCppRows=1,embeddingRowsInCompileDatabase=0,separatePostBuildEmbeddingCommands=1,actualStrictCommands=4,actualPrivateClassicCommands=5,staticLibrariesPhysicallyCopied=29,rawMetadataBytesUnchanged=True,rawMetadataOriginalConfiguredPathsPreserved=True,receiptRequiresExternalParentZeroAndIndependentReview=True,allInputsValidatedBeforeCopies=True,allCopiesAndOriginalsRehashed=True,resourceNativeRuntimeValidation=None,reviewedEnginePins=None)
for key in('gcReconfigureAllowed','engineExecuted','bootstrapExecuted','componentOrGuestExecuted','operationalAdmission','runtimeAcceptanceClaim'):receipt[key]=False
ve['receipt_model'](receipt);check('receipt DATA shape only positive, no frozen object',True)
for key,value in [('variant','gc-off'),('nativeInputsVerified',355),('selectedManifestCount',11),('compileDatabaseRows',68),('embeddingRowsInCompileDatabase',1),('rawMetadataBytesUnchanged',False),('receiptRequiresExternalParentZeroAndIndependentReview',False),('engineExecuted',True),('gcReconfigureAllowed',True),('resourceNativeRuntimeValidation',True),('runtimeAcceptanceClaim',True)]:
 z=copy.deepcopy(receipt);z[key]=value;deny('receipt DATA refuses '+key,lambda z=z:ve['receipt_model'](z))
g=(O/'guard.py').read_text();body=(O/'freeze.py').read_text();controller=(O/'controller.py').read_text();v=(O/'verify.py').read_text()
for n,value in{
 'raw classifier before library ledger':g.index('model.validate_metadata(')<g.index("ledger=read(refs['buildInputLedger'])"),
 'no old selector or355 API':all(x not in g+body for x in('verifyProductionTicks','cryptoOwner','metadata-admission.mjs')),
 'actual configured layer no rebinding':"assert layer.HERE==SOURCE/"in g and not any(x in g+body for x in('layer.HERE =','layer.REPO =','io.OUTPUT =','sys.modules[')),
 'full proof before model import':g.index("for key,value in contract['requiredFixedValues'].items()")<g.index("spec_from_file_location('genuine_resource342_raw_metadata_model'"),
 'Ninja raw before status assertions':body.index("write('normal-off-embedding.after.terminal.json'")<body.index('assert status==0'),
 'fresh post-Ninja metadata equality':"assert embedding==meta['actualEmbeddingCompileCommands']"in body,
 'engine read after new command gate':body.index('io.compile_command(embedding[0]')<body.index("g.checked(frame['refs']['engine'])"),
 'full source audits final and failure':"finally:recheck(frame)"in g and "finally:g.recheck(frame)"in controller and "try:g.recheck(frame)"in body,
 'held output identity and private mode':"os.O_NOFOLLOW"in body and "same_root();g.recheck(frame)"in body and "os.umask(0o077)"in body,
 'whole metadata no projection':"rawMetadataBytesUnchanged=True,rawMetadataOriginalConfiguredPathsPreserved=True"in body,
 'frozen verifier does not rerun originalwork':all(x not in v for x in('subprocess','spec_from_file_location','original\'][','cryptoOwner')),
 'no HOME CODEX_HOME repurpose':not any(x in g+body+controller for x in("['HOME']=","['CODEX_HOME']=","HOME=","CODEX_HOME=")),
}.items():check(n,value)
asts=[]
for q in sorted(O.glob('*.py')):ast.parse(q.read_bytes(),filename=str(q));asts.append(q.name)
check('all Python AST parses',True)
check('freeze output remains absent',not env['FREEZE'].exists())
result=dict(schemaVersion=1,state='RESOURCE342_FREEZER_SOURCE_DATA_PURE_CHECKS_PASSED_NO_ACTIONS',sourceOnly=True,checks=len(checks),checkNames=checks,pythonAstFiles=asts,metadataModelOnlyExtracted=True,commandFunctionsOnlyExtracted=True,actualCompilerCommandsParsedAsData=62,copyFunctionsExecuted=False,genuineLayerImported=False,genuineGuardOrFreezerInvoked=False,ninjaInvoked=False,engineExecuted=False,sourceAndRuntimeAuthorityCreated=False,baseCopyRows=623,baseCopyBytes=plan['baseCopyBytes'],verifiedReferences=7500,verifiedReferenceBytes=plan['verifiedReferenceBytes'])
if len(sys.argv)==2:
 with Path(sys.argv[1]).open('x')as out:json.dump(result,out,indent=2);out.write('\n')
else:assert len(sys.argv)==1
print(json.dumps(result))
