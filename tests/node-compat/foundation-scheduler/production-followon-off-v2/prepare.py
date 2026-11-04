"""Finite packet-only transformations. Original sources are never written."""
from pathlib import Path
import hashlib
import json
import os
import re

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
STRICT = ['sync','runtime','late','callbacks']
SOURCES = {name:'tests/node-compat/foundation-add-abort/run-production-v11-'+name+'.mjs' for name in STRICT}
SOURCES['stream-web'] = 'tests/node-compat/foundation-stream-web/production-candidate/run-native-component-v11.mjs'
START = {'sync':'const prefix=', 'runtime':'const previous=', 'late':'const witWorld=',
         'callbacks':'const initialization=[];', 'stream-web':'const expected='}
END = {'stream-web':'const fixturePaths='}
sha = lambda value:hashlib.sha256(value).hexdigest()

def generate(name,original):
    old = REPO/SOURCES[name]
    target = HERE/'runners'/(name+'.mjs')
    text = original
    changes = []
    def replace(before,after,count=1):
        nonlocal text
        assert text.count(before) == count,(name,before,text.count(before))
        text = text.replace(before,after)
        changes.append({'before':before,'after':after,'count':count})
    for match in list(re.finditer(r"from (['\"])(\.[^'\"]+)\1",original)):
        spec = match.group(2)
        if spec.endswith('production-v11-preflight.mjs'):
            replace(match.group(0),"from '../../production-regression-candidate-v4/preflight.mjs'")
        else:
            relative = os.path.relpath((old.parent/spec).resolve(),target.parent).replace(os.sep,'/')
            if not relative.startswith('.'):
                relative = './'+relative
            replace(match.group(0),'from '+match.group(1)+relative+match.group(1))
    replace('{verifyProductionV11}','{verifyProductionTicks}')
    if name in STRICT:
        replace('const productionPreflight=await verifyProductionV11();',
                'const productionPreflight=(await verifyProductionTicks({gcStress:false})).report;')
    else:
        replace('const releasePreflight=await verifyProductionV11();',
                'const releasePreflight=await verifyProductionTicks({gcStress:false});')
        replace('const result={schema:1,', 'const result={schema:1,productionTickAdmission:releasePreflight.report,')
    # The real original fixture/oracle directories remain canonical.
    old_relative = os.path.relpath(old,target.parent).replace(os.sep,'/')
    replace('here=dirname(fileURLToPath(import.meta.url))',
            "here=dirname(fileURLToPath(new URL('"+old_relative+"',import.meta.url)))")
    if name in ['sync','runtime','callbacks']:
        replace("'sm-uncaught-event-v3-protected-abort-v2'",
                "'sm-uncaught-event-v3-protected-abort-v2-private-ticks-v1'")
    # Host report namespaces only. No vector/source/error marker is changed.
    if name in STRICT:
        filenames = {'callbacks':'callback'}
        suffix = filenames.get(name,name)
        old_report = 'production-v11-'+suffix+'-results.json'
        new_report = 'private-ticks-'+suffix+'-results.json'
        replace("join(here,'"+old_report+"')",
                "join("+('output' if name=='late' else 'h.output')+",'private-ticks-"+suffix+"-summary.json')")
        replace("'"+old_report+"'","'"+new_report+"'")
        states = {'sync':'strict-sync-acceptance-passed','runtime':'runtime-unhandled-boundary-acceptance-passed',
                  'late':'post-binding-acceptance-passed','callbacks':'finalizer-getter-cleanup-acceptance-passed'}
        replace("'production-v11-"+states[name]+"'","'production-private-ticks-"+states[name]+"'")
        if name!='late':
            kinds={'sync':'strict-event','runtime':'runtime','callbacks':'callbacks'}
            replace("kind:'production-v11-"+kinds[name]+"'","kind:'production-private-ticks-"+kinds[name]+"'")
    else:
        replace("join(here,'native-component-v11-results.json')","join(harness.output,'stream-web-summary.json')")
        replace('on new m0.11 core engine;','on production private-ticks m0.11 core engine;')
    # Update report-only statements that otherwise falsely name the old engine.
    for before,after in [
        ('Actual combined production v11 stream/web ON, entropy OFF engine with core m0.11;',
         'Actual combined production private-ticks stream/web ON, entropy OFF engine with core m0.11;'),
        ('Actual production v11 guest embedding patch;', 'Actual production private-ticks guest embedding layer;'),
        ('Actual combined production v11 OFF engine;', 'Actual combined production private-ticks OFF engine;'),
    ]:
        if before in text:
            replace(before,after)
    restored = text
    for change in reversed(changes):
        assert restored.count(change['after']) == change['count']
        restored = restored.replace(change['after'],change['before'])
    assert restored == original
    def block(value):
        end = END.get(name,'const report=')
        return value[value.index(START[name]):value.index(end)]
    assert block(text) == block(original),'Semantic case/control section changed'
    return text,changes,block(text)

expected = {row['path']:row['sha256'] for row in json.loads((HERE/'ancestry.json').read_text())['inputs']}
rows = []
for name,path in SOURCES.items():
    source = (REPO/path).read_bytes();assert sha(source)==expected[path]
    text,changes,semantic = generate(name,source.decode())
    target = HERE/'runners'/(name+'.mjs');target.write_text(text)
    rows.append({'name':name,'original':path,'originalSha256':sha(source),
                 'generated':str(target.relative_to(HERE)),'generatedSha256':sha(text.encode()),
                 'semanticBlockSha256':sha(semantic.encode()),'semanticBlockStart':START[name],
                 'semanticBlockEnd':END.get(name,'const report='),
                 'reverseDeclaredEditsRestoresOriginalBytes':True,'changes':changes})
(HERE/'runner-transformations.json').write_text(json.dumps({'state':'PACKET_ONLY_FINITE_ADMISSION_POLICY_PATH_AND_REPORT_EDITS','runners':rows},indent=2)+'\n')
print(json.dumps({'generatedBodies':len(rows),'originalFilesWritten':False,'semanticBlocksIdentical':5}))
