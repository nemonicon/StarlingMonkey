"""Root: restore pinned Playwright in a fresh directory and record current Chrome."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
WORK = Path('/private/tmp/starling-node-compat/next-rsc-stream-observer-v4-host-tools-v1')
NODE = Path('/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
NPM = Path('/Users/dan/.local/state/fnm_multishells/48029_1794045403532/lib/node_modules/npm/bin/npm-cli.js').resolve()
CHROME = Path('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')


def row(path):
    raw = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))


def save(path, value):
    with path.open('x') as f:
        json.dump(value, f, indent=2)
        f.write('\n')


def main():
    assert __debug__ and sys.flags.isolated and sys.dont_write_bytecode
    assert row(NODE)['sha256'] == 'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'
    WORK.mkdir(mode=0o700)
    root = WORK / 'browser-tools'
    root.mkdir()
    save(root / 'package.json', dict(name='starling-next-v4-browser-tools', version='1.0.0', private=True,
         dependencies={'playwright-core': '1.64.1'}))
    env = os.environ.copy()
    env.update(PATH=str(NODE.parent) + ':' + env.get('PATH', ''), PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD='1')
    records = []
    for label, argv in [
        ('node-version', [str(NODE), '--version']),
        ('npm-version', [str(NODE), str(NPM), '--version']),
        ('chrome-version', [str(CHROME), '--version']),
        ('npm-install', [str(NODE), str(NPM), 'install', '--ignore-scripts', '--no-audit', '--no-fund', '--package-lock=true']),
    ]:
        result = subprocess.run(argv, cwd=root, env=env, capture_output=True, timeout=120)
        for suffix, raw in [('stdout', result.stdout), ('stderr', result.stderr)]:
            with (WORK / (label + '.' + suffix)).open('xb') as f:
                f.write(raw)
        records.append(dict(label=label, argv=argv, rawExitCode=result.returncode,
                            stdout=row(WORK / (label + '.stdout')), stderr=row(WORK / (label + '.stderr'))))
        save(WORK / (label + '.json'), records[-1])
        assert result.returncode == 0, label
    assert (WORK / 'node-version.stdout').read_text().strip() == 'v22.14.0'
    assert (WORK / 'chrome-version.stdout').read_text().strip() == 'Google Chrome 157.0.8103.39'
    package = root / 'node_modules/playwright-core'
    pkg = json.loads((package / 'package.json').read_bytes())
    assert pkg['name'] == 'playwright-core' and pkg['version'] == '1.64.1'
    lock = json.loads((root / 'package-lock.json').read_bytes())
    selected = lock['packages']['node_modules/playwright-core']
    assert selected['version'] == '1.64.1'
    assert selected['resolved'] == 'https://registry.npmjs.org/playwright-core/-/playwright-core-1.64.1.tgz'
    assert selected['integrity'] == 'sha512-BC4s8y6SEVA6Q1rSxZTto8hI1KUI3xXlHGZgvGqP4IqPdI/a6FX9H29IDNz7vKo9l21b6LfYosScPL6M3xxyDQ=='
    files = sorted(package.rglob('*'))
    assert all(not p.is_symlink() for p in files)
    inventory = [row(p) for p in files if p.is_file()]
    hosts = [row(CHROME), row(package / 'index.js'), row(package / 'index.mjs'),
             row(package / 'package.json'), row(root / 'package-lock.json'), row(root / 'package.json')]
    for name, expected in [('index.js', 'a58fb2cec4293e7dcf73c58a179898a4f3986666451a19da4e731fa3af63265b'),
                           ('index.mjs', '3d36e2132d3c8b62397d23f0bb4177336aaee503203ae2a2c90fbeb5bf3317dd'),
                           ('package.json', '8aa1c9863fa8dea324e674254158cdc79440f4124ef2d84d38053013541cb7d6')]:
        assert row(package / name)['sha256'] == expected
    result = dict(schemaVersion=1, state='ROOT_V4_BROWSER_TOOL_SELECTION_PASSED_NOT_BROWSER_EXECUTED_V1',
                  passed=True, selector=row(Path(__file__).resolve()), node=row(NODE), npm=row(NPM),
                  browserTools=str(root), chromeVersion='157.0.8103.39', playwrightVersion='1.64.1',
                  commands=records, hostRequirements=hosts, playwrightPackageFiles=inventory,
                  previousChromeVersion='156.0.8078.81', browserVersionChanged=True,
                  chromeHashScope='Executable launcher only; not entire application bundle',
                  fullWorkloadInvoked=False, fullNextAccepted=False)
    save(HERE / 'browser-tool-selection.json', result)
    print(json.dumps(dict(result=row(HERE / 'browser-tool-selection.json'), files=len(inventory),
                         browserTools=str(root), passed=True)))


if __name__ == '__main__':
    main()
