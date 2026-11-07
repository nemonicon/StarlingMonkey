"""Pure Source/plan checks; controller imported/invoked nowhere."""
from pathlib import Path
import ast
import hashlib
import json

HERE=Path(__file__).resolve().parent
OLD=HERE.parent/'next-native-portable-generator-check-v1'
BUILDER=HERE.parent/'next-native-portable-build-preparation-v4'


def row(p):
    b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))


if __name__=='__main__':
    old=json.loads((OLD/'plan.json').read_bytes());plan=json.loads((HERE/'plan.json').read_bytes())
    assert (HERE/'run.py').read_bytes()==(OLD/'run.py').read_bytes()
    assert {k for k in plan if plan[k]!=old[k]}=={'materializerIndex','materializationRoot','sourceRoot','composition','materializationSummary','roleContentSha256','portableAdmission'}
    assert plan['materializerIndex']==row(HERE.parent/'next-native-portable-source-v2/index.json')
    physical=Path(plan['materializationRoot'])
    assert plan['composition']==row(physical/'composition.json')
    assert plan['materializationSummary']==row(physical/'source-materialization.json')
    actual=json.loads((HERE.parent/'next-module-boundary-native-root-results-v1/portable-selection.json').read_text())
    assert actual['composition']==plan['composition'] and actual['sourceMaterialization']==plan['materializationSummary']
    assert actual['sourceRoot']==plan['sourceRoot'] and actual['roleContentSha256']==plan['roleContentSha256']
    assert plan['portableAdmission']['sourceIndex']==row(BUILDER/'index.json')
    assert plan['portableAdmission']['module']==row(BUILDER/'portable.py') and plan['portableAdmission']['plan']==row(BUILDER/'plan.json')
    assert Path(plan['portableAdmission']['module']['path']).parent==Path(plan['portableAdmission']['plan']['path']).parent
    assert plan['roleContentSha256']!=old['roleContentSha256'] and plan['sourceRoot']!=old['sourceRoot']
    assert plan['sourceRoot']==plan['materializationRoot']+'/source'
    assert plan['roleContentSha256']=='cfbd75be70aeaa36006009fa6580b8f0f4bb789852e8d8201eefefd09d0a1550'
    assert plan['expectedRoleCounts']==old['expectedRoleCounts']
    for key in ['node','monitor','python','commandDonor','outputPrefix','perCommandSeconds','outerSeconds','minimumFreeBytes','maxAcceptedRawStreamBytes','maxAcceptedOutputBytes']:
        assert plan[key]==old[key]
    assert plan['perCommandSeconds']==30 and plan['outerSeconds']==900
    for key in ['actualRootAuthority','actualRuntime','actualGeneratorProof']:assert plan[key]is None
    ast.parse((HERE/'run.py').read_text());ast.parse((HERE/'test-source.py').read_text())
    print(json.dumps(dict(sourceOnly=True,controllerByteIdentical=True,commandsAndOwnershipCapsUnchanged=True,
        freshPhysicalDescriptorsBound=True,actualGeneratorAuthorityAndProofPending=True,oldProofRetargeted=False,generatorsOrActorInvoked=False)))
