"""Independent data/Source reader. No owner imports, APIs or workloads."""
from pathlib import Path
import ast,hashlib,json,os,stat,subprocess
HERE=Path(__file__).resolve().parent;SOURCE=HERE.parent/'ownership-secret-component-candidate-v1'
checks=0;identities={};verified={}
def need(v):
 global checks
 assert v;checks+=1
def read(p):return json.loads(Path(p).read_bytes())
def ident(p):
 s=p.lstat();need(stat.S_ISREG(s.st_mode));return(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,str(p.resolve()))
def row(p):
 p=Path(p);need(p.is_absolute()and str(p)==os.path.normpath(str(p))and '\\'not in str(p)and '\0'not in str(p))
 before=ident(p);h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 need(ident(p)==before);r=dict(path=str(p),sha256=h.hexdigest(),bytes=before[2]);identities[str(p)]=before;verified[str(p)]=r;return r
def verify(r):need(row(r['path'])==r)
def names(root):
 need(root.is_dir()and not root.is_symlink());out=set()
 for p in root.rglob('*'):
  need(not p.is_symlink()and(p.is_dir()or p.is_file()))
  if p.is_file():out.add(p.relative_to(root).as_posix())
 return out
def family(ix):
 need(verified[ix['path']]==ix);base=Path(ix['path']).parent;want={'index.json'}
 for m in read(ix['path'])['files']:
  n=m['path'];need(n not in want and n and not n.startswith('/')and '\\'not in n and all(x not in('','.','..')for x in n.split('/')));want.add(n)
  need(verified[str(base/n)]==dict(path=str(base/n),sha256=m['sha256'],bytes=m['bytes']))
 need(names(base)==want)
source=row(SOURCE/'index.json');need(source['sha256']=='4a2c1e2076c3215d094482abc6609481ca4e4c2d980cfa9daa158c44d02665f2')
for m in read(source['path'])['files']:verify(dict(m,path=str(SOURCE/m['path'])))
family(source)
refs=read(SOURCE/'references.json');inputs=read(SOURCE/'source-inputs.json');deriv=read(SOURCE/'derivations.json')
need(len(inputs['files'])==33290 and len(inputs['families'])==24 and len({r['path']for r in inputs['files']})==33290)
for r in inputs['files']:verify(r)
for ix in inputs['families']:family(ix)
for own,key in [('guest.mjs','guestDonor'),('public-abi.wit','witDonor')]:need((SOURCE/own).read_bytes()==Path(deriv[key]['path']).read_bytes())
donor=Path(deriv['primitiveDonor']['path']).read_text();d=deriv['primitiveBlock'];block=donor[d['start']:d['end']]
need(len(block.encode())==d['bytes']==3121 and hashlib.sha256(block.encode()).hexdigest()==d['sha256'])
prefix=(SOURCE/'caller-primitives.mjs').read_text();body=(SOURCE/'caller-body.mjs').read_text();build=(SOURCE/'build.mjs').read_text()
need(prefix.endswith(block)and build==prefix+body and build[:-len(body)]==prefix and build[len(prefix):]==body)
actual=read(refs['actualRetainedPreflightReview']['result']['path']);contract=read(refs['actualRetainedPreflightContract']['path']);data=read(refs['actualRetainedRecordData']['path']);h=data['historicalBootstrap'];v=data['currentVerification']
need(actual['state']==contract['requiredReviewState']=='INDEPENDENT_CRYPTO_OWNER355_SECRET_RETAINED_PREFLIGHT_RESULTS_REVIEW_PASSED_V1')
for g in ['requiredFixedValues','requiredExactDescriptors','requiredPairs']:
 for k,x in contract[g].items():need(actual[k]==x)
