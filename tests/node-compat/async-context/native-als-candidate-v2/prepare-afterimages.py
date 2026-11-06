"""Authoring-only localized ALS composition on authenticated 9aec Source.

No helper, compiler, engine, target code, Git or native producer is invoked.
Root owns the later whole Next generation and its native admission producer.
"""
from pathlib import Path
import copy
import hashlib
import json

OWN = Path(__file__).resolve().parent
REPO = OWN.parents[3]
PARENT = OWN.parent / 'native-als-candidate-v1'
BASE = Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v1-source')
POLICY = REPO / 'tests/node-compat/foundation-crypto/node-crypto-hash-hmac-native-controller-candidate-v3/producer/policy.json'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def main():
    policy = json.loads(POLICY.read_text())
    manifest = {r['path']: r['sha256'] for r in policy['expectedNativeSourceManifest']}
    assert len(manifest) == 357
    source = copy.deepcopy(json.loads((PARENT / 'integration-edits.json').read_text())['files'])
    joined = []
    for row in source:
        name = row['path']
        edits = row['edits']
        if name == 'runtime/event_loop.cpp':
            edits[2] = {
                'before': '      (void)retiring.get().task->cancel(engine);',
                'after': '#ifdef NODE_COMPAT_ASYNC_LOCAL_STORAGE\n      core::async_context::ResourceStore::Scope context(engine->cx(), core::async_context::store(), retiring.get().task->async_context());\n#endif\n      (void)retiring.get().task->cancel(engine);',
            }
            edits[3] = {
                'before': '    bool success = running.get().task->run(engine);',
                'after': '    bool success;\n    {\n#ifdef NODE_COMPAT_ASYNC_LOCAL_STORAGE\n      core::async_context::ResourceStore::Scope context(cx, core::async_context::store(), running.get().task->async_context());\n#endif\n      success = running.get().task->run(engine);\n    }',
            }
            for signature in ['bool EventLoop::require_internal_ticks_quiescent(JSContext* cx) {',
                              'bool EventLoop::require_internal_tick_reset_allowed(JSContext* cx) {']:
                edits.append({'before': signature, 'after': signature + '\n#ifdef NODE_COMPAT_ASYNC_LOCAL_STORAGE\n  if (!core::async_context::require_quiescent_server_boundary(cx)) return false;\n#endif'})
        if name == 'builtins/web/timers.cpp':
            edits = [
                {'before': '            TimerArgumentsVector&& args)\n      : timer_id_(id)',
                 'after': '            TimerArgumentsVector&& args, HandleObject resource)\n      : api::AsyncTask(resource), timer_id_(id)'},
                {'before': '  RefPtr<TimerTask> timer = js_new<TimerTask>(id, delay, repeat, handler, std::move(arguments));',
                 'after': '  RootedObject resource(cx);\n  if (!api::AsyncTask::capture_context(cx, &resource)) return false;\n  RefPtr<TimerTask> timer = js_new<TimerTask>(id, delay, repeat, handler, std::move(arguments), resource);'},
            ]
        if name == 'cmake/builtins.cmake':
            # Preserve the original local insertion, including all 9aec options.
            edits = copy.deepcopy(edits)
            index = next(i for i, e in enumerate(edits) if 'option(NODE_COMPAT_ASYNC_LOCAL_STORAGE' in e['after'])
            edits[index]['after'] = edits[index]['after'].replace(
                '    target_compile_definitions(extension_api INTERFACE NODE_COMPAT_ASYNC_LOCAL_STORAGE=1)',
                '    if(ENABLE_JS_DEBUGGER)\n        message(FATAL_ERROR "Native ALS does not share its allocation metadata builder with Debugger")\n    endif()\n    target_compile_definitions(extension_api INTERFACE NODE_COMPAT_ASYNC_LOCAL_STORAGE=1)')
            edits[index]['after'] = edits[index]['after'].replace(
                'if(NOT TARGET builtin_node_compat OR NOT NODE_COMPAT_INTERNAL_TICKS)',
                'if(NOT TARGET builtin_node_compat OR NOT NODE_COMPAT_INTERNAL_TICKS OR NOT NODE_COMPAT_STRICT_INITIALIZATION)')
        if name == 'builtins/web/fetch/request-response.cpp':
            edits = copy.deepcopy(edits)
            index = next(i for i, e in enumerate(edits) if 'new<ResponseFutureTask>' in e['after'])
            # Change the complete ownership-transfer join, rather than allow a
            # later metadata refusal to orphan the still-owned future handle.
            edits[index] = {
                'before': '    SetReservedSlot(body_owner, static_cast<uint32_t>(Request::Slots::PendingResponseHandle),\n                    PrivateValue(nullptr));\n    ENGINE->queue_async_task(js_new<ResponseFutureTask>(body_owner, pending_handle));',
                'after': '    RootedObject promise(cx, Request::response_promise(body_owner)), resource(cx);\n    if (!api::AsyncTask::context_from_promise(cx, promise, &resource)) return false;\n    // Validate the operation resource before transferring the pending handle.\n    SetReservedSlot(body_owner, static_cast<uint32_t>(Request::Slots::PendingResponseHandle),\n                    PrivateValue(nullptr));\n    ENGINE->queue_async_task(js_new<ResponseFutureTask>(body_owner, pending_handle, resource));',
            }
        path = BASE / name
        before = path.read_bytes()
        assert sha(before) == manifest[name], ('unauthenticated baseline', name)
        text = before.decode()
        for e in edits:
            assert text.count(e['before']) == 1, ('nonunique/missing anchor', name, e['before'][:80])
            text = text.replace(e['before'], e['after'], 1)
        reverse = text
        for e in reversed(edits):
            assert reverse.count(e['after']) == 1, ('nonunique inverse', name)
            reverse = reverse.replace(e['after'], e['before'], 1)
        assert reverse.encode() == before
        out = OWN / 'after' / name
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text)
        joined.append({'path': name, 'beforeSha256': sha(before), 'beforeBytes': len(before),
                       'afterSha256': sha(text.encode()), 'afterBytes': len(text.encode()), 'edits': edits})
    result = {'schemaVersion': 1, 'sourceOnly': True, 'uncompiled': True,
              'baseSourceRoot': str(BASE), 'baseNativeSourceFiles': 357,
              'basePolicy': {'path': str(POLICY), 'sha256': sha(POLICY.read_bytes()), 'bytes': POLICY.stat().st_size},
              'parentUnsealedV1Preserved': True, 'baselineWholeAfterimagesNeverOverwritten': True,
              'v1DivergentAnchorsAdapted': ['event_loop:retiring-traced-task', 'event_loop:running-traced-task',
                                         'timers:owned-constructor', 'timers:owned-registration'],
              'files': joined}
    (OWN / 'localized-edits.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'files': len(joined), 'reversibleEdits': sum(len(r['edits']) for r in joined),
                      'nativeActions': False}))

if __name__ == '__main__':
    main()
