"""Seal pure/data/source checks only; never execute any replay body."""
from pathlib import Path
import ast
import hashlib
import json
import subprocess

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
NODE=Path('/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
def sha(data):return hashlib.sha256(data).hexdigest()
def row(path):
    assert path.is_file()and not path.is_symlink()
    data=path.read_bytes();return {'path':str(path),'sha256':sha(data),'bytes':len(data)}
def main():
    (HERE/'data-test-results.json').write_bytes(Path('/tmp/starling-node-compat/exact-policy-tag-data-v1.json').read_bytes())
    checks=[]
    for p in sorted(HERE.glob('*.py')):ast.parse(p.read_text());checks.append({'path':p.name,'kind':'Python AST','exitCode':0})
    proof=json.loads((HERE/'transformation-proof.json').read_bytes())
    paths=[NODE,BASE/'production-regression-candidate-v1/index.json',BASE/'production-regression-candidate-v1/derivations.json',
      BASE/'registrar-ancestry-oracle-amendment-v1/index.json',BASE/'registrar-ancestry-oracle-amendment-v1/transformation-proof.json',
      BASE/'integration-candidate-v1/runtime-contract.mjs',BASE/'integration-candidate-v1/policy.json',BASE/'production-adoption-v1/reviewed-runtime-pins-v1.json',BASE/'production-adoption-v1/root-pin-review-receipt.json']
    for record in proof['records']:
        before=HERE/'before'/record['path'];after=HERE/'proposed'/record['path']
        assert row(before)['sha256']==record['beforeSha256'] and row(after)['sha256']==record['afterSha256']
        reverse=after.read_text()
        for edit in reversed(record['edits']):
            assert reverse.count(edit['new'])==1;reverse=reverse.replace(edit['new'],edit['old'])
        assert reverse.encode()==before.read_bytes()
        result=subprocess.run([str(NODE),'--check',str(after)],capture_output=True);assert result.returncode==0,result.stderr
        checks.append({'argv':[str(NODE),'--check',str(after)],'exitCode':0})
    result=subprocess.run([str(NODE),'--check',str(HERE/'test-data.mjs')],capture_output=True);assert result.returncode==0,result.stderr
    checks.append({'argv':[str(NODE),'--check',str(HERE/'test-data.mjs')],'exitCode':0})
    records=json.loads((BASE/'production-regression-candidate-v1/derivations.json').read_bytes())['records']
    paths.extend(BASE/'production-regression-candidate-v1'/record['destinationPath']for record in records)
    pins=json.loads((BASE/'production-adoption-v1/reviewed-runtime-pins-v1.json').read_bytes())
    for pin in pins['variants'].values():paths.append(Path(pin['enginePath']+'.build.json'))
    gc=pins['variants']['gc-off'];paths.extend([Path(gc['commandsPath']),Path(gc['freezeReceiptPath'])])
    (HERE/'syntax-results.json').write_text(json.dumps({'state':'SOURCE_SYNTAX_ONLY_PASSED','checks':checks,'guestExecuted':False},indent=2)+'\n')
    paths.extend(p for p in HERE.rglob('*')if p.is_file()and p.name not in ['index.json','input-freeze.json','source-receipt.json'])
    raw=(json.dumps({'schemaVersion':1,'state':'EXACT_POLICY_TAG_AND_REAL_GC_FIELD_CONSUMED_SOURCE_INPUTS','inputs':[row(p)for p in sorted(set(paths))],'engineBytesConsumed':False},indent=2)+'\n').encode()
    (HERE/'input-freeze.json').write_bytes(raw)
    (HERE/'source-receipt.json').write_text(json.dumps({'schemaVersion':1,'state':'FIVE_EXACT_POLICY_TAGS_AND_REAL_GC_SCHEMA_SOURCE_READY_NOT_REPLAYED','inputFreezeSha256':sha(raw),
      'parentSourceIndexSha256':'81c55887dc5e767db27477ba28f0e7a26a948435c7ddc61c70da329d4bd7f029','requiredRegistrarAmendmentIndexSha256':'7462f1255f4fd5048e345a96d58908c8e6251158bf36e5ab4450dab97be193b4',
      'currentBodiesAudited':64,'oldBodiesByteIdentical':57,'changedHostHarnessBodies':7,'newTagStatements':5,'actualFrozenTagChecks':20,'badVersionRefusals':100,'unknownVariantRefusals':4,
      'gcUsesActualPinFields':True,'oldPinSchemaSynthesized':False,'guestOracleFacadeBytesChanged':False,'metadataProjected':False,'engineBytesRead':False,
      'replayOrPreflightOrGuestOrHostOrBuildExecuted':False,'runtimeAcceptanceClaim':False},indent=2)+'\n')
    files=[{**row(p),'path':str(p.relative_to(HERE))}for p in sorted(HERE.rglob('*'))if p.is_file()and p.name!='index.json']
    (HERE/'index.json').write_text(json.dumps({'schemaVersion':1,'state':'EXACT_CLASSIC_POLICY_TAG_AND_GC_SCHEMA_AMENDMENT_SEALED','files':files,'runtimeAcceptanceClaim':False},indent=2)+'\n')
    print(json.dumps({'indexSha256':sha((HERE/'index.json').read_bytes()),'files':len(files),'inputs':len(json.loads(raw)['inputs'])}))
if __name__=='__main__':main()
