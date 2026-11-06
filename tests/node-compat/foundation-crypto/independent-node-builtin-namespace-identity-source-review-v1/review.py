"""Finite independent Source/DATA/pure review, never compiler/helper/fixture/guest."""
from pathlib import Path
import ast,hashlib,json,stat,os,sys,copy
sys.dont_write_bytecode=True
R=Path('/Users/dan/dev/StarlingMonkey');K=R/'tests/node-compat/foundation-crypto';O=K/'node-builtin-namespace-identity-candidate-v1';P=Path(__file__).resolve().parent
checks=0;seen={};ids={}
def yes(v,m='check'):
 global checks
 checks+=1
 assert v,m
def identity(s):return(s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
def desc(p):
 p=Path(p);yes(p.is_absolute()and '..'not in p.parts)
 for x in [p,*p.parents]:yes(not x.is_symlink(),str(x))
 s=p.stat();yes(stat.S_ISREG(s.st_mode));data=p.read_bytes();yes(identity(s)==identity(p.stat()),'stable '+str(p));return dict(path=str(p),sha256=hashlib.sha256(data).hexdigest(),bytes=len(data))
def checked(r):
 p=Path(r['path']);yes(set(r)=={'path','sha256','bytes'})
 if str(p)in seen:yes(seen[str(p)]==r and ids[str(p)]==identity(p.stat()),'same '+str(p))
 else:yes(desc(p)==r,'hash '+str(p));seen[str(p)]=r;ids[str(p)]=identity(p.stat())
 return p
def read(r):return json.loads(checked(r).read_bytes())
ix=dict(path=str(O/'index.json'),sha256='5342a3567e543fa1e2717c9d9263fbd39230b395c879b0fa0877e35871e943e5',bytes=4857);v=read(ix);names={'index.json'}
for r in v['files']:
 name=r['path'];yes(not name.startswith('/')and all(p not in ('','.','..')for p in name.split('/'))and name not in names);names.add(name);checked(dict(r,path=str(O/name)))
yes(names=={p.relative_to(O).as_posix()for p in O.rglob('*')if p.is_file()}and not any(p.is_symlink()for p in O.rglob('*')))
d=read(desc(O/'derivation.json'));before=checked(d['before']).read_bytes();yes(checked(d['liveBefore']).read_bytes()==before);after=checked(d['after']).read_bytes();forward=before
for edit in d['edits']:yes(forward.count(edit['before'].encode())==1);forward=forward.replace(edit['before'].encode(),edit['after'].encode())
yes(forward==after,'whole forward');inverse=after
for edit in reversed(d['edits']):yes(inverse.count(edit['after'].encode())==1);inverse=inverse.replace(edit['after'].encode(),edit['before'].encode())
yes(inverse==before,'whole inverse')
prospective=read(desc(O/'prospective-source-manifest.json'));meta=read(prospective['baseMetadata']);yes(len(meta)==83 and len(meta['sourceManifest'])==357 and len(meta['componentizeSourceManifest'])==3 and len(meta['selectedModuleManifests'])==12)
base=meta['sourceManifest'];future=prospective['manifest'];yes(len(future)==357 and len({r['path']for r in future})==357);yes([r['path']for r in base]==[r['path']for r in future]);changed=[]
SOURCE=Path(d['before']['path']).parents[1]
for a,b in zip(base,future):
 yes(set(a)==set(b)=={'path','sha256'})
 p=SOURCE/a['path'];rr=desc(p);yes(rr['sha256']==a['sha256'],'retained source '+a['path']);checked(rr)
 if a!=b:changed.append(a['path']);yes(b['path']=='runtime/script_loader.cpp'and b['sha256']==d['after']['sha256'])
yes(changed==['runtime/script_loader.cpp']and prospective['retainedNativeFiles']==356 and prospective['changedNativeFiles']==1 and prospective['newNativeFiles']==0)
yes(prospective['externalEmbeddingSources']==meta['componentizeSourceManifest'])
# Stable exact API implementation and registration callers, without evaluating them.
apiFiles=[SOURCE/'runtime/engine.cpp',SOURCE/'runtime/script_loader.h',SOURCE/'include/extension-api.h',SOURCE/'builtins/node-compat/register.cpp']
for p in apiFiles:checked(desc(p))
reg=(SOURCE/'builtins/node-compat/register.cpp').read_text();engine=(SOURCE/'runtime/engine.cpp').read_text();cpp=after.decode()
for bare in ['crypto','buffer','stream']:
 yes('define_builtin_module("node:'+bare+'",'in reg and 'define_builtin_module("'+bare+'",'in reg,'registered '+bare)
yes('Second argument to defineBuiltinModule must be an object'in engine and 'name.ptr.get(), args.get(1)'in engine)
yes('if (!std::string_view(path.get()).starts_with("node:"))'in cpp)
for needle in ['RootedString node_prefix(cx, JS_NewStringCopyZ(cx, "node:"));','RootedString canonical_specifier(cx, JS_ConcatStrings(cx, node_prefix, specifier));','RootedValue canonical_id(cx, StringValue(canonical_specifier));','RootedValue canonical_builtin(cx);','&canonical_builtin.toObject() == builtin_obj.get()','specifier_val.set(canonical_id);','get_builtin_module(cx, specifier_val, builtin_obj)']:
 yes(cpp.count(needle)==1,needle)
for old,new in [('static JSObject *get_builtin_module','bool module_load_hook'),('bool module_metadata_hook','ScriptLoader::ScriptLoader'),('bool ScriptLoader::define_builtin_module','void ScriptLoader::enable_module_mode')]:
 def section(text):return text[text.index(old):text.index(new)]
 yes(section(before.decode())==section(cpp),'unchanged '+old)
yes(cpp.count('if (!node_prefix) {\n        return false;')==1 and cpp.count('if (!canonical_specifier) {\n        return false;')==1)
yes('if (!JS::MapGet(cx, builtinModules, canonical_id, &canonical_builtin)) {\n        return false;'in cpp)
yes(cpp.index('RootedValue specifier_val')<cpp.index('RootedString node_prefix')<cpp.index('specifier_val.set(canonical_id)')<cpp.index('get_builtin_module(cx, specifier_val, builtin_obj)'))
# Actual pinned JSAPI declarations and module hook consistency contract.
headers=Path(meta['enginePath']).parent.parent/'spidermonkey-dist-release/include/js'
# The engine artifact lives below WORK/artifacts; headers are below WORK.
for name in ['String.h','MapAndSet.h','Modules.h','RootingAPI.h']:
 p=headers/name;checked(desc(p))
yes('JSString* JS_ConcatStrings(JSContext* cx,'in(headers/'String.h').read_text());yes('JS::Handle<JSString*> left'in(headers/'String.h').read_text())
yes('HandleValue key, MutableHandleValue rval'in(headers/'MapAndSet.h').read_text())
# Model AST extraction executes only the author's canonical DATA predicate.
modelText=(O/'test-model.py').read_text();tree=ast.parse(modelText);node=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='canonical');scope={};exec(compile(ast.Module(body=[node],type_ignores=[]),str(O/'test-model.py'),'exec'),scope);canonical=scope['canonical']
pure=[]
def case(name,request,mapping,want):yes(canonical(request,mapping)==want,name);pure.append(name)
a={};b={}
for name,request,mapping,want in [('same-object','crypto',{'crypto':a,'node:crypto':a},'node:crypto'),('distinct-equal-objects','crypto',{'crypto':a,'node:crypto':b},'crypto'),('missing-bare','crypto',{'node:crypto':a},'crypto'),('missing-prefixed','crypto',{'crypto':a},'crypto'),('prefix-stays','node:crypto',{'crypto':a,'node:crypto':a},'node:crypto'),('different-prefix-stays','node:crypto',{'node:crypto':a,'node:node:crypto':a},'node:crypto'),('custom-unpaired','custom:key',{'custom:key':a},'custom:key'),('custom-explicit-pair','custom:key',{'custom:key':a,'node:custom:key':a},'node:custom:key'),('Unicode-exact','café',{'café':a,'node:café':a},'node:café'),('NUL-no-truncate','a\0b',{'a\0b':a,'node:a':a},'a\0b'),('NUL-synthetic-pair','a\0b',{'a\0b':a,'node:a\0b':a},'node:a\0b'),('model-primitive','x',{'x':7,'node:x':7},'x')]:case(name,request,mapping,want)
for bare in ['crypto','buffer','stream','path/posix','stream/promises','assert/strict']:
 for order in [(bare,'node:'+bare),('node:'+bare,bare)]:
  modules={};values=[];mapping={bare:a,'node:'+bare:a}
  for request in order:
   key=canonical(request,mapping);modules.setdefault(key,object());values.append(modules[key])
  yes(values[0]is values[1]and len(modules)==1);pure.append('both-order '+str(order))
