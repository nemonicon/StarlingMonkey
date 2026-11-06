"""Read/hash/parse only. The separately recorded Ninja deps query already ran.
No compiler, configure, process launch, helper or native engine call here.
"""
from pathlib import Path
import gzip,hashlib,json,os,re,shlex
HERE=Path(__file__).resolve().parent
SOURCE=Path('/private/tmp/starling-node-compat/next-native-profile-v4/source')
WORK=Path('/private/tmp/starling-node-compat/next-native-build-v3')
DONOR=Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v1-source')
def desc(path):
 p=Path(path);h=hashlib.sha256();n=0
 with p.open('rb')as f:
  for block in iter(lambda:f.read(4*1024**2),b''):h.update(block);n+=len(block)
 return dict(path=str(p.resolve()),sha256=h.hexdigest(),bytes=n)
def save(name,value):(HERE/name).write_text(json.dumps(value,indent=2)+'\n')
amend=json.loads((HERE/'source-amendment.json').read_bytes());ledgerrow=amend['reviewedLedger']['descriptor'];assert desc(ledgerrow['path'])==ledgerrow
ledger={x['path']:x for x in json.loads(Path(ledgerrow['path']).read_bytes())['files']}
query=json.loads((HERE/'query-terminal.json').read_bytes());capture=query['stdout'];assert desc(capture['retained']['path'])==capture['retained']
data=gzip.decompress(Path(capture['retained']['path']).read_bytes());assert len(data)==capture['decodedBytes']and hashlib.sha256(data).hexdigest()==capture['decodedSha256']
deps=sorted({x.strip()for x in data.decode().splitlines()if x.startswith('    ')})
for path in deps:assert desc(path)==ledger[path],path
old_project=[]
for path in deps:
 p=Path(path)
 if p.is_relative_to(DONOR):
  rel=p.relative_to(DONOR).as_posix();old_project.append(dict(relativePath=rel,donor=ledger[path],presentCurrent=(SOURCE/rel).is_file()))
missing=sorted(x['relativePath']for x in old_project if not x['presentCurrent'])
additions={x['path']:x for x in amend['nativeInputAdditions']};assert missing==sorted(additions)
for rel,row in additions.items():assert row['source']==ledger[str(DONOR/rel)]and desc(row['afterimage']['path'])==row['afterimage']
composition=json.loads((SOURCE.parent/'composition.json').read_bytes());assert len(composition['files'])==composition['nativeSourceFiles']==432
for row in composition['files']:
 actual=desc(SOURCE/row['path']);assert actual['sha256']==row['sha256']and actual['bytes']==row['bytes']
db=json.loads((WORK/'build/compile_commands.json').read_bytes());assert len(db)==80
sdk=next((WORK/'extracted-wasi-sdk').iterdir());system=[sdk/'share/wasi-sysroot/include/wasm32-wasi/c++/v1',sdk/'share/wasi-sysroot/include/wasm32-wasi',sdk/'share/wasi-sysroot/include',sdk/'lib/clang/21/include'];assert all(p.is_dir()for p in system)
pattern=re.compile(r'^\s*#\s*include\s*(["<])([^">]+)[">]',re.M)
def normal(p):return Path(os.path.normpath(str(p)))
def virtual(p):
 p=normal(p)
 if p.is_relative_to(WORK/'native-source'):return SOURCE/p.relative_to(WORK/'native-source')
 return p
def physical(p):
 if p.is_file():return p
 if p.is_relative_to(SOURCE)and p.relative_to(SOURCE).as_posix()in additions:return DONOR/p.relative_to(SOURCE)
 return None