need(actual['coverage']==contract['requiredCoverage']and actual['recordData']==refs['actualRetainedRecordData'])
need(sorted(v)==refs['currentVerificationFields']and v['protectedFileRows']==28256 and v['retainedTreeScopes']==8)
need(len(h)==41 and len(h['metadata'])==75 and len(h['selectedManifests'])==11 and h['currentCompleteVerifierCalls']==1)
need(h['engine']==refs['engine']and h['metadataDescriptor']==refs['metadata']and h['freezeReceipt']==refs['freezeReceipt'])
need(h['nativeSourceFiles']==355 and h['externalEmbeddingSources']==3 and len(h['metadata']['sourceManifest'])==355 and len(h['metadata']['componentizeSourceManifest'])==3)
need(h['sourceRoot']==refs['physicalRoles']['frozenNativeSourceRoot']and h['componentizeSourceRoot']==refs['physicalRoles']['frozenEmbeddingSourceRoot'])
need(h['metadata']['cryptoKeyOwnershipPolicy']['version']=='sm-webcrypto-key-owner-and-prototype-guard-source-v1'and h['metadata']['cryptoSecretFailureSourcePolicy']['version']=='sm-webcrypto-secret-failure-owner-source-v2')
need(h['metadata']['gcStress']is False and h['metadata']['oomTesting']is False and h['metadata']['entropyPolicy']=='off')
need(all(v[k]==0 for k in ['helperInvocations','originalApiInvocations','historicalRecheckInvocations','processesSpawned','filesCreated']))
pack=read(refs['packagingMap']['path']);publication=read(pack['publicationIndex']['path']);root=Path(pack['publicationRoot']);expected={r['path']:r for r in pack['files']};links={r['destination']:r for r in pack['links']};pub={r['path']:r for r in publication['files']};found=set();foundlinks=set()
need(len(expected)==4934 and len(links)==22 and pack['toolFiles']==4890 and pack['packagingFiles']==44)
rs=root.stat();need(rs.st_dev==pack['rootIdentity']['device']and rs.st_ino==pack['rootIdentity']['inode']and stat.S_IMODE(rs.st_mode)==0o700)
for role in pack['roleRoots']:
 p=root/role;need(p.is_dir()and not p.is_symlink())
 for q in p.rglob('*'):
  n=q.relative_to(root).as_posix();s=q.lstat()
  if q.is_symlink():
   link=links[n];need(os.readlink(q)==link['newLinkText']and str(q.resolve())==str(root/link['mappedTarget']));foundlinks.add(n)
  elif q.is_dir():need(stat.S_IMODE(s.st_mode)==0o700)
  else:
   m=expected[n];need(s.st_nlink==1 and stat.S_IMODE(s.st_mode)==m['mode']);need({k:pub[n][k]for k in ['path','sha256','bytes','mode']}==m);need(verified[str(q)]==dict(path=str(q),sha256=m['sha256'],bytes=m['bytes']));found.add(n)
need(found==set(expected)and foundlinks==set(links))
for key in ['retainedApi','packagingHelper','durableHelper','abiHelper','monitor','node']:need(verified[refs[key]['path']]==refs[key])
for name in ['authority.mjs','proofs.mjs']:need(str(Path(refs['packagingHelper']['path']).parent/name)in verified)
for name in ['toolchain.mjs','module-selection.mjs','profile-bundler.mjs','componentizer.mjs','capability-policy.mjs']:
 p=Path(refs['physicalRoles']['packagingRoot'])/'tests/node-compat'/name;need(str(p)in verified)
need(build.count('record=await api.retainedSecretBootstrapPreflight(')==1 and build.count('await selected.componentize(bundle.code,options)')==1)
need('selectedManifestsForEngine('not in build and 'secretArtifactBootstrapPreflight('not in build)
need('builtinMap(h.selectedManifests)'in build and 'builtinManifests:h.selectedManifests,virtualModules:{}'in build and 'componentOptions({engine:h.engine,adapter:packaging.adapter},wit)'in build)
need('if(record)await record.recheck();'in build and 'try{await recheck();}catch'in build and 'try{if(out)await out.recheck();}catch'in build)
need("await out.write('crypto-secret-owner.component.wasm',result.component)"in build and 'abi.parsePublicWit(emitted)'in build and 'abi.checkTranspileMetadata(generated)'in build)
for p in SOURCE.rglob('*.py'):ast.parse(p.read_bytes());need(True)
for path,i in identities.items():need(ident(Path(path))==i)
for ix in [source,*inputs['families']]:family(ix)
need(read(SOURCE/'pure-results.json')['checks']==45)
for key in ['outputRoot','externalRoot']:need(not Path(refs[key]).exists()and not Path(refs[key]).is_symlink())
out=dict(schemaVersion=1,sourceIndex=source,sourceMembers=35,declaredInputs=33290,completeFamilies=24,logicalBytes=sum(r['bytes']for r in inputs['files']),checks=checks,wholeClosureHashesAndBookendsPassed=True,packagingFiles=4934,packagingLinks=22,packagingModesMembershipAndTargetsPassed=True,fullRetainedContractDataEquality=True,historicalFields=41,metadataFields=75,nativeSourceFiles=355,externalEmbeddingSources=3,selectedManifests=11,primitiveExactBytes=3121,wholeCallerAssemblyReversed=True,guestAndWitByteExact=True,storedOwnerPureChecksAuthenticatedNotRerun=45,ownerApiOrHelperOrBundlerOrComponentizerOrGuestInvoked=False)
(HERE/'checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
