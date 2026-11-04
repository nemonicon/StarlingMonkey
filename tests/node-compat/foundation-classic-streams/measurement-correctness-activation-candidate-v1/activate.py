"""Future finite activation action. Source preparation never calls this main."""
import sys
sys.dont_write_bytecode=True
if not __debug__:raise RuntimeError('Activation requires assertions')
from pathlib import Path
import hashlib,importlib.util,json,os,stat
from authority import PRODUCER_INDEX,RECIPE,LABEL,DECLARED,CANONICAL,FREEZE,load_authority
HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'measurement-correctness-candidate-v1'
BASE_INDEX='138a4e0bcfe22ef3b48375257a50958f595dcebb607fc9267a30080948d612da'
AMEND=HERE.parent/'measurement-correctness-reporting-amendment-v1'
AMEND_INDEX='0558b50589680f9e1b812c8a62210233a768385bfabeae2f07be47c2e1fe5350'
OUTPUT=HERE.parent/'measurement-correctness-activated-v1'
PRODUCER=CANONICAL/'tests/node-compat/foundation-classic-streams/measurement-producer-candidate-v3'
def sha(data):return hashlib.sha256(data).hexdigest()
def regular(path,digest=None,size=None):
    path=Path(path);before=path.lstat();assert stat.S_ISREG(before.st_mode)and not path.is_symlink(),path
    raw=path.read_bytes();after=path.lstat();assert(before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns)
    assert digest is None or sha(raw)==digest,path;assert size is None or len(raw)==size,path
    return raw
def indexed(root,digest):
    raw=regular(root/'index.json',digest);rows=json.loads(raw)['files'];seen=set()
    for row in rows:
        name=row['path'];assert name not in seen and not Path(name).is_absolute()and all(p not in ('','.','..')for p in name.split('/'));seen.add(name)
        cursor=root
        for part in name.split('/'):cursor/=part;assert not cursor.is_symlink()
        regular(cursor,row['sha256'],row['bytes'])
    return rows
def within(root,path):return path==root or root in path.parents
def tool_snapshot(roots,collect=None):
    trees=[];links=[];canonical=[p.resolve(strict=True)for p in roots]
    for root in roots:
        assert root.is_dir()and not root.is_symlink();members=[]
        for directory,dirs,files in os.walk(root,followlinks=False):
            for name in sorted(dirs+files):
                path=Path(directory)/name;mode=path.lstat().st_mode;kind='symlink'if stat.S_ISLNK(mode)else'directory'if stat.S_ISDIR(mode)else'file'if stat.S_ISREG(mode)else None
                assert kind;members.append({'path':str(path.relative_to(root)),'kind':kind})
                if kind=='file'and collect is not None:collect(path)
                elif kind=='symlink':
                    target=path.resolve(strict=True);assert any(within(p,target)for p in canonical);target_kind='directory'if target.is_dir()else'file'if target.is_file()else None;assert target_kind
                    row={'path':str(path),'linkText':os.readlink(path),'resolvedTarget':str(target),'targetKind':target_kind}
                    if target_kind=='file':raw=regular(target);row.update(targetSha256=sha(raw),targetBytes=len(raw))
                    links.append(row)
            dirs[:]=[name for name in dirs if not(Path(directory)/name).is_symlink()]
        trees.append({'path':str(root),'realPath':str(root.resolve()),'entries':sorted(members,key=lambda r:r['path'])})
    return trees,links
