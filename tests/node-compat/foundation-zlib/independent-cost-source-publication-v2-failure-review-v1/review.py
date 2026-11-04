"""Read-only M3 audit; stdout only, no owner module imports/actions."""
from pathlib import Path
import hashlib,json,stat
HERE=Path(__file__).resolve().parent
BASE=HERE.parent
ROOT=BASE/'cost-source-publication-v2-precopy-failure-root-results.json'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
assert sha(ROOT)=='072dafb208503a2f3b45d69f0230abb3d4104240e2c02962c6d83c00be789457'
root=json.loads(ROOT.read_bytes())
for name in ['authority','sourceIndex','terminal','stdout','stderr','modeAudit']:
    row=root[name];path=Path(row['path']);assert sha(path)==row['sha256']and path.stat().st_size==row['bytes']
authority=json.loads(Path(root['authority']['path']).read_bytes())
capsules=[]
for name in ['sourceIndependentReview','rootReviewedPair']:
    proof=authority[name];path=Path(proof['index']['path']);assert sha(path)==proof['index']['sha256']
    index=json.loads(path.read_bytes());members=[path]+[path.parent/row['path']for row in index['files']]
    for member in members:
        info=member.lstat();assert stat.S_ISREG(info.st_mode)and stat.S_IMODE(info.st_mode)==0o644
        capsules.append(str(member))
assert len(capsules)==20
owner=BASE/'cost-tooling-candidate-v2'
assert sha(owner/'index.json')=='6793721e6781bf045825f2a1c83108f97136f682fdae4d725ece4c31c750891b'
plan=json.loads((owner/'publication-plan.json').read_bytes());assert len(plan['objects'])==5058
for row in plan['objects']:assert stat.S_IMODE(Path(row['source']).lstat().st_mode)==row['mode']
publisher=(owner/'publish.py').read_text()
assert "if 'mode'in row:need(stat.S_IMODE(before.st_mode)==row['mode'],'Source permission drift')"in publisher
assert "'mode':0o600,'role':tag"in publisher
assert publisher.index('for r in objects:source(r)')<publisher.index('root=Publication(DESTINATION)')
try:Path('/tmp/starling-node-compat/zlib-cost-source-v2').lstat();raise AssertionError('Target appeared')
except FileNotFoundError:pass
assert json.loads(Path(root['terminal']['path']).read_bytes())['rawExitCode']==1
print(json.dumps({'state':'INDEPENDENT_COST_TOOLING_M3_PRECOPY_FAILURE_CONFIRMED','baseModeMismatches':0,'dynamicOriginalModes':'0644','misappliedOutputMode':'0600','dynamicMismatches':20,'destinationAbsent':True,'ownerActionInvoked':False}))
