# Executes the real optional-feature guards without downloading dependencies.
import datetime
import hashlib
import json
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[3]
with tempfile.TemporaryDirectory(prefix='sm-events-cmake-') as temporary:
    temporary = pathlib.Path(temporary)
    source = temporary / 'source'
    source.mkdir()
    (source / 'builtins').symlink_to(root / 'builtins', target_is_directory=True)
    mock = source / 'mock'
    mock.mkdir()
    (source / 'empty.cpp').write_text('int sm_events_cmake_guard;\n')
    (mock / 'add_builtin.cmake').write_text('''function(add_builtin)
 if(ARGV0 STREQUAL "builtins::node_compat" AND ENABLE_BUILTIN_NODE_COMPAT)
  add_library(builtin_node_compat STATIC "${CMAKE_CURRENT_SOURCE_DIR}/empty.cpp")
 endif()
endfunction()
''')
    (source / 'CMakeLists.txt').write_text('''cmake_minimum_required(VERSION 3.25)
project(EventsGuard LANGUAGES CXX)
add_library(extension_api INTERFACE)
add_library(builtin_web_text_codec INTERFACE)
add_library(builtin_web_event INTERFACE)
add_library(builtin_web_abort INTERFACE)
add_library(builtin_web_queue_microtask INTERFACE)
list(PREPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/mock")
include("''' + str(root / 'cmake/builtins.cmake') + '''")
if(TARGET builtin_node_compat)
 get_target_property(defs builtin_node_compat COMPILE_DEFINITIONS)
 file(WRITE "${CMAKE_BINARY_DIR}/definitions.txt" "${defs}")
endif()
''')
    cases = [
        ('default-core-on', ['-DENABLE_BUILTIN_NODE_COMPAT=ON'], True, False),
        ('events-on', ['-DENABLE_BUILTIN_NODE_COMPAT=ON', '-DNODE_COMPAT_EVENTS=ON'], True, True),
        ('events-without-core', ['-DENABLE_BUILTIN_NODE_COMPAT=OFF', '-DNODE_COMPAT_EVENTS=ON'], False, False),
        ('off-without-core', ['-DENABLE_BUILTIN_NODE_COMPAT=OFF', '-DNODE_COMPAT_EVENTS=OFF'], True, False),
    ]
    reports = []
    for name, flags, accepted, definition in cases:
        build = temporary / name
        process = subprocess.run(['cmake', '-S', str(source), '-B', str(build), *flags], text=True, capture_output=True)
        assert (process.returncode == 0) == accepted, (name, process.stdout, process.stderr)
        if accepted and (build / 'definitions.txt').exists():
            assert ('NODE_COMPAT_EVENTS=1' in (build / 'definitions.txt').read_text()) == definition
        if not accepted:
            assert 'NODE_COMPAT_EVENTS requires ENABLE_BUILTIN_NODE_COMPAT=ON' in process.stderr
        reports.append(dict(name=name, flags=flags, accepted=accepted, eventsDefinition=definition, exitCode=process.returncode))
    report = dict(schema=1, atUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  kind='Actual cmake/builtins.cmake with unrelated dependency target creation mocked; configure only, no compilation',
                  sourceSha256=hashlib.sha256((root / 'cmake/builtins.cmake').read_bytes()).hexdigest(), cases=reports)
    (pathlib.Path(__file__).parent / 'cmake-policy-results.json').write_text(json.dumps(report, indent=2) + '\n')
    print('Events CMake guard:', len(reports), 'PASS')
