#!/usr/bin/env python3
"""Behavioral tests using only offline unsigned envelopes."""
import contextlib
import io
import random
import unittest

import intent


def envelope(data='18160ddd', destination=intent.decoder.ZTO, chain=1,
             value=0, gas=100000, priority=1000000000, fee=2000000000):
    fields = [chain, 0, priority, fee, gas,
              b'' if destination is None else bytes.fromhex(destination[2:]),
              value, bytes.fromhex(data), []]
    return '0x02' + intent.decoder.rlp_encode(fields).hex()


def address_word(address):
    return '00' * 12 + address[2:]


def amount_word(amount):
    return amount.to_bytes(32, 'big').hex()


class IntentTests(unittest.TestCase):
    def test_zto_demo_and_exact_budget(self):
        result = intent.interpret(intent.decoder.demo_transaction())
        self.assertEqual(result['destinationLabel'], 'ZTO')
        self.assertEqual(result['calldata']['candidateMethod'], 'totalSupply')
        self.assertEqual(result['calldata']['arguments'], {})
        self.assertEqual(result['feeBudget']['gasFeeCapWei'], '200000000000000')
        self.assertEqual(result['transaction']['chainId'], '1')
        self.assertTrue(any('Selectors can collide' in w for w in result['warnings']))

    def test_all_supported_static_calls(self):
        cases = [
            ('18160ddd', 'totalSupply', {}, ''),
            ('70a08231', 'balanceOf', {'account': intent.decoder.ZTO}, address_word(intent.decoder.ZTO)),
            ('dd62ed3e', 'allowance', {'owner': intent.decoder.ZTO, 'spender': intent.IMD},
             address_word(intent.decoder.ZTO) + address_word(intent.IMD)),
            ('a9059cbb', 'transfer', {'recipient': intent.IMD, 'amountBaseUnits': '123'},
             address_word(intent.IMD) + amount_word(123)),
            ('095ea7b3', 'approve', {'spender': intent.IMD, 'amountBaseUnits': '123'},
             address_word(intent.IMD) + amount_word(123)),
            ('23b872dd', 'transferFrom', {'from': intent.decoder.ZTO, 'recipient': intent.IMD,
                                      'amountBaseUnits': '123'},
             address_word(intent.decoder.ZTO) + address_word(intent.IMD) + amount_word(123)),
        ]
        for selector, method, arguments, words in cases:
            with self.subTest(method=method):
                call = intent.interpret(envelope(selector + words))['calldata']
                self.assertEqual(call['status'], 'abi-pattern-match')
                self.assertEqual(call['candidateMethod'], method)
                self.assertEqual(call['arguments'], arguments)

    def test_approval_boundaries(self):
        for amount, kind in [(0, 'zero'), (1, 'finite'),
                             (intent.UINT256_MAX - 1, 'finite'),
                             (intent.UINT256_MAX, 'maximum-uint256')]:
            result = intent.interpret(envelope('095ea7b3' + address_word(intent.IMD) + amount_word(amount)))
            self.assertEqual(result['calldata']['approvalKind'], kind)
            self.assertEqual(result['calldata']['arguments']['amountBaseUnits'], str(amount))
            self.assertEqual(any('potentially unlimited' in w for w in result['warnings']),
                             amount == intent.UINT256_MAX)

    def test_exact_lengths_reject_truncation_and_trailing_bytes(self):
        for selector, (_, fields) in intent.METHODS.items():
            data = selector + '00' * 32 * len(fields)
            for malformed in (data + '00', data[:-2] if fields else data + '00' * 32):
                self.assertEqual(intent.interpret(envelope(malformed))['calldata']['status'],
                                 'malformed-known-selector')

    def test_nonzero_address_padding_rejected_in_every_position(self):
        for selector, (_, fields) in intent.METHODS.items():
            for index, (_, kind) in enumerate(fields):
                if kind != 'address':
                    continue
                words = ['00' * 32 for _ in fields]
                words[index] = '01' + '00' * 31
                call = intent.interpret(envelope(selector + ''.join(words)))['calldata']
                self.assertEqual(call['status'], 'malformed-known-selector')
                self.assertIn('nonzero address padding', call['reason'])
                self.assertNotIn('arguments', call)

    def test_labels_require_ethereum_chain(self):
        self.assertEqual(intent.interpret(envelope(destination=intent.IMD))['destinationLabel'], 'IMD')
        self.assertIsNone(intent.interpret(envelope(chain=4663))['destinationLabel'])
        self.assertIsNone(intent.interpret(envelope(destination='0x' + '12' * 20))['destinationLabel'])

    def test_unknown_empty_short_and_creation_calldata(self):
        for data, status in [('', 'empty'), ('a9', 'unrecognized'),
                             ('a9059c', 'unrecognized'), ('ffffffff', 'unrecognized')]:
            call = intent.interpret(envelope(data))['calldata']
            self.assertEqual(call['status'], status)
            self.assertNotIn('candidateMethod', call)
        self.assertEqual(intent.interpret(envelope(destination=None))['calldata']['status'],
                         'contract-creation')

    def test_value_fee_order_and_oversize_warnings(self):
        result = intent.interpret(envelope(value=7, priority=3, fee=2, gas=11))
        self.assertEqual(result['feeBudget']['valuePlusGasFeeCapWei'], '29')
        self.assertTrue(any('Priority fee exceeds' in w for w in result['warnings']))
        self.assertTrue(any('Native ETH' in w for w in result['warnings']))
        result = intent.interpret(envelope(value=2**256))
        self.assertTrue(any('value exceeds 256 bits' in w for w in result['warnings']))

    def test_random_uint256_amounts_preserved_exactly(self):
        rng = random.Random(7371559)
        for _ in range(200):
            amount = rng.getrandbits(256)
            result = intent.interpret(envelope('a9059cbb' + address_word(intent.IMD) + amount_word(amount)))
            self.assertEqual(result['calldata']['arguments']['amountBaseUnits'], str(amount))

    def test_malformed_envelopes_still_rejected(self):
        for raw in ('0x', '0x02c0', '0x01c0', '0x02zz'):
            with self.assertRaises(ValueError):
                intent.interpret(raw)

    def test_cli_demo_and_usage(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(intent.main(['--demo']), 0)
        self.assertIn('ZTO', output.getvalue())
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(intent.main([]), 2)


if __name__ == '__main__':
    unittest.main()
