"""Source/DATA only, plus tiny owned stdlib-copy077 regression; no build tools."""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,os,re,sys,tempfile
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_bytes())
def sha(b):return hashlib.sha256(b).hexdigest()
def load(name,file):
 spec=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
ext=load('new_proposed_pure_extension','producer-extension.py');copier=load('new_owned_copy_primitive','copy-source.py')
plan=read(HERE/'integration-plan.json');refs=read(HERE/'references.json');checks=[]
def good(name,f):f();checks.append(dict(name=name,passed=True))
def bad(name,f):
 try:f()
 except (AssertionError,KeyError,ValueError):checks.append(dict(name=name,refused=True));return
 raise AssertionError('Negative accepted:'+name)
for key in ['diagnosticSource','diagnosticSourcePeer','diagnosticSdkSyntax','diagnosticInventory','parentMetadataFieldShapeOnly','parentRecipe','parentHelper','parentPolicy','parentClassifier','cmakeAddBuiltin','nativeDiagnosticCmake','externalCmake','sharedParentToolLedger']:
 r=refs[key];b=Path(r['path']).read_bytes();assert len(b)==r['bytes']and sha(b)==r['sha256']
for key in ['diagnosticSource','diagnosticSourcePeer','diagnosticSdkSyntax']:
 ix=refs[key];root=Path(ix['path']).parent;m=read(ix['path']);names={'index.json'}
 for r in m['files']:
  assert r['path'] not in names;names.add(r['path']);b=(root/r['path']).read_bytes();assert(len(b),sha(b))==(r['bytes'],r['sha256'])
 assert names=={p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}
assert len(plan['nativeSources'])==357 and len(plan['externalSources'])==3
assert (plan['retainedParentFiles'],len(plan['changedNativePaths']),len(plan['newNativePaths']))==(349,6,2)
assert len(plan['publicWholeManifests'])==11 and len(plan['sourceDerivedBaseMetadataFields'])==80
assert plan['proposedRawMetadataFields']==82 and len(plan['newTopLevelMetadataFields'])==2
for root in plan['contexts'].values():assert not Path(root).exists()
recipe=Path(refs['parentRecipe']['path']).read_text();helper=Path(refs['parentHelper']['path']).read_text()
tools={'helper':Path(refs['parentHelper']['path']).read_bytes(),'policy':Path(refs['parentPolicy']['path']).read_bytes()}
guards=[]
for line_no,line in enumerate(recipe.splitlines(),1):
 if 'sha256_file "$consumers_layer_root/layer-policy.py"' in line or 'assert digest(layer_file) ==' in line:
  match=re.search(r'([a-f0-9]{64})',line);assert match;guards.append(dict(role='helper',line=line_no,expected=match.group(1),source=line))
 if 'sha256_file "$consumers_layer_root/policy.json"' in line:
  match=re.search(r'([a-f0-9]{64})',line);assert match;guards.append(dict(role='policy',line=line_no,expected=match.group(1),source=line))
assert [g['role']for g in guards].count('helper')==5 and [g['role']for g in guards].count('policy')==2
def test_guards(values,rows=guards):assert all(sha(values[g['role']])==g['expected']for g in rows)
good('all seven actual recipe digest equalities use actual file bytes',lambda:test_guards(tools))
for i in range(7):
 gs=copy.deepcopy(guards);gs[i]['expected']='0'*64
 bad('single stale recipe guard '+str(i),lambda gs=gs:test_guards(tools,gs))
