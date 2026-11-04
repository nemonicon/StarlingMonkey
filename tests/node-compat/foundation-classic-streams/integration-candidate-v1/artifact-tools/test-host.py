"""Pure classifier/source and owned tiny-text tests; no artifact-tool main."""
import sys
sys.dont_write_bytecode = True
import ast
import json
import os
from pathlib import Path
import tempfile
from artifact_common import (HERE, REPO, RECIPE, LABELS, classify, compile_command, manifest,
    embedding_command, validate_plan, execute_plan, checked_below, sha, digest, capture_regular)

results = []
def check(name, operation):
    operation()
    results.append({'name': name, 'passed': True})
def equal(a, b):
    assert a == b

def rejects(operation):
    try:
        operation()
    except (AssertionError, FileExistsError, FileNotFoundError, ValueError):
        return
    raise AssertionError('Malformed fixture accepted')

def base(label='normal-off'):
    return {'buildRecipeSha256': RECIPE, 'gcStress': label == 'gc-off',
        'entropyPolicy': 'runtime-only' if label == 'normal-runtime' else 'off',
        'classicStreamsEnabled': label != 'disabled-off',
        **{name: True for name in ('profileEnabled','pathEnabled','eventsEnabled','stringDecoderEnabled',
           'assertEnabled','querystringEnabled','utilEnabled','streamWebEnabled','internalTicksEnabled',
           'strictInitialization','abiFixEnabled','bigIntFixEnabled')},
        **{name: False for name in ('oomTesting','debuggerEnabled','wptSupportEnabled')}}

