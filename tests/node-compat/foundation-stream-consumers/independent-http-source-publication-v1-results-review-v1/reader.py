"""Read/hash actual source-copy provenance only. No owner import or action."""
from pathlib import Path
import hashlib,json,os,stat
P=Path(__file__).resolve().parent;S=P.parent/'http-construction-candidate-v1'
OUT=Path('/private/tmp/starling-node-compat/consumers355-http-source-v1')
SOURCE='dc98f4653eec1719e07d64ecfa8eb93ecfea1748bb3640521e0ac2a7e6aa5487'
PUB='37fe3e00e33b195a808362e4119c12fdea9fb36acaeefcaebd8d61601ec8b67e'
seen={};physical={};checks=0
def need(v,m):
 global checks
 if not v:raise AssertionError(m)
 checks+=1
def identity(s):return(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
def digest(p):
 h=hashlib.sha256();n=0
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b);n+=len(b)
 return h.hexdigest(),n
def row(p):
 p=Path(p);h,n=digest(p);return dict(path=str(p),sha256=h,bytes=n)
def verify(r,role):
 p=Path(r['path']);need(p.is_file()and not p.is_symlink(),'ordinary leaf '+str(p));real=str(p.resolve());need(real==str(p)or str(p).startswith('/tmp/')and real=='/private'+str(p),'declared canonical/system/tmp context')
 a=p.stat();cached=physical.get(real)
 if cached is None:
  h,n=digest(p);b=p.stat();need(identity(a)==identity(b),'stable streamed read');physical[real]=dict(sha256=h,bytes=n,identity=identity(b))
 else:need(identity(a)==cached['identity'],'previously hashed physical file remains unchanged')
 actual=physical[real];need(actual['sha256']==r['sha256']and actual['bytes']==r['bytes'],'actual exact source bytes '+str(p))
 if str(p)in seen:need(all(seen[str(p)][k]==r[k]for k in ['path','sha256','bytes']),'consistent declared descriptor');seen[str(p)]['roles'].add(role)
 else:seen[str(p)]={k:r[k]for k in ['path','sha256','bytes']};seen[str(p)]['roles']={role}
 return r
def data(r,role='data'):verify(r,role);return json.loads(Path(r['path']).read_bytes())
def local(n):need(isinstance(n,str)and n and not n.startswith('/')and '\\'not in n and '\0'not in n and all(s not in ['', '.', '..']for s in n.split('/')),'finite local path');return n
def index(r,count):
 x=data(r,'index');need(x['schemaVersion']==1 and len(x['files'])==count,'exact finite index '+str(count));rows=[];names=set()
 for v in x['files']:
  n=local(v['path']);need(n not in names,'unique source member');names.add(n);rr=dict(path=str(Path(r['path']).parent/n),sha256=v['sha256'],bytes=v['bytes']);verify(rr,'indexed-member');rows.append(rr)
 return x,rows
