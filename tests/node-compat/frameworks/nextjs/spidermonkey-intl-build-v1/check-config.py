"""Exercise actual CMake selection, without downloads, compilers or Mach."""
from pathlib import Path
import json
import os
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]


def main():
    rows = []
    with tempfile.TemporaryDirectory(prefix='starling-intl-config-') as name:
        root = Path(name)
        project = root / 'project'
        project.mkdir()
        (project / 'deps').mkdir()
        (project / 'CMakeLists.txt').write_text('cmake_minimum_required(VERSION 3.27)\nproject(SelectionOnly LANGUAGES NONE)\nlist(PREPEND CMAKE_MODULE_PATH "' + str(REPO / 'cmake') + '")\ninclude(spidermonkey)\n')
        dist = root / 'dist'
        (dist / 'include').mkdir(parents=True)
        env = {k: v for k, v in os.environ.items() if k not in ('SPIDERMONKEY_BINARIES', 'BASH_ENV', 'ENV', 'CMAKE_TOOLCHAIN_FILE')}
        env.update(GIT_CONFIG_GLOBAL='/dev/null', GIT_CONFIG_NOSYSTEM='1', GIT_AUTHOR_NAME='Fixture', GIT_AUTHOR_EMAIL='fixture@example.invalid', GIT_COMMITTER_NAME='Fixture', GIT_COMMITTER_EMAIL='fixture@example.invalid', GIT_AUTHOR_DATE='2001-01-01T00:00:00Z', GIT_COMMITTER_DATE='2001-01-01T00:00:00Z')

        def case(label, flags, prebuilt, intl_header, expect, diagnostic):
            (dist / 'include/js-config.h').write_text('#define JS_HAS_INTL_API 1\n' if intl_header else '/* #undef JS_HAS_INTL_API */\n')
            current = {**env}
            if prebuilt:
                current['SPIDERMONKEY_BINARIES'] = str(dist)
            argv = [shutil.which('cmake'), '-S', str(project), '-B', str(root / label), *flags]
            result = subprocess.run(argv, env=current, capture_output=True, text=True, timeout=30)
            output = result.stdout + result.stderr
            passed = (result.returncode == 0) == expect and diagnostic in output
            rows.append(dict(label=label, rawExitCode=result.returncode, passed=passed, output=output))
            assert passed, (label, output)

        case('default-prebuilt', [], True, False, True, 'Using pre-built SpiderMonkey artifacts from local directory')
        case('intl-rejects-old-prebuilt', ['-DSPIDERMONKEY_INTL=ON'], True, False, False, 'does not define JS_HAS_INTL_API=1')
        case('intl-explicit-prebuilt', ['-DSPIDERMONKEY_INTL=ON'], True, True, True, 'Using pre-built SpiderMonkey artifacts from local directory')
        case('intl-requires-selection', ['-DSPIDERMONKEY_INTL=ON'], False, False, False, 'Intl requires SPIDERMONKEY_BUILD_FROM_SOURCE')
        case('force-env-conflict', ['-DSPIDERMONKEY_BUILD_FROM_SOURCE=ON'], True, False, False, 'conflicts with SPIDERMONKEY_BINARIES')
        source = project / 'deps/spidermonkey-source'
        source.mkdir()
        (source / 'fixture.txt').write_text('Not the real SpiderMonkey source.\n')
        for args in (['init', '-q'], ['add', '.'], ['-c', 'core.hooksPath=/dev/null', 'commit', '-qm', 'Fixture'], ['tag', 'FIREFOX_147_0_4_RELEASE_STARLING']):
            subprocess.run(['git', '-C', str(source), *args], env=env, check=True, capture_output=True, timeout=10)
        case('force-rejects-stale-cache-and-wrong-revision', ['-DSPIDERMONKEY_BUILD_FROM_SOURCE=ON', '-DSPIDERMONKEY_INTL=ON', '-DSM_LIB_DIR=' + str(dist)], False, True, False, 'SpiderMonkey source revision is')
    print(json.dumps(dict(passed=True, scope='CMake selection only; no fetch/build/runtime', cases=rows), indent=2))


if __name__ == '__main__':
    main()
