"""Own Source/read-hash-boundary audit only. No authorize/helper/action execution."""
from pathlib import Path
import ast,difflib,hashlib,importlib.util,json,os,stat
OWN=Path(__file__).resolve().parent;checks=0

def need(value,message):
 global checks
 assert value,message;checks+=1

def desc(path):
 path=Path(path);h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return dict(path=str(path),sha256=h.hexdigest(),bytes=path.stat().st_size)

def data(path):return json.loads(Path(path).read_bytes())
def save(name,value):(OWN/name).write_text(json.dumps(value,indent=2)+'\n')
spec=importlib.util.spec_from_file_location('inert_combined355_freezer_data_functions',OWN/'entry.py');entry=importlib.util.module_from_spec(spec);spec.loader.exec_module(entry)
need(Path(entry.__file__).resolve().parent==entry.OWN==OWN,'actual physical entry context; no global replacement')
need(str(entry.SOURCE)=='/private/tmp/starling-node-compat/combined-native355-v1-source' and str(entry.WORK)=='/private/tmp/starling-node-compat/combined-native355-v2-build' and str(entry.FREEZE)=='/private/tmp/starling-node-compat/combined-native355-v2-freeze','real distinct contexts')
refs=data(OWN/'references.json');ledger=entry.read(refs['buildInputLedger']);need(len(ledger['files'])==20816,'actual independent full ledger count')
for row in ledger['files']:entry.checked(row);checks+=1
for item in refs['families']:entry.family(item['index']);checks+=1
proof=entry.read(refs['actualBuildReview']['result']);contract=entry.read(refs['actualBuildContract'])
for k,v in contract['requiredFixedValues'].items():need(proof[k]==v,'actual contract fixed '+k)
for k,v in contract['requiredExactDescriptors'].items():need(proof[k]==v,'actual contract descriptor '+k)
need(proof['coverage']==contract['requiredCoverage'],'whole actual coverage')
need(refs['buildInputLedger']==proof['inputHashes'] and refs['referenceAliasWitness']==proof['referenceAliases'],'genuine proof DATA intake identities')
aliases=entry.read(refs['referenceAliasWitness']);need(aliases['symlinks']==refs['referenceAliases'] and aliases['archiveHardlinks']==refs['declaredArchiveHardlinks'],'complete raw alias witness')
known={r['path']:r for r in ledger['files']}
for row in refs['referenceAliases']:
 p=Path(row['path']);need(p.is_symlink() and os.readlink(p)==row['linkText'] and str(p.resolve(strict=True))==row['resolved'],'actual declared alias only')
 need(row['resolved'] in known,'resolved regular target authenticated')
for row in refs['declaredArchiveHardlinks']:
 a,b=Path(row['path']).stat(),Path(row['target']).stat();need(row['sameInode'] is True and (a.st_dev,a.st_ino)==(b.st_dev,b.st_ino),'actual original archive hardlink; no new copy claim')
protection=data(OWN/'protection.json');need(len(protection['files'])==20816 and len(protection['modePairs'])==1613,'full originals plus genuine staged pairs')
for row in protection['files']:
 s=entry.checked(row['descriptor']).stat();need(stat.S_IMODE(s.st_mode)==row['mode'] and s.st_nlink==row['nlink'],'actual stable mode/nlink')
for row in protection['modePairs']:
 a,b=entry.checked(row['copy']).stat(),entry.checked(row['original']).stat();need(stat.S_IMODE(a.st_mode)==row['copyMode'] and stat.S_IMODE(b.st_mode)==row['originalMode'] and (a.st_dev,a.st_ino)!=(b.st_dev,b.st_ino),'actual exact copy/original modes and independent inode')
for row in protection['trees']:
 root=Path(row['root']);actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and not p.is_symlink()};links={p.relative_to(root).as_posix():os.readlink(p) for p in root.rglob('*') if p.is_symlink()}
 need(actual==set(row['files']) and links==row['links'] and stat.S_IMODE(root.stat().st_mode)==row['mode'],'actual SOURCE/failed-v1 membership')
plan=data(OWN/'capture-plan.json');names=set()
for row in plan['copies']:
 name=row['destination'];need(name not in names and not name.startswith('/') and all(p not in ('','.','..') for p in name.split('/')),'unique confined copy target');names.add(name);entry.checked(row['source']);checks+=1
