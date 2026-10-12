#!/usr/bin/env python3
"""Review bounded public evidence in a deterministic offline HANDOFF archive."""
import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import zipfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
LIMIT = 99000
INDEX = 'REVIEW.json'
KINDS = ('pinned-snapshot', 'transfer-window', 'transfer-comparison', 'unsigned-transaction')
NOTICE = ('Integrity and structural consistency only. Provider observations do not prove '
          'authenticity, completeness, independence or finality. Unsigned inspection '
          'does not establish simulation, inclusion or safety to sign.')


def load(name, relative):
    path = HERE / 'vendor' / relative
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


handoff = load('review_handoff', 'handoff/handoff.py')
inspector = load('review_inspector', 'handoff-inspect/inspect_handoff.py')
pinned = load('review_pinned', 'pinned-snapshot/pinned_snapshot.py')
cross = load('review_cross', 'transfer-crosscheck/crosscheck.py')
intent = load('review_intent', 'erc20-intent/intent.py')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def parse(raw):
    require(isinstance(raw, bytes) and len(raw) <= LIMIT, 'JSON exceeds byte limit')
    def invalid(value):
        raise ValueError('nonstandard JSON constant: ' + value)
    return json.loads(raw, object_pairs_hook=handoff.unique_object, parse_constant=invalid)


def encode(obj):
    return (json.dumps(obj, indent=2, sort_keys=True) + '\n').encode()


def describe(kind, raw):
    obj = parse(raw)
    require(isinstance(obj, dict), 'evidence must be a JSON object')
    if kind == 'pinned-snapshot':
        return pinned.inspect(obj)
    if kind == 'transfer-window':
        checked = cross.checked(obj)
        return {key: checked[key] for key in ('chain_id', 'token_address', 'from_block',
                    'to_block', 'decimals', 'from_block_anchor', 'to_block_anchor')} | {
                    'transfer_count': len(checked['transfers'])}
    if kind == 'transfer-comparison':
        evidence = obj.get('evidence')
        require(isinstance(evidence, dict) and set(evidence) == {'left', 'right'},
                'comparison must retain both observations')
        rebuilt = cross.compare(evidence['left'], evidence['right'])
        require(set(obj) == set(rebuilt) | {'evidence'}, 'unexpected comparison fields')
        require(all(encode(obj[key]) == encode(value) for key, value in rebuilt.items()),
                'comparison report disagrees with retained observations')
        return {key: rebuilt[key] for key in ('status', 'providers', 'token',
                  'from_block', 'to_block', 'transfer_counts', 'metadata_differences')} | {
                  'conflicts': len(rebuilt['conflicts']),
                  'only_left': len(rebuilt['only_left']), 'only_right': len(rebuilt['only_right'])}
    if kind == 'unsigned-transaction':
        require(set(obj) == {'transaction_hex', 'provenance'}, 'invalid unsigned input fields')
        require(obj['provenance'] in ('synthetic unsigned demo', 'user-supplied unsigned envelope'),
                'explicit unsigned provenance required')
        summary = intent.interpret(obj['transaction_hex'])
        summary['provenance'] = obj['provenance']
        return summary
    raise ValueError('unsupported evidence kind')


def context(inputs):
    """Only link matching numbered/hash-anchored state; never imply atomicity."""
    if not {'pinned-snapshot', 'transfer-window'} <= set(inputs):
        return {'status': 'separate observations', 'note': 'No paired supply/window context.'}
    snap, win = [parse(inputs[k]) for k in ('pinned-snapshot', 'transfer-window')]
    a = snap['block']
    b = win['to_block_anchor']
    same_number = int(a['number'], 16) == b['number']
    if same_number:
        require(a['hash'].lower() == b['hash'].lower(), 'same closing block has conflicting hashes')
    same_token = snap['params'][0]['to'].lower() == win['token_address'].lower()
    return {'status': 'matching closing anchor' if same_number and same_token else 'separate observations',
            'same_token': same_token, 'same_closing_block_number': same_number,
            'note': 'Matching anchors are provider consistency, not an atomic or finality proof.'}


def build(inputs):
    require(isinstance(inputs, dict) and bool(inputs) and set(inputs) <= set(KINDS),
            'supply one or more supported evidence kinds')
    entries, files = [], {}
    for kind, raw in sorted(inputs.items()):
        summary = describe(kind, raw)
        name = 'evidence/' + kind + '.json'
        files[name] = raw
        entries.append({'kind': kind, 'path': name, 'sha256': handoff.digest(raw), 'summary': summary})
    files[INDEX] = encode({'schema': 'evidence-review/1', 'notice': NOTICE,
                           'entries': entries, 'context': context(inputs)})
    archive = handoff.build(files)
    require(len(archive) <= LIMIT, 'archive exceeds 99,000-byte budget; choose a smaller window')
    return archive