def save(n,v):(P/n).write_text(json.dumps(v,indent=2)+'\n')
root_row=dict(path=str(P.parent/'http-source-publication-v1-root-results.json'),sha256='10e3a3422ee4780bfe91b4e31f9df5050f0f83f7b6dbff2e81cc624f1ded665a',bytes=4001)
root=data(root_row,'Root-actual-publication-result')
for k in ['sourceIndex','rootAction','config','externalTerminal','externalLaunch','started','externalStdout','externalStderr','publicationIndex','publicationCompletion','publicationRecord']:verify(root[k],'Root-'+k)
need(root['sourceIndex']['sha256']==SOURCE and root['publicationIndex']['sha256']==PUB,'exact source/publication identities')
source,source_rows=index(root['sourceIndex'],39);peer,peer_rows=index(root['sourceReview']['index'],8);peer_result=data(root['sourceReview']['result'],'actual-independent-source-peer')
need(peer_result['state']=='INDEPENDENT_CONSUMERS355_HTTP_CONSTRUCTION_SOURCE_REVIEW_PASSED_V1'and peer_result['httpSourceIndexSha256']==SOURCE and peer_result['sourceOnly']is True and peer_result['sourceReviewPassed']is True and peer_result['ownerActionsInvoked']is False,'exact source-only peer')
need(sum(r==root['sourceReview']['result']for r in peer_rows)==1,'original peer result indexed once')
action=data(root['rootAction'],'Root-source-copy-authority');config=data(root['config'],'private-publication-config')
need(action['state']=='ROOT_REVIEWED_CONSUMERS355_HTTP_SOURCE_PUBLICATION_V1'and action['sourceIndexSha256']==SOURCE and action['sourcePublicationAllowed']is True and action['outputRoot']==str(OUT),'new explicit source-only copy authority')
need(action['runtimeActionsAllowed']is False and action['operationalAdmission']is False and action['sourcePromotionAllowed']is False and action['sourceIndependentReview']==root['sourceReview'],'no runtime/promotion authority')
need(config['sourceIndexSha256']==SOURCE and config['rootAction']==root['rootAction'],'actual config/source/Root binding')
terminal=data(root['externalTerminal'],'external-raw-terminal');started=data(root['started'],'external-started')
need(terminal['pid']==16764 and terminal['rawExitCode']==0 and terminal['timeout']is False and terminal['parentOwnedGroupGone']is True and terminal['deadlineSeconds']==900,'external publisher raw0/clean/bounded')
need(terminal['authority']==root['rootAction']and terminal['config']==root['config']and started['pid']==terminal['pid']and started['argv']==terminal['argv'],'external caller identity')
need(terminal['argv']==['python3',str(S/'publish.py'),'--config',json.dumps(root['config'],separators=(',',':'))],'actual original publisher/config argv')
for k in ['stdout','stderr']:verify(terminal[k],'complete-external-'+k)
need(terminal['stderr']['bytes']==0 and terminal['runtimeActionsInvoked']is False and terminal['sourcePublicationOnly']is True,'retained empty stderr and source-copy scope')
publication,rows=index(root['publicationIndex'],32);by={str(Path(r['path']).relative_to(OUT)):r for r in rows}
record=data(root['publicationRecord'],'actual-publication-record');completion=data(root['publicationCompletion'],'actual-publication-completion')
need(record==dict(schemaVersion=1,state='CONSUMERS355_HTTP_SOURCE_PUBLISHED_PENDING_REVIEW_V1',sourceIndexSha256=SOURCE,proposalIndex=root['sourceIndex'],outputRoot=str(OUT),originalContextsKeptExternal=True,runtimeActionsInvoked=False,operationalAdmission=False),'complete actual record keeps original proposal context')
need(completion==dict(schemaVersion=1,state='SOURCE_PUBLICATION_COMPLETE_EXTERNAL_ZERO_AND_REVIEW_REQUIRED_V1',sourceIndexSha256=SOURCE,index=dict(root['publicationIndex'],path='index.json'),runtimeActionsInvoked=False),'complete publication completion binds actual index')
need(json.loads(Path(terminal['stdout']['path']).read_bytes())==dict(output=str(OUT),index=completion['index'],completion=dict(path='completion.json',sha256=root['publicationCompletion']['sha256'],bytes=root['publicationCompletion']['bytes']),runtimeActionsInvoked=False),'full publisher stdout decoded')
need(OUT.is_dir()and not OUT.is_symlink()and stat.S_IMODE(OUT.stat().st_mode)==0o700,'ordinary private0700 publication root')
actual=[]
for p in OUT.rglob('*'):
 need(not p.is_symlink(),'no published symlink')
 if p.is_dir():need(stat.S_IMODE(p.stat().st_mode)==0o700,'private0700 published subdirectory')
 else:need(p.is_file()and p.stat().st_nlink==1 and stat.S_IMODE(p.stat().st_mode)==0o600,'ordinary distinct0600 published file');actual.append(str(p.relative_to(OUT)))
need(set(actual)==set(by)|{'index.json','completion.json'}and len(actual)==34,'exact32 indexed34 actual file membership')
payload=json.loads((S/'payload.json').read_bytes())['files'];need(len(payload)==18,'exact18 payload files')
orig={str(Path(r['path']).relative_to(S)):r for r in source_rows};copies=[]
def copied(name,origin):
 r=by[name];need(r['sha256']==origin['sha256']and r['bytes']==origin['bytes'],'byte-exact copied source descriptor '+name)
 src=Path(origin['path']);dst=OUT/name;need(identity(src.stat())[:2]!=identity(dst.stat())[:2],'distinct source/copy inode '+name)
 copies.append(dict(name=name,original=origin,published=r,distinctInode=True))
