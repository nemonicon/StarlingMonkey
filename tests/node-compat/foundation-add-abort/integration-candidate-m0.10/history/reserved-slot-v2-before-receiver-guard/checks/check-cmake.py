"""Actual add_builtin configure/generate checks; no compilation or linking."""
from pathlib import Path
import hashlib
import json
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'source'
workspace = Path(tempfile.mkdtemp(prefix='sm-abort-m10-cmake-', dir='/tmp/starling-node-compat'))
fixture = workspace / 'fixture'
fixture.mkdir()
for name in ['builtins', 'runtime', 'include']:
    (fixture / name).symlink_to(SOURCE / name, target_is_directory=True)
(fixture / 'embedding.cpp').write_text('int source_only_embedding_layout_check;\n')
(fixture / 'CMakeLists.txt').write_text('''cmake_minimum_required(VERSION 3.25)
project(ProtectedAbortPolicy LANGUAGES CXX)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
add_library(extension_api INTERFACE)
add_library(spidermonkey INTERFACE)
add_library(multipart INTERFACE)
add_library(host_api INTERFACE)
add_library(OpenSSL::Crypto INTERFACE IMPORTED)
list(PREPEND CMAKE_MODULE_PATH "''' + str(SOURCE / 'cmake') + '''")
include("''' + str(SOURCE / 'cmake/builtins.cmake') + '''")
add_library(embedding_layout_check STATIC embedding.cpp)
target_link_libraries(embedding_layout_check PRIVATE extension_api)
if(TARGET builtin_node_compat)
 foreach(prop LINK_LIBRARIES MANUALLY_ADDED_DEPENDENCIES)
  get_target_property(value builtin_node_compat ${prop})
  file(APPEND "${CMAKE_BINARY_DIR}/node-properties.txt" "${prop}=${value}\\n")
 endforeach()
endif()
''')
cases = [
    ('default-off', ['-DENABLE_BUILTIN_NODE_COMPAT=ON'], False, None),
    ('events-on', ['-DENABLE_BUILTIN_NODE_COMPAT=ON', '-DNODE_COMPAT_EVENTS=ON'], True, None),
    ('off-missing-event', ['-DENABLE_BUILTIN_NODE_COMPAT=ON', '-DENABLE_BUILTIN_WEB_EVENT=OFF'], False, None),
    ('off-missing-abort', ['-DENABLE_BUILTIN_NODE_COMPAT=ON', '-DENABLE_BUILTIN_WEB_ABORT=OFF'], False, None),
    ('off-missing-queue', ['-DENABLE_BUILTIN_NODE_COMPAT=ON', '-DENABLE_BUILTIN_WEB_QUEUE_MICROTASK=OFF'], False, None),
    ('missing-core', ['-DNODE_COMPAT_EVENTS=ON'], True, 'NODE_COMPAT_EVENTS requires ENABLE_BUILTIN_NODE_COMPAT=ON'),
    ('missing-event', ['-DENABLE_BUILTIN_NODE_COMPAT=ON', '-DNODE_COMPAT_EVENTS=ON', '-DENABLE_BUILTIN_WEB_EVENT=OFF'], True, 'requires builtin_web_event'),
    ('missing-abort', ['-DENABLE_BUILTIN_NODE_COMPAT=ON', '-DNODE_COMPAT_EVENTS=ON', '-DENABLE_BUILTIN_WEB_ABORT=OFF'], True, 'requires builtin_web_abort'),
    ('missing-queue', ['-DENABLE_BUILTIN_NODE_COMPAT=ON', '-DNODE_COMPAT_EVENTS=ON', '-DENABLE_BUILTIN_WEB_QUEUE_MICROTASK=OFF'], True, 'requires builtin_web_queue_microtask'),
]
results = []
for name, options, enabled, refusal in cases:
    build = workspace / name
    command = ['cmake', '-S', str(fixture), '-B', str(build), '-G', 'Ninja', *options]
    process = subprocess.run(command, capture_output=True, text=True)
    entry = {'name': name, 'command': command, 'exitCode': process.returncode,
             'stdout': process.stdout, 'stderr': process.stderr, 'expectedFeature': enabled}
    results.append(entry)
    if refusal:
        assert process.returncode != 0 and refusal in process.stdout + process.stderr, entry
        continue
    assert process.returncode == 0, entry
    cache = (build / 'CMakeCache.txt').read_text()
    assert 'NODE_COMPAT_EVENTS:BOOL=' + ('ON' if enabled else 'OFF') in cache
    commands = json.loads((build / 'compile_commands.json').read_text())
    assert commands
    for compiled in commands:
        assert ('-DNODE_COMPAT_EVENTS_ADD_ABORT_LISTENER=1' in compiled['command'].split()) == enabled, compiled
    # A generated dummy embedding verifies interface propagation, not the real
    # external ComponentizeJS target; the recipe independently checks that later.
    assert any(e['file'].endswith('/embedding.cpp') for e in commands)
    properties = (build / 'node-properties.txt').read_text()
    for target in ['builtin_web_event', 'builtin_web_abort', 'builtin_web_queue_microtask']:
        assert (target in properties) == enabled, properties
    if enabled:
        order = (build / 'builtins.incl').read_text()
        for prerequisite in ['builtins::web::event', 'builtins::web::abort', 'builtins::web::queue_microtask']:
            assert order.index(prerequisite) < order.index('builtins::node_compat')
    entry.update(layoutCompileCommandCount=len(commands), properties=properties,
                 cacheSha256=hashlib.sha256(cache.encode()).hexdigest(),
                 compileCommandsSha256=hashlib.sha256((build / 'compile_commands.json').read_bytes()).hexdigest())
script_mode = subprocess.run(['cmake', '-P', str(SOURCE / 'cmake/builtins.cmake')], cwd=fixture, capture_output=True, text=True)
assert script_mode.returncode == 0, script_mode.stderr
report = {'state': 'CONFIGURE_GENERATE_ONLY_NO_BUILD', 'actualAddBuiltin': True,
          'dummyDependencyTargets': True, 'workspace': str(workspace), 'cases': results,
          'scriptMode': {'exitCode': script_mode.returncode, 'stdout': script_mode.stdout,
                         'stderr': script_mode.stderr, 'scope': 'Code-free builtin listing only; no target, layout flag or compilation proof'},
          'sourceSha256': hashlib.sha256((SOURCE / 'cmake/builtins.cmake').read_bytes()).hexdigest(),
          'driverSha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          'engineBuilt': False, 'guestExecuted': False}
(HERE / 'cmake-results.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'configureCases': len(cases), 'passed': True, 'engineBuilt': False}))
