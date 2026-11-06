"""Prepare authenticated freeze Source DATA. Never invoke admission or copy payloads."""
from pathlib import Path
import hashlib,json,posixpath,stat
OWN=Path(__file__).resolve().parent;K=OWN.parent;REPO=OWN.parents[3]
def row(path):
 path=Path(path);b=path.read_bytes();return dict(path=str(path),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def read(path):return json.loads(Path(path).read_bytes())
def save(name,value):(OWN/name).write_text(json.dumps(value,indent=2)+'\n')
def main():
 p3=K/'node-crypto-hash-hmac-native-controller-candidate-v3';producer=read(p3/'references.json')
 adapter=K/'node-crypto-hash-hmac-artifact-revalidation-candidate-v2';a=read(adapter/'references.json')
 review=K/'independent-node-crypto-hash-hmac-artifact-revalidation-v2-results-review-v2';proof=read(review/'results.json');actual=read(proof['actualRevalidationResult']['path'])
 assert row(review/'index.json')['sha256']=='a39cce0d73a502f89bb6cd1c48289c08d1e6d3e9b2650db5b0fcca6c655af896'
 metadata=read(proof['rawMetadata']['path']);ledger=read(proof['inputHashes']['path'])['files'];by_path={r['path']:r for r in ledger}
 work=Path(producer['workRoot']);build=Path(metadata['cmakeCachePath']).parent;selected={}
 def select(path,role):
  path=str(path);r=by_path[path]
  if path in selected:assert selected[path]['source']==r;selected[path]['roles'].append(role)
  else:selected[path]=dict(source=r,destination='build-evidence/'+Path(path).relative_to(work).as_posix(),roles=[role])
 for r in ledger:
  p=Path(r['path'])
  if p.is_relative_to(build)and p.suffix in ['.a','.o','.obj']:select(p,'actual-current-build-library-or-object')
  elif p.is_relative_to(work)and p.name in ['CMakeCache.txt','compile_commands.json','build.ninja','rules.ninja','null.cpp','Cargo.toml','Cargo.lock','configdata.pm','moz-config.h','js-confdefs.h','wasi-sdk-version.txt']:select(p,'finite-current-WORK-build-witness')
 for key in ['cmakeCachePath','compileCommandsPath']:select(metadata[key],'raw83-direct-build-reference')
 for d in [metadata['zlibSelectedCodecInput']['archive'],metadata['openssl']['library'],metadata['privateRustupBootstrapPolicy']['beforeInstallRecord'],metadata['privateRustupBootstrapPolicy']['settingsAtBuildCompletion'],metadata['nodeCryptoHashHmacPolicy']['actualInstallationOrder']['source'],metadata['nodeCryptoHashHmacPolicy']['actualNinjaCapture']['stdout'],metadata['nodeCryptoHashHmacPolicy']['actualNinjaCapture']['stderr']]:select(d['path'],'selected-raw83-library-install-or-command-witness')
 # Every literal .a link argument has a copied physical role. No command runs.
 for word in metadata['nodeCryptoHashHmacPolicy']['actualLinkEvidence']['linkArgv']:
  if word.endswith('.a'):
   path=word if word.startswith('/')else posixpath.normpath(str(build)+'/'+word)
   select(path,'actual-guest-link-archive')
 save('work-copy-plan.json',dict(schemaVersion=1,files=sorted(selected.values(),key=lambda r:r['destination']),selectionRule='Build-directory .a/.o/.obj + finite named witnesses + explicit raw83 required witnesses + every actual .a link argument; SDK distributions and full archive/source trees remain referenced, not copied',copyBytes=sum(r['source']['bytes']for r in selected.values())))
 # Derive a complete current file closure for all eleven declared trees. The
 # historical21451 ledger remains byte-exact and is not silently replaced.
 trees=read(a['baseArtifactTrees']['path'])['trees'];extra={}
 for tree in trees:
  for entry in tree['entries']:
   if entry['kind']=='file':
    p=Path(tree['root'])/entry['path']
    if str(p)not in by_path:extra[str(p)]=row(p)
 save('distribution-reference-additions.json',dict(schemaVersion=1,files=sorted(extra.values(),key=lambda r:r['path']),historicalLedgerFiles=len(ledger),trees=11,originalLedgerChanged=False,allOriginalTreeRegularFilesCovered=True))
 base_inputs=read(a['baseSourceInputs']['path']);additional=read(adapter/'source-inputs.json')
 families={r['path']:r for r in base_inputs['families']+additional['families']}
 for p in [review,Path(a['producerControllerIndex']['path']).parent,adapter,Path(proof['sourceReview']['index']['path']).parent,Path(a['originalFailureReview']['index']['path']).parent,Path(a['monitorIndex']['path']).parent]:
  r=row(p/'index.json');families[r['path']]=r
 for key in ['predecessorReview']:
  r=proof[key]['index'];families[r['path']]=r
 files=[*base_inputs['files'],*additional['files'],a['baseArtifactTrees'],a['producerReferences'],a['producerIo'],a['producerAdmission'],proof['actualRevalidationResult'],proof['rawMetadata'],proof['inputHashes'],proof['referenceAliases'],proof['distributionData'],row(review/'result-contract.json')]
 for r in metadata['selectedModuleManifests']:files.append(row(Path(producer['configuredSourceRoot'])/r['path']))
 for key in ['metadataModel','hashModel','policy','recipe','helper']:files.append(producer[key])
 unique={}
 for r in files:
  assert r['path']not in unique or unique[r['path']]==r;unique[r['path']]=r
 save('source-inputs.json',dict(schemaVersion=1,files=sorted(unique.values(),key=lambda r:r['path']),families=list(families.values()),currentArtifactLedger=proof['inputHashes'],treeInventory=a['baseArtifactTrees'],aliases=proof['referenceAliases'],distributionData=proof['distributionData'],fullReferenceClosureIncludesEveryTreeRegularFile=True))
 # Exact pure model bytes are frozen alongside the NEW verifier. Original P3
 # admission/helper retain their own genuine original module paths and owner.
 for key,name in [('metadataModel','metadata_model.py'),('hashModel','hash_model.py')]:
  raw=Path(producer[key]['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==producer[key]['sha256'];(OWN/name).write_bytes(raw)
 cp=(p3/'copy_io.py').read_text();old='''            with target.open('xb') as result:
                if row.get('original') is not None:''';new='''            with target.open('xb') as result:
                os.fchmod(result.fileno(), 0o600)
                if row.get('original') is not None:''';assert cp.count(old)==1;cp=cp.replace(old,new);(OWN/'copy_io.py').write_text(cp)
 refs=dict(schemaVersion=1,state='HASH_HMAC357_REVALIDATED_ARTIFACT_FREEZER_REFERENCES_V1',
  producerIndex=a['producerControllerIndex'],integrationIndex=a['integrationSourceIndex'],producerReferences=a['producerReferences'],producerIo=a['producerIo'],producerAdmission=a['producerAdmission'],originalCopyIo=row(p3/'copy_io.py'),
  artifactReview=dict(index=row(review/'index.json'),result=row(review/'results.json')),artifactContract=row(review/'result-contract.json'),artifactResult=proof['actualRevalidationResult'],artifactLedger=proof['inputHashes'],artifactTrees=a['baseArtifactTrees'],referenceAliases=proof['referenceAliases'],distributionData=proof['distributionData'],
  actualStageReview=producer['actualStageReview'],actualStageContract=producer['actualStageContract'],stageJournal=producer['stageJournal'],engine=proof['engine'],metadata=proof['metadata'],originalFailureReview=a['originalFailureReview'],originalFailureContract=a['originalFailureContract'],originalBuildResult=a['originalBuildResult'],originalBuildObservation=a['originalRootObservation'],failedReadOnlyObservation=a['failedReadOnlyRootObservation'],indexException=a['indexException'],baselineTreeTransport=a['baselineTreeTransport'],indexModel=row(adapter/'index_data.py'),tmpAliasPolicy=a['tmpAliasPolicy'],
  configuredSourceRoot=producer['configuredSourceRoot'],workRoot=producer['workRoot'],freezeRoot=producer['freezeRoot'],externalRoot='/private/tmp/starling-node-compat/node-crypto-hash-hmac-v3-freeze-v1-external-root',
  sourceInputs=row(OWN/'source-inputs.json'),referenceAdditions=row(OWN/'distribution-reference-additions.json'),workCopyPlan=row(OWN/'work-copy-plan.json'),monitorIndex=a['monitorIndex'],monitorEntry=a['monitorEntry'],python=a['python'],
  activePolicy=producer['policy'],activeRecipe=producer['recipe'],activeHelper=producer['helper'],pureMetadataModel=producer['metadataModel'],pureHashModel=producer['hashModel'],
  entry=row(OWN/'entry.py'),newSourcePeer=None,rootAuthority=None,actualFreeze=None,actualFrozenReview=None,pins=None,bootstrap=None,runtime=None,operationalAdmission=False)
 save('references.json',refs)
 save('derivations.json',dict(schemaVersion=1,copyIo=dict(original=row(p3/'copy_io.py'),after=row(OWN/'copy_io.py'),before=old,afterText=new,singleReplacement=True),models=dict(metadata=dict(original=producer['metadataModel'],after=row(OWN/'metadata_model.py')),hash=dict(original=producer['hashModel'],after=row(OWN/'hash_model.py')))))
 print(json.dumps(dict(workWitnesses=len(selected),workCopyBytes=sum(r['source']['bytes']for r in selected.values()),newDistributionReferenceFiles=len(extra),sourceFiles=len(unique),families=len(families))))
if __name__=='__main__':main()