def main():
    assert len(sys.argv)==6,'OWN_INDEX_SHA REVIEWED_PINS PIN_SHA ROOT_REVIEW_RECEIPT REVIEW_SHA'
    own_sha,pin_path,pin_sha,review_path,review_sha=sys.argv[1:]
    pins,pin_raw,review,review_raw=load_authority(pin_path,pin_sha,review_path,review_sha)
    own_rows=indexed(HERE,own_sha);base_rows=indexed(BASE,BASE_INDEX);amend_rows=indexed(AMEND,AMEND_INDEX)
    assert not OUTPUT.exists()and not OUTPUT.is_symlink()
    stage=OUTPUT.with_name(OUTPUT.name+'.staging');assert not stage.exists()and not stage.is_symlink(),'Preserve any partial activation'
    assert DECLARED.is_dir()and not DECLARED.is_symlink()and DECLARED.resolve(strict=True)==CANONICAL
    assert CANONICAL.is_dir()and not CANONICAL.is_symlink()
    producer_rows=indexed(PRODUCER,PRODUCER_INDEX)
    # All executable future verifier bytes precede importing that actual code.
    assert 'benchmark_common'not in sys.modules and 'ancestry.artifact_common'not in sys.modules
    sys.path.insert(0,str(PRODUCER))
    spec=importlib.util.spec_from_file_location('benchmark_common',PRODUCER/'benchmark_common.py');backend=importlib.util.module_from_spec(spec);sys.modules['benchmark_common']=backend;spec.loader.exec_module(backend)
    backend.require_source_root(CANONICAL)
    receipt,metadata,receipt_sha=backend.verify_frozen(LABEL)
    pin=pins['variants'][LABEL]
    observed={'engineSha256':receipt['engineSha256'],'engineBytes':receipt['engineBytes'],'metadataSha256':receipt['metadataSha256'],
      'freezeReceiptSha256':receipt_sha,'freezeRoot':str(FREEZE),'recipeSha256':RECIPE,'sourceIndexSha256':receipt['sourceIndexSha256'],
      'sourceFiles':342,'addonFiles':2,'sourceContractVersion':'sm-classic-trace-source-v1','classicStreamsEnabled':metadata['classicStreamsEnabled']}
    for key,value in observed.items():assert pin[key]==value,key
    assert metadata['diagnosticOnly']is True and metadata['classicStreamsEnabled']is True and metadata['gcStress']is False
    assert receipt['nativeInputsVerified']==342 and receipt['addonInputsVerified']==2 and receipt['externalEmbeddingInputsVerified']==3
    assert receipt['sourceIndexSha256']==PRODUCER_INDEX
    names=['native-provider.mjs','guest.mjs','workload.mjs','encoding-cases.mjs','activation-contract.mjs','runtime-preflight.template.mjs','consumed.mjs','bundle-diagnostic.mjs','completion.mjs','run.UNEXECUTED.mjs','node-workload-oracle.json','node-encoding-oracle.json']
    payload={name:regular(BASE/name)for name in names}
    payload['component-driver.mjs']=regular(AMEND/'proposed/component-driver.mjs');payload['bounded-comparison.mjs']=regular(AMEND/'bounded-comparison.mjs')
    payload['reviewed-pins.json']=pin_raw;payload['root-review-receipt.json']=review_raw
    config={'schemaVersion':1,'state':'ROOT_REVIEWED_CLASSIC_DIAGNOSTIC_CORRECTNESS_ACTIVATION_V1','variant':LABEL,'producerIndexSha256':PRODUCER_INDEX,'recipeSha256':RECIPE,
      'producerRoot':str(PRODUCER),'sourceRoot':str(CANONICAL),'declaredConfiguredSourceRoot':str(DECLARED),'canonicalDiagnosticSourceRoot':str(CANONICAL),
      'reviewedPinsPath':str(OUTPUT/'reviewed-pins.json'),'reviewedPinsSha256':pin_sha,'rootReviewReceiptPath':str(OUTPUT/'root-review-receipt.json'),'rootReviewReceiptSha256':review_sha,
      'reviewedActualEngine':{**{k:pin[k]for k in ['engineSha256','engineBytes','metadataSha256','freezeReceiptSha256','sourceFiles','addonFiles']},'diagnosticOnly':True},
      'runtimeAcceptanceClaim':False,'timingAllowed':False}
    payload['activation-template.json']=(json.dumps(config,indent=2)+'\n').encode()
    payload['README.md']=b'Root-reviewed diagnostic correctness source family only;20/14 actual guest gates remain unexecuted. No timing authority.\n'
    inputs={}
    def add(path,digest=None,size=None,role='actual-consumed-input'):
        path=Path(path);assert not path.is_symlink();path=path.resolve(strict=True);raw=regular(path,digest,size)
        row={'path':str(path),'sha256':sha(raw),'bytes':len(raw),'role':role}
        if str(path)in inputs:
            assert inputs[str(path)]['sha256']==row['sha256']and inputs[str(path)]['bytes']==row['bytes'];return
        inputs[str(path)]=row
    for root,rows,digest in [(HERE,own_rows,own_sha),(BASE,base_rows,BASE_INDEX),(AMEND,amend_rows,AMEND_INDEX),(PRODUCER,producer_rows,PRODUCER_INDEX)]:
        add(root/'index.json',digest)
        for row in rows:add(root/row['path'],row['sha256'],row['bytes'])
    # The actual verifier reopens absolute preparation references in their
    # original context. They remain explicitly historical, never relocated.
    for root in [BASE,PRODUCER]:
        preparation=json.loads(regular(root/'input-freeze.json'))
        for row in preparation['inputs']:add(root/row['path'],row['sha256'],row['bytes'],'original-context-preparation-or-runtime-tool-dependency')
    for row in receipt['copies']:add(row['path'],row['sha256'],row['bytes'])
    add(FREEZE/(LABEL+'-freeze-receipt.json'),receipt_sha)
    for row in metadata['sourceManifest']:add(CANONICAL/row['path'],row['sha256'])
    for row in backend.capture_addons():add(CANONICAL/row['path'],row['sha256'])
    for row in backend.tool_dependencies(CANONICAL):add(CANONICAL/row['path'],row['sha256'],row['bytes'])
    add(pin_path,pin_sha);add(review_path,review_sha)
    original=json.loads(regular(BASE/'input-freeze.json'))
    roots=[Path(row['path'])for row in original['toolTrees']];tool_trees,tool_links=tool_snapshot(roots,add)
    assert tool_trees==original['toolTrees']and tool_links==original['toolLinks'],'Tool membership/link drift needs new review'
    for name,raw in payload.items():inputs[name]={'path':name,'sha256':sha(raw),'bytes':len(raw),'boundary':'.'}
    manifest={'schemaVersion':1,'state':'ROOT_REVIEWED_DIAGNOSTIC_CORRECTNESS_FULL_ACTUAL_CONSUMED_SEAL','inputs':sorted(inputs.values(),key=lambda r:r['path']),
      'toolTrees':tool_trees,'toolLinks':tool_links,'invocation':original['invocation'],
      'sourceContext':{'declaredConfiguredSourceRoot':str(DECLARED),'canonicalDiagnosticSourceRoot':str(CANONICAL),'metadataRewritten':False,'preparationRowsRelocated':False}}
    payload['input-freeze.json']=(json.dumps(manifest,indent=2)+'\n').encode();compiled=payload['runtime-preflight.template.mjs'].decode()
    for key,value in {'CONFIG_SHA':sha(payload['activation-template.json']),'INPUTS_SHA':sha(payload['input-freeze.json'])}.items():compiled=compiled.replace('@'+key+'@',value)
    assert '@CONFIG_SHA@'not in compiled and '@INPUTS_SHA@'not in compiled;payload['runtime-preflight.mjs']=compiled.encode()
    record={'schemaVersion':1,'state':'ROOT_REVIEWED_CORRECTNESS_ACTIVATION_CREATED_GUEST_UNEXECUTED','producerIndexSha256':PRODUCER_INDEX,'recipeSha256':RECIPE,
      'parentCorrectnessIndexSha256':BASE_INDEX,'mandatoryReportingIndexSha256':AMEND_INDEX,'activationProducerIndexSha256':own_sha,
      'pinsSha256':pin_sha,'rootReviewSha256':review_sha,'actualON':observed,'frozenRowsConsumed':len(receipt['copies']),'consumedInputs':len(inputs),'toolLinks':len(tool_links),
      'declaredConfiguredSourceRoot':str(DECLARED),'canonicalDiagnosticSourceRoot':str(CANONICAL),'metadataRewritten':False,'guestOrPackagerOrTargetHostExecuted':False,'runtimeAcceptanceClaim':False,'timingAllowed':False}
    payload['source-receipt.json']=(json.dumps(record,indent=2)+'\n').encode()
    index={'schemaVersion':1,'state':'ROOT_REVIEWED_DIAGNOSTIC_CORRECTNESS_SOURCE_FAMILY_NOT_EXECUTED','files':[{'path':name,'sha256':sha(raw),'bytes':len(raw)}for name,raw in sorted(payload.items())],'runtimeAcceptanceClaim':False}
    payload['index.json']=(json.dumps(index,indent=2)+'\n').encode()
    load_authority(pin_path,pin_sha,review_path,review_sha);indexed(HERE,own_sha)
    for row in inputs.values():
        if Path(row['path']).is_absolute():regular(row['path'],row['sha256'],row['bytes'])
    assert tool_snapshot(roots)==(tool_trees,tool_links)
    assert not OUTPUT.exists()and not OUTPUT.is_symlink()and not stage.exists()and not stage.is_symlink();stage.mkdir(exist_ok=False)
    for name,raw in payload.items():
        path=stage/name;path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('xb')as stream:stream.write(raw)
        assert regular(path,sha(raw))==raw
    load_authority(pin_path,pin_sha,review_path,review_sha)
    for row in inputs.values():
        if Path(row['path']).is_absolute():regular(row['path'],row['sha256'],row['bytes'])
    assert tool_snapshot(roots)==(tool_trees,tool_links)
    for name,raw in payload.items():regular(stage/name,sha(raw),len(raw))
    assert not OUTPUT.exists()and not OUTPUT.is_symlink();stage.rename(OUTPUT)
    print(json.dumps({'output':str(OUTPUT),'indexSha256':sha(payload['index.json']),'consumedInputs':len(inputs),'runtimeAcceptanceClaim':False}))
if __name__=='__main__':main()
