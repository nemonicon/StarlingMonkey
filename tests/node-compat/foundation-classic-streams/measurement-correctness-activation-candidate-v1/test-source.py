"""Pure source/authority/scratch checks. No activation or backend import."""
from pathlib import Path
import ast,hashlib,importlib.util,json,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'measurement-correctness-candidate-v1'
AMEND=HERE.parent/'measurement-correctness-reporting-amendment-v1'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def main():
    assert len(sys.argv)in(2,6);output=Path(sys.argv[1]).absolute();assert str(output).startswith('/tmp/starling-node-compat/')and not output.exists();output.mkdir(parents=True,exist_ok=False)
    spec=importlib.util.spec_from_file_location('pure_correctness_authority',HERE/'authority.py');authority=importlib.util.module_from_spec(spec);spec.loader.exec_module(authority)
    checks=[]
    def check(name,value=True):assert value,name;checks.append(name)
    def rejected(name,document):
        raw=(json.dumps(document)+'\n').encode();path=output/('case'+str(len(checks))+'.json');path.write_bytes(raw)
        try:authority.load_authority(path,sha(raw),output/'must-not-read-review.json',sha(b'absent'))
        except(AssertionError,KeyError,TypeError):check(name)
        else:raise AssertionError('Unexpected authority acceptance')
    rejected('null authority refuses before artifact/output',None)
    rejected('checked-in future null template refuses',json.loads((HERE/'future-authority.json').read_bytes()))
    rejected('v2 authority cannot activate v3',{'schemaVersion':1,'state':'ROOT_REVIEWED_CLASSIC_TRACE_BENCHMARK_DIAGNOSTIC_FREEZES_V2'})
    rejected('unreviewed actual exporter state refuses',{'schemaVersion':1,'state':'UNREVIEWED_CLASSIC_TRACE_BENCHMARK_DIAGNOSTIC_PIN_CANDIDATES_V3'})
    rejected('production authority cannot become diagnostic',{'schemaVersion':1,'state':'REVIEWED_REAL_CLASSIC_TRACE_PRODUCTION_FREEZES_V1'})
    rejected('requested ON null refuses',{'schemaVersion':1,'state':'ROOT_REVIEWED_CLASSIC_TRACE_BENCHMARK_DIAGNOSTIC_FREEZES_V3','variants':{'benchmark-classic-on':None,'benchmark-classic-off':None}})
    invalid=output/'malformed.json';invalid.write_text('{bad')
    try:authority.document(invalid,sha(b'not same bytes'))
    except AssertionError:check('exact primitive authority hash before JSON parse')
    else:raise AssertionError('Malformed authority was parsed')
    for root,digest in [(BASE,'138a4e0bcfe22ef3b48375257a50958f595dcebb607fc9267a30080948d612da'),(AMEND,'0558b50589680f9e1b812c8a62210233a768385bfabeae2f07be47c2e1fe5350')]:
        raw=(root/'index.json').read_bytes();assert sha(raw)==digest
        for row in json.loads(raw)['files']:assert sha((root/row['path']).read_bytes())==row['sha256']
        check('immutable parent rehashed '+root.name)
    source=(HERE/'activate.py').read_text()
    check('exact authorities before genuine verifier import',source.index('load_authority(pin_path')<source.index("spec_from_file_location('benchmark_common'"))
    check('declared/canonical roots kept separate and realpath-bound','DECLARED.resolve(strict=True)==CANONICAL'in source)
    check('all40 producer files authenticated before verifier import',source.index('producer_rows=indexed(PRODUCER,PRODUCER_INDEX)')<source.index("spec_from_file_location('benchmark_common'"))
    check('genuine frozen verifier and source gate called, never projected','backend.require_source_root(CANONICAL)'in source and 'backend.verify_frozen(LABEL)'in source)
    check('all observed actual tuple values cross-bind reviewed pin','assert pin[key]==value'in source)
    check('afterimage/helper mandatory','regular(AMEND/\'proposed/component-driver.mjs\')'in source and "regular(AMEND/'bounded-comparison.mjs')"in source)
    check('whole source/addon/tool/frozen rows and original preparation included',all(x in source for x in ['metadata[\'sourceManifest\']','backend.capture_addons()','backend.tool_dependencies(CANONICAL)',"receipt['copies']","for root in [BASE,PRODUCER]"]))
    check('exact tool tree and link membership inherited',"tool_trees==original['toolTrees']and tool_links==original['toolLinks']"in source)
    inherited=json.loads((BASE/'inherited-inputs.json').read_bytes())
    for row in inherited['files']:
        assert sha((BASE/row['path']).read_bytes())==row['sha256']
        assert (BASE/row['path']).read_bytes()==(HERE.parents[3]/row['origin']).read_bytes()
    check('original workload/boundary/oracle/completion afterimages still exact',len(inherited['files'])==5)
    check('partial/existing/symlink output cannot be overwritten','not OUTPUT.is_symlink()'in source and 'not stage.is_symlink()'in source and "path.open('xb')"in source)
    check('post-stage authority/source recheck before publish',source.rfind('load_authority(pin_path')>source.index('stage.mkdir(exist_ok=False)')and'stage.rename(OUTPUT)'in source)
    for path in HERE.glob('*.py'):ast.parse(path.read_text());check('Python AST '+path.name)
    check('activation output absent',not(HERE.parent/'measurement-correctness-activated-v1').exists())
    check('activation staging absent',not(HERE.parent/'measurement-correctness-activated-v1.staging').exists())
    if len(sys.argv)==6:
        pins,_,review,_=authority.load_authority(*sys.argv[2:])
        check('actual caller-supplied Root JSON schema compatible as data only',pins['variants']['benchmark-classic-off']is None and review['runtimeAcceptanceClaim']is False)
    result={'schemaVersion':1,'state':'PURE_CORRECTNESS_ACTIVATION_SOURCE_AND_NEGATIVE_AUTHORITY_CHECKS_PASSED','passed':len(checks),'checks':checks,
      'actualRootPinsEmbedded':False,'actualRootAuthorityDataOnlyCompared':len(sys.argv)==6,'actionMainOrGenuineVerifierOrPreflightOrGuestOrNativeOrTargetHostInvoked':False,'activationOutputCreated':False}
    with(output/'results.json').open('x')as stream:json.dump(result,stream,indent=2);stream.write('\n')
    print(json.dumps({'passed':len(checks),'output':str(output)}))
if __name__=='__main__':main()
