"""Create a separate host experiment without editing the executed bridge control."""
from pathlib import Path

here = Path(__file__).resolve().parent
source = (here / 'run-host.mjs').read_text()
edits = [
    ("import {createRequestBridge} from './bridge.mjs';", "import {createRequestBridge} from './bridge.mjs';\nimport {createHostModuleRequire} from './module-host-provider.mjs';"),
    ("suite: 'FULL_NEXT_NODE_HOST_REQUEST_BRIDGE_V1'", "suite: 'FULL_NEXT_NODE_HOST_MODULE_CORE_HTTP_BRIDGE_V1'"),
    ("const require = createRequire(join(application, 'server.js'));", "const moduleObservations = {};\n  const require = createHostModuleRequire(join(application, 'server.js'), moduleObservations);\n  result.moduleSource = await descriptor(join(here, '../../../foundation-module/node-module-candidate-v1/module-core.mjs'));\n  result.hostModuleProvider = await descriptor(join(here, 'module-host-provider.mjs'));\n  result.moduleObservations = moduleObservations;"),
    ("const save = () => writeFile", "const save = () => { if (result.moduleObservations?.snapshot) result.moduleSnapshot = result.moduleObservations.snapshot(); return writeFile"),
    ("JSON.stringify(result, null, 2) + '\\n');", "JSON.stringify(result, null, 2) + '\\n'); };"),
]
for before, after in edits:
    assert source.count(before) == 1, before
    source = source.replace(before, after)
with (here / 'run-module-host.mjs').open('x') as file:
    file.write(source)
print('Created separate module-core full Next host experiment')
