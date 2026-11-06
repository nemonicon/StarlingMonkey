"""Finite Source/read/hash/AST checker. No owner/API/toolchain import or actions."""
from pathlib import Path
import ast,hashlib,json,os,re,stat
P=Path(__file__).resolve().parent;checks=0;files={};identities={};families={}
def need(v,label):
 global checks
 checks+=1;assert v,label
def row(r):
 p=Path(r['path']);s=p.lstat();identity=(s.st_dev,s.st_ino,s.st_size,s.st_mode,s.st_nlink,s.st_mtime_ns,s.st_ctime_ns);need(stat.S_ISREG(s.st_mode)and s.st_size==r['bytes'],'ordinary exact file')
 if r['path']in files:need(files[r['path']]==r and identities[r['path']]==identity,'same declared descriptor/identity');return
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 z=p.lstat();need(identity==(z.st_dev,z.st_ino,z.st_size,z.st_mode,z.st_nlink,z.st_mtime_ns,z.st_ctime_ns)and h.hexdigest()==r['sha256'],'complete stable source/input hash');files[r['path']]=r;identities[r['path']]=identity
def read(r):row(r);return json.loads(Path(r['path']).read_bytes())
def exact(root,names):
 need(not any(x.is_symlink()for x in root.rglob('*')),'no indexed family aliases');need({x.relative_to(root).as_posix()for x in root.rglob('*')if x.is_file()}==names,'complete indexed family')
def family(ix):
 if ix['path']in families:need(families[ix['path']]==ix,'same family pin');return
 v=read(ix);root=Path(ix['path']).parent;names={'index.json'}
 for r in v['files']:
  n=r['path'];need(n not in names and n and not n.startswith('/')and all(x not in('','.','..')for x in n.split('/')),'unique relative member');names.add(n);row(dict(path=str(root/n),sha256=r['sha256'],bytes=r['bytes']))
 exact(root,names);families[ix['path']]=ix
refs=json.loads((P/'references.json').read_bytes());inputs=json.loads((P/'source-inputs.json').read_bytes());closure=json.loads((P/'source-closure.json').read_bytes())
for x in inputs['files']:row(x)
for x in inputs['families']:family(x)
for b in inputs['boundaries']:
 v=read(b['manifest']);need(len(v[b['field']])==b['expectedRows'],'actual finite boundary count')
 for r in v[b['field']]:row(r)
 for ix in v.get(b['familyField'],[]):family(ix)
inventory=read(refs['packageInventory'])['package'];need(inventory['root']==refs['loaderPackageRoot']and len(inventory['files'])==4889 and len(inventory['links'])==21,'actual package inventory')
package=Path(inventory['root']);need(stat.S_IMODE(package.stat().st_mode)==0o700,'private package root');names=set();links={x['path']:x for x in inventory['links']}
for r in inventory['files']:
 row({k:r[k]for k in ['path','sha256','bytes']});p=Path(r['path']);need(p==package/r['relativePath']and stat.S_IMODE(p.stat().st_mode)==r['mode']and p.stat().st_nlink==1,'package physical role/mode');names.add(r['relativePath'])
actual=set()
for p in package.rglob('*'):
 n=p.relative_to(package).as_posix()
 if p.is_symlink():need(n in links and os.readlink(p)==links[n]['target']and str(p.resolve(strict=True))==links[n]['resolvedPath']and p.resolve(strict=True).is_relative_to(package),'exact confined package link');actual.add(n)
 elif p.is_file():need(n in names,'known package file');actual.add(n)
need(actual==names|set(links),'package whole membership')
entry=(P/'entry.mjs').read_text();parent=(P/'external.py').read_text();construct=(P/'construct.mjs').read_text();bundle=(P/'bundle.mjs').read_text()
for p in P.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
need("const ORIGINAL='"+str(P)+"'"in entry and "OWN=REPO/'tests/node-compat/foundation-scheduler/combined-native-component-caller-candidate-v1'"in parent,'real own module contexts')
need('const f=await authenticate(configDescriptor,phase)'in entry and entry.index('const f=await authenticate(configDescriptor,phase)')<entry.index('const api=await import('),'complete Source authentication before custom import')
need('await c.packageTree('in entry and 'await c.file(refs.node);await c.recheck();return' in entry,'full private package/node guard before import')
need('record=await api.combinedNativeBootstrapPreflight({configDescriptor:f.refs.readOnlyConfig})'in entry and 'if(record)await record.recheck();await f.c.recheck()'in entry,'genuine retained API plus own returned fresh rechecks')
need('selectedManifestsForEngine('not in entry+bundle+construct and 'builtinMap(h.selectedManifests)'in bundle and 'builtinManifests:h.selectedManifests'in bundle,'full11 builtinMap/bundler without old9 cast')
need('await bundleProfile('in bundle and 'loadExperimentalClockPackage'not in bundle and 'bundleProfile'not in construct,'separate actual phase module imports')
need(construct.index('const captured=await writeWhole(')<construct.index('need(component.bytes<='),'full returned binary captured before own size limit')
need('await selected.componentize(source,options)'in construct and 'noUnavailableBytesClaimed:true'in construct,'genuine loader call and honest pre-return failure limitation')
need('await import('not in(P/'io.mjs').read_text()and not re.search(r'import\s.*transpiled',construct),'no generated application module import')
for name in ['NODE_OPTIONS','NODE_PATH','PYTHONPATH','PYTHONHOME','NAPI_RS_NATIVE_LIBRARY_PATH','NODE_COMPAT_COMPONENTIZE_MODULE']:need(name in entry and name in parent,'matching selected override refusal/removal '+name)
need(parent.index("assert all(refs[k]is not None")<parent.index('spec=importlib.util.spec_from_file_location'),'pending-proof refusal before monitor import')
need(parent.index("print(json.dumps(dict(schemaVersion=1,state='COMBINED355_CALLER_RAW_TERMINAL_UNREVIEWED_V1'")<parent.index('clean_terminal(terminal)'),'whole durable raw terminal before success interpretation')
for p,identity in identities.items():
 s=Path(p).lstat();need(identity==(s.st_dev,s.st_ino,s.st_size,s.st_mode,s.st_nlink,s.st_mtime_ns,s.st_ctime_ns),'complete current final Source/input identity')
pending=[k for k in ['fixtureSourcePeer','fixtureReviewRequiredState','fixtureReviewSourceField','actualReadOnlyReview','actualReadOnlyContract','readOnlyConfig','actualReadOnlyRequiredState']if refs[k]is None]
report=dict(schemaVersion=1,passed=True,sourceOnly=True,checks=checks,directRows=len(inputs['files']),sourceBoundaryManifests=inputs['boundaries'],currentUniqueFiles=len(files),currentFamilyIndices=len(families),packageRegularFiles=4889,packageLinks=21,staticModules=len(closure['staticModules']),staticEdges=len(closure['staticEdges']),pendingPrerequisites=pending,actionsBlocked=bool(pending),ownerHelpersOrApisInvoked=False,inheritedHistoricalTreesRecopied=False)
print(json.dumps(report))