# Raw two-order fixture sources and observations remain unevaluated.
fixture=read(desc(O/'fixture-plan.json'));bare=(O/'bare-first.mjs').read_text();pref=(O/'prefixed-first.mjs').read_text();yes(bare[bare.index('export function run'):]==pref[pref.index('export function run'):])
yes([x for x in bare.splitlines()if x.startswith('import ')]==["import * as cryptoBare from 'crypto';","import * as cryptoNode from 'node:crypto';","import * as bufferBare from 'buffer';","import * as bufferNode from 'node:buffer';","import * as streamBare from 'stream';","import * as streamNode from 'node:stream';"])
yes([x for x in pref.splitlines()if x.startswith('import ')]==[bare.splitlines()[n]for n in [1,0,3,2,5,4]])
yes(all(x not in bare for x in ['createHash(','createHmac(','new Buffer','digest(','crypto.subtle.']))
yes(fixture['rawNativeImportsRequired']is fixture['bundlingMustNotCanonicalizeBareSpecifiers']is True and fixture['actualFixtureExecuted']is False)
for p in O.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
# Read retained single frontend proof, including its failed outer driver.
sourceResult=read(desc(O/'results.json'));plan=read(sourceResult['syntaxPlan']);copyMap=read(desc(O/'syntax-raw-copy-map.json'))
for r in copyMap['files']:yes(checked(r['original']).read_bytes()==checked(r['copy']).read_bytes())
terminal=read(desc(O/'syntax-evidence/command/terminal.json'));start=read(desc(O/'syntax-evidence/command/started.json'))
yes(terminal['rawExitCode']==0 and terminal['timeout']is terminal['forcedCleanup']is False and terminal['allObservedOwnedGroupsGone']is terminal['parentOwnedGroupGone']is True)
yes(all(terminal[k]==[]for k in ['signals','interruptedSignals','errors','remainingObservedPids']));yes(terminal['stdout']['bytes']==terminal['stderr']['bytes']==0)
yes(start['argv']==plan['argv']and start['timeoutSeconds']==plan['timeoutSeconds']==60)
argv=plan['argv'];yes('-fsyntax-only'in argv and '-c'not in argv and '-o'not in argv and argv[-1]==plan['privateMainInput']['path']);yes(plan['privateMainInput']['sha256']==d['after']['sha256'])
private=checked(plan['privateMainInput']);yes(private.read_bytes()==after);overlay=read(plan['overlay']);yes(len(overlay['roots'])==1)
obs=read(sourceResult['postFailureReadOnlyObservation']);deps=read(sourceResult['actualDependencyEvidence']);yes(obs['compilerOrProcessOrGuestRerun']is False and obs['uniqueActualDependencyFiles']==1041 and len(deps['files'])==1041)
for r in deps['files']:
 checked(r['resolved'])
