#!/usr/bin/env python3
"""Run reviewed offline line commands and keep bounded receipts in gathering/."""
import datetime
import json
from pathlib import Path
import subprocess

COMMANDS = [
    ['line-1/tools/snapshot-check/test_checks.py'],
    ['line-1/tools/pinned-snapshot/test_pinned.py'],
    ['line-2/tools/handoff/handoff.py', 'demo'],
    ['line-2/tools/handoff/handoff.py', 'verify', 'line-2/handoff.zip'],
    ['line-2/tools/handoff-inspect/test_inspect.py'],
    ['line-2/tools/handoff-inspect/inspect_handoff.py', 'demo'],
    ['line-2/tools/handoff-compare/test_compare.py'],
    ['line-2/tools/handoff-compare/compare_handoff.py', 'demo'],
    ['line-3/tools/zto-eip1559-decoder/test_decoder.py'],
    ['line-3/tools/zto-eip1559-decoder/tx_decode.py', '--demo'],
    ['line-3/tools/erc20-intent/test_intent.py'],
    ['line-3/tools/erc20-intent/intent.py', '--demo'],
    ['line-4/tools/erc20-transfer-window/test_transfer_window.py'],
    ['line-4/tools/transfer-crosscheck/test_crosscheck.py'],
    ['line-4/tools/transfer-crosscheck/crosscheck.py', '--demo'],
    ['shared/evidence-handoff/test_bundle.py'],
    ['shared/evidence-handoff/bundle.py', 'demo'],
    ['shared/tx-preflight/test_preflight.py'],
    ['shared/tx-preflight/preflight.py', 'demo'],
    ['gathering/review_checks.py'],
]


def main():
    directory = Path('gathering/checks/round-03')
    directory.mkdir(parents=True, exist_ok=True)
    results = []
    for index, args in enumerate(COMMANDS, 1):
        command = ['python3', '-B', *args]
        run = subprocess.run(command, capture_output=True, text=True, timeout=90)
        record = {'command': command, 'exit': run.returncode,
                  'checked_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  'stdout': run.stdout, 'stderr': run.stderr}
        raw = json.dumps(record, indent=2) + '\n'
        if len(raw.encode()) > 100000:
            raise ValueError('check receipt exceeds file limit')
        (directory / f'{index:02d}.json').write_text(raw)
        results.append({'command': args, 'exit': run.returncode})
        print(f'{index:02d}: exit {run.returncode}: {" ".join(args)}', flush=True)
    (directory / 'summary.json').write_text(json.dumps(results, indent=2) + '\n')
    return int(any(item['exit'] for item in results))


if __name__ == '__main__':
    raise SystemExit(main())
