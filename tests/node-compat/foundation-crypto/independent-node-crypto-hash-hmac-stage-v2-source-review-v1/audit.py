"""Independent Source/read/hash/AST only. No Git/authorize/stage/helper calls."""
from pathlib import Path
import hashlib,json,stat,ast,configparser
P=Path(__file__).resolve().parent;S=P.parent/'node-crypto-hash-hmac-stage-candidate-v2'
PIN=dict(path=str(S/'index.json'),sha256='ed0a32411eb33c5a1ab56ba96d27123fa3e83c31e962ebe81fbcaf066b1b4fbe',bytes=5028)
checks=0;files={};families={}
def need(v,m):
 global checks
 assert v,m;checks+=1

def checked(d):
 p=Path(d['path']);actual=p
 if str(p).startswith('/tmp/'):
  need(Path('/tmp').is_symlink()and Path('/tmp').resolve()==Path('/private/tmp'),'declared system tmp alias');actual=Path('/private'+str(p))
 a=actual.lstat();need(stat.S_ISREG(a.st_mode)and a.st_size==d['bytes'],'regular pinned file '+str(p));h=hashlib.sha256()
 with actual.open('rb')as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 z=actual.lstat();need((a.st_dev,a.st_ino,a.st_mode,a.st_nlink,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_mode,z.st_nlink,z.st_size,z.st_mtime_ns,z.st_ctime_ns)and h.hexdigest()==d['sha256'],'stable hash '+str(p));files[d['path']]=d;return actual

def read(d):return json.loads(checked(d).read_bytes())
def family(d):
 v=read(d);base=Path(d['path']).parent;names={'index.json'};rows=[d]
 for r in v['files']:
  n=r['path'];need(n not in names and n and not n.startswith('/')and '\\'not in n and all(q not in('','.','..')for q in n.split('/')),'unique family path');names.add(n);x=dict(r,path=str(base/n));checked(x);rows.append(x)
 need(not any(f.is_symlink()for f in base.rglob('*'))and{f.relative_to(base).as_posix()for f in base.rglob('*')if f.is_file()}==names,'exact family membership');families[d['path']]=d;return rows

def descriptor(p):
 b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
rows=family(PIN);need(len(rows)==33,'32 source members plus index');refs=json.loads((S/'references.json').read_text());inputs=json.loads((S/'input-hashes.json').read_text());need(len(inputs['files'])==2779 and len(inputs['families'])==13,'declared complete current intake')
for d in inputs['files']:checked(d)
for d in inputs['families']:family(d)
source_rows=family(refs['integrationIndex']);need(len(source_rows)==58,'whole7c5a family');integration=Path(refs['integrationIndex']['path']).parent;native=json.loads((integration/'native-origins.json').read_text())['files'];tools=json.loads((integration/'tool-origins.json').read_text())['files'];embedding=json.loads((integration/'embedding-origins.json').read_text())['files'];need((len(native),len(tools),len(embedding))==(357,1227,3),'genuine357+1227+3 original rows');declared=json.loads((integration/'input-hashes.json').read_text());need(len(declared['files'])==2622,'integration declared current inputs')
for d in declared['files']:checked(d)
plan=json.loads((S/'stage-copy-plan.json').read_text());expected={}
for d in native+tools:
 origin=checked(dict(path=d['original'],sha256=d['sha256'],bytes=d['bytes']));n=d['path'];need(n not in expected,'base plan unique');expected[n]=dict(path=n,original=d['original'],sha256=d['sha256'],bytes=d['bytes'],sourceMode=stat.S_IMODE(origin.stat().st_mode),targetMode=0o600,roles=sorted([d.get('role','GENUINE_DONOR_TOOL_DATA'),'EXACT_7C5A_STAGE_PLAN_ROW']))
for d in source_rows:
 origin=checked(d);n=origin.relative_to(Path('/Users/dan/dev/StarlingMonkey')).as_posix();need(n not in expected,'genuine sealed family no overlap');expected[n]=dict(path=n,original=d['path'],sha256=d['sha256'],bytes=d['bytes'],sourceMode=stat.S_IMODE(origin.stat().st_mode),targetMode=0o600,roles=['SEALED_7C5A_FAMILY_STAGED_DATA_ACTIVE_PRODUCER_REMAINS_ORIGINAL'])
