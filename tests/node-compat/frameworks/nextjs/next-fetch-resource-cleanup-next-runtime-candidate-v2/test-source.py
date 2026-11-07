"""Check the unchanged client's literal path contract; no JS parser or process."""
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent


def main():
    plan = json.loads((HERE / 'plan.json').read_text())
    source = (HERE / 'run-contracts.mjs').read_text()
    literals = re.findall(r"assert\.equal\(root,'([^']+)'\+runId\+'/client'\);", source)
    assert len(literals) == 1 and literals[0].endswith('-')
    assert plan['outputPrefix'] == literals[0][:-1]
    run_id = 'cleanup-476b-next-corrected'
    assert re.fullmatch('[a-z0-9][a-z0-9-]{0,47}', run_id)
    expected = literals[0] + run_id + '/client'
    assert plan['outputPrefix'] + '-' + run_id + '/client' == expected
    print(json.dumps(dict(sourceOnly=True, literalClientContractChecked=True,
          derivedClientPath=expected, javascriptParsedOrExecuted=False,
          processOrActorInvoked=False, actualNextRuntimeAccepted=False)))


if __name__ == '__main__':
    main()
