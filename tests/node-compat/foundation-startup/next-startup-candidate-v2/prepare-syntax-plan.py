"""DATA-only dormant plan. Writes this family only; never spawns any process."""
from pathlib import Path
import hashlib,json,shlex,difflib
OWN=Path(__file__).resolve().parent;REPO=OWN.parents[3]
BASE=REPO/'tests/node-compat/async-context/native-als-candidate-v3';TIMER=REPO/'tests/node-compat/foundation-timers/node-timers-candidate-v1';BYTE=REPO/'tests/node-compat/buffer-next-candidate-v1';RNG=REPO/'tests/node-compat/node-crypto-rng-candidate-v1';START=OWN.parent/'next-startup-candidate-v1';FS=REPO/'tests/node-compat/foundation-fs/next-fs-candidate-v3'
def d(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def read(p):return json.loads(Path(p).read_bytes())
def save(n,v):(OWN/n).write_text(json.dumps(v,indent=2)+'\n')
assert not(OWN/'index.json').exists()
base=read(BASE/'sdk-plan.json');meta=read(base['references']['metadata']['path']);db=read(base['references']['compileDatabase']['path']);source_root=Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v1-source');stage=Path('/private/tmp/starling-node-compat/next-startup-v2-sdk-syntax-v1')
# Only the genuine timer virtual addition is applied to corrected ALSV3. This
# never substitutes a namespace, own module constant or stale V2 constructor.
v2=REPO/'tests/node-compat/async-context/native-als-candidate-v2/after/include/extension-api.h';v3=BASE/'after/include/extension-api.h';timer=TIMER/'after/include/extension-api.h';a=v2.read_text();b=timer.read_text();ops=[]
for tag,i,j,k,l in difflib.SequenceMatcher(None,a,b,autojunk=False).get_opcodes():
 if tag=='equal':continue
 assert tag=='insert';left=a[max(0,i-80):i];right=a[i:i+80];assert left and right;needle=left+right;replacement=left+b[k:l]+right
 ops.append(dict(before=needle,after=replacement,inserted=b[k:l]))
joined=v3.read_text()
for op in ops:assert joined.count(op['before'])==1;joined=joined.replace(op['before'],op['after'])
assert 'resource = nullptr' in joined or 'resource=nullptr' in joined
assert 'keeps_event_loop_alive() const' in joined
syntax_header=OWN/'syntax-overlay/include/extension-api.h';syntax_header.parent.mkdir(parents=True,exist_ok=True);syntax_header.write_text(joined)
save('alsv3-timer-header-join.json',dict(schemaVersion=1,alsV2=d(v2),alsV3=d(v3),timerHeader=d(timer),editsOnCorrectedV3=ops,after=d(syntax_header),preservesActualNullableCtorFix=True,vmChangesIncluded=False))
# Afterimage table: start with real held402 Source map construction, no metadata.
rows={r['path']:r for r in read(TIMER/'prospective-source-manifest.json')['files']}
for row in read(BYTE/'derivations.json')['changedExistingFiles']:rows[row['installedPath']]=dict(path=row['installedPath'],afterimage=row['after'])
for row in read(RNG/'integration.json')['overlays']:
 if isinstance(row,dict)and row['installedPath']!='cmake/builtins.cmake':rows[row['installedPath']]=dict(path=row['installedPath'],afterimage=row['after'])
for row in read(BASE/'profile-selection.json')['overlay']:
 # V3's other22 rows are already composed in timer Source. Apply only fixed2.
 if '/native-als-candidate-v3/after/'in row['source']['path']:rows[row['path']]=dict(path=row['path'],afterimage=row['source'])
rows['include/extension-api.h']=dict(path='include/extension-api.h',afterimage=d(syntax_header))
# FSv3 changes packaging four, never replace exact shared native provider CPP.
fs=read(FS/'source-selection.json')if(FS/'source-selection.json').exists()else None
for p in (FS/'after').rglob('*'):
 if p.is_file():
  rel=p.relative_to(FS/'after').as_posix();rows[rel]=dict(path=rel,afterimage=d(p))
# Source path roles explicitly used by startup factory generation.
for name in ['startup-core.mjs','next-startup-factory.generated.h','export-manifest.process.node-v22.14.0.json','export-manifest.os.node-v22.14.0.json','export-manifest.url.node-v22.14.0.json','private-startup-export-manifest.v1.json']:
 rows['builtins/node-compat/'+name]=dict(path='builtins/node-compat/'+name,afterimage=d(OWN/name))
for p in (OWN/'after').rglob('*'):
 if p.is_file():
  rel=p.relative_to(OWN/'after').as_posix();rows[rel]=dict(path=rel,afterimage=d(p))
# All VFS redirections have an actual regular source file. Root must copy them
# to private real files before the frontend, particularly new main CPP inputs.
copies=[]
for rel,row in sorted(rows.items()):
 if 'afterimage' not in row:continue
 desc=row['afterimage'];assert d(desc['path'])==desc
 copies.append(dict(relativePath=rel,source=desc,privatePath=str(stage/'source'/rel),logicalPath=str(source_root/rel)))
# Packaging CMake may sit outside original native row inventory; count it honestly.
public_schema_paths={'cmake/builtins.cmake'}
native_rows={k:v for k,v in rows.items()if k not in public_schema_paths}
# Authentic raw commands; do not guess a new kernel's historical compilation.
reg=next(r for r in db if r['file']==str(source_root/'builtins/node-compat/register.cpp'))
unit_specs=[('buffer','builtins/node-compat/buffer.cpp',None),('module-p2','builtins/node-compat/module-kernel.cpp','register'),('startup','builtins/node-compat/next-startup.cpp','register'),('rng','builtins/node-compat/crypto-rng.cpp','register'),('registration','builtins/node-compat/register.cpp',None),('performance','builtins/web/performance.cpp',None)]
common=['NODE_COMPAT_MODULE','NODE_COMPAT_ASYNC_LOCAL_STORAGE','NODE_COMPAT_TIMERS','NODE_COMPAT_NEXT_PERFORMANCE','NODE_COMPAT_ENTROPY_RUNTIME_ONLY'];node=['NODE_COMPAT_FS','NODE_COMPAT_NEXT_STARTUP','NODE_COMPAT_CRYPTO_RANDOM'];units=[]
for uid,rel,donor in unit_specs:
 original=reg if donor else next(r for r in db if r['file']==str(source_root/rel))
 argv=shlex.split(original['command']);wrapper=argv.pop(0);assert d(wrapper)==base['references']['compilerWrapper'];kept=[];removed=[];i=0
 while i<len(argv):
  x=argv[i]
  if x in ['-o','-MF','-MT','-MQ','-MJ']:
   removed+=argv[i:i+2];i+=2;continue
  if x in ['-c','-MD','-MMD','-MP','-MG']or x==original['file']:
   removed.append(x);i+=1;continue
  if x.startswith(('-MF','-MT','-MQ','-MJ','-fprofile-instr-generate','-ftime-trace')):removed.append(x);i+=1;continue
  kept.append(x);i+=1
 added=['-D'+n+'=1'for n in common+(node if rel.startswith('builtins/node-compat/')else [])if not any(x.startswith('-D'+n+'=')for x in kept)]
 include_dirs=[str(source_root),str(source_root/'builtins/node-compat'),str(source_root/'builtins/web')]
 for dirname in include_dirs:
  if '-I'+dirname not in kept:added.append('-I'+dirname)
 # Resolve compiler's clang++ basename from its same pinned SDK, retaining the
 # C++ driver mode. Leaf identity/symlink witnesses are inherited descriptors.
 clang=Path(base['references']['compilerLeaf']['path']).parent/'clang++';assert clang.resolve()==Path(base['references']['compilerLeaf']['path'])
 output=stage/'commands'/uid
 command=[str(clang),*kept,*added,'-ivfsoverlay',str(stage/'overlay.json'),'-fsyntax-only','-MD','-MF',str(output)+'.d','-MT',uid,'-x','c++',str(stage/'source'/rel)]
 assert '-c'not in command and '-o'not in command;assert command[command.index('-MF')+1].startswith(str(stage)+'/commands/')
 units.append(dict(id=uid,relativePath=rel,actualCompileRow=original,prospectiveNewUnit=bool(donor),commandDonor='actual registration target flags'if donor else'exact actual unit flags',source=rows[rel]['afterimage'],privateMainPath=str(stage/'source'/rel),argv=command,removedOutputAndDependencyArguments=removed,addedRequestedSyntaxDefinitionsAndIncludes=added,requiresRealMainFile=True,stdout=str(output)+'.stdout',stderr=str(output)+'.stderr',terminal=str(output)+'.terminal.json',timeoutSeconds=120))
# Exact absent inherited -I spellings are declared, not created or silently fixed.
absent=[]
for u in units:
 for x in u['argv']:
  if x.startswith('-I')and not Path(x[2:]).exists()and x[2:]not in absent:absent.append(x[2:])
refs={k:v for k,v in base['references'].items()if k in ['compileDatabase','metadata','engine','inputLedger','aliasInventory','compilerLeaf','compilerWrapper','monitorIndex','python','processObserver']}
refs.update(alsV3Index=d(BASE/'index.json'),timerIndex=d(TIMER/'index.json'),byteIndex=d(BYTE/'index.json'),rngIndex=d(RNG/'index.json'),fsV3Index=d(FS/'index.json'))
save('sdk-syntax-plan.json',dict(schemaVersion=1,state='DORMANT_NEXT_BYTE_STARTUP_RNG_PERFORMANCE_SDK_FRONTEND_PLAN_V1',references=refs,baseRawMetadataFields=83,baseRawMetadataIsNewProfile=False,privateRoot=str(stage),sourceCopies=copies,units=units,rootAuthority=None,sourceReview=None,compilerAuthorization=None,actualOutputs=None,compilerExecuted=False,actionAllowed=False,macroMode='Prospective syntax-only requested definitions; not observed CMake/build metadata',observedAbsentInheritedIncludeDirectories=absent,overlayTemplate=dict(version=0,**{'case-sensitive':'true','use-external-names':False},roots=[dict(type='file',name=c['logicalPath'],**{'external-contents':c['privatePath']})for c in copies]),monitor=dict(api='original0af monitor(argv,cwd,env,output,timeout,authorityDescriptor)',perChildTimeoutSeconds=120,outerTimeoutSeconds=1800),requiredBeforeAndFinal=['authenticate exact compiler leaf/wrapper/symlink chain/SDK distributions and real headers using inherited ledger+aliases','authenticate complete selected Source families before any imported owner helper; no helper needed','copy each source into fresh owned regular private file, explicitfchmod/fsync; no hardlinks/original writes','full original input ledger/alias/tree bookends before/final, raw83 bytes preserved as ancestry','record complete raw stdout/stderr and original terminal including cleanup before assertions'],limits=['frontend syntax only; no object/link/build/engine/guest/crypto/clock calls','new private main files must physically exist, VFS alone does not satisfy clang driver existence checks','private .d depfiles only; no original -o/-c/dependency writes; no newcache/compiler launcher/global env mutation','VM Source is not included; Root must compose any later exact VM delta before whole-profile build','this is not a fresh native producer/classifier/admission/metadata or an execution grant']))
# Compact exact performance transformations, composable without overwriting V3.
local=[]
filemap={'builtins/web/performance.cpp':REPO/'builtins/web/performance.cpp','builtins/web/performance.h':REPO/'builtins/web/performance.h','builtins/node-compat/next-startup.cpp':START/'after/builtins/node-compat/next-startup.cpp','cmake/builtins.cmake':RNG/'after/cmake/builtins.cmake','builtins/node-compat/startup-core.mjs':START/'startup-core.mjs'}
for rel,before in filemap.items():
 after=OWN/'startup-core.mjs'if rel.endswith('startup-core.mjs')else OWN/'after'/rel
 old=before.read_text();new=after.read_text();edits=[]
 for tag,i,j,k,l in difflib.SequenceMatcher(None,old,new,autojunk=False).get_opcodes():
  if tag=='equal':continue
  edits.append(dict(offset=i,old=old[i:j],new=new[k:l]))
 s=old
 for e in reversed(edits):assert s[e['offset']:e['offset']+len(e['old'])]==e['old'];s=s[:e['offset']]+e['new']+s[e['offset']+len(e['old']):]
 assert s==new
 local.append(dict(path=rel,before=d(before),after=d(after),edits=edits))
save('localized-edits.json',dict(schemaVersion=1,scope='Own exact performance/startup v2 transformations; Source text/data only',files=local,alsV3TimerHeaderJoin=d(OWN/'alsv3-timer-header-join.json'),oldSourceAndBaseEngineUnchanged=True,newNativePaths=[],newFlag='NODE_COMPAT_NEXT_PERFORMANCE',defaultFlag=False,syntaxPlan=d(OWN/'sdk-syntax-plan.json')))
print('PASS dormant six-unit SDK plan and exact own localized transformations; compiler not invoked')
