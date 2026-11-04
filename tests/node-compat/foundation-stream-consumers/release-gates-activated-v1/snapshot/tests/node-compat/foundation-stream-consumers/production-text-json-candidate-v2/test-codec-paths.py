"""CONS355-M1 physical path and AST checks before any future build; no imports."""
from pathlib import Path
import ast,hashlib,json,re
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
OLD=HERE.with_name('production-text-json-candidate-v1')
BASE=Path('/tmp/starling-node-compat/zlib-source-v4')
REL='tests/node-compat/foundation-zlib/native-integration-candidate-v4/codec-evidence.py'
SHA='3df425d7fcfaf241b7c8d6f889bcefb8efde229af8df5e4c610e18a49b1bfd0c'
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    checks=[]
    def check(name,ok):assert ok,name;checks.append(name)
    source=(HERE/'proposed/tests/node-compat/build-engine.sh').read_text()
    check('missingOldRelativeLookupRemoved',"codec_file=layer_file.parent/'codec-evidence.py'"not in source)
    expected="codec_file=pathlib.Path(repo)/'"+REL+"'"
    check('twoExplicitParent350PostLinkLookups',source.count(expected)==2)
    blocks=[ast.parse(m.group(2))for m in re.finditer(r"<<'([A-Z][A-Z0-9_]*)'\n(.*?)\n\1(?:\n|$)",source,re.S)]
    assigned=[node for tree in blocks for node in ast.walk(tree)if isinstance(node,ast.Assign)and any(isinstance(n,ast.Name)and n.id=='codec_file'for n in node.targets)]
    check('twoASTAssignments',len(assigned)==2)
    for node in assigned:
        expr=node.value
        assert isinstance(expr,ast.BinOp)and isinstance(expr.op,ast.Div)and isinstance(expr.right,ast.Constant)and expr.right.value==REL
        call=expr.left;assert isinstance(call,ast.Call)and isinstance(call.func,ast.Attribute)and isinstance(call.func.value,ast.Name)and call.func.value.id=='pathlib'and call.func.attr=='Path'
        assert len(call.args)==1 and isinstance(call.args[0],ast.Name)and call.args[0].id=='repo'
    check('bothLookupsUseActualRepositoryRoot',True)
    check('bothExistingExactDigestAssertions',source.count("assert digest(codec_file)=='"+SHA+"'")==2)
    records=[]
    for root in[REPO,BASE]:
        path=root/REL;check('actualParentHelper:'+str(root),path.is_file()and not path.is_symlink()and digest(path)==SHA)
        records.append({'path':str(path),'realpath':str(path.resolve()),'sha256':digest(path),'bytes':path.stat().st_size})
    for root in[OLD,HERE]:check('missingChildLookup:'+root.name,not(root/'codec-evidence.py').exists())
    check('shellUsesParentLayerRoot','layer_root="$repo_root/tests/node-compat/foundation-zlib/native-integration-candidate-v4"'in source and '"$layer_root/codec-evidence.py"'in source)
    check('pythonLayerAlreadyUsesAuthenticatedParent',"codec_file=HERE.parents[1]/'foundation-zlib/native-integration-candidate-v4/codec-evidence.py'"in(HERE/'layer-policy.py').read_text())
    check('unchanged355Manifest',digest(HERE/'expected-native-source-manifest.json')==digest(OLD/'expected-native-source-manifest.json'))
    rows=json.loads((HERE/'expected-native-source-manifest.json').read_bytes())
    for row in rows:
        child=HERE/'proposed'/row['path'];before=OLD/'proposed'/row['path']
        if child.exists():assert child.read_bytes()==before.read_bytes()
    check('allSevenNativeAfterimagesByteIdentical',True)
    for name in['policy.json','layer-policy.py','native.UNAPPLIED.patch']:
        check('unchangedNativeAuthority:'+name,digest(HERE/name)==digest(OLD/name))
    check('futurePinsStillNull',json.loads((HERE/'admission-pins.json').read_bytes())['reviewedFutureEnginePins']is None)
    # Actual old missing child and wrong known existing bytes are rejected by
    # the same path+hash precondition; never import or call the codec collector.
    def checked(root,relative):
        assert relative==REL
        path=root/relative;assert path.is_file()and not path.is_symlink()and digest(path)==SHA
        return path
    checked(REPO,REL)
    for root,relative in[(OLD,'codec-evidence.py'),(REPO,'tests/node-compat/foundation-zlib/native-integration-candidate-v4/layer-policy.py')]:
        try:checked(root,relative)
        except AssertionError:pass
        else:raise AssertionError('Unexpected helper lookup admitted')
    check('negativeUnknownAndMissingLookupRefused',True)
    print(json.dumps({'schemaVersion':1,'state':'CONS355_M1_SOURCE_PATH_CORRECTION_CHECKED','checks':checks,'passed':len(checks),'actualParentHelperInputs':records,'sourceOnly':True,'codecHelperImported':False,'nativeBuildFactoryGuestOrHostExecuted':False}))
if __name__=='__main__':main()