for name in payload:copied(name,orig[name])
copied('proposal-index.json',root['sourceIndex']);copied('source-publication-root-authority.json',root['rootAction']);copied('source-publication-config.json',root['config'])
for r in peer_rows:copied('source-peer/'+str(Path(r['path']).relative_to(Path(root['sourceReview']['index']['path']).parent)),r)
copied('source-peer/index.json',root['sourceReview']['index'])
need((OUT/'closure.json').read_bytes()==(S/'closure.json').read_bytes()and(OUT/'prerequisites.json').read_bytes()==(S/'prerequisites.json').read_bytes(),'published closure/context bytes unchanged')
need((OUT/'proposal-index.json').read_bytes()==Path(record['proposalIndex']['path']).read_bytes(),'proposal capsule is data; original proposal index used externally')
need('publish.py'not in by and 'input-freeze.json'not in by and 'copy_primitives.py'not in by,'no publisher/preparation context transplanted into active runtime payload')

# Complete original external closure: each physical file is streamed once, with
# stable identity rechecks on aliases/repeated descriptors within this reader.
closure=json.loads((OUT/'closure.json').read_bytes());need(len(closure['files'])==12667,'complete12667 external files')
need(closure['selectedRuntimeFrozenCopies']==1164 and closure['nativeSourcesPerContext']==355 and closure['actualToolRows']==4892,'observed declared native/tool coverage counts')
for r in closure['files']:verify(r,'complete-original-external-closure')
freeze=json.loads((S/'input-freeze.json').read_bytes());need(len(freeze['files'])==12789,'original12789 preparation context rows')
for r in freeze['files']:verify(r,'original-source-preparation-context')
prior=data(next(r for r in peer_rows if r['path'].endswith('/rehashed-inputs.json')),'source-peer-full-input-ledger')
for r in prior['files']:verify(r,'freshly-rehashed-prior-physical-input')
def inventory(root):
 result=[]
 def walk(p,prefix):
  for q in sorted(p.iterdir()):
   s=q.lstat();kind='symlink'if stat.S_ISLNK(s.st_mode)else'directory'if stat.S_ISDIR(s.st_mode)else'file'if stat.S_ISREG(s.st_mode)else None;need(kind is not None,'ordinary source inventory');n=prefix+q.name;result.append(dict(path=n,kind=kind))
   if kind=='directory':walk(q,n+'/')
 walk(Path(root),'');return sorted(result,key=lambda r:r['path'])
for t in closure['toolTrees']:need(str(Path(t['path']).resolve())==t['realPath']and inventory(t['path'])==t['entries'],'complete tool membership remains exact')
need(len(closure['toolTrees'])==2 and len(closure['toolLinks'])==22,'two trees22links')
for r in closure['toolLinks']:need(Path(r['path']).is_symlink()and os.readlink(r['path'])==r['linkText']and str(Path(r['path']).resolve())==r['resolvedTarget'],'exact external npm link')
snapshot=inventory(closure['familySnapshotRoot']);need(all(r['kind']!='symlink'for r in snapshot)and sorted(r['path']for r in snapshot if r['kind']=='file')==closure['familySnapshotMembers']and len(closure['familySnapshotMembers'])==1678,'complete original1678-file snapshot')
need(len(closure['liveInputs'])==8,'LIVE8 remains exact')
for r in closure['liveInputs']:verify(r,'external-live-WIT-adapter')
pr=json.loads((OUT/'prerequisites.json').read_bytes());need(pr['paths']['familyRoot']=='/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-stream-consumers/release-gates-activated-v3'and pr['nativeConfiguredSourceRoot']=='/private/tmp/starling-node-compat/consumers-source-v2'and pr['nativeFrozenSourceRoot']=='/tmp/starling-node-compat/production-consumers-v1/native-freeze/source','original family/configured/frozen contexts preserved')
need(pr['paths']['packagingRoot']==pr['paths']['familyRoot']+'/snapshot'and pr['normalRuntimeEngineSha256']=='b227a8d2e6fb6b83da556d3520dceec82d5e1978801ba3c607bc9a31aa28ad60','actual RuntimeOnly engine and original packaging context')
admission=(OUT/'admission.mjs').read_text();worker=(OUT/'worker.mjs').read_text()
need("publicationIndex.path===join(HERE,'index.json')"in admission and 'descriptor(publication.proposalIndex)'in admission and "join(p.paths.familyRoot,'native-preflight.mjs')"in admission,'published HERE uses actual original native bridge; no proposal rebasing')
need("join(HERE,'classic-ordinary.mjs')"in worker and "join(HERE,'consumer-probes.mjs')"in worker,'only new small fixture modules resolve against actual publication')
for p in OUT.glob('*.mjs'):
 for spec in __import__('re').findall(r'(?:from\s*|import\s*)[\'\"]([^\'\"]+)[\'\"]',p.read_text()):
  if spec.startswith('.'):need((p.parent/spec).is_file(),'physical published local import exists '+spec)
