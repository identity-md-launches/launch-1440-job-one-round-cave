"""Offline checks using retained real mainnet ZTO evidence, then mutations."""
import copy
import contextlib
import io
import json
from pathlib import Path
import unittest
from unittest import mock
import crosscheck as c


class CrosscheckTests(unittest.TestCase):
    def setUp(self):
        self.left, self.right = [json.loads((Path(__file__).parent / name).read_text())
                                 for name in ("publicnode.json", "drpc.json")]

    def refresh(self, capture):
        events, duplicates = c.window.validate_logs(capture["raw_logs"], capture["decimals"],
            capture["token_address"], capture["from_block"], capture["to_block"])
        capture.update(transfers=events, duplicate_count=duplicates, transfer_count=len(events))

    def test_real_agreement(self):
        r = c.compare(self.left, self.right)
        self.assertEqual(r["status"], "agreement")
        self.assertEqual(r["transfer_counts"], [3, 3])

    def test_missing_event_is_disagreement(self):
        removed = self.right["raw_logs"].pop(0)
        self.refresh(self.right)
        r = c.compare(self.left, self.right)
        self.assertEqual(r["status"], "disagreement")
        self.assertEqual(len(r["only_left"]), 1)
        self.assertEqual(r["only_left"][0]["transaction_hash"], removed["transactionHash"])

    def test_conflicting_event(self):
        self.right["raw_logs"][0]["data"] = "0x" + format(123, "064x")
        self.refresh(self.right)
        self.assertEqual(len(c.compare(self.left, self.right)["conflicts"]), 1)

    def test_boundary_disagreement(self):
        # First boundary in the real fixture has no event, so this is valid but different evidence.
        self.right["from_block_anchor"]["hash"] = "0x" + "ab" * 32
        r = c.compare(self.left, self.right)
        self.assertIn("from_block_anchor", r["metadata_differences"])
        self.assertEqual(r["status"], "disagreement")

    def test_duplicates_do_not_create_disagreement(self):
        self.right["raw_logs"].append(copy.deepcopy(self.right["raw_logs"][0]))
        self.refresh(self.right)
        self.assertEqual(c.compare(self.left, self.right)["status"], "agreement")

    def test_order_does_not_create_disagreement(self):
        self.right["raw_logs"].reverse()
        self.refresh(self.right)
        self.assertEqual(c.compare(self.left, self.right)["status"], "agreement")

    def test_malformed_captures_fail(self):
        mutations = [("chain_id", True), ("schema_version", True), ("rpc", False),
                     ("decimals", 256), ("transfer_count", 0), ("decimals_block", 1),
                     ("from_block", -1), ("raw_logs", None), ("transfers", []),
                     ("read_only", 1), ("provider_result", "unvalidated")]
        for key, value in mutations:
            with self.subTest(key=key):
                bad = copy.deepcopy(self.right)
                bad[key] = value
                with self.assertRaises(c.window.RpcError):
                    c.compare(self.left, bad)

    def test_raw_evidence_is_revalidated(self):
        self.right["raw_logs"][0]["removed"] = True
        with self.assertRaises(c.window.RpcError):
            c.compare(self.left, self.right)

    def test_same_url_rejected(self):
        self.right["rpc"] = self.left["rpc"] + "/"
        with self.assertRaises(c.window.RpcError):
            c.compare(self.left, self.right)

    def test_distinct_ranges_disagree(self):
        self.right["from_block"] -= 1
        self.right["from_block_anchor"]["number"] -= 1
        self.assertIn("from_block", c.compare(self.left, self.right)["metadata_differences"])

    def test_live_mode_pins_same_range(self):
        with mock.patch.object(c.window, "rpc", side_effect=["0x1", hex(26177321)]), \
                mock.patch.object(c, "capture", side_effect=[self.left, self.right]) as acquire, \
                contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(c.main([]), 0)
        self.assertEqual([call.args[1:] for call in acquire.call_args_list],
                         [("zto", 26177298, 26177309)] * 2)
        self.assertEqual(json.loads(output.getvalue())["status"], "agreement")

    def test_second_provider_failure_has_no_agreement_output(self):
        with mock.patch.object(c, "capture", side_effect=[self.left, c.window.RpcError("offline")]), \
                contextlib.redirect_stdout(io.StringIO()) as output:
            with self.assertRaises(c.window.RpcError):
                c.main(["--from-block", "26177298", "--to-block", "26177309"])
        self.assertEqual(output.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
