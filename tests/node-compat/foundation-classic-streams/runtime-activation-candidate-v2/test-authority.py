"""Owned negative documents only; no artifact imports, fabricated engine pins or output."""
import hashlib
import json
from pathlib import Path
import tempfile
from authority import LABELS, load_authority, read_document

root = Path(tempfile.mkdtemp(prefix='classic-activation-authority-v1-', dir='/tmp/starling-node-compat'))
checks = []
def negative(name, document):
    path = root / (str(len(checks)) + '.json')
    data = json.dumps(document).encode(); path.write_bytes(data)
    try: load_authority(path, hashlib.sha256(data).hexdigest(), root / 'must-not-be-read.json', hashlib.sha256(b'not read').hexdigest())
    except (AssertionError, KeyError, TypeError): checks.append(name)
    else: raise AssertionError('Unexpected admission')
negative('null document refused', None)
negative('unconfigured pins refused before review file access', {'schemaVersion':1,'state':'UNCONFIGURED_CLASSIC_PRODUCTION_FREEZES','variants':{x:None for x in LABELS}})
negative('unreviewed exporter refused before review file access', {'schemaVersion':1,'state':'UNREVIEWED_CLASSIC_PRODUCTION_PIN_CANDIDATES_V1','variants':{x:None for x in LABELS}})
negative('reviewed outer label cannot admit null rows', {'schemaVersion':1,'state':'REVIEWED_REAL_CLASSIC_PRODUCTION_FREEZES_V1','variants':{x:None for x in LABELS}})
negative('missing label refused', {'schemaVersion':1,'state':'REVIEWED_REAL_CLASSIC_PRODUCTION_FREEZES_V1','variants':{}})
path=root/'changed.json';path.write_bytes(b'{broken')
try: read_document(path,hashlib.sha256(b'prior').hexdigest())
except AssertionError: checks.append('document hash checked before parsing')
else: raise AssertionError('Changed authority parsed')
result={'schemaVersion':1,'state':'AUTHORITY_NEGATIVE_DOCUMENT_CHECKS_PASSED','passed':len(checks),'failures':0,'checks':checks,'output':str(root),
        'actualOrSyntheticEnginePinsUsed':False,'artifactModuleImported':False,'activationOutputCreated':False,'guestExecuted':False}
(root/'results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