bad('policy bytes changed without updating recipe joins',lambda:test_guards(dict(tools,policy=tools['policy']+b'\n')))
bad('helper bytes changed without updating recipe joins',lambda:test_guards(dict(tools,helper=tools['helper']+b'\n')))
policy_literal=re.search(r"POLICY_SHA256='([a-f0-9]{64})'",helper).group(1)
assert policy_literal==sha(tools['policy']);checks.append(dict(name='actual helper POLICY_SHA256 matches actual policy bytes',passed=True))
for anchor in read(HERE/'recipe-insertions.json')['sourceAnchors']:assert recipe.count(anchor['before'])==1
def apply_patch_text(before,patch):
 source_lines=before.splitlines(True);out=[];cursor=0;lines=patch.splitlines(True);at=2
 while at<len(lines):
  h=re.match(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@',lines[at]);assert h
  start=int(h.group(1))-1;out.extend(source_lines[cursor:start]);cursor=start;at+=1
  while at<len(lines)and not lines[at].startswith('@@'):
   line=lines[at];at+=1
   if line.startswith(' '):assert source_lines[cursor]==line[1:];out.append(line[1:]);cursor+=1
   elif line.startswith('-'):assert source_lines[cursor]==line[1:];cursor+=1
   elif line.startswith('+'):out.append(line[1:])
   else:raise AssertionError('Unexpected patch record')
 out.extend(source_lines[cursor:]);return ''.join(out)
patch=(HERE/'embedding-diagnostic.UNAPPLIED.patch').read_text()
a=Path(refs['externalEmbeddingBefore']['path']).read_text();b=Path(refs['externalEmbeddingAfter']['path']).read_text()
assert apply_patch_text(a,patch)==b
import difflib
inverse=''.join(difflib.unified_diff(b.splitlines(True),a.splitlines(True),fromfile='a/embedding/embedding.cpp',tofile='b/embedding/embedding.cpp',n=3))
assert apply_patch_text(b,inverse)==a
checks.append(dict(name='actual embedding delta forward+inverse text, no patch/tool/stage action',passed=True))
cmake=Path(refs['nativeDiagnosticCmake']['path']).read_text()
assert cmake.count('Instrument private lifecycle snapshots" OFF')==1 and cmake.count('Enable private lifecycle module" OFF')==1
assert 'target_compile_definitions(extension_api INTERFACE NODE_COMPAT_LIFECYCLE_DIAGNOSTICS=1)'in cmake
assert 'target_compile_definitions(host_api PRIVATE NODE_COMPAT_LIFECYCLE_DIAGNOSTICS=1)'in cmake
assert 'PRIVATE spidermonkey extension_api' in Path(refs['cmakeAddBuiltin']['path']).read_text()
assert 'add_builtin(componentize::embedding SRC embedding/embedding.cpp)' in Path(refs['externalCmake']['path']).read_text()
root=plan['contexts']['configuredSourceRoot'];work=plan['contexts']['workRoot']
native_paths=[r['path']for r in plan['nativeSources']if r['path'].endswith('.cpp')and r['path'].startswith(('builtins/','runtime/'))]
def command(path):return 'clang++ --target=wasm32-wasi -O3 -DNDEBUG -fno-exceptions -DNODE_COMPAT_LIFECYCLE_DIAGNOSTICS=1 -c '+path
entries=[dict(file=root+'/'+path,command=command(root+'/'+path))for path in native_paths]
old_meta=read(refs['parentMetadataFieldShapeOnly']['path']);old_db=read(old_meta['compileCommandsPath'])
old_source=old_meta['combinedNativeSourcePolicy']['configuredSourceRoot']
other=[r['file'][len(old_source)+1:]for r in old_db if r['file'].startswith(old_source+'/')and not r['file'].startswith((old_source+'/builtins/',old_source+'/runtime/'))]
assert len(other)==5
entries += [dict(file=root+'/'+path,command=command(root+'/'+path))for path in other]
entries += [dict(file=work+'/engine-private/starling-raw.wasm/null.cpp',command=command(work+'/engine-private/starling-raw.wasm/null.cpp'))]
emb=[dict(source=work+'/componentize-private/embedding/embedding.cpp',command=command(work+'/componentize-private/embedding/embedding.cpp'))]
options={k:'ON'for k in ['NODE_COMPAT_LIFECYCLE_DIAGNOSTICS','ENABLE_BUILTIN_DIAGNOSTICS_CLOCK_LIFECYCLE','ENABLE_BUILTIN_WEB_PERFORMANCE']}
def classify(es=entries,em=emb,req=options,obs=options):return ext.classify_commands(plan,es,em,req,obs)
classification=classify();checks.append(dict(name='synthetic diagnostic357 command partition; never observed compile proof',passed=True))
shared_index=next(i for i,r in enumerate(entries)if r['file']==root+'/runtime/js.cpp')
for name,edit in [
 ('missing native macro',lambda es:es.__setitem__(next(i for i,r in enumerate(es)if r['file']==root+'/runtime/js.cpp'),dict(file=root+'/runtime/js.cpp',command=command(root+'/runtime/js.cpp').replace('-DNODE_COMPAT_LIFECYCLE_DIAGNOSTICS=1 ','')))),
 ('wrong macro value',lambda es:es[shared_index].update(command=es[shared_index]['command'].replace('DIAGNOSTICS=1','DIAGNOSTICS=0'))),
 ('syntax evidence cannot stand in for actual compile',lambda es:es[shared_index].update(command=es[shared_index]['command']+' -fsyntax-only')),
 ('duplicate source command',lambda es:es.append(es[0])),
 ('hash357 macro cannot leak in',lambda es:es[shared_index].update(command=es[shared_index]['command']+' -DNODE_COMPAT_CRYPTO_HASH_HMAC=1'))]:
 es=copy.deepcopy(entries);edit(es);bad(name,lambda es=es:classify(es=es))
bad('embedding missing diagnostic macro',lambda:classify(em=[dict(emb[0],command=emb[0]['command'].replace('-DNODE_COMPAT_LIFECYCLE_DIAGNOSTICS=1 ',''))]))
bad('observed options disagree',lambda:classify(obs=dict(options,NODE_COMPAT_LIFECYCLE_DIAGNOSTICS='OFF')))
fields=ext.diagnostic_fields(plan,classification,dict(namespace='NS_DEF(diagnostics::clock_lifecycle)',count=1,performanceTargetEnabled=True))
assert set(fields)==set(plan['newTopLevelMetadataFields']) and all(v['diagnosticOnly']is True for v in fields.values())
assert len(set(plan['sourceDerivedBaseMetadataFields'])|set(fields))==82
checks.append(dict(name='two new fields returned separately; no old metadata frame accepted/projected',passed=True))
bad('absent actual installation',lambda:ext.diagnostic_fields(plan,classification,dict(namespace='NS_DEF(diagnostics::clock_lifecycle)',count=0,performanceTargetEnabled=True)))
bad('partial proposal refuses all action readiness',lambda:ext.require_complete_wiring(read(HERE/'future-wiring.json')))
copy_cases=[]
with tempfile.TemporaryDirectory(prefix='diag357-source-copy077-')as scratch:
 d=Path(scratch);data=b'public Source copy fixture\n';source=d/'source';source.write_bytes(data);os.chmod(source,0o644)
 prior=os.umask(0o077)
 try:
  for mode in [0o644,0o755]:
   old=d/('old-'+oct(mode));fd=os.open(old,os.O_CREAT|os.O_EXCL|os.O_WRONLY,mode);os.write(fd,data);os.close(fd)
   assert old.stat().st_mode&0o777==mode&~0o077
   assert old.stat().st_mode&0o777!=mode
   new=d/('new-'+oct(mode));actual=copier.copy_file(source,new,sha(data),len(data),mode)
   assert actual['mode']==mode and new.read_bytes()==data and source.read_bytes()==data
   copy_cases.append(dict(requestedMode=mode,oldActualMode=old.stat().st_mode&0o777,newActualMode=new.stat().st_mode&0o777,bytes=len(data),actualOwnedHostScratchOnly=True))
  bad('wrong expected copy hash refuses',lambda:copier.copy_file(source,d/'bad','0'*64,len(data),0o644))
 finally:os.umask(prior)
for f in HERE.glob('*.py'):ast.parse(f.read_bytes())
for key in ['diagnosticSource','diagnosticSourcePeer','diagnosticSdkSyntax','parentRecipe','parentHelper','parentPolicy','parentClassifier']:
 r=refs[key];assert sha(Path(r['path']).read_bytes())==r['sha256']
result=dict(schemaVersion=1,state='PARTIAL_DIAGNOSTIC357_SOURCE_EXTENSION_CHECKS_PASSED_NOT_A_BUILD_PRODUCER',
 checks=checks,actualParentRecipeGuardRows=guards,actualParentHelperLiteralGuards=5,actualParentPolicyLiteralGuards=2,
 actualParentHelperPolicyConstantMatches=True,realTinyOwnedCopy077Cases=copy_cases,scratchRemoved=True,
 sourceArithmetic=dict(retained=349,changed=6,new=2,total=357,external=3),publicManifestCount=11,
 sourceDerivedBaseFields=80,newDiagnosticFields=2,proposedRawMetadataFields=82,syntheticCommandRows=69,
 ownCompleteProducer=False,ownCompleteClassifier=False,stageOrBuildOrCompilerOrEngineOrGuestClockInvoked=False,
 nativeHelpersInvoked=False,runtimeAcceptance=False,operationalAdmission=False)
print(json.dumps(result,indent=2))
