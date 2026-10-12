#!/usr/bin/env python3
"""Offline failure and provenance checks using the included real capture."""
import copy
import contextlib
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
import pinned_snapshot as tool

EXAMPLE = json.loads(Path(__file__).with_name('example-zto.json').read_text())


class Tests(unittest.TestCase):
    def replay(self, change=None):
        values = [EXAMPLE['chain_id'], EXAMPLE['block'], EXAMPLE['result'], EXAMPLE['block_after']]
        values = copy.deepcopy(values)
        if change:
            change(values)
        calls = []
        def read(method, params):
            calls.append((method, copy.deepcopy(params)))
            return values[len(calls) - 1]
        return read, calls

    def test_capture_pins_actual_number(self):
        read, calls = self.replay()
        bundle = tool.capture(read=read)
        n = EXAMPLE['block']['number']
        self.assertEqual(calls, [('eth_chainId', []),
            ('eth_getBlockByNumber', ['finalized', False]),
            ('eth_call', [tool.CALL, n]), ('eth_getBlockByNumber', [n, False])])
        self.assertEqual(tool.inspect(bundle)['total_supply_base_units'], str(int(EXAMPLE['result'], 16)))

    def test_wrong_chain_stops_before_call(self):
        read, calls = self.replay(lambda v: v.__setitem__(0, '0x89'))
        with self.assertRaisesRegex(ValueError, 'mainnet'):
            tool.capture(read=read)
        self.assertEqual(len(calls), 1)

    def test_wrong_explicit_block_stops_before_call(self):
        read, calls = self.replay()
        with self.assertRaisesRegex(ValueError, 'different block number'):
            tool.capture(tag='0x1', read=read)
        self.assertEqual(len(calls), 2)

    def test_combined_size_limit(self):
        read, _ = self.replay()
        with patch.object(tool, 'LIMIT', 1000):
            with self.assertRaisesRegex(ValueError, 'combined snapshot'):
                tool.capture(read=read)

    def test_changed_hash_rejected(self):
        read, _ = self.replay(lambda v: v[3].__setitem__('hash', EXAMPLE['block']['parentHash']))
        with self.assertRaisesRegex(ValueError, 'hash changed'):
            tool.capture(read=read)

    def test_malformed_supply_rejected(self):
        for result in (None, '0x1', '0x' + 'gg' * 32, []):
            read, calls = self.replay(lambda v: v.__setitem__(2, result))
            with self.assertRaises(ValueError):
                tool.capture(read=read)
            self.assertEqual(len(calls), 3)

    def test_offline_tampering_rejected(self):
        changes = [lambda b: b['params'].__setitem__(1, 'latest'),
                   lambda b: b['params'][0].__setitem__('to', '0xd34a99bc0f67ae1bbd63c660e6d0b0dd03e263b7'),
                   lambda b: b.__setitem__('method', 'eth_sendTransaction'),
                   lambda b: b['block_after'].__setitem__('number', '0x1'),
                   lambda b: b['block_after'].__setitem__('timestamp', '0x1'),
                   lambda b: b.__setitem__('requested_block', '0x1'),
                   lambda b: b.__setitem__('captured_at', 'yesterday'),
                   lambda b: b.__setitem__('chain_id', '0x89')]
        for change in changes:
            bundle = copy.deepcopy(EXAMPLE)
            change(bundle)
            with self.assertRaises(ValueError):
                tool.inspect(bundle)

    def test_pending_and_invalid_tags_no_reads(self):
        for tag in ('pending', '0x01', 'bad', None):
            with patch.object(tool, 'public_read') as network:
                with self.assertRaises(ValueError):
                    tool.capture(tag=tag)
                network.assert_not_called()

    def test_readonly_guard_precedes_network(self):
        with patch.object(tool.urllib.request, 'urlopen') as network:
            with self.assertRaises(ValueError):
                tool.public_read(tool.rpc.DEFAULT_RPC, 'eth_sendRawTransaction', [])
            network.assert_not_called()

    def test_inspect_cli_offline_and_controlled_errors(self):
        for raw, code in ((json.dumps(EXAMPLE).encode(), 0), (b'null', 1), (b'{', 1), (b'[]', 1)):
            stdin = io.TextIOWrapper(io.BytesIO(raw))
            with patch.object(sys, 'argv', ['pinned', 'inspect']), patch.object(sys, 'stdin', stdin), \
                 patch.object(tool.urllib.request, 'urlopen') as network, \
                 contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(tool.main(), code)
                network.assert_not_called()

    def test_response_limits_and_envelope(self):
        for raw in (b' ' * (tool.LIMIT + 1), b'null', b'{"jsonrpc":"2.0","id":2,"result":"0x1"}'):
            with patch.object(tool.urllib.request, 'urlopen') as network:
                network.return_value.__enter__.return_value.read.return_value = raw
                with self.assertRaises((ValueError, RuntimeError)):
                    tool.public_read(tool.rpc.DEFAULT_RPC, 'eth_chainId', [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
