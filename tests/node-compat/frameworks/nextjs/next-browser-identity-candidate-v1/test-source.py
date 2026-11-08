"""Source text/JSON/AST only. Does not evaluate JS, imports of targets, or actors."""
from pathlib import Path
import ast
import hashlib
import json

HERE = Path(__file__).resolve().parent
BASE = HERE.parent

def row(path):
    raw = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))

def main():
    count = 0
    def check(value):
        nonlocal count
        assert value
        count += 1
    read = lambda path: json.loads(path.read_text())
    d = read(HERE/'derivation.json')
    check(row(BASE/'next-browser-netlog-candidate-v1/index.json') == d['parentSourceIndex'])
    worker = (BASE/'next-browser-netlog-candidate-v1/browser-check.mjs').read_text()
    for change in d['workerReplacements']:
        check(worker.count(change['before']) == 1)
        worker = worker.replace(change['before'],change['after'])
    check(worker == (HERE/'browser-check.mjs').read_text())
    check(row(BASE/'next-browser-netlog-candidate-v1/analyze.py') == d['unchangedAnalyser'])
    check((HERE/'analyze.py').read_bytes() == (BASE/'next-browser-netlog-candidate-v1/analyze.py').read_bytes())
    check(row(HERE/'identity-gate.mjs') == d['newPureGate'])
    plan = read(HERE/'plan.json')
    check(plan['contextExtraHTTPHeaders'] == {'Accept-Encoding':'identity'})
    check(plan['originalWholePerTestMilliseconds'] == 20000)
    check(plan['requestedCircularCapMegabytes'] == 16 and plan['finalFileReadLimitBytes'] == 20*1024*1024)
    check(plan['identityNegotiationGate']['configurationOrPublicRequestMetadataAloneSufficient'] is False)
    check(plan['identityNegotiationGate']['actualNegotiation'] is None)
    check(worker.count('await ') == (BASE/'next-browser-netlog-candidate-v1/browser-check.mjs').read_text().count('await '))
    check(worker.count('.getReader(') == (BASE/'next-browser-netlog-candidate-v1/browser-check.mjs').read_text().count('.getReader('))
    check("'--log-net-log='+netlogPath,'--net-log-max-size-mb=16'" in worker)
    check('result.identityNegotiation?.passed===true' in worker)
    gate = (HERE/'identity-gate.mjs').read_text()
    check("const requestIdentityObserved = evidence.identityObserved;" in gate)
    check("params.line === 'POST /actions HTTP/1.1\\r\\n'" in gate)
    check('contentEncoding.length === 0' in gate)
    check('await ' not in gate and 'fetch(' not in gate and 'readFile' not in gate)
    for kind,filename in [('native','plan.json'),('stock','plans.json')]:
        root = BASE/('next-browser-identity-'+kind+'-candidate-v1')
        parent = BASE/('next-browser-netlog-'+kind+'-candidate-v1')
        derivation = read(root/'derivation.json'); p=read(root/filename); old=read(parent/filename)
        check(row(parent/'index.json') == derivation['parentSourceIndex'])
        for name in derivation['copiedExactly']:
            check((root/name).read_bytes() == (parent/name).read_bytes())
        change = derivation['onlyOperationalDelta']; before=(parent/change['file']).read_text()
        check(before.count(change['before']) == 1)
        check((root/change['file']).read_text() == before.replace(change['before'],change['after']))
        check([key for key in p if p[key]!=old.get(key)] == derivation['changedPlanFields'])
        for key in ['outputPrefix','runId','requiredObservations','applicationInputs','applicationBuildResult',
                    'applicationBuildReview','applicationRootIdentity']:
            check(p[key] == old[key])
        check(p['sourceFamilies'][:-2] == old['sourceFamilies'])
        check(p['sourceFamilies'][-2] == row(parent/'index.json'))
        check(p['protectedInputs'][:-2] == old['protectedInputs'])
        check(p['protectedInputs'][-2:] == [row(HERE/'browser-check.mjs'),row(HERE/'identity-gate.mjs')])
        check(p['browserIdentityDiagnostic']['actualRun'] is None and p['browserIdentityDiagnostic']['actualNegotiation'] is None)
        if p['identitySourceBindingPending']:
            check(p['identitySourceIndex'] is None and p['sourceFamilies'][-1] is None)
        else:
            check(p['identitySourceIndex'] == row(HERE/'index.json') and p['sourceFamilies'][-1] == p['identitySourceIndex'])
        selected = p['browserSource'] if kind=='native' else p['arms']['stock']['browserSource']
        check(selected == row(HERE/'browser-check.mjs'))
        for file in root.glob('*.py'):
            ast.parse(file.read_text());check(True)
    for file in HERE.glob('*.py'):
        ast.parse(file.read_text());check(True)
    print(json.dumps(dict(sourceChecks=count,passed=True,scope='Text/JSON/PythonAST only; JS gate not evaluated',
                         nodeExecuted=False,guardExecuted=False,actorExecuted=False,actualNegotiationObserved=False)))

if __name__ == '__main__':
    main()
