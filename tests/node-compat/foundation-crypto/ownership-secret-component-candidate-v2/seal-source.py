"""Seal this fresh source packet; no owner or guest operation is performed."""
from pathlib import Path
import ast
import hashlib
import json

HERE = Path(__file__).resolve().parent
assert not (HERE / 'index.json').exists()


def row(path):
    p = Path(path)
    b = p.read_bytes()
    return dict(path=str(p), sha256=hashlib.sha256(b).hexdigest(), bytes=len(b))


def read(name):
    return json.loads((HERE / name).read_bytes())


def write(name, value):
    with (HERE / name).open('x') as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write('\n')


closure = read('closure-verification.json')
pure = read('pure-results.json')
refs = read('references.json')
assert closure['files'] == 33364 and closure['families'] == 27
assert closure['fullHashesPassed'] and closure['fullFamilyMembershipPassed'] and closure['finalIdentitiesPassed']
assert pure['checks'] == 20 and pure['passed'] and pure['inertModuleImported']
assert not pure['constructionApiInvoked'] and not pure['packagerImported'] and not pure['engineOrGuestExecuted']
for p in HERE.rglob('*.py'):
    ast.parse(p.read_bytes(), filename=str(p))
write('results.json', dict(schemaVersion=1, state='SECRET_OWNER355_COMPONENT_CONSTRUCTION_SOURCE_SEALED_UNREVIEWED_V2',
                          sourceOnly=True, sourceRoot=str(HERE), constructionEntry=row(HERE / 'build.mjs'),
                          parentSourceIndex=refs['parentSourceIndex'], priorConstructionFailureReview=refs['priorConstructionFailureReview'],
                          retainedSourceIndex=refs['retainedSourceIndex'], actualRetainedPreflightReview=refs['actualRetainedPreflightReview'],
                          nativeEngine=refs['engine'], metadata=refs['metadata'], freezeReceipt=refs['freezeReceipt'],
                          nativeSourceFiles=355, externalEmbeddingSources=3, selectedWholeManifests=11, rawMetadataFields=75,
                          guest=refs['guest'], wit=refs['wit'], guestAndAbiByteExact=True, fullPrototypeCase3Preserved=True,
                          requiredPackagingEnvironment=refs['requiredPackagingEnvironment'], physicalRoles=refs['physicalRoles'],
                          sourceInputFiles=closure['files'], completeFamilies=closure['families'], logicalProtectedBytes=closure['logicalBytes'],
                          pureChecks=pure['checks'], inertModuleImported=True, constructorApiInvoked=False,
                          actualRetainedApiInvoked=False, packagerOrComponentizerInvoked=False, engineOrGuestExecuted=False,
                          ordinaryGuestExportsInvoked=False, keyOperationsInvoked=False, generatedModuleImported=False,
                          sourceIndependentReview=None, rootAuthority=None, actualComponent=None, actualRuntimeAuthority=None,
                          operationalAdmission=False, runtimeAcceptanceClaim=False,
                          remainingGates=['Independent source review', 'Fresh explicit Root construction phase and owned raw lifecycle',
                                          'Actual whole component/ABI/loading-protocol review', 'Separate full retained/fresh guarded runtime validation']))
write('source-receipt.json', dict(schemaVersion=1, sourceOnly=True, result=row(HERE / 'results.json'),
                                 sourceInputs=row(HERE / 'source-inputs.json'), closure=row(HERE / 'closure-verification.json'),
                                 pureChecks=row(HERE / 'pure-results.json'), sourceIndependentReview=None, rootAuthority=None,
                                 ownerActionsInvoked=False, operationalAdmission=False))
members = []
for p in sorted(HERE.rglob('*')):
    assert not p.is_symlink()
    if p.is_file():
        members.append(dict(row(p), path=p.relative_to(HERE).as_posix()))
write('index.json', dict(schemaVersion=1, files=members))
assert {p.relative_to(HERE).as_posix() for p in HERE.rglob('*') if p.is_file()} == {'index.json'} | {r['path'] for r in members}
for r in members:
    assert row(HERE / r['path']) == dict(r, path=str(HERE / r['path']))
print(json.dumps(dict(index=row(HERE / 'index.json'), result=row(HERE / 'results.json'), members=len(members)), indent=2))
