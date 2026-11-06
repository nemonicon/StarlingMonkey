"""Host Source preparation only. Writes only this unsealed family/scratch tests.
Independent reviewers must read retained output or use a separately owned copy.
No native provider/compiler, application, server or target engine action.
"""
from pathlib import Path
import hashlib,json,subprocess,tempfile,shutil,time
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[3]
NODE=Path('/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
FS=REPO/'tests/node-compat/foundation-fs/next-fs-candidate-v2'
M1=REPO/'tests/node-compat/foundation-module/node-module-candidate-v1'
M2=REPO/'tests/node-compat/foundation-module/node-module-candidate-v2'
def desc(p):
 b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def put(n,x):(HERE/n).write_text(json.dumps(x,indent=2)+'\n')
def family(root,pin):
 index=desc(root/'index.json');assert index['sha256']==pin
 rows=json.loads((root/'index.json').read_text())['files']
 for row in rows:
  p=root/row['path'];d=desc(p);assert d['sha256']==row['sha256'] and d['bytes']==row['bytes']
 return index
before=[family(M2,'c69350e3ed12574b2a21b0a5c224d9e16c70c5ec725c3da3b14c1ad860812687'),family(FS,'3ae731760ad061efebdd650ff263a3c5dc405359af722defac22dee0d639ebc9')]
assert desc(NODE)['sha256']=='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'
commands=[]
def run(label,args,cwd=REPO):
 argv=[str(NODE),*map(str,args)];start=time.monotonic();r=subprocess.run(argv,cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=60)
 (HERE/(label+'.stdout.log')).write_bytes(r.stdout);(HERE/(label+'.stderr.log')).write_bytes(r.stderr)
 row=dict(argv=argv,exitCode=r.returncode,elapsedSeconds=time.monotonic()-start,stdout=desc(HERE/(label+'.stdout.log')),stderr=desc(HERE/(label+'.stderr.log')),sourceHostOnly=True)
 put(label+'.terminal.json',row);commands.append(row);assert r.returncode==0,(label,r.stderr.decode())
run('generation',[HERE/'generate-startup-factory.mjs'])
run('generation-check',[HERE/'generate-startup-factory.mjs','--check'])
run('host-tests',[HERE/'test-host.mjs'])
for n in ['startup-core.mjs','test-host.mjs','generate-startup-factory.mjs','bootstrap-entry.template.mjs','validate-manifest.mjs','after/builtins/node-compat/generate-factories.mjs']:
 run('grammar-'+Path(n).name,['--check',HERE/n])
# Test the ACTUAL installed sibling layout; no repository-relative imports.
with tempfile.TemporaryDirectory(prefix='next-startup-installed-',dir='/private/tmp/starling-node-compat') as t:
 root=Path(t)
 for n in ['startup-core.mjs','startup-builtin-inventory.node-v22.14.0.json','generate-startup-factory.mjs','next-startup-factory.generated.h','export-manifest.process.node-v22.14.0.json','export-manifest.os.node-v22.14.0.json','export-manifest.url.node-v22.14.0.json','private-startup-export-manifest.v1.json','validate-manifest.mjs','manifest.schema.json']:shutil.copyfile(HERE/n,root/n)
 run('installed-generator-check',[root/'generate-startup-factory.mjs','--check'],root)
old=(M1/'module-kernel.cpp').read_text();new=(HERE/'after/builtins/node-compat/module-kernel.cpp').read_text()
assert old[old.index('static bool builtin('):]==new[new.index('static bool builtin('):]
for symbol in ['next_fs::stat_path','next_fs::read_bytes','next_fs::realpath','next_fs::cwd','LossyUTF8CharsToNewTwoByteCharsZ']:assert symbol in new
for oldcall in ['fopen(','fread(','getcwd(','::realpath(','stat(path']:assert oldcall not in new
composition=json.loads((HERE/'registration-composition.json').read_text());reg=(HERE/'after/builtins/node-compat/register.cpp').read_text();reverse=reg
for edit in reversed(composition['exactReversibleEdits']):
 at=edit['offsetBeforeEdit'];assert reverse[at:at+len(edit['new'])]==edit['new'];reverse=reverse[:at]+edit['old']+reverse[at+len(edit['new']):]
assert hashlib.sha256(reverse.encode()).hexdigest()==composition['preFSCompositionSha256']
assert composition['fsDonor']['sha256']==desc(FS/'after/builtins/node-compat/register.cpp')['sha256']
cm=(HERE/'after/cmake/builtins.cmake').read_text();fsdelta=(FS/'after/cmake/builtins.cmake').read_text()[len((REPO/'cmake/builtins.cmake').read_text()):].lstrip('\n')
assert fsdelta in cm and 'option(NODE_COMPAT_NEXT_STARTUP' in cm and 'NODE_COMPAT_NEXT_STARTUP "Experimental deployed Node process/os/url startup" OFF' in cm
for n in ['cwd','chdir','read_bytes','stat_path','realpath']:assert 'bool '+n+'(' in (FS/'after/builtins/node-compat/next-fs-native.h').read_text()
# A truthful Source union, not a cast of any built engine/metadata frame.
parent=json.loads((M2/'prospective-source-manifest.json').read_text());rows={x['path']:{**x,'sourceRole':'unchanged Module-v2 prospective manifest DATA'} for x in parent['files']}
for f in sorted((FS/'after').rglob('*')):
 if f.is_file():rows[str(f.relative_to(FS/'after'))]={'path':str(f.relative_to(FS/'after')),'sha256':desc(f)['sha256'],'afterimage':desc(f),'sourceRole':'held FS-v2 Source afterimage'}
for f in sorted((HERE/'after').rglob('*')):
 if f.is_file():rows[str(f.relative_to(HERE/'after'))]={'path':str(f.relative_to(HERE/'after')),'sha256':desc(f)['sha256'],'afterimage':desc(f),'sourceRole':'own composed startup/Module-provider afterimage'}
installed=['startup-core.mjs','startup-builtin-inventory.node-v22.14.0.json','generate-startup-factory.mjs','next-startup-factory.generated.h','export-manifest.process.node-v22.14.0.json','export-manifest.os.node-v22.14.0.json','export-manifest.url.node-v22.14.0.json','private-startup-export-manifest.v1.json','startup.LICENSE.node']
# next-startup.cpp is in after/, the remaining9 are new sibling payloads.
for n in installed:
 f=HERE/n;key='builtins/node-compat/'+n;assert key not in rows;rows[key]={'path':key,'sha256':desc(f)['sha256'],'afterimage':desc(f),'sourceRole':'new startup Source file'}
assert len(rows)==381
parentPaths={x['path'] for x in parent['files']};deltaNew=set(rows)-parentPaths;deltaChanged=[x for x in parent['files'] if x['sha256']!=rows[x['path']]['sha256']]
put('prospective-source-manifest.json',dict(schemaVersion=1,state='UNCOMPILED_COMPOSED_SOURCE_PLAN',nativeSourceFiles=len(rows),sourceArithmetic=dict(moduleV2Parent=len(parentPaths),newFSAndStartupPaths=len(deltaNew),changedParentPaths=len(deltaChanged)),files=[rows[k] for k in sorted(rows)],externalEmbeddingSources=parent['externalEmbeddingSources'],externalEmbeddingChanges=False,actualBuilt=False,actualMetadataSchema=None,qualification='Prospective Module-v2+held FS-v2+startup Source ONLY. No Buffer.concat/util/ALS/HTTP future overlay silently included; no old raw83 metadata projection. New genuine integration/producer/metadata admission remains required.'))
inputs=[NODE,M1/'module-kernel.cpp',M1/'after/builtins/node-compat/register.cpp',M1/'after/cmake/builtins.cmake',M2/'prospective-source-manifest.json',FS/'after/builtins/node-compat/next-fs-native.h',FS/'after/builtins/node-compat/next-fs.cpp',REPO/'runtime/event_loop.h',REPO/'runtime/node_tick_queue.h',REPO/'runtime/node_tick_queue.cpp',REPO/'host-apis/wasi-0.2.10/bindings/bindings.h',REPO/'builtins/node-compat/events.mjs',REPO/'builtins/node-compat/events-add-abort-listener.mjs',REPO/'builtins/node-compat/querystring.mjs',REPO/'tests/node-compat/profile-bundler.mjs',REPO/'tests/node-compat/module-selection.mjs']
put('references.json',dict(schemaVersion=1,parentSourceFamilies=before,currentInputs=[desc(p) for p in inputs],nativeFSAPIAuthor='separate held FS-v2 Source, no frontend/runtime proof',readOnlyRuntimeAPIsInvoked=False,originalHash357Artifact='9aec/raw83 ancestry remains frozen and unchanged; not relabeled successful BUILD',actualNativeBuild=None,actualGuest=None))
assert before==[family(M2,before[0]['sha256']),family(FS,before[1]['sha256'])]
put('source-checks.json',dict(schemaVersion=1,passed=True,hostChecks=json.loads((HERE/'host-tests.json').read_text())['checks'],grammarCommands=6,installedGeneratorLayoutPassed=True,commands=commands,fsRegistrationReversePassed=True,moduleCompileAndBuiltinTailUnchanged=True,prospectiveNativeSourceFiles=381,nativeCompilerInvoked=False,guestExecuted=False,scope='Host Source/pure/factory/generation/grammar checks only; not CPP syntax, ABI, link, WASI imports, native FIFO, provider ownership or runtime proof.'))
print(json.dumps(dict(passed=True,hostChecks=195,grammar=6,nativeSourcePlan=len(rows),newPaths=len(deltaNew),changedParent=len(deltaChanged),nativeCompilerInvoked=False)))
