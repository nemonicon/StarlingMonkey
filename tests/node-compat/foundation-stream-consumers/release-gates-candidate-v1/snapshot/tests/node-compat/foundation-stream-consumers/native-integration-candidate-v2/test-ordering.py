"""C355-M1 source-order and benign scratch-hash tests; never run a real verifier."""
from pathlib import Path
import ast,copy,hashlib,json,os,re
HERE=Path(__file__).resolve().parent
OLD=HERE.with_name('native-integration-candidate-v1')
checks=[]
def check(name,value=True):assert value,name;checks.append(name)
def digest(value):return hashlib.sha256(value).hexdigest()
def main():
    source=(HERE/'artifact-tools/artifact_common.py').read_text();tree=ast.parse(source)
    functions={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
    reader=functions['verify_frozen_variant'];barrier=reader.body[1]
    check('firstStatementStillFiniteLabelAssert',isinstance(reader.body[0],ast.Assert))
    check('secondStatementUniversalCurrentDependencyAuthentication',isinstance(barrier,ast.Expr)and isinstance(barrier.value,ast.Call)and isinstance(barrier.value.func,ast.Name)and barrier.value.func.id=='tool_dependencies'and len(barrier.value.args)==1 and isinstance(barrier.value.args[0],ast.Name)and barrier.value.args[0].id=='REPO')
    imports=[n for n in ast.walk(reader)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr in ['spec_from_file_location','exec_module','module_from_spec']]
    check('allConfiguredCustomImportsAfterBarrier',imports and all(n.lineno>barrier.lineno for n in imports))
    old=ast.parse((OLD/'artifact-tools/artifact_common.py').read_text())
    oldreader=next(n for n in old.body if isinstance(n,ast.FunctionDef)and n.name=='verify_frozen_variant')
    check('oldReaderHadNoSuchEarlyBarrier',not any(isinstance(n,ast.Expr)and isinstance(n.value,ast.Call)and isinstance(n.value.func,ast.Name)and n.value.func.id=='tool_dependencies'for n in oldreader.body[:2]))
    standard={'hashlib','json','os','pathlib','re','shlex','shutil'}
    for node in tree.body:
        if isinstance(node,ast.Import):assert all(n.name in standard for n in node.names)
        if isinstance(node,ast.ImportFrom):assert node.module in standard
    check('NoExternalHelperRunsAtCommonModuleImport',True)
    primitives=['sha','checked','checked_below','tool_dependencies']
    for name in primitives:
        for node in ast.walk(functions[name]):
            assert not isinstance(node,(ast.Import,ast.ImportFrom))
            if isinstance(node,ast.Call)and isinstance(node.func,ast.Name):assert node.func.id not in ['exec','eval','__import__']
    check('BarrierPrimitivesHashDataOnly',True)
    # Execute only the first TWO source statements and existing hash primitives.
    # No receipt, engine, decoder, native verifier or helper module is opened.
    output=Path(os.environ['CONSUMERS_ORDERING_TEST_OUTPUT']);assert not output.exists()
    output.mkdir(parents=True)
    configured=output/'configured';toolhome=output/'artifact-tools';configured.mkdir();toolhome.mkdir()
    codec=configured/'codec-evidence.py';layer=configured/'layer-policy.py'
    baseline={codec:b"raise RuntimeError('scratch codec must never execute')\n",layer:b"raise RuntimeError('scratch layer must never execute')\n"}
    for path,value in baseline.items():path.write_bytes(value)
    contract=json.loads((HERE/'admission-pins.json').read_bytes())
    pins={'schemaVersion':1,'recipeSha256':contract['productionRecipeSha256'],'sourcePolicySha256':contract['policySha256'],'sourceHelperSha256':contract['helperSha256'],'nativeSources':355,'reviewedEnginePins':None,
      'toolDependencies':[{'path':p.name,'sha256':digest(value),'bytes':len(value)}for p,value in baseline.items()]}
    pinbytes=(json.dumps(pins,indent=2)+'\n').encode();pinfile=toolhome/'tool-pins.json';pinfile.write_bytes(pinbytes)
    state={'dispatches':0}
    def dispatch():state['dispatches']+=1
    module=ast.Module(body=[copy.deepcopy(functions[name])for name in primitives],type_ignores=[])
    prefix=ast.FunctionDef(name='prefix',args=ast.arguments(posonlyargs=[],args=[ast.arg(arg='label')],kwonlyargs=[],kw_defaults=[],defaults=[]),body=copy.deepcopy(reader.body[:2])+[ast.Expr(value=ast.Call(func=ast.Name(id='dispatch',ctx=ast.Load()),args=[],keywords=[]))],decorator_list=[])
    module.body.append(prefix);ast.fix_missing_locations(module)
    scope={'Path':Path,'hashlib':hashlib,'json':json,'re':re,'HERE':toolhome,'REPO':configured,'RECIPE':contract['productionRecipeSha256'],'POLICY':contract['policySha256'],'HELPER':contract['helperSha256'],'TOOL_PINS_SHA':digest(pinbytes),'LABELS':('normal-off','normal-runtime','gc-off','disabled-off'),'dispatch':dispatch}
    exec(compile(module,'<scratch-two-statement-prefix-and-hash-primitives-only>','exec'),scope)
    for label in ['normal-off','gc-off','disabled-off']:
        prior=state['dispatches'];scope['prefix'](label);check('cleanScratchPrefix:'+label,state['dispatches']==prior+1)
    for name,path,kind in [('codec',codec,'tamper'),('layer',layer,'tamper'),('missing-codec',codec,'missing')]:
        prior=state['dispatches']
        if kind=='tamper':path.write_bytes(b"raise RuntimeError('tampered scratch helper must never execute')\n")
        else:path.unlink()
        try:scope['prefix']('normal-off')
        except AssertionError:pass
        else:raise AssertionError('Scratch helper tamper was not refused')
        check('refusedBeforeDispatch:'+name,state['dispatches']==prior)
        path.write_bytes(baseline[path])
    prior=state['dispatches'];pinfile.write_bytes(pinbytes+b' ')
    try:scope['prefix']('normal-off')
    except AssertionError:pass
    else:raise AssertionError('Changed scratch tool manifest admitted')
    check('changedToolPinsRefusedBeforeDispatch',state['dispatches']==prior);pinfile.write_bytes(pinbytes)
    try:scope['prefix']('unknown')
    except AssertionError:pass
    else:raise AssertionError('Unknown label admitted')
    check('unknownLabelRefusedBeforeDispatch',state['dispatches']==prior)
    scope['prefix']('normal-off');check('restoredScratchPositive',state['dispatches']==prior+1)
    for path,value in baseline.items():assert path.read_bytes()==value
    check('scratchOnlyNoHelperExecuted',True)
    bootstrap=(HERE/'artifact-tools/bootstrap-classifier.py').read_text();exporter=(HERE/'artifact-tools/export-pin-candidate.py').read_text()
    check('bootstrapUsesUniversalReader',"common.verify_frozen_variant(variant,return_receipt_digest=True)"in bootstrap)
    check('exporterUsesUniversalReader',"verify_frozen_variant(label, output, return_receipt_digest=True)"in exporter)
    check('noAddedProductionOwnerFunction',set(functions)=={n.name for n in old.body if isinstance(n,ast.FunctionDef)})
    result={'schemaVersion':1,'state':'C355_M1_ORDERING_AND_OWNED_SCRATCH_HASH_REFUSAL_CHECKED','checks':checks,'passed':len(checks),'scratchToolRows':2,'actualConfiguredToolRows':767,'scope':'Only copied two-statement reader prefix and hash primitives executed against owned scratch data. Genuine verifier/bootstrap/codec/layer/helper imports were not called.','genuineVerifierOrHelperExecuted':False,'scratchDispatches':state['dispatches']}
    with(output/'results.json').open('x')as out:json.dump(result,out,indent=2);out.write('\n')
    print(json.dumps({'state':result['state'],'passed':len(checks),'genuineVerifierOrHelperExecuted':False}))
if __name__=='__main__':main()