need(len(expected)==1642 and plan['files']==[expected[n]for n in sorted(expected)],'entire1642 exact original/mode/role union');expected_embedding=[]
for d in embedding:
 f=checked(dict(path=d['original'],sha256=d['sha256'],bytes=d['bytes']));expected_embedding.append(dict(d,sourceMode=stat.S_IMODE(f.stat().st_mode),targetMode=0o600))
need(plan['embeddingData']==expected_embedding,'separate3 exact embedding DATA, not configured copy role')
# Reverse all27 actual whole-controller transformations, then replay forwards.
derivation=json.loads((S/'v2-derivation.json').read_text());checked(derivation['donorIndex']);before=checked(derivation['donorController']).read_text();after=checked(derivation['outputController']).read_text();need(len(derivation['edits'])==27,'27 exact Source substitutions');forward=before
for e in derivation['edits']:
 need(forward.count(e['before'])==e['count'],'forward exact occurrence count');forward=forward.replace(e['before'],e['after'])
need(forward==after,'whole forward controller equals actual afterimage');reverse=after
for e in reversed(derivation['edits']):
 for offset in reversed(e['afterPositions']):
  need(reverse[offset:offset+len(e['after'])]==e['after'],'inverse exact positioned span');reverse=reverse[:offset]+e['before']+reverse[offset+len(e['after']):]
need(reverse==before,'whole reverse controller equals authentic2395 donor')
# Verify actual original Git-config role without exposing values or invoking Git.
history=json.loads((S/'history-and-git-isolation-evidence.json').read_text());config=checked(history['originalRepositoryConfig']);c=configparser.RawConfigParser();c.read_string(config.read_text());keys=[dict(section='['+section+']',key=key)for section in c.sections()for key in c[section]];need(keys==history['configurationKeysOnly'],'actual config key names exactly evidence');need(not any(k['key'].startswith(('include','uploadpack.','filter.'))for k in keys),'no current executable/include config family in pinned keys')
recipe=checked(history['recipe']).read_text();need("['git', 'diff', '--binary', 'HEAD']"in recipe and "command('git', 'rev-parse', 'HEAD')"in recipe,'actual named producer provenance Git uses');need('export SPIDERMONKEY_BINARIES='in recipe,'real prebuilt SpiderMonkey source branch')
for row in history['projectMatches']:
 text=checked(row['original']).read_text().splitlines();need(text[row['line']-1]==row['text'],'actual project Git source match')
external=checked(history['externalCMake']).read_text();need('git 'not in external.lower()and history['externalCMakeGitQueries']==[],'actual unchanged external CMake no Git query');need(history['rootProvenanceGitOperations']==['diff --binary HEAD','rev-parse HEAD']and history['rootRepositoryHistoryRequiredByInspectedCode']is False,'bounded named history evidence')
for f in S.glob('*.py'):ast.parse(f.read_text(),filename=str(f));checks+=1
root=json.loads((S/'root-authority.template.json').read_text());need(root['stageControllerIndex']is root['stageControllerReview']is None and root['sourceStageAllowed']is False,'Root/peer/action unissued')
# No sealed self-writing source check is executed by this reviewer.
need("(OWN/'pure-check-results.json').write_text"in(S/'test-pure.py').read_text(),'self-writing owner check identified and not rerun')
summary=dict(schemaVersion=1,state='INDEPENDENT_STAGE_V2_SOURCE_AUTHENTICATION_PASSED',sourceIndex=PIN,checks=checks,currentUniqueInputFiles=len(files),families=len(families),ownerIndexedFiles=32,ownerActualFiles=33,nativeSourceFiles=357,retainedParentNativeFiles=353,changedParentNativeFiles=2,newNativeFiles=2,toolSourceFiles=1227,integrationFamilyRows=58,sourceCopies=1642,embeddingDataCopies=3,exactControllerEdits=27,sourceConfigKeysOnly=keys,gitOrAuthorizeOrStageOrHelperInvoked=False,ownerSelfWritingTestsInvoked=False)
(P/'source-authentication.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items()if k!='sourceConfigKeysOnly'}))
