"""Owned host-only source staging; never edits the repository or compiles code."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('destination');args=parser.parse_args()
    root=Path(args.destination).absolute();assert not root.exists(),'Use a fresh owned test root'
    policy=json.loads((HERE/'policy.json').read_bytes())
    plan={}
    for row in policy['parentExpectedNativeSourceManifest']:
        data=(REPO/row['path']).read_bytes();assert sha(data)==row['sha256'];plan[row['path']]=data
    for row in json.loads((HERE/'native-source-mapping.json').read_bytes())['files']:
        data=(HERE/'source'/row['path']).read_bytes();assert sha(data)==row['sha256'];plan[row['path']]=data
    for name in ['module-selection.mjs','classic-streams-admission.mjs']:
        plan['tests/node-compat/'+name]=(HERE/'source/tests/node-compat'/name).read_bytes()
    for name in ['private-ticks-admission.mjs','legacy-stream-web-receipts.json','profile-bundler.mjs']:
        plan['tests/node-compat/'+name]=(REPO/'tests/node-compat'/name).read_bytes()
    for name in ['foundation-scheduler/integration-candidate-v1/policy.json','foundation-scheduler/integration-candidate-v1/layer-policy.py','foundation-scheduler/admission-candidate-v1/pins.json']:
        plan['tests/node-compat/'+name]=(REPO/'tests/node-compat'/name).read_bytes()
    for name in ['policy.json','layer-policy.py','admission-pins.json']:
        plan['tests/node-compat/foundation-classic-streams/integration-candidate-v1/'+name]=(HERE/name).read_bytes()
    plan['package.json']=b'{"type":"module"}\n'
    root.mkdir(parents=True)
    for name,data in sorted(plan.items()):
        path=root/name;path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('xb')as stream:stream.write(data)
    print(json.dumps({'state':'OWNED_SOURCE_ONLY_HOST_TEST_ROOT','path':str(root),'files':len(plan),'nativeInputs':342,'compilerInvoked':False,'guestInvoked':False}))
if __name__=='__main__':main()
