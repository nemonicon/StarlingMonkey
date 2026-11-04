"""Root collector; invoke only after observing the suite's raw terminal status."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
WASMTOOLS = Path('/tmp/starling-node-compat/native-build/cache/wasm-tools/1448/wasm-tools')

def digest(data):
    return hashlib.sha256(data).hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('variant', choices=['normal-off', 'normal-runtime', 'gc-off'])
    parser.add_argument('--raw-exit-code', type=int, required=True)
    parser.add_argument('--tool-session', type=int, required=True)
    args = parser.parse_args()
    assert args.raw_exit_code == 0
    root = Path('/tmp/starling-node-compat/production-classic-corrected-runtime-v1')/args.variant
    report_bytes = (root/'results.json').read_bytes()
    completion_bytes = (root/'completion.json').read_bytes()
    report = json.loads(report_bytes)
    completion = json.loads(completion_bytes)
    assert report['status'] == 'FUTURE_CLASSIC_REAL_COMPONENT_GATES_PASSED'
    assert report['variant'] == args.variant and report['ordinaryGroups'] == 19
    pins = json.loads((HERE/'reviewed-trace-runtime-pins-v1.json').read_bytes())
    pin = pins['variants'][args.variant]
    assert pin['sourceContractVersion'] == 'sm-classic-trace-source-v1'
    assert report['engineSha256'] == pin['engineSha256']
    assert report['pin'] == pin
    assert report['engineReceipt']['classicTraceSourcePolicy']['version'] == 'sm-classic-trace-source-v1'
    assert report['gcStressConfigured'] is (args.variant == 'gc-off')
    assert completion['state'] == 'CLASSIC_GATE_OUTPUTS_COMPLETE_REQUIRES_EXTERNAL_EXIT_ZERO'
    assert completion['finalAdmissionRecheckCompletedBeforeReportPublication'] is True
    assert completion['requiresIndependentTerminalExitCodeZero'] is True
    assert completion['engineSha256'] == report['engineSha256']
    assert completion['results']['sha256'] == digest(report_bytes)
    for row in completion['files']:
        path = root/row['path']
        path.relative_to(root)
        assert path.is_file() and not path.is_symlink()
        data = path.read_bytes()
        assert digest(data) == row['sha256'] and len(data) == row['bytes'], path
    oracle = json.loads((HERE.parent/'production-trace-runtime-activated-v1/harness/node-oracle-results.json').read_bytes())
    retained = report['snapshotAndRetained']['retained']
    assert [row['call'] for row in retained] == [1, 2, 3]
    observed = retained + [report['snapshotAndRetained']['fresh'], report['wasmtime']['observed']]
    for row in observed:
        assert row['ordinary'] == oracle['transformedObserved']
        assert row['snapshotIdentity'] is (True if row['call'] == 1 else None)
        assert row['retainedDefaultBefore'] == (65536 if row['call'] == 1 else 777)
        assert len(row['deferred']) == 48 and len(row['overloads']) == 17 and len(row['limits']) == 3
        assert row['nativeHex'] == '00cafeff'
        if args.variant == 'gc-off':
            assert row['rooting'] == {'hexRounds':8,'streamIdentity':True,'callbackCalls':1,'abortCalls':1,'disposedCalls':0}
    assert len(report['initializationFailures']) == 65
    for row in report['initializationFailures']:
        assert row['expectedFactoryMessage'] in row['error']
    assert len(report['deployedControls']) == 2
    assert report['deployedFailures']['jco']['status'] == 0
    assert report['deployedFailures']['wasmtime']['status'] > 0
    expected_imports = ['wasi:random/random@0.2.10'] if args.variant == 'normal-runtime' else []
    assert report['component']['interfaceAudit']['emittedImports'] == expected_imports
    audits = []
    assert digest(WASMTOOLS.read_bytes()) == 'b332dd79057dafdcc8a36ca933d0d499acea506b56b1ea28e28fbb036c9e713d'
    for name in completion['componentFiles']:
        path = root/name
        wit = subprocess.run([str(WASMTOOLS), 'component', 'wit', str(path)], check=True, capture_output=True)
        text = wit.stdout.decode()
        imports = []
        for line in text.splitlines():
            if line.strip().startswith('import '):
                imports.append(line.strip().removeprefix('import ').removesuffix(';'))
        assert sorted(imports) == expected_imports, (name, imports)
        assert 'export run: func() -> string;' in text
        audits.append({'path':str(path),'sha256':digest(path.read_bytes()),'emittedImports':imports,
                       'witSha256':digest(wit.stdout),'wasmtoolsExitCode':wit.returncode})
    assert len(audits) == 5
    result = {'schemaVersion':1,'state':'ROOT_CORRECTED_CLASSIC_COMPONENT_SUITE_VERIFIED',
              'variant':args.variant,'rawTerminalExitCodeObservedByRoot':args.raw_exit_code,
              'sourceContractVersion':'sm-classic-trace-source-v1',
              'runtimeFamilyIndexSha256':'e1f87cd6a2fd09ff34055187bfb938c2b094c3fd333ef9f57b6a1eea4c175b78',
              'toolSession':args.tool_session,'engineSha256':report['engineSha256'],
              'resultSha256':digest(report_bytes),'completionSha256':digest(completion_bytes),
              'completionFilesRehashed':len(completion['files']),'ordinaryGroups':19,
              'deferredCallAndConstructCases':48,'overloadRefusals':17,'stateLimitCases':3,
              'initializerFailures':65,'retainedJcoCalls':3,'freshJcoCalls':1,'freshWasmtimeCalls':1,
              'deployedFatalDiscardCase':1,'deployedCleanControls':2,'components':audits,
              'emittedWasiImports':expected_imports,'gcStressConfigured':args.variant == 'gc-off',
              'gcScope':'Combined owners only; no isolated VM-root proof' if args.variant == 'gc-off' else 'Not configured; no forced-GC proof from this suite',
              'fatalScope':'Own error fields checked in clean controls; generic host trap does not identify origin',
              'overallRoadmapComplete':False,'completeNodeStreamsClaim':False,'performanceClaim':False}
    output = HERE/('corrected-'+args.variant+'-component-root-results.json')
    with output.open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'state':result['state'],'variant':args.variant,'files':len(completion['files']),
                      'components':len(audits),'emittedImports':expected_imports,'output':str(output)}))

if __name__ == '__main__':
    main()
