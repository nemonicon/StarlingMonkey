"""Read-only Source/AST and finite bound arithmetic; no JS or target module evaluation."""
from pathlib import Path
import ast
import hashlib
import json

HERE = Path(__file__).resolve().parent

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
    plan, contract = read(HERE/'plan.json'), read(HERE/'marker-contract.json')
    check(row(Path(plan['baseSourceIndex']['path'])) == plan['baseSourceIndex'])
    check(row(Path(plan['baseEntry']['path'])) == plan['baseEntry'])
    check(row(HERE/'guest-entry.mjs') == plan['entry'])
    check(row(HERE/'marker-contract.json') == plan['markerContract'])
    before = Path(plan['baseEntry']['path']).read_text()
    text = before
    for change in contract['entryReplacements']:
        check(text.count(change['before']) == 1)
        text = text.replace(change['before'],change['after'])
    check(text == (HERE/'guest-entry.mjs').read_text())
    check(len(contract['entryReplacements']) == 9)
    check(text.count('await ') == before.count('await ')+1)
    check(text.count('.getReader(') == before.count('.getReader('))
    check(text.count('.getWriter(') == before.count('.getWriter('))
    check("res.once('error'" not in text and "res.on('error'" not in text)
    check("    return requestHandler(req,res);" in text)
    check("    guestCompletionRecord(completionTrace,'adapter-post-cleanup'" in text)
    check("    guestCompletionRecord(completionTrace,'adapter-normal-return-site'" in text)
    check('completionHolder={trace:undefined};' in text)
    check('if(completionHolder!==undefined)completionHolder.trace=completionTrace;' in text)
    check('return handleResources(...args,completionHolder);},undefined,incoming,outparam);' in text)
    check("const value=await handler.handle(incoming,outparam,completionHolder);" in text)
    child = text[text.index('            const value=await handler.handle'):text.index('        },undefined);',text.index('            const value=await handler.handle'))]
    check('return value;' in child and 'throw error;' in child and 'disposeBeforeEntry' not in child)
    check(plan['promiseObservation']['oldAsyncReturnAlreadyAdoptedHandlerPromise'] is True)
    check(plan['promiseObservation']['missingAwaitFix'] is False)
    check(plan['promiseObservation']['guaranteedExtraMicrotaskCount'] is None)
    base_plan = read(Path(plan['baseSourceIndex']['path']).parent/'plan.json')
    check(plan['worldSourceIndex'] == base_plan['worldSourceIndex'] and plan['witDirectory'] == base_plan['witDirectory'])
    check(plan['worldSourceIndex']['sha256'] == '802595f5a32dd93fc95c63eb95c901352ecb8da180152735982c344d6b827f58')
    check(Path(plan['worldSourceIndex']['path']).parent == Path(plan['witDirectory']))
    check(len(plan['selectedInterfaces']) == len(set(plan['selectedInterfaces'])) == 13)
    check(all(value.endswith('@0.2.10') for value in plan['selectedInterfaces']))
    check(plan['componentExports'] == ['wasi:http/incoming-handler@0.2.10'])
    for ref in plan['facadeReferences'] + plan['witInputs']:
        check(row(Path(ref['path'])) == ref)
    for key in ['requiredCompiledRequestResponse','requiredCompiledModuleLoader','requiredCleanupSourceIndex',
                'requiredFullNativeBuildReview','requiredCurrentInteropRuntimeReview','ancestorConstructionReviewForCurrentIntegration']:
        check(row(Path(plan[key]['path'])) == plan[key])
    prior = read(Path(plan['ancestorConstructionReviewForCurrentIntegration']['path']))
    check(plan['requiredEngine'] == prior['engine'] and plan['requiredNativeMetadata'] == prior['nativeMetadata'])
    check(plan['requiredFullNativeBuildReview'] == prior['fullBuildReview'])
    check(plan['requiredCurrentInteropRuntimeReview']['sha256'] == '55a255e7fd932133b144e32e7c7c26ecb31ad3403a5a0b8112f13c67fef13b17')
    derivation = read(HERE/'derivation.json')
    for ref in derivation['APIWitnesses']:
        check(row(Path(ref['path'])) == {key:ref[key] for key in ['path','sha256','bytes']})
    check(row(Path(plan['priorResponseCompletionRuntimeReview']['path'])) == plan['priorResponseCompletionRuntimeReview'])
    for key in ['actualEngine','actualNativeMetadata','actualRootAuthority','actualConstructor','actualComponent','actualImportFunctionCount','actualRuntime']:
        check(plan[key] is None)
    check(contract['routeAdmissions'] == [{'method':'GET','pathname':'/actions'},{'method':'POST','pathname':'/actions'},{'method':'GET','pathname':'/action-result'}])
    check(contract['correlation']['tokensGloballyUnique'] is False and contract['correlation']['adapterClassicJoinProved'] is False)
    # Independent contract envelope arithmetic only. Does not execute the JavaScript logger.
    frame = dict(marker=contract['marker'],version=1,sequence=256,lane='adapter',token=9007199254740991,
        method='POST',path='/action-result',event='child-handler-promise-fulfilled',phase='handler-await',
        readBytes=9007199254740991,readChunks=9007199254740991,flags=7,caughtType='undefined')
    encoded = json.dumps(frame,separators=(',',':'),ensure_ascii=True).encode('ascii')+b'\n'
    check(len(encoded) <= 512)
    for normal_attempts in [0,1,254,255,256,257,1000]:
        normal = min(normal_attempts,255)
        truncation = int(normal_attempts > 255)
        check(normal+truncation <= 256)
    for file in HERE.glob('*.py'):
        ast.parse(file.read_text());check(True)
    print(json.dumps(dict(sourceAndBoundChecks=count,passed=True,artificialEnvelopeBytes=len(encoded),
        scope='Source text/JSON/PythonAST and independent bound arithmetic, not JS logger behavior',
        javaScriptExecuted=False,nodeExecuted=False,guardExecuted=False,constructorExecuted=False,
        targetBinaryPayloadHashed=False,newPromiseMarkerObserved=False)))

if __name__ == '__main__':
    main()
