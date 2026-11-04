"""Configure-only policy proof with actual staged add_builtin; never builds."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'source'
workspace = Path(tempfile.mkdtemp(prefix='stream-web-cmake-', dir='/tmp/starling-node-compat'))
fixture = workspace / 'fixture'
fixture.mkdir()
for directory in ['builtins', 'runtime', 'include']:
    (fixture / directory).symlink_to(SOURCE / directory, target_is_directory=True)
(fixture / 'CMakeLists.txt').write_text('''cmake_minimum_required(VERSION 3.25)
project(StreamWebPolicy LANGUAGES CXX)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
add_library(extension_api INTERFACE)
add_library(spidermonkey INTERFACE)
add_library(multipart INTERFACE)
add_library(host_api INTERFACE)
add_library(OpenSSL::Crypto INTERFACE IMPORTED)
list(PREPEND CMAKE_MODULE_PATH "''' + str(SOURCE / 'cmake') + '''")
include("''' + str(SOURCE / 'cmake/builtins.cmake') + '''")
set(out "${CMAKE_BINARY_DIR}/node-properties.txt")
if(TARGET builtin_node_compat)
  foreach(prop SOURCES COMPILE_DEFINITIONS INCLUDE_DIRECTORIES MANUALLY_ADDED_DEPENDENCIES LINK_LIBRARIES)
    get_target_property(value builtin_node_compat ${prop})
    file(APPEND ${out} "${prop}=${value}\\n")
  endforeach()
else()
  file(WRITE ${out} "TARGET_ABSENT=true\\n")
endif()
''')
cases = [
    ('core-on-default-off', ['-DENABLE_BUILTIN_NODE_COMPAT=ON'], True, False, None),
    ('core-on-streams-off', ['-DENABLE_BUILTIN_NODE_COMPAT=ON', '-DENABLE_BUILTIN_WEB_STREAMS=OFF'], True, False, None),
    ('module-on', ['-DENABLE_BUILTIN_NODE_COMPAT=ON', '-DNODE_COMPAT_STREAM_WEB=ON'], True, True, None),
    ('core-off-default-off', ['-DENABLE_BUILTIN_NODE_COMPAT=OFF'], False, False, None),
    ('missing-core', ['-DENABLE_BUILTIN_NODE_COMPAT=OFF', '-DNODE_COMPAT_STREAM_WEB=ON'], False, True, 'ENABLE_BUILTIN_NODE_COMPAT=ON'),
    ('missing-streams', ['-DENABLE_BUILTIN_NODE_COMPAT=ON', '-DNODE_COMPAT_STREAM_WEB=ON', '-DENABLE_BUILTIN_WEB_STREAMS=OFF'], True, True, 'ENABLE_BUILTIN_WEB_STREAMS=ON'),
    ('missing-codec', ['-DENABLE_BUILTIN_NODE_COMPAT=ON', '-DNODE_COMPAT_STREAM_WEB=ON', '-DENABLE_BUILTIN_WEB_TEXT_CODEC=OFF'], True, True, 'ENABLE_BUILTIN_WEB_TEXT_CODEC=ON'),
]
observed = []
for name, options, core, enabled, failure in cases:
    build = workspace / name
    command = ['cmake', '-S', str(fixture), '-B', str(build), '-G', 'Ninja', *options]
    result = subprocess.run(command, capture_output=True, text=True)
    entry = {'name': name, 'command': command, 'exitCode': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}
    observed.append(entry)
    if failure:
        assert result.returncode != 0 and failure in result.stdout + result.stderr, entry
        entry['expectedConfigurationRefusal'] = failure
        continue
    assert result.returncode == 0, entry
    cache = (build / 'CMakeCache.txt').read_text()
    assert 'NODE_COMPAT_STREAM_WEB:BOOL=' + ('ON' if enabled else 'OFF') in cache
    properties = (build / 'node-properties.txt').read_text()
    entry['properties'] = properties
    commands = json.loads((build / 'compile_commands.json').read_text())
    kernels = [c for c in commands if c['file'].endswith('/node-compat/stream-web-kernel.cpp')]
    registrations = [c for c in commands if c['file'].endswith('/node-compat/register.cpp')]
    assert bool(kernels) == enabled
    assert bool(registrations) == core
    for command in registrations:
        assert ('-DNODE_COMPAT_STREAM_WEB=1' in command['command'].split()) == enabled
    if core:
        assert ('builtins/node-compat/stream-web-kernel.cpp' in properties) == enabled
        dependencies = next(line for line in properties.splitlines() if line.startswith('MANUALLY_ADDED_DEPENDENCIES='))
        assert ('builtin_web_streams' in dependencies) == enabled
        links = next(line for line in properties.splitlines() if line.startswith('LINK_LIBRARIES='))
        assert ('builtin_web_streams' in links) == enabled
        if enabled:
            assert 'builtin_web_text_codec' in dependencies
            assert str(fixture) in properties
        installed = (build / 'builtins.incl').read_text()
        assert installed.index('builtins::web::text_codec') < installed.index('builtins::node_compat')
        if 'builtins::web::streams' in installed:
            assert installed.index('builtins::web::streams') < installed.index('builtins::node_compat')
        else:
            assert not enabled
        entry['installDeclarationOrderVerified'] = True
    entry['kernelCompileCommands'] = kernels
    entry['registrationCompileCommands'] = registrations
    entry['cacheSha256'] = hashlib.sha256(cache.encode()).hexdigest()

script = subprocess.run(['cmake', '-P', str(SOURCE / 'cmake/builtins.cmake')], cwd=fixture, capture_output=True, text=True)
assert script.returncode == 0, script.stderr
report = {'scope': 'Actual staged add_builtin configure/generate policy with dummy dependency targets; no compilation/link or engine proof',
          'workspace': str(workspace), 'cases': observed, 'scriptMode': {'exitCode': script.returncode, 'stdout': script.stdout, 'stderr': script.stderr},
          'engineBuilt': False}
(HERE / 'cmake-results.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'configureCases': len(cases), 'passed': True, 'scriptModePassed': True, 'engineBuilt': False}))