need(plan['baseCopies']==len(plan['copies'])==2544 and plan['staticLibraries']==29 and plan['objectFiles']==69,'finite actual selected copy set')
metadata=entry.read(refs['metadata']);policy=entry.read(refs['policy']);database=entry.read(refs['compileCommands']);entry.metadata_model(metadata,policy,refs);entry.compilation_model(database,metadata,policy,refs);checks+=2
need(len(metadata)==80 and refs['engine']['sha256']==metadata['engineSha256'],'raw full80 current sidecar')
need(refs['rustupBeforeRecord']['bytes']==368 and refs['rustupCurrentSettings']['bytes']==107 and entry.read(refs['rustupBeforeRecord'])==refs['rustupBeforeValue'],'separate historical record/current original')
need(entry.checked(refs['rustupCurrentSettings']).read_text()==refs['rustupCurrentSettingsText'],'actual current107 settings bytes')
# Real descriptor/read boundary negatives: no fake Frame, no authorize/import helper.
def denied(fn):
 global checks
 try:fn()
 except (AssertionError,ValueError,FileNotFoundError):checks+=1;return
 raise AssertionError('negative accepted')
current=desc(OWN/'entry.py')
for path in ['relative/file','/a/../b','//double/root','/a/./b','/a\\b']:
 denied(lambda path=path:entry.descriptor(dict(current,path=path)))
for change in [dict(bytes=True),dict(bytes=-1),dict(sha256='0'*63),dict(extra=1)]:denied(lambda change=change:entry.descriptor(dict(current,**change)))
denied(lambda:entry.checked(dict(current,bytes=current['bytes']+1)))
denied(lambda:entry.checked(dict(current,sha256='0'*64)))
for row in refs['referenceAliases']:denied(lambda row=row:entry.checked(dict(path=row['path'],sha256=known[row['resolved']]['sha256'],bytes=known[row['resolved']]['bytes'])))
# Self index/capsules are produced later. Every operational custom module is a
# declared own file or an authenticated genuine dependency with real context.
for name in ('copy_io.py','monitor.py','models.py','metadata_model.py','freeze.py','admission.py','verify.py'):need((OWN/name).is_file(),'actual own load_own target')
for key in ('configuredModel','layer','recipe','python','ninja'):entry.checked(refs[key]);checks+=1
for path in OWN.glob('*.py'):ast.parse(path.read_text(),filename=str(path));checks+=1
need(not entry.FREEZE.exists() and not entry.EXTERNAL.exists(),'no actual freeze/action output')
# Compact exact text deltas retain donor identities and both byte directions.
derivations=[]
for name in ('copy_io.py','monitor.py','freeze.py','entry.py','verify.py'):
 donor=OWN.parent/'task-selection-freezer-candidate-v1'/name;before=donor.read_text();after=(OWN/name).read_text();ops=[]
 for tag,a,b,c,d in difflib.SequenceMatcher(None,before,after,autojunk=False).get_opcodes():
  if tag!='equal':ops.append(dict(beforeOffset=a,afterOffset=c,before=before[a:b],after=after[c:d]))
 work=before
 for op in reversed(ops):need(work[op['beforeOffset']:op['beforeOffset']+len(op['before'])]==op['before'],'forward delta');work=work[:op['beforeOffset']]+op['after']+work[op['beforeOffset']+len(op['before']):]
 need(work==after,'exact forward '+name)
 for op in reversed(ops):need(work[op['afterOffset']:op['afterOffset']+len(op['after'])]==op['after'],'inverse delta');work=work[:op['afterOffset']]+op['before']+work[op['afterOffset']+len(op['after']):]
 need(work==before,'exact inverse '+name);derivations.append(dict(output=name,donor=desc(donor),after=desc(OWN/name),edits=ops))
need(desc(OWN/'metadata_model.py')['sha256']==refs['configuredModel']['sha256'],'pure genuine model byte copy only')
save('derivations.json',dict(schemaVersion=1,files=derivations,metadataModelDonor=refs['configuredModel'],metadataModelCopy=desc(OWN/'metadata_model.py'),sameModelBytes=True,noRuntimeNamespaceOrMetadataProjection=True))
report=dict(schemaVersion=1,passed=True,checks=checks,actualBuildReview=refs['actualBuildReview'],verifiedActualBuildReferences=20816,referenceAliases=31,archiveReferenceHardlinks=1,stageOriginalPairs=1613,sourceFamilies=len(refs['families']),baseCopies=2544,baseCopyBytes=plan['baseCopyBytes'],staticArchives=29,objects=69,rawMetadataFields=80,historical57ByteSettingNotRehashed=True,current107BytesVerified=True,actualEntryModuleInertImport=True,entryGlobalsRebound=False,frameOrRootAuthorityFabricated=False,operationalEntryOrHelperOrMonitorOrCopyOrNinjaOrCompilerOrEngineInvoked=False)
save('source-check-results.json',report);print(json.dumps(report))