def traverse(proposed_include=False):
 edges={};unknown={};visited=set()
 for row in db:
  argv=shlex.split(row['command']);includes=[]
  for i,token in enumerate(argv):
   value=argv[i+1]if token in ['-I','-isystem','-iquote']else(token[2:]if token.startswith('-I')else None)
   if value:includes.append(virtual(Path(value)if Path(value).is_absolute()else Path(row['directory'])/value))
  if proposed_include and row['file'].endswith('/builtins/web/performance.cpp'):includes.append(SOURCE)
  todo=[virtual(Path(row['file']))];seen=set()
  while todo:
   path=todo.pop()
   if path in seen:continue
   seen.add(path);p=physical(path)
   if p is None or not path.is_relative_to(SOURCE):continue
   visited.add(str(path));text=p.read_text()
   for match in pattern.finditer(text):
    name=match.group(2);line=text.count('\n',0,match.start())+1
    found=None
    for directory in ([path.parent]if match.group(1)=='"'else[])+includes+system:
     candidate=normal(directory/name)
     if physical(candidate)is not None:found=candidate;break
    key=(str(path),line,name)
    if found is None:
     unknown[key]=dict(source=str(path),line=line,include=name,kind='quoted'if match.group(1)=='"'else'angle');continue
    if found.is_relative_to(SOURCE):
     rel=found.relative_to(SOURCE).as_posix();entry=edges.setdefault(key,dict(source=str(path),line=line,include=name,resolvedProjectPath=rel,missingCurrentSelection=not found.is_file(),translationUnits=[]))
     if row['file']not in entry['translationUnits']:entry['translationUnits'].append(row['file'])
     todo.append(found)
 return dict(projectFilesVisited=len(visited),projectEdges=list(edges.values()),unresolvedLiteralIncludes=list(unknown.values()))
before=traverse();after=traverse(True)
direct=[]
for p in sorted(SOURCE.rglob('*')):
 if p.is_file()and p.suffix in ['.cpp','.c','.h','.hpp','.inc','.incl']:
  text=p.read_text()
  for m in re.finditer(r'^\s*#\s*include\s*"([^\"]+)"',text,re.M):direct.append(dict(source=p.relative_to(SOURCE).as_posix(),line=text.count('\n',0,m.start())+1,include=m.group(1)))
assert len(direct)==661
perf=[x for x in before['unresolvedLiteralIncludes']if x['include']=='host-apis/wasi-0.2.10/bindings/bindings.h'];assert perf and not any(x['include']==perf[0]['include']for x in after['unresolvedLiteralIncludes'])
assert all(x['include']=='memory-reporting.h'for x in after['unresolvedLiteralIncludes']),after['unresolvedLiteralIncludes']
assert not any('-DMEM_STATS'in x['command']for x in db)
save('quoted-include-audit.json',dict(schemaVersion=1,actualCompileDatabase=desc(WORK/'build/compile_commands.json'),compileRows=80,directSelectedQuotedIncludes=direct,beforeProposedPerformanceInclude=before,afterProposedPerformanceInclude=after,unresolvedConditionalPolicy='memory-reporting.h is behind MEM_STATS; all80 actual commands omit MEM_STATS. Literal scan is conservative across preprocessor branches.',explicitSdkImplicitDirectories=[str(x)for x in system],compilerInvoked=False,preprocessorSuccessClaim=False))
save('closure-results.json',dict(schemaVersion=1,state='NEXT_NATIVE_COMPILED_HEADER_CLOSURE_SOURCE_AUDIT_PASSED',oldActualUniqueNinjaDependencies=len(deps),allAuthenticatedAgainstReviewedLedger=True,reviewedLedger=ledgerrow,oldProjectDependencies=len(old_project),oldProjectRows=old_project,missingNativeInputs=missing,currentSourceFilesAuthenticated=432,prospectiveNativeFiles=435,embeddingUnchanged=3,actualCompileRows=80,allSelectedQuotedIncludes=661,knownUnselectedConditionalHeader='memory-reporting.h/MEM_STATS',additionalCmakeIncludeCorrectionRequired=True,sourceAmendment=desc(HERE/'source-amendment.json'),quotedIncludeAudit=desc(HERE/'quoted-include-audit.json'),oldActualNinjaQuery=desc(HERE/'query-terminal.json'),compilerOrConfigureBuildInvoked=False,engineOrGuestExecuted=False,fullNextBuildSuccessClaim=False))
print(json.dumps(dict(passed=True,oldActualDependencies=len(deps),oldProjectDependencies=len(old_project),missing=missing,prospectiveNativeFiles=435,compileRows=80,allSelectedQuotedIncludes=661,afterUnresolved=after['unresolvedLiteralIncludes'],dataOnly=True)))
