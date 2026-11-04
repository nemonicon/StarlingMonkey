"""Exercise only the recipe's external-source hash/capture block on tiny copies."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
def main():
    recipe=(HERE/'source/tests/node-compat/build-engine.sh').read_text()
    blocks=re.findall(r"<<'([A-Z][A-Z0-9_]*)'\n(.*?)\n\1(?:\n|$)",recipe,re.S)
    code=next(body for label,body in blocks if label=='PYEMBED')
    pins=json.loads((REPO/'tests/node-compat/foundation-classic-streams/production-runtime-activated-v3/runtime-pins.json').read_bytes())
    source=Path(pins['variants']['normal-off']['componentizeSourceRoot'])
    expected={'embedding/embedding.cpp':'9dcb63beaf55ff6af9ca4d2019316d4a167657c02ed76a1bf246012da0bcd205','embedding/embedding.h':'de2c1ae6c7f881902675d79e4bedaeece6953e70e1eac8291165ad0d5cd0eb0e','CMakeLists.txt':'4bd9bb94f5b79a2c9eb8ef7d98bc4b712e7b9cc2702467436a87e1845240c5e8'}
    root=Path('/tmp/starling-node-compat/trace-external3-source-data-v1');root.mkdir(exist_ok=False)
    rows=[]
    for i,changed in enumerate([None,*expected]):
        current=root/str(i)
        for name,digest in expected.items():
            raw=(source/name).read_bytes();assert hashlib.sha256(raw).hexdigest()==digest
            target=current/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw+(b'\n'if name==changed else b''))
        output=current/'capture.json'
        run=subprocess.run([sys.executable,'-c',code,str(current),str(output)],capture_output=True,text=True)
        assert run.returncode==(0 if changed is None else 1)
        assert output.exists()is(changed is None),'An unreviewed row must fail before capture publication'
        if changed is None:assert json.loads(output.read_bytes())==[{'path':name,'sha256':digest}for name,digest in expected.items()]
        rows.append({'changedCopyOnly':changed,'exitCode':run.returncode,'capturePublished':output.exists(),'stdout':run.stdout,'stderr':run.stderr})
    result={'schemaVersion':1,'state':'EXACT_EXTERNAL3_PRECONFIGURE_CAPTURE_DATA_TESTS_PASSED','passed':len(rows),'checks':rows,
      'unchangedInputs':expected,'sourceCopiesOnly':True,'configureCompilerProducerMainGuestOrTargetHostExecuted':False}
    (HERE/'evidence/external-capture-tests.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'state':result['state'],'passed':len(rows)}))
if __name__=='__main__':main()
