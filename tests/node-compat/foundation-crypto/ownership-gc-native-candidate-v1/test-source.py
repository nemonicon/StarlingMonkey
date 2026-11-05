"""Pure models, source AST and retained DATA hashing; no action module imports."""
from pathlib import Path
import ast,hashlib,json,os,tempfile,sys
import context as C
from pin_model import select
from data_io import regular,descriptor,write
HERE=Path(__file__).resolve().parent;K=HERE.parent;checks=0
def check(v):
    global checks
    assert v;checks+=1
def rejects(f):
    global checks
    try:f()
    except (AssertionError,KeyError,TypeError):checks+=1;return
    raise AssertionError('Negative accepted')
root=json.loads((HERE/'future-root-authority.template.json').read_bytes())
for phase in C.PHASES:rejects(lambda phase=phase:C.phase_model(root,phase,'0'*64))
for phase in C.PHASES:
    synthetic=dict(root,state=C.AUTHORITY_STATE,phase=phase,sourceIndexSha256='0'*64)
    synthetic[phase+'Allowed']=True;check(C.phase_model(synthetic,phase,'0'*64))
    for field,value in [('normalMutationAllowed',True),('metadataProjectionAllowed',True),('configuredSourceRoot',C.NORMAL_SOURCE),('workRoot','/private/tmp/starling-node-compat/crypto-owner-v2-build'),('freezeRoot','/private/tmp/starling-node-compat/production-crypto-owner-v2/native-freeze')]:
        rejects(lambda field=field,value=value:C.phase_model({**synthetic,field:value},phase,'0'*64))
    rejects(lambda:C.phase_model(synthetic,phase,'1'*64))
refs=json.loads((HERE/'references.json').read_bytes())
normal_metadata=json.loads(Path('/private/tmp/starling-node-compat/production-crypto-owner-v2/native-freeze/normal-off.engine.wasm.build.json').read_bytes())
rejects(lambda:C.metadata_model(normal_metadata))
normal_pin=None
proof=json.loads((K/'independent-native-v2-validation-bootstrap-results-review-v1/results.json').read_bytes())
paths=[]
def collect(v):
    if isinstance(v,dict):
        if {'path','sha256','bytes'}<=v.keys()and v['sha256']=='e6bdb310607ff972133db03ac46c8047cdd2d80fceb4a2d1dcb62d68c8e943a9':paths.append(v)
        for x in v.values():collect(x)
    elif isinstance(v,list):
        for x in v:collect(x)
collect(proof)
for r in paths:
    p=regular(r);d=json.loads(p.read_bytes())
    if d.get('state')=='ROOT_REVIEWED_CRYPTO_OWNER355_VALIDATION_BOOTSTRAP_V2':normal_pin=d;break
check(normal_pin is not None);rejects(lambda:select(normal_pin,{},'0'*64,'1'*64))
rejects(lambda:select(json.loads((HERE/'future-gc-pins.template.json').read_bytes()),{},'0'*64,'1'*64))
check(Path(C.TOOLS).parents[4]==Path(C.SOURCE))
check(Path(C.NORMAL_SOURCE+'/tests/node-compat/foundation-crypto/native-integration-candidate-v2/artifact-tools').parents[4]!=Path(C.SOURCE))
common_source=Path(C.NORMAL_SOURCE+'/tests/node-compat/foundation-crypto/native-integration-candidate-v2/artifact-tools/artifact_common.py').read_text();common_ast=ast.parse(common_source)
for name in ['destination','validate_plan','execute_plan','verify_frozen_variant']:
    fn=next(x for x in common_ast.body if isinstance(x,ast.FunctionDef)and x.name==name);check('output' in [x.arg for x in fn.args.args])
count=0
for p in HERE.glob('*.py'):
    tree=ast.parse(p.read_text());count+=1
    for node in ast.walk(tree):
        if isinstance(node,(ast.Assign,ast.AnnAssign,ast.AugAssign)):
            targets=node.targets if isinstance(node,ast.Assign)else[node.target]
            for target in targets:check(not(isinstance(target,ast.Attribute)and isinstance(target.value,ast.Name)and target.value.id=='common'and target.attr in ['HERE','REPO','OUTPUT']))
deriv=json.loads((HERE/'freezer-derivations.json').read_bytes());body=(HERE/'freezer-body.py').read_text();check(body.startswith(deriv['prefix']));body=body[len(deriv['prefix']):]
for edit in reversed(deriv['edits']):check(body.count(edit['after'])==edit['count']);body=body.replace(edit['after'],edit['before'])
original=regular(deriv['source']).read_text();check(body==original[original.index(deriv['extractStart']):original.index(deriv['extractEnd'])])
export=json.loads((HERE/'export-derivations.json').read_bytes());text=(HERE/'export-body.py').read_text().split('\n',1)[1];check(text.count(export['after'])==1);text=text.replace(export['after'],export['before']);old=regular(export['source']).read_text();check(text==old[old.index(export['extractStart']):old.index(export['extractEnd'])])
inputs=json.loads((HERE/'input-freeze.json').read_bytes())
for r in inputs['files']:regular(r);checks+=1
scratch=Path(tempfile.mkdtemp(prefix='crypto-owner355-gc-source-tests-v1-',dir='/private/tmp/starling-node-compat'));p=scratch/'fixture.txt';p.write_bytes(b'benign immutable descriptor fixture\n');d=descriptor(p);check(regular(d)==p);rejects(lambda:regular({**d,'bytes':d['bytes']+1}));rejects(lambda:regular({**d,'sha256':'0'*64}));link=scratch/'symlink';link.symlink_to(p);rejects(lambda:regular({**d,'path':str(link)}))
for path in [C.SOURCE,C.WORK,C.FREEZE,C.BUILD_OUTPUT,C.JOURNAL]:check(not Path(path).exists())
protection=json.loads((HERE/'normal-protection.json').read_bytes());freeze=Path(protection['freezeReceipt']['path']).parent;check({p.relative_to(freeze).as_posix()for p in freeze.rglob('*')if p.is_file()}==set(protection['requiredNormalFreezeMembership']))
name=sys.argv[1]if len(sys.argv)==2 else'source-test-results.json';assert '/'not in name and name.endswith('.json')
write(HERE/name,dict(schemaVersion=1,state='READ_HASH_PURE_MODELS_AND_SOURCE_AST_PASSED',checks=checks,pythonAstModules=count,actualInputRowsRehashed=len(inputs['files']),freezerExactReversals=len(deriv['edits']),exportExactReversals=1,scratchOutput=str(scratch),sourceActionModulesImported=False,ownerHelpersOrBootstrapPreflightOrNativeBuildFreezeExportGuestCryptoGcActionsInvoked=False,syntheticPositivePhaseModelsArePureDataOnly=True,normalMetadataAndNormalPinRejectedWithoutProjection=True,noGcDestinationsCreated=True))
print(json.dumps(dict(checks=checks,pythonAstModules=count,inputs=len(inputs['files']),ownerActionsInvoked=False,scratchOutput=str(scratch))))