yes(sourceResult['clangRawExitCode']==0 and sourceResult['originalDriverToolExitCode']==1 and sourceResult['namespaceFixRuntimeObserved']is False)
failure=read(sourceResult['originalDriverFailure']);yes(failure['rawToolDriverExitCode']==1 and failure['clangRawExitCode']==0 and failure['compilerRerun']is False)
# Repeat every observed content/identity and the source closed set.
for r in list(seen.values()):yes(desc(r['path'])==r and identity(Path(r['path']).stat())==ids[r['path']],'final '+r['path'])
yes(names=={p.relative_to(O).as_posix()for p in O.rglob('*')if p.is_file()})
summary=dict(schemaVersion=1,passed=True,checks=checks,authenticatedFiles=len(seen),sourcePayloads=len(names)-1,forwardInverseWholeFileEdits=len(d['edits']),nativeSources=357,retainedNativeFiles=356,changedNativeFiles=1,externalEmbeddingSources=3,actualDependencyRows=1041,independentSyntheticModelCases=len(pure),syntheticCaseNames=pure,sourcePythonAsts=len(list(O.glob('*.py'))),retainedClangRawExitCode=0,retainedOriginalDriverExitCode=1,inertModelAstOnly=True,compilerRerun=False,helperInvoked=False,fixtureImportedOrExecuted=False,engineOrGuestOrCryptoInvoked=False)
(P/'check-results.json').write_text(json.dumps(summary,indent=2)+'\n');(P/'input-hashes.json').write_text(json.dumps(dict(schemaVersion=1,files=sorted(seen.values(),key=lambda x:x['path'])),indent=2)+'\n');print(json.dumps(summary))
