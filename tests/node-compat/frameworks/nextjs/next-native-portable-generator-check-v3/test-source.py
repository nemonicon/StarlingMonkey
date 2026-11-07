"""Pure Source/plan checks; controller imported/invoked nowhere."""
from pathlib import Path
import ast
import hashlib
import json

HERE=Path(__file__).resolve().parent
OLD=HERE.parent/'next-native-portable-generator-check-v2'
BUILDER=HERE.parent/'next-native-portable-build-preparation-v5'


def row(p):
    b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))


if __name__=='__main__':
    old=json.loads((OLD/'plan.json').read_bytes());plan=json.loads((HERE/'plan.json').read_bytes())
    assert (HERE/'run.py').read_bytes()==(OLD/'run.py').read_bytes()
    assert {k for k in plan if plan[k]!=old[k]}=={'materializerIndex','materializationRoot','sourceRoot','composition','materializationSummary','roleContentSha256','portableAdmission'}
    assert plan['materializerIndex']==row(HERE.parent/'next-native-portable-source-v3/index.json')
    physical=Path(plan['materializationRoot'])
    assert plan['composition']==row(physical/'composition.json')
    assert plan['materializationSummary']==row(physical/'source-materialization.json')
    actual=json.loads((physical/'source-materialization.json').read_text())
    composition=json.loads((physical/'composition.json').read_text())
    assert actual['composition']==plan['composition'] and actual['files']==825 and actual['bytes']==7548909
    assert actual['roleContentSha256']==plan['roleContentSha256'] and composition['sourceRoot']==plan['sourceRoot']
    assert actual['compilerOrGuestExecuted']is actual['generatedBuildMetadataProjected']is False
    assert plan['portableAdmission']['sourceIndex']==row(BUILDER/'index.json')
    pending=json.loads((HERE/'pending-bindings.json').read_text())
    selection_ref=pending['actualPortableSelection'];assert selection_ref==row(Path(selection_ref['path']))
    selection=json.loads(Path(selection_ref['path']).read_text())
    assert selection['composition']==plan['composition'] and selection['sourceMaterialization']==plan['materializationSummary']
    assert selection['sourceRoot']==plan['sourceRoot'] and selection['roleContentSha256']==plan['roleContentSha256']
    assert len(selection['physicalRecords'])==825 and len(selection['directoryRecords'])==171
    assert plan['portableAdmission']['module']==row(BUILDER/'portable.py') and plan['portableAdmission']['plan']==row(BUILDER/'plan.json')
    assert Path(plan['portableAdmission']['module']['path']).parent==Path(plan['portableAdmission']['plan']['path']).parent
    assert plan['roleContentSha256']!=old['roleContentSha256'] and plan['sourceRoot']!=old['sourceRoot']
    assert plan['sourceRoot']==plan['materializationRoot']+'/source'
    assert plan['roleContentSha256']=='77346c39fb532ac32e8c50e4988d8a77ee367b13e4493ec6d82964e5b074d14a'
    assert plan['expectedRoleCounts']==old['expectedRoleCounts']
    for key in ['node','monitor','python','commandDonor','outputPrefix','perCommandSeconds','outerSeconds','minimumFreeBytes','maxAcceptedRawStreamBytes','maxAcceptedOutputBytes']:
        assert plan[key]==old[key]
    assert plan['perCommandSeconds']==30 and plan['outerSeconds']==900
    for key in ['actualRootAuthority','actualRuntime','actualGeneratorProof']:assert plan[key]is None
    ast.parse((HERE/'run.py').read_text());ast.parse((HERE/'test-source.py').read_text())
    print(json.dumps(dict(sourceOnly=True,controllerByteIdentical=True,commandsAndOwnershipCapsUnchanged=True,
        actualCompositionAndSummaryBound=True,newPhysicalSelectionDataBound=True,builderSourceIndexBound=True,
        actualGeneratorAuthorityAndProofPending=True,oldProofRetargeted=False,generatorsOrActorInvoked=False)))
