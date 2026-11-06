"""Independent bounded SOURCE/DATA intake, no operational imports or calls."""
from pathlib import Path
import ast,hashlib,json,os,re,stat,subprocess,time
OWN=Path(__file__).resolve().parent
SOURCE=OWN.parent/'combined-native-component-caller-candidate-v1'
EXPECTED='aec12b5c21995f1f080871be2d8fa77ee5aa20fe884e220dd94db7d6573993f1'
rows={};identities={};families={};checks=0
def need(v,m):
 global checks
 if not v:raise AssertionError(m)
 checks+=1
def digest(path):
 h=hashlib.sha256()
 with path.open('rb')as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
def descriptor(path):return dict(path=str(path),sha256=digest(path),bytes=path.stat().st_size)
def key(s):return(s.st_dev,s.st_ino,s.st_size,s.st_mode,s.st_nlink,s.st_mtime_ns,s.st_ctime_ns)
def checked(r):
 need(type(r)is dict and type(r['path'])is str and Path(r['path']).is_absolute(),'absolute descriptor')
 p=Path(r['path']);s=p.lstat();need(stat.S_ISREG(s.st_mode)and s.st_size==r['bytes'],'regular exact file')
 if str(p)in rows:
  need(rows[str(p)]==r and identities[str(p)]==key(s),'same descriptor/identity');return p
 need(digest(p)==r['sha256']and key(s)==key(p.lstat()),'full stable SHA '+str(p))
 rows[str(p)]=r;identities[str(p)]=key(s);return p
def read(r):return json.loads(checked(r).read_bytes())
def family(ix):
 if ix['path']in families:need(families[ix['path']]==ix,'same family');return
 v=read(ix);root=Path(ix['path']).parent;names={'index.json'}
 for r in v['files']:
  n=r['path'];need(n not in names and n and not n.startswith('/')and all(x not in('','.','..')for x in n.split('/')),'unique member')
  names.add(n);checked(dict(path=str(root/n),sha256=r['sha256'],bytes=r['bytes']))
 paths=list(root.rglob('*'));need(not any(p.is_symlink()for p in paths),'no family symlinks')
 need({p.relative_to(root).as_posix()for p in paths if p.is_file()}==names,'exact whole indexed family')
 families[ix['path']]=ix
ix=descriptor(SOURCE/'index.json');need(ix['sha256']==EXPECTED and ix['bytes']==16238,'sealed owner pin')
family(ix);need(len(read(ix)['files'])==96,'96 owner members')
inputs=json.loads((SOURCE/'source-inputs.json').read_bytes());refs=json.loads((SOURCE/'references.json').read_bytes())
for r in inputs['files']:checked(r)
for r in inputs['families']:family(r)
boundary=[]
for b in inputs['boundaries']:
 value=read(b['manifest']);entries=value[b['field']];need(len(entries)==b['expectedRows'],'finite boundary rows')
 for r in entries:checked(r)
 for r in value.get(b['familyField'],[]):family(r)
 boundary.append({'manifest':b['manifest'],'rows':len(entries)})
package=read(refs['packageInventory'])['package'];base=Path(package['root'])
need(len(package['files'])==4889 and len(package['links'])==21 and stat.S_IMODE(base.stat().st_mode)==0o700,'package4889+21 private')
names=set();links={r['path']:r for r in package['links']}
for r in package['files']:
 checked({k:r[k]for k in ['path','sha256','bytes']});p=Path(r['path']);need(p==base/r['relativePath']and stat.S_IMODE(p.lstat().st_mode)==r['mode']and p.lstat().st_nlink==1,'package file role/mode')
 names.add(r['relativePath'])
found=set()
for p in base.rglob('*'):
 n=p.relative_to(base).as_posix()
 if p.is_symlink():
  r=links[n];need(os.readlink(p)==r['target']and str(p.resolve(strict=True))==r['resolvedPath']and p.resolve(strict=True).is_relative_to(base)and p.resolve(strict=True).relative_to(base).as_posix()in names,'package link')
  found.add(n)
 elif p.is_file():need(n in names,'package membership');found.add(n)
