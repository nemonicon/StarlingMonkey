"""Seal source and completed pure/Node-source checks; no replay activation."""
from pathlib import Path
import ast
import hashlib
import json
import subprocess

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
REPO=HERE.parents[3]
NODE=Path('/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
def sha(data):return hashlib.sha256(data).hexdigest()
def record(path):
    assert path.is_file() and not path.is_symlink()
    data=path.read_bytes();return {'path':str(path),'sha256':sha(data),'bytes':len(data)}
def main():
    (HERE/'guard-test-results.json').write_bytes(Path('/tmp/starling-node-compat/registrar-ancestry-guard-first.json').read_bytes())
    host=Path('/tmp/starling-node-compat/registrar-oracle-path-host-v1/results.json')
    (HERE/'path-oracle-test-results.json').write_bytes(host.read_bytes())
    proof=json.loads((HERE/'transformation-proof.json').read_bytes())
    for row in proof['records']:
        before=(HERE/'before'/row['path']).read_bytes();after=(HERE/'proposed'/row['path']).read_bytes()
        assert sha(before)==row['beforeSha256'] and sha(after)==row['afterSha256']
        reverse=after.decode()
        for edit in reversed(row['edits']):
            assert reverse.count(edit['new'])==edit.get('occurrences',1)
            reverse=reverse.replace(edit['new'],edit['old'])
        assert reverse.encode()==before
    helper=(HERE/'proposed/release/helpers/native-scalar-harness.mjs').read_text()
    guard=(HERE/'guard-source.mjs').read_text().split('// BEGIN FINITE',1)[1]
    assert '// BEGIN FINITE'+guard==helper[helper.index('// BEGIN FINITE'):helper.index('// END FINITE CLASSIC REGISTRAR ORACLE ANCESTRY')+len('// END FINITE CLASSIC REGISTRAR ORACLE ANCESTRY\n')]
    syntax=[]
    for p in sorted(HERE.rglob('*.py')):ast.parse(p.read_text());syntax.append({'path':str(p.relative_to(HERE)),'kind':'Python AST','exitCode':0})
    for p in [HERE/'guard-source.mjs',HERE/'test-guard.mjs',HERE/'proposed/release/helpers/native-scalar-harness.mjs',HERE/'proposed/release/runners/path.mjs']:
        result=subprocess.run([str(NODE),'--check',str(p)],capture_output=True)
        assert result.returncode==0,result.stderr
        syntax.append({'path':str(p.relative_to(HERE)),'argv':[str(NODE),'--check',str(p)],'exitCode':0})
    (HERE/'syntax-results.json').write_text(json.dumps({'state':'SOURCE_SYNTAX_ONLY_PASSED','checks':syntax},indent=2)+'\n')
    paths=[BASE/'production-regression-candidate-v1/index.json',BASE/'independent-production-regression-registrar-correction-v1/index.json',
      REPO/'tests/node-compat/foundation-scheduler/integration-candidate-v1/policy.json',REPO/'tests/node-compat/foundation-scheduler/taskqueue-owner-v2/starling-taskqueue-ticks.UNAPPLIED.patch',
      BASE/'integration-candidate-v1/policy.json',BASE/'implementation-candidate-v1-allocation-order-amendment/native-integration.corrected.UNAPPLIED.patch',
      Path('/tmp/starling-node-compat/production-classic-artifacts-v1/native-freeze/normal-off.engine.wasm.build.json'),
      Path('/tmp/starling-node-compat/production-classic-artifacts-v1/native-freeze/source/builtins/node-compat/register.cpp'),NODE,
      REPO/'builtins/node-compat/path.mjs',REPO/'builtins/node-compat/path-matcher.mjs']
    for name in ['assert','querystring','util']:
        paths.append(REPO/('tests/node-compat/foundation-'+name+'/native-node-results.json'))
    for row in proof['records']:paths.append(BASE/'production-regression-candidate-v1'/row['path'])
    for name in ['semantic.mjs','glob.mjs']:paths.append(REPO/('tests/node-compat/foundation-scheduler/production-release-runner-v3/oracles/'+name))
    for p in (REPO/'tests/node-compat/foundation-path/upstream').rglob('*'):
        if p.is_file():paths.append(p)
    paths.extend(REPO/('tests/node-compat/foundation-path/'+name)for name in ['lexical-vectors.json','semantic-results.json','glob-vectors.json','glob-differences.json','glob-results.json'])
    data=json.loads(host.read_bytes());paths.append(host)
    paths.extend(Path(row['path'])for row in data['outputs'])
    paths.extend(p for p in HERE.rglob('*')if p.is_file() and p.name not in ['index.json','input-freeze.json','source-receipt.json'])
    rows=[record(p)for p in sorted(set(paths))]
    raw=(json.dumps({'schemaVersion':1,'state':'REGISTRAR_ANCESTRY_AND_NODE_SUBPROCESS_CONSUMED_INPUTS','inputs':rows,'guestOrNativeExecuted':False},indent=2)+'\n').encode()
    (HERE/'input-freeze.json').write_bytes(raw)
    (HERE/'source-receipt.json').write_text(json.dumps({'schemaVersion':1,'state':'REGISTRAR_ANCESTRY_AND_NODE_PATH_SOURCE_READY_NOT_REPLAYED','inputFreezeSha256':sha(raw),
      'parentIndexSha256':'81c55887dc5e767db27477ba28f0e7a26a948435c7ddc61c70da329d4bd7f029','changedHostHarnessBodies':2,'oldBodiesByteIdentical':62,
      'guardActualDataPositives':3,'guardNegativeCases':45,'nodeOracleSubprocesses':2,'oldOracleOutputsUnchanged':5,
      'oracleDocumentsRewritten':False,'metadataProjected':False,'guestSemanticBytesChanged':False,'replayActivationInvoked':False,'guestOrHostExecuted':False},indent=2)+'\n')
    files=[{**record(p),'path':str(p.relative_to(HERE))}for p in sorted(HERE.rglob('*'))if p.is_file() and p.name!='index.json']
    (HERE/'index.json').write_text(json.dumps({'schemaVersion':1,'state':'REGISTRAR_AND_NODE_PATH_HOST_HARNESS_AMENDMENT_SEALED','files':files,'runtimeAcceptanceClaim':False},indent=2)+'\n')
    print(json.dumps({'indexSha256':sha((HERE/'index.json').read_bytes()),'files':len(files),'inputs':len(rows)}))
if __name__=='__main__':main()
