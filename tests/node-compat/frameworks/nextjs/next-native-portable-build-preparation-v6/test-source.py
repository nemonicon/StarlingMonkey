"""Source/policy invariants only; do not import preparation/action entrypoints."""
from pathlib import Path
import ast
import hashlib
import json

HERE=Path(__file__).resolve().parent
OLD=HERE.parent/'next-native-portable-build-preparation-v5'


def row(p):
    b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))


if __name__=='__main__':
    before=json.loads((OLD/'plan.json').read_bytes());after=json.loads((HERE/'plan.json').read_bytes())
    assert {k for k in after if after[k]!=before[k]}=={'portableSourcePolicy','portableCargoPolicy'}
    for name in ['run.py','prepare.py','cargo-selection.py','root-authority.template.json']:
        assert (HERE/name).read_bytes()==(OLD/name).read_bytes()
    assert (HERE/'portable.py').read_bytes()==(HERE.parent/'next-native-portable-build-preparation-v2/portable.py').read_bytes()
    policy=after['portableSourcePolicy'];old=before['portableSourcePolicy']
    assert {k for k in policy if policy[k]!=old[k]}=={'materializerIndex','materializerSelection','expectedBytes','roleContentSha256'}
    assert policy['expectedCounts']==old['expectedCounts']=={'native-policy-source':435,'build-support':387,'componentize-embedding':3}
    assert policy['expectedFiles']==825 and policy['expectedBytes']==7548976
    assert policy['roleContentSha256']=='89331d9264f7807ed5241d109531e1131d4e79ce588596e1d9e30a1a706bbc27'
    mat_index=HERE.parent/'next-native-portable-source-v4/index.json'
    assert all(row(mat_index)[k]==policy['materializerIndex'][k]for k in ['sha256','bytes'])
    assert policy['materializerSelection']['repositoryPath']=='tests/node-compat/frameworks/nextjs/next-native-portable-source-v4/selection.json'
    mat=HERE.parent/'next-native-portable-source-v4/selection.json';assert all(row(mat)[k]==policy['materializerSelection'][k]for k in ['sha256','bytes'])
    assert after['portableAdmissionSourceIndex']==before['portableAdmissionSourceIndex'] and after['portableAdmissionModule']==before['portableAdmissionModule']
    assert after['portableCargoPolicy']==dict(before['portableCargoPolicy'],helper=row(HERE/'cargo-selection.py'))
    for key in ['disk','timeouts','cmakeAdditions','wrapperPython','baseRunner','basePlan']:
        assert after[key]==before[key]
    assert after['actionsAllowed']is False
    template=json.loads((HERE/'root-authority.template.json').read_bytes())
    for key in ['workRoot','configureAllowed','buildAllowed','installedGeneratorResult','portableSelection','portableCargoSelection']:
        assert template[key]is None
    for q in HERE.glob('*.py'):ast.parse(q.read_text())
    print(json.dumps(dict(sourceOnly=True,operationalFilesByteIdentical=4,localGeneratorAdmissionApiByteIdentical=True,
        newMaterializerIndexBound=True,newPhysicalSelectionOrGeneratorProofClaimed=False,
        nativeCommandsOrPreparationInvoked=False,cppCompiled=False)))