need(found==names|set(links),'whole package membership')
metadata=read(refs['nativeMetadata']);need(len(metadata)==80 and len(metadata['sourceManifest'])==355 and len(metadata['componentizeSourceManifest'])==3 and len(metadata['selectedModuleManifests'])==11,'actual full80/355+3/11 metadata')
bootstrap_proof=read(refs['actualBootstrapReview']['result']);bootstrap=read(bootstrap_proof['bootstrapFrame'])
readonly=read(refs['actualReadOnlyData']);need(readonly['bootstrap']==bootstrap and readonly['sourceIndex']==refs['nativeApiSourceIndex'],'actual retained full bootstrap, original c365 context')
need(readonly['bootstrap']['metadata']==metadata and readonly['currentVerification']['helperInvocations']==0 and readonly['currentVerification']['processesSpawned']==0,'whole unchanged metadata and distinct readonly scope')
for pair,contract_name,state in [(refs['actualBootstrapReview'],'actualBootstrapContract','INDEPENDENT_COMBINED355_NORMAL_OFF_BOOTSTRAP_RESULTS_REVIEW_PASSED_V1'),(refs['actualReadOnlyReview'],'actualReadOnlyContract',refs['actualReadOnlyRequiredState'])]:
 proof=read(pair['result']);contract=read(refs[contract_name]);need(proof['state']==state and proof['verifiedPassed']is True and contract['requiredReviewState']==state,'genuine actual proof states')
 for group in ['requiredFixedValues','requiredExactDescriptors']:
  for k,v in contract.get(group,{}).items():need(proof[k]==v,'contract '+k)
 if 'requiredCoverage'in contract:need(proof['coverage']==contract['requiredCoverage'],'actual proof coverage')
entry=(SOURCE/'entry.mjs').read_text();ext=(SOURCE/'external.py').read_text();bundle=(SOURCE/'bundle.mjs').read_text();construct=(SOURCE/'construct.mjs').read_text();io=(SOURCE/'io.mjs').read_text()
for p in SOURCE.glob('*.py'):ast.parse(p.read_text(),filename=str(p));checks+=1
need("const ORIGINAL='"+str(SOURCE)+"'"in entry and "OWN=REPO/'tests/node-compat/foundation-scheduler/combined-native-component-caller-candidate-v1'"in ext,'genuine own constants')
need(entry.index('const f=await authenticate(configDescriptor,phase)')<entry.index('const api=await import('),'preimport authentication')
need('if(record)await record.recheck();await f.c.recheck();'in entry and "'Caller phase and final protection failed'"in entry,'native/current final/failure rechecks')
need('builtinMap(h.selectedManifests)'in bundle and 'builtinManifests:h.selectedManifests'in bundle,'whole11 native map')
need('selectedManifestsForEngine('not in entry+bundle+construct,'no old native selector')
need('loadExperimentalClockPackage'not in bundle and 'bundleProfile'not in construct,'separate phases')
need('root.guestSourceSha256===root.bundle.sha256' in entry and "for(const k of ['nativeEngine','nativeMetadata','guestSourceSha256','witWorldSha256','worldName','selectedInterfaces','disableFeatures','privateTemporaryRoot'])"in entry,'actual paired Root inputs before load')
need(construct.index('const captured=await writeWhole(')<construct.index('need(component.bytes<='),'full component bytes before own cap')
need('await selected.componentize(source,options)'in construct and "wasiShim:false"in construct,'real selected API and unimported Jco output')
need('noUnavailableBytesClaimed:true'in construct and 'fullOpaqueValueClaim:false'in io,'capture limits honest')
need('primary={present:false}'in bundle and 'primary={present:false}'in construct and 'primaryPresent=false'in entry,'null-safe primary presence')
need('finally:recheck();package_tree('in ext,'outer final and failure protections')
tree=ast.parse(ext);parent=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='parent')
calls=[n for n in ast.walk(parent)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=='monitor'];need(len(calls)==1 and len(calls[0].args)==6,'genuine six-argument monitor')
for p,i in identities.items():need(key(Path(p).lstat())==i,'final current identity')
summary={'schemaVersion':1,'state':'INDEPENDENT_SOURCE_DATA_INTAKE_PASSED','checks':checks,'ownerSourceIndex':ix,'ownerMembers':96,
 'uniqueFullHashFiles':len(rows),'uniqueLogicalBytes':sum(r['bytes']for r in rows.values()),'families':len(families),'boundaryRoles':boundary,
 'privatePackageRegularFiles':4889,'privatePackageLinks':21,'nativeSourceFiles':355,'externalEmbeddingSources':3,'fullMetadataFields':80,'selectedWholeManifests':11,
 'operationalEntryOrApiInvoked':False,'nativeEngineOrGuestInvoked':False,'allIndexedMembershipChecked':True,'inheritedTreesRecopied':False}
(OWN/'intake-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary))