def main():
    output = Path(os.environ.get('NODE_COMPAT_CLASSIC_ARTIFACT_TEST_OUTPUT', str(HERE/'python-test-results.json')))
    assert not output.exists()
    for label in LABELS:
        model = base(label)
        check('pure-label-' + label, lambda m=model, l=label: equal(classify(m,l),(m['gcStress'],m['entropyPolicy'])))
    for name, change in [('old306-recipe', {'buildRecipeSha256':'869d188de3843b5d527d236a9e5c9af6ba1193f118dc9ad786df6266e1606173'}),
        ('synthetic',{'syntheticMetadataOnly':True}),('diagnostic',{'diagnosticOnly':True}),
        ('diagnostic-null',{'diagnosticOnly':None}),('diagnostic-policy',{'internalTickDiagnosticPolicy':{}}),
        ('wrong-classic',{'classicStreamsEnabled':False}),('wrong-gc',{'gcStress':True}),
        ('wrong-entropy',{'entropyPolicy':'runtime-only'}),('missing-ticks',{'internalTicksEnabled':False}),
        ('missing-foundation',{'utilEnabled':False}),('oom',{'oomTesting':True})]:
        check('classify-reject-' + name,lambda c=change: rejects(lambda: classify({**base(),**c},'normal-off')))
    check('unknown-label-rejected',lambda: rejects(lambda: classify(base(),'gc-runtime')))
    check('disabled-needs-classic-false',lambda: rejects(lambda: classify(base(),'disabled-off')))
    args='clang++ -O3 -DNDEBUG -DNODE_COMPAT_INTERNAL_TICKS=1 -DNODE_COMPAT_STRICT_INITIALIZATION=1 -DNODE_COMPAT_EVENTS_ADD_ABORT_LISTENER=1 -DNODE_COMPAT_ENTROPY_POLICY=1 -c /owned/runtime/event_loop.cpp -o out.o'
    check('nonprivate-command',lambda: compile_command(args,False,'runtime/event_loop.cpp'))
    check('embedding-without-private-macros',lambda:compile_command(args.replace('/owned/runtime/event_loop.cpp','/owned/embedding/embedding.cpp'),False,'embedding/embedding.cpp'))
    private=args.replace('/owned/runtime/event_loop.cpp','/owned/builtins/node-compat/register.cpp')+' -DNODE_COMPAT_STREAM_WEB=1 -DNODE_COMPAT_CLASSIC_STREAMS=1'
    check('private-classic-command',lambda: compile_command(private,False,'builtins/node-compat/register.cpp'))
    check('private-gc-all-target-TUs',lambda: compile_command(private+' -DNODE_COMPAT_GC_STRESS=1',False,'builtins/node-compat/register.cpp',True,True))
    check('disabled-private-without-classic',lambda: compile_command(private.replace(' -DNODE_COMPAT_CLASSIC_STREAMS=1',''),False,'builtins/node-compat/register.cpp',False))
    check('runtime-command',lambda: compile_command(args+' -DNODE_COMPAT_ENTROPY_RUNTIME_ONLY=1',True,'runtime/event_loop.cpp'))
    for name, command, runtime, source, classic, gc in [
      ('classic-on-runtime',args+' -DNODE_COMPAT_CLASSIC_STREAMS=1',False,'runtime/event_loop.cpp',True,False),
      ('gc-on-embedding',args+' -DNODE_COMPAT_GC_STRESS=1',False,'embedding/embedding.cpp',True,True),
      ('missing-private-gc',private,False,'builtins/node-compat/register.cpp',True,True),
      ('entropy-policy-missing',args.replace(' -DNODE_COMPAT_ENTROPY_POLICY=1',''),False,'runtime/event_loop.cpp',True,False),
      ('debug',args+' -DDEBUG=1',False,'runtime/event_loop.cpp',True,False),
      ('undef-release',args+' -UNDEBUG',False,'runtime/event_loop.cpp',True,False),
      ('syntax-only',args+' -fsyntax-only',False,'runtime/event_loop.cpp',True,False),
      ('standalone-D',args+' -D UNREVIEWED=1',False,'runtime/event_loop.cpp',True,False),
      ('standalone-U',args+' -U UNREVIEWED',False,'runtime/event_loop.cpp',True,False),
      ('undef-base',args+' -UNODE_COMPAT_INTERNAL_TICKS',False,'runtime/event_loop.cpp',True,False),
      ('undef-runtime',args+' -UNODE_COMPAT_ENTROPY_RUNTIME_ONLY',False,'runtime/event_loop.cpp',True,False),
      ('wrong-input',args.replace('/owned/runtime/event_loop.cpp','/owned/runtime/other.cpp'),False,'runtime/event_loop.cpp',True,False),
      ('wrong-runtime',args+' -DNODE_COMPAT_ENTROPY_RUNTIME_ONLY=0',True,'runtime/event_loop.cpp',True,False),
      ('duplicate-classic',private+' -DNODE_COMPAT_CLASSIC_STREAMS=1',False,'builtins/node-compat/register.cpp',True,False)]:
        check('command-reject-'+name,lambda c=command,r=runtime,s=source,e=classic,g=gc: rejects(lambda:compile_command(c,r,s,e,g)))
    raw=b'ninja: Entering directory\nclang++ -O3 -c /owned/embedding/embedding.cpp -o x.o\n'
    check('after-only-parent-select',lambda:equal(embedding_command(raw,'/owned/embedding/embedding.cpp'),['clang++ -O3 -c /owned/embedding/embedding.cpp -o x.o']))
    check('duplicate-parent-rejected',lambda:rejects(lambda:embedding_command(raw+raw,'/owned/embedding/embedding.cpp')))
    with tempfile.TemporaryDirectory(prefix='classic342-artifacts-owned-text-') as temp:
        root=Path(temp);source=root/'input.txt';source.write_text('owned plain text\n');target=root/'freeze'/'copy.txt';receipt=root/'freeze'/'receipt.json'
        row={'original':source,'target':target,'sha256':sha(source),'shared':False}
        check('regular-capture',lambda:equal(capture_regular(source),(source.read_bytes(),sha(source))))
        check('bad-plan-before-first-copy',lambda:rejects(lambda:validate_plan([row,{**row,'target':root/'escape'}],receipt,root/'freeze')))
        check('invalid-plan-no-output',lambda:equal(target.exists(),False))
        check('prevalidate-plan',lambda:validate_plan([row],receipt,root/'freeze'))
        check('exclusive-tiny-text-copy',lambda:execute_plan([row],root/'freeze'))
        check('copied-bytes',lambda:equal(target.read_bytes(),source.read_bytes()))
        check('no-variant-overwrite',lambda:rejects(lambda:validate_plan([row],receipt,root/'freeze')))
        check('shared-identical-only',lambda:validate_plan([{**row,'shared':True}],receipt,root/'freeze'))
        check('wrong-shared-hash',lambda:rejects(lambda:validate_plan([{**row,'shared':True,'sha256':'1'*64}],receipt,root/'freeze')))
        alias=root/'alias';alias.symlink_to(source)
        check('source-leaf-symlink-rejected',lambda:rejects(lambda:checked_below(root,'alias',sha(source))))
        check('source-parent-escape-rejected',lambda:rejects(lambda:checked_below(root,'../input.txt',sha(source))))
        check('duplicate-target-rejected',lambda:rejects(lambda:validate_plan([row,row],receipt,root/'freeze')))
    original=(HERE/'ancestry/production-artifacts-v1/build-one.py').read_text();new=(HERE/'build-one.py').read_text()
    old_tree,new_tree=ast.parse(original),ast.parse(new)
    definitions=[row for row in old_tree.body if isinstance(row,(ast.FunctionDef,ast.ClassDef)) and row.name!='main']
    assert len(definitions)==8
    for row in definitions:
        current=next(item for item in new_tree.body if type(item)is type(row) and item.name==row.name)
        check('lifecycle-byte-identity-'+row.name,lambda a=row,b=current:equal(ast.get_source_segment(original,a),ast.get_source_segment(new,b)))
    for path in sorted(HERE.glob('*.py')):check('python-source-parse-'+path.name,lambda p=path:ast.parse(p.read_text()))
    parents=json.loads((HERE/'parent-inputs.json').read_text())
    for row in parents['files']:
        check('parent-unchanged-'+Path(row['path']).name,lambda r=row:equal(sha(REPO/r['path']),r['sha256']))
        check('parent-preserved-'+Path(row['path']).name,lambda r=row:equal(sha(HERE/r['preservedCopy']),r['sha256']))
    report={'state':'PURE_CLASSIFIER_SOURCE_AND_OWNED_TEXT_TESTS_PASSED','tests':len(results),'passed':len(results),'results':results,
       'launcherMainExecuted':False,'freezerMainExecuted':False,'exporterMainExecuted':False,'metadataAdmissionExecuted':False,
       'engineOrGuestExecuted':False,'actual342ArtifactCreated':False,'actualPins':None,'lifecycleDefinitionsByteIdentical':8}
    with output.open('x') as stream:json.dump(report,stream,indent=2);stream.write('\n')
    print(json.dumps({'tests':len(results),'passed':len(results),'output':str(output),'artifactMainsExecuted':False}))

if __name__=='__main__':main()