for real,entry in physical.items():need(identity(Path(real).stat())==entry['identity'],'all hashed physical inputs stable through final audit')
save('copy-provenance.json',dict(schemaVersion=1,copies=copies,payloadCopies=18,allCopiedSourceBytesExact=True,allCopiedSourceInodesDistinct=True,
 publishedRoot=str(OUT),proposalRoot=str(S),runtimeContexts=pr['paths'],nativeConfiguredSourceRoot=pr['nativeConfiguredSourceRoot'],nativeFrozenSourceRoot=pr['nativeFrozenSourceRoot'],
 sourcePeerAndProposalCapsulesDataOnly=True,preparationManifestsNotRelocated=True))
save('rehashed-inputs.json',dict(schemaVersion=1,files=[dict(r,roles=sorted(r['roles']))for r in sorted(seen.values(),key=lambda r:r['path'])],physicalFilesStreamedOnce=len(physical),stablePhysicalIdentityRecheckedOnRepeatedDescriptors=True,ownerActionsInvoked=False))
save('results.json',dict(schemaVersion=1,state='INDEPENDENT_CONSUMERS355_HTTP_SOURCE_PUBLICATION_PASSED_V1',sourceIndexSha256=SOURCE,publicationIndexSha256=PUB,
 publisherRawExitCode=0,verifiedPassed=True,runtimeActionsInvoked=False,sourceOnly=True,sourcePublicationObserved=True,
 rootResult=root_row,sourceIndex=root['sourceIndex'],sourceReview=root['sourceReview'],rootAction=root['rootAction'],config=root['config'],externalTerminal=root['externalTerminal'],
 publicationIndex=root['publicationIndex'],publicationCompletion=root['publicationCompletion'],publicationRecord=root['publicationRecord'],
 actualIndexedFiles=32,actualRegularFiles=34,payloadCopies=18,wholePayloadBytesEqual=True,allCopiedSourceInodesDistinct=True,rootAndDirectoriesMode='0700',fileMode='0600',symlinks=0,
 runtimeClosureFiles=12667,preparationReferences=12789,toolTrees=2,knownToolLinks=22,snapshotFiles=1678,liveInputs=8,selectedNativeFrozenCopies=1164,nativeSourcesPerConfiguredAndFrozenContext=355,
 uniqueDeclaredInputsVerified=len(seen),uniquePhysicalFilesStreamed=len(physical),originalContextsRemainExternalAndUnchanged=True,proposalAndPublishedContextsCorrectlySeparated=True,
 rawRootSessionObservedByThisReader=False,retainedExternalRawTerminalVerified=True,parentOwnedGroupGone=True,
 metadataProjection=False,sourcePromotionAllowed=False,bundleComponentOrHostAuthorityIssued=False,futureBundle=None,futureComponent=None,futureHosts=None,
 reviewerReadHashDataOnly=True,reviewerPublisherHelperPreflightBundlerComponentGuestHostNativeActionsInvoked=False,
 operationalAdmission=False,runtimeAcceptanceClaim=False,timingAllowed=False,concreteBlockers=[],checks=checks,limitations=[
 'Actual SOURCE copy and provenance only; no native/build, bundle, component, typegraph or host runtime proof is issued.',
 'Publisher raw zero and cleanup are authenticated retained Root terminal data, not a direct reviewer observation of the original session.',
 'The eighteen active payload files preserve their bytes but execute from the new publication context; proposal/source-peer capsules remain data and are not reinterpreted as relocated preparation roots.',
 'Original a986 native-admission, configured355/frozen355, tool, WIT/adapter and native pins remain external, complete and unchanged.',
 'Normal RuntimeOnly b227 is the existing consumers355 tuple. No other355 metadata, old342 result or CryptoKey-owner proof is projected onto it.',
 'Any bundle, component or stock-host phase needs its own explicit new Root authority and independent output review. No operational/runtime/performance or request-body/reuse/GC claim follows.']))
print(json.dumps(dict(state='INDEPENDENT_CONSUMERS355_HTTP_SOURCE_PUBLICATION_PASSED_V1',indexed=32,actual=34,payload=18,physicalFiles=len(physical),declaredInputs=len(seen),checks=checks)))