def inspect(data, expected=None):
    require(isinstance(data, bytes) and len(data) <= LIMIT, 'archive exceeds byte budget')
    receipt = inspector.inspect_stream(io.BytesIO(data), inspector.Limits(
        archive_bytes=LIMIT, payload_bytes=LIMIT, manifest_bytes=LIMIT,
        metadata_bytes=LIMIT, files=len(KINDS) + 1), expected)
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        require(INDEX in archive.namelist(), 'missing review index')
        index = parse(archive.read(INDEX))
        require(isinstance(index, dict) and set(index) == {'schema', 'notice', 'entries', 'context'}
                and index['schema'] == 'evidence-review/1' and index['notice'] == NOTICE
                and isinstance(index['entries'], list) and 1 <= len(index['entries']) <= len(KINDS),
                'invalid review index')
        inputs = {}
        for entry in index['entries']:
            require(isinstance(entry, dict) and set(entry) == {'kind', 'path', 'sha256', 'summary'},
                    'invalid index entry')
            kind = entry['kind']
            require(isinstance(kind, str) and kind in KINDS and kind not in inputs,
                    'unsupported or duplicated kind')
            require(entry['path'] == 'evidence/' + kind + '.json', 'invalid evidence path')
            raw = archive.read(entry['path'])
            require(entry['sha256'] == handoff.digest(raw)
                    and encode(entry['summary']) == encode(describe(kind, raw)),
                    'review index differs from evidence')
            inputs[kind] = raw
        require(set(archive.namelist()) == {handoff.MANIFEST, INDEX} | {
            'evidence/' + k + '.json' for k in inputs}, 'unexpected archive payload')
    require(encode(index['context']) == encode(context(inputs)), 'declared context differs from evidence')
    return {'schema': 'evidence-review-receipt/1', 'integrity': receipt,
            'evidence': index['entries'], 'context': index['context'], 'limits': NOTICE}


def read_file(raw):
    return handoff.regular_bytes(handoff.workspace_path(raw), LIMIT)


def write_new(raw, data):
    path = handoff.workspace_path(raw, must_exist=False)
    with path.open('xb') as handle:
        handle.write(data)


def demo():
    inputs = {p.stem: p.read_bytes() for p in sorted((HERE / 'examples').glob('*.json'))}
    packed = build(inputs)
    require(packed == build(dict(reversed(list(inputs.items())))), 'non-deterministic archive')
    receipt = inspect(packed)
    receipt['demo'] = 'Retained real public-chain observations plus a synthetic unsigned ZTO envelope.'
    receipt['deterministic'] = True
    return receipt


def capture(endpoint, blocks=12):
    require(type(blocks) is int and 1 <= blocks <= 2000, 'window must contain 1..2000 blocks')
    snap = pinned.capture(endpoint)
    end = int(snap['block']['number'], 16)
    start = max(0, end - blocks + 1)
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        cross.window.main(['--rpc', endpoint, '--token', 'zto',
                           '--from-block', str(start), '--to-block', str(end)])
    return {'pinned-snapshot': encode(snap), 'transfer-window': output.getvalue().encode()}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('demo')
    pack = commands.add_parser('pack')
    pack.add_argument('output')
    for kind in KINDS:
        pack.add_argument('--' + kind)
    check = commands.add_parser('inspect')
    check.add_argument('archive')
    check.add_argument('--sha256', help='independently obtained trusted archive digest')
    live = commands.add_parser('capture')
    live.add_argument('output', help='new workspace ZIP file; never overwritten')
    live.add_argument('--rpc', required=True, help='public HTTPS or the supplied loopback /rpc/1 endpoint')
    live.add_argument('--blocks', type=int, default=12)
    args = parser.parse_args(argv)
    try:
        if args.command == 'demo':
            result = demo()
        elif args.command == 'inspect':
            result = inspect(read_file(args.archive), args.sha256)
        else:
            # Validate the output before any network reads and refuse overwrite.
            output = handoff.workspace_path(args.output, must_exist=False)
            require(not output.exists(), 'output already exists')
            if args.command == 'capture':
                inputs = capture(args.rpc, args.blocks)
            else:
                inputs = {kind: read_file(getattr(args, kind.replace('-', '_')))
                          for kind in KINDS if getattr(args, kind.replace('-', '_'))}
            data = build(inputs)
            result = inspect(data)
            write_new(args.output, data)
            result['output'] = args.output
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except (ValueError, RuntimeError, OSError, TypeError, KeyError, RecursionError,
            zipfile.BadZipFile, EOFError) as error:
        print('evidence-review: ' + str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
