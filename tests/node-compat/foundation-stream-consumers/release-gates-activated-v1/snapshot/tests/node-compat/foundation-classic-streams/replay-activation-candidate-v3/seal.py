"""Seal the source-only producer after pure checks; never activate a family."""
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
    assert path.is_file() and not path.is_symlink()
    data=path.read_bytes();return {'path':str(path),'sha256':sha(data),'bytes':len(data)}
def indexed(root,expected):
    data=(root/'index.json').read_bytes();assert sha(data)==expected
    x=json.loads(data)
    for r in x['files']:
        p=root/r['path'];assert row(p)['sha256']==r['sha256'] and row(p)['bytes']==r['bytes']
    return x
def main():
    checks=[]
    argv=['python3',str(HERE/'test-source.py')]
    result=subprocess.run(argv,capture_output=True)
    (HERE/'test-source.stdout.txt').write_bytes(result.stdout)
    (HERE/'test-source.stderr.txt').write_bytes(result.stderr)
    assert result.returncode==0,result.stderr
    checks.append({'argv':argv,'exitCode':0,'pureGroups':14,'scope':'Source/owned text/actual Root authority documents only; main unexecuted'})
    for p in sorted(HERE.glob('*.py')):ast.parse(p.read_text());checks.append({'path':p.name,'kind':'AST','exitCode':0})
    result=subprocess.run([str(NODE),'--check',str(HERE/'native-preflight.template.mjs')],capture_output=True)
    assert result.returncode==0,result.stderr
    checks.append({'argv':[str(NODE),'--check',str(HERE/'native-preflight.template.mjs')],'exitCode':0})
    (HERE/'check-results.json').write_text(json.dumps({'schemaVersion':1,'state':'PURE_AND_SOURCE_SYNTAX_CHECKS_PASSED','checks':checks,'activationOrNativeGuestHostExecuted':False},indent=2)+'\n')
    proof=json.loads((HERE/'derivation-proof.json').read_bytes())
    text=(HERE/'activate.py').read_text()
    for edit in reversed(proof['edits']):
        assert text.count(edit['new'])==1
        text=text.replace(edit['new'],edit['old'])
    assert sha(text.encode())==proof['beforeProducerSha256']
    roots=[(BASE/'replay-activation-candidate-v2','afd5a7148f0a7737e919d84cf8e97d224e4f8e5126b8e46e498444ac3f3cf4f5'),
      (BASE/'production-regression-candidate-v1','81c55887dc5e767db27477ba28f0e7a26a948435c7ddc61c70da329d4bd7f029'),
      (BASE/'registrar-ancestry-oracle-amendment-v1','7462f1255f4fd5048e345a96d58908c8e6251158bf36e5ab4450dab97be193b4'),
      (BASE/'exact-policy-tag-amendment-v1','fd0242e16c6d684b91a332ff00005bf2a25b25d133b4d819e8e16341cac6306c')]
    paths=[]
    for root,expected in roots:
        document=indexed(root,expected);paths.append(root/'index.json');paths.extend(root/r['path']for r in document['files'])
    for name in ['reviewed-runtime-pins-v1.json','root-pin-review-receipt.json']:paths.append(BASE/'production-adoption-v1'/name)
    paths.append(NODE)
    for name in ['registrar-ancestry-oracle-amendment-v1','exact-policy-tag-amendment-v1']:
        document=json.loads((BASE/name/'input-freeze.json').read_bytes())
        paths.extend(Path(r['path'])for r in document['inputs'])
    paths.extend(p for p in HERE.rglob('*')if p.is_file() and p.name not in ['index.json','input-freeze.json','source-receipt.json'])
    records=[row(p)for p in sorted(set(paths))]
    raw=(json.dumps({'schemaVersion':1,'state':'SOURCE_ONLY_REPLAY_V3_CONSUMED_PREPARATION_INPUTS','inputs':records,'activationMainExecuted':False},indent=2)+'\n').encode()
    (HERE/'input-freeze.json').write_bytes(raw)
    (HERE/'source-receipt.json').write_text(json.dumps({'schemaVersion':1,'state':'SOURCE_ONLY_CLASSIC_REPLAY_V3_READY_MAIN_UNEXECUTED','inputFreezeSha256':sha(raw),
      'parentActivationIndexSha256':roots[0][1],'parentSourceIndexSha256':roots[1][1],'registrarOracleAmendmentIndexSha256':roots[2][1],'exactPolicyTagAmendmentIndexSha256':roots[3][1],
      'producerSha256':sha((HERE/'activate.py').read_bytes()),'inheritedBodies':64,'oldBodiesByteIdentical':57,'changedHostHarnessBodies':7,'guestSemanticBodiesChanged':False,
      'authorityAndTemplateByteIdentical':True,'reviewedNativePinsSha256':'c998dce40ff66a1764ad8c44f8a492b830d40bb6dce958aab711ecf3c5bcbf3e',
      'rootReviewReceiptSha256':'1df0d5bcbb4792efa9fe7329b164aede3a2da7bc4dec6c90d011972cfb6d7f56',
      'allowedRuntimeFamilies':['production-runtime-activated-v1','production-runtime-activated-v2','production-runtime-activated-v3'],
      'actualRuntimeIndexBound':None,'httpComponentPinStillNull':True,'pureSourceGroups':14,'activationOutputCreated':False,'guestOrHostExecuted':False,'runtimeAcceptanceClaim':False},indent=2)+'\n')
    files=[{**row(p),'path':str(p.relative_to(HERE))}for p in sorted(HERE.rglob('*'))if p.is_file() and p.name!='index.json']
    (HERE/'index.json').write_text(json.dumps({'schemaVersion':1,'state':'CLASSIC_REPLAY_V3_HOST_HARNESS_AMENDMENT_ACTIVATION_SOURCE_SEALED','files':files,'runtimeAcceptanceClaim':False},indent=2)+'\n')
    print(json.dumps({'indexSha256':sha((HERE/'index.json').read_bytes()),'files':len(files),'inputs':len(records)}))
if __name__=='__main__':main()
