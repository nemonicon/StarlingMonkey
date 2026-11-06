"""Root observer for separately issued bundle/fresh component construction.

No ordinary guest export is authorized. Both the whole Python parent and its
fresh Node child use the original owned monitor with explicit deadlines.
"""
from pathlib import Path
import hashlib,importlib.util,json,os,sys
R=Path('/Users/dan/dev/StarlingMonkey');S=R/'tests/node-compat/foundation-scheduler'
P=S/'combined-native-component-caller-candidate-v1'
PEER=S/'independent-combined355-component-caller-source-review-v1'
PYTHON=Path('/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9')
SOURCE_SHA='aec12b5c21995f1f080871be2d8fa77ee5aa20fe884e220dd94db7d6573993f1'
def d(p):
 p=Path(p);assert p.is_file() and not p.is_symlink();h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 return dict(path=str(p),sha256=h.hexdigest(),bytes=p.stat().st_size)
def read(p):return json.loads(Path(p).read_bytes())
def write(p,v):
 with Path(p).open('x') as f:json.dump(v,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def family(p):
 p=Path(p);v=read(p/'index.json');names={'index.json'}
 for row in v['files']:
  n=row['path'];assert n not in names and not Path(n).is_absolute() and '..' not in Path(n).parts;names.add(n);x=d(p/n);assert x['sha256']==row['sha256'] and x['bytes']==row['bytes']
 assert not any(q.is_symlink() for q in p.rglob('*'));assert {q.relative_to(p).as_posix() for q in p.rglob('*') if q.is_file()}==names
 return d(p/'index.json')
def main():
 assert len(sys.argv)==3 and sys.argv[1] in ['bundle','construct'] and sys.argv[2] in ['pure','resource','fatal','init-fatal','clock-snapshot','surviving-interest']
 phase,case=sys.argv[1:];own=family(P);assert own['sha256']==SOURCE_SHA
 peer_index=family(PEER);proof=read(PEER/'results.json');contract=read(P/'future-source-review-contract.json')
 assert proof['state']==contract['requiredState'] and proof['componentSourceIndexSha256']==SOURCE_SHA
 for k,v in contract['requiredFixedValues'].items():assert type(proof[k]) is type(v) and proof[k]==v
 refs=read(P/'references.json');catalogue=read(refs['fixtureCatalogue']['path']);fixture=next(f for f in catalogue['fixtures'] if f['id']==case)
 out=Path(refs['outputBase']+'-'+phase+'-'+case);external=Path(str(out)+'-external-root');tmp=Path(str(out)+'-tmp');caller=Path(str(out)+'-root-caller')
 for path in [out,external,tmp,caller]:assert not path.exists() and not path.is_symlink()
 root=read(P/'future-root-authority.template.json');root.pop('requiredIssuedState')
 root.update(state='ROOT_REVIEWED_COMBINED355_COMPONENT_CALLER_V1',sourceIndex=own,sourceIndependentReview=dict(index=peer_index,result=d(PEER/'results.json')),phase=phase,fixtureId=case,entry=d(P/'entry.mjs'),externalController=d(P/'external.py'),fixtureSource=fixture['source'],fixtureWit=fixture['wit'],worldName=fixture['worldName'],nativeEngine=refs['nativeEngine'],nativeMetadata=refs['nativeMetadata'],readOnlyConfig=refs['readOnlyConfig'],actualBootstrapReview=refs['actualBootstrapReview'],actualReadOnlyReview=refs['actualReadOnlyReview'],selectedInterfaces=fixture['selectedInterfaces'],disableFeatures=fixture['disableFeatures'],bundlePreparationAllowed=phase=='bundle',componentConstructionAllowed=phase=='construct',engineInitializationAllowed=phase=='construct',nativeReadOnlyApiAllowed=True,outputRoot=str(out),externalRoot=str(external),privateTemporaryRoot=str(tmp),ownedNodeDeadlineSeconds=1200 if phase=='bundle' else 2400)
 prefix=S/('combined-native-component-v1-'+phase+'-'+case)
 if phase=='construct':
  inputs=read(S/('combined-native-component-v1-'+case+'-bundle-inputs.json'))
  assert set(inputs)=={'bundleReport','bundle','bundleExternalTerminal'}
  for row in inputs.values():assert d(row['path'])==row
  root.update(inputs,guestSourceSha256=inputs['bundle']['sha256'],witWorldSha256=fixture['wit']['sha256'])
  lrrefs=read(Path(refs['loaderSourceIndex']['path']).parent/'references.json')
  loader=dict(schemaVersion=1,state='ROOT_REVIEWED_EXPERIMENTAL_CLOCK_PACKAGE_CONSTRUCTION_V2',phase='experimental-component-construction',sourceIndex=refs['loaderSourceIndex'],sourceIndependentReview=refs['loaderSourcePeer'],packageRoot=refs['loaderPackageRoot'],packageModuleInitializationAllowed=True,componentConstructionAllowed=True,engineInitializationDuringConstructionAllowed=True,nativeArtifactAdmissionMustBePerformedByCaller=True,freshOwnedNodeProcessRequired=True)
  for k in ['nativeEngine','nativeMetadata','guestSourceSha256','witWorldSha256','worldName','selectedInterfaces','disableFeatures','privateTemporaryRoot']:loader[k]=root[k]
  for k in ['toolsBuildReview','failedAdapterPhaseReview','metadataReview']:loader[k]=lrrefs[k]
  for k in ['adapterPromotionAllowed','defaultPackagerReplacementAllowed','keyOrCryptoWorkloadsAllowed','ordinaryGuestExportsAllowed','hostServersAllowed','runtimeAcceptanceClaim','operationalAdmission','timingAllowed']:loader[k]=False
  la=Path(str(prefix)+'-loader-root-authority.json');write(la,loader)
  lc=Path(str(prefix)+'-loader-root-config.json');write(lc,dict(schemaVersion=1,state='CLOCK_PACKAGE_LOADER_CONFIG_V2',sourceIndex=refs['loaderSourceIndex'],rootAuthority=d(la)))
  root.update(loaderRootAuthority=d(la),loaderConfig=d(lc))
 authority=Path(str(prefix)+'-root-authority.json');write(authority,root)
 config=read(P/'future-config.template.json');config.update(sourceIndex=own,phase=phase,fixtureId=case,rootAuthority=d(authority))
 config_path=Path(str(prefix)+'-root-config.json');write(config_path,config)
 argv=[str(PYTHON),'-B','-I',str(P/'external.py'),phase,json.dumps(d(config_path),separators=(',',':'))]
 outer_deadline=1800 if phase=='bundle' else 3000
 invocation=Path(str(prefix)+'-root-invocation.json');write(invocation,dict(schemaVersion=1,phase=phase,fixtureId=case,sourceIndex=own,sourcePeer=root['sourceIndependentReview'],rootAuthority=d(authority),config=d(config_path),rootLauncher=d(Path(__file__).resolve()),python=d(PYTHON),actualArgv=argv,outerParentDeadlineSeconds=outer_deadline,ownedNodeDeadlineSeconds=root['ownedNodeDeadlineSeconds'],engineInitializationAllowed=phase=='construct',ordinaryGuestExportsAllowed=False))
 caller.mkdir(mode=0o700);env={k:os.environ[k] for k in ['HOME','USER','LOGNAME','TMPDIR'] if k in os.environ};env.update(PATH='/usr/bin:/bin:/usr/sbin:/sbin',PYTHONDONTWRITEBYTECODE='1');write(caller/'environment-policy.json',dict(keys=sorted(env),valuesRetained=False,childOverridesSetByReviewedController=True))
 family(Path(refs['monitorIndex']['path']).parent);assert d(refs['monitorEntry']['path'])==refs['monitorEntry']
 spec=importlib.util.spec_from_file_location('genuine0af_combined_component_root_monitor',refs['monitorEntry']['path']);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 print(json.dumps(dict(event='combined-component-root-launch',phase=phase,fixtureId=case,invocation=d(invocation))),flush=True)
 t=m.monitor(argv,str(R),env,caller,outer_deadline,d(authority));clean=t['rawExitCode']==0 and t['allObservedOwnedGroupsGone'] is t['parentOwnedGroupGone'] is True and t['timeout'] is t['forcedCleanup'] is False and all(t[k]==[] for k in ['errors','signals','interruptedSignals','remainingObservedPids'])
 print(json.dumps(dict(event='combined-component-root-terminal',phase=phase,fixtureId=case,rawExitCode=t['rawExitCode'],terminal=d(caller/'terminal.json'),clean=clean)),flush=True)
 raise SystemExit(0 if clean else 1)
if __name__=='__main__':main()
