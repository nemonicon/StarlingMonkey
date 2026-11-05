"""Future GC-only UNREVIEWED pin export, from actual explicit-root verifier."""
from pathlib import Path
import importlib.util,json,sys
import context as C,guard
from data_io import write
def export(config):
    frame=guard.authorize(config,'export');common=guard.load_common(frame)
    spec=importlib.util.spec_from_file_location('gc_actual_pin_body',Path(__file__).parent/'export-body.py');body=importlib.util.module_from_spec(spec);spec.loader.exec_module(body)
    candidate=body.candidate('gc-off',Path(C.FREEZE),common)
    document=dict(schemaVersion=1,state='UNREVIEWED_CRYPTO_OWNER355_ISOLATED_GC_PIN_CANDIDATE_V1',variants={n:candidate if n=='gc-off'else None for n in ('normal-off','normal-runtime','gc-off','disabled-off')},requiresIndependentReviewAndNewRootNativeReview=True,consumerPinsModified=False,guestExecutedByExporter=False)
    output=frame['root']['pinCandidateOutput'];assert output==C.BUILD_OUTPUT+'/gc-pin.UNREVIEWED.json'
    guard.recheck(frame);write(output,document);guard.recheck(frame);return document
if __name__=='__main__':assert len(sys.argv)==2;print(json.dumps(export(json.loads(sys.argv[1]))))
