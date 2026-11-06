"""Read/hash retained .d data only; never launches compiler or changes old results."""
from pathlib import Path
import hashlib,json,os,shlex
OWN=Path(__file__).resolve().parent;ROOT=Path('/private/tmp/starling-node-compat/next-startup-v2-sdk-syntax-v1');PLAN=OWN.parent/'next-startup-candidate-v2/sdk-syntax-plan.json'
def d(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def read(p):return json.loads(Path(p).read_bytes())
plan=read(PLAN);original=read(ROOT/'result.json');ledger=read(plan['references']['inputLedger']['path']);aliases=read(plan['references']['aliasInventory']['path']);a={r['path']:r for r in aliases['symlinks']};expected={r['path']:r for r in ledger['files']};virtual={os.path.normpath(r['logicalPath']):r['privatePath']for r in plan['sourceCopies']};private={r['privatePath']:r['source']for r in plan['sourceCopies']};before={};observed={};cases=[]
# Verify each dot/dotdot traversal before normalizing. All encountered aliases
# require exact existing witnesses; normalization never invents a file identity.
def resolve_known(raw):
 p=Path(raw);assert p.is_absolute();current=Path('/')
 for name in p.parts[1:]:
  if name=='.':continue
  if name=='..':assert current.is_dir()and not current.is_symlink();current=current.parent;continue
  current=current/name
  if current.is_symlink():
   row=a.get(str(current));assert row is not None,(str(current),'unknown alias');assert os.readlink(current)==row['linkText']and str(current.resolve())==row['resolved'];current=Path(row['resolved'])
 return current
for p in [PLAN,ROOT/'result.json',ROOT/'overlay.json']+[ROOT/'commands'/u['id']/'terminal.json'for u in plan['units']]+[ROOT/'commands'/(u['id']+'.d')for u in plan['units']if(ROOT/'commands'/(u['id']+'.d')).exists()]:before[str(p)]=d(p)
for u in plan['units']:
 term=read(ROOT/'commands'/u['id']/'terminal.json');dep=ROOT/'commands'/(u['id']+'.d');rows=[];errors=[]
 if dep.exists():
  text=dep.read_text().replace('\\\n','').replace('\\\r\n','');target,sep,tail=text.partition(':');assert sep and target.strip()==u['id'];names=shlex.split(tail,comments=False,posix=True)
  for name in names:
   raw=Path(name)if Path(name).is_absolute()else Path(u['actualCompileRow']['directory'])/name
   try:
    lexical=os.path.normpath(str(raw))
    if lexical in virtual:p=Path(virtual[lexical]);kind='actual VFS redirected Source'
    else:p=resolve_known(raw);kind='protected physical original'
    if str(p)in private:reference=private[str(p)];kind='actual private Source copy'
    else:reference=expected.get(str(p));assert reference is not None,('not in protected ledger',str(p))
    actual=observed.get(str(p))or d(p);observed[str(p)]=actual;assert actual['sha256']==reference['sha256']and actual['bytes']==reference['bytes']
    rows.append(dict(logical=str(raw),physical=actual,role=kind))
   except BaseException as e:errors.append(dict(logical=str(raw),error=repr(e)))
 cases.append(dict(id=u['id'],rawExitCode=term['rawExitCode'],cleanupGone=term['parentOwnedGroupGone']and term['allObservedOwnedGroupsGone'],originalMonitorTerminal=d(ROOT/'commands'/u['id']/'terminal.json'),rawStderr=d(ROOT/'commands'/u['id']/'stderr.log'),depfile=d(dep)if dep.exists()else None,dependencyCount=len(rows),dependencies=rows,errors=errors,sourceCppParsedSuccessfully=term['rawExitCode']==0))
assert before=={p:d(p)for p in before}
report=dict(schemaVersion=1,state='RETAINED_NEXT_SDK_DEPENDENCY_DATA_RECONCILIATION_V1',readOnly=True,originalResult=d(ROOT/'result.json'),originalResultRemainsFailedUnaccepted=True,originalDriverDependencyReaderBug='Valid clang .d bin/../ and private/../ spellings were refused by a strict no-dotdot regular-file helper; no compiler diagnostic was altered',units=cases,uniqueDependencyFilesRehashed=len(observed),allRetainedDependencyPathsAuthenticated=not any(r['errors']for r in cases),originalFilesUnchanged=True,compilerOrGuestOrEngineInvoked=False,originalSourceAndPrivateCopiesProtection=original['finalProtection'],privateCopiesUnchanged=original['privateCopiesUnchanged'],originalInputPlanDefects=['module/startup fell through to old9aec ScriptLoader header without registered builtin lookup declaration','registration lacked actual Module factory generated header; intended Source files were absent from68-copy plan'])
p=OWN/'dependency-reconciliation.json';p.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(report=d(p),allDependenciesAuthenticated=report['allRetainedDependencyPathsAuthenticated'],unique=report['uniqueDependencyFilesRehashed'],units=[dict(id=r['id'],rawExitCode=r['rawExitCode'],dependencies=r['dependencyCount'],errors=len(r['errors']))for r in cases])))
