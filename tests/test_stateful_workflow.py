"""Mandatory synthetic contracts; select the educational defect via ASIQ_LAB_IMPLEMENTATION."""
import os
import unittest


class StatefulWorkflowTests(unittest.TestCase):
    def test_invoice_rejects_out_of_domain_inputs_before_storage(self):
        from labs.stateful_workflow.workflow import FixedWorkflow
        for lines, tax in [((("1.00", -1),), "0"), ((("-0.01", 1),), "0"),
                           ((("1", 1),), "-0.1"), ((("1", True),), "0"),
                           ((("1", 1.5),), "0")]:
            with self.subTest(lines=lines, tax=tax):
                lab = FixedWorkflow()
                with self.assertRaises(ValueError):
                    lab.issue_invoice(lines, tax)
                self.assertEqual(lab._invoices, {})

    def workflow(self, **kwargs):
        # Deliberately inside the test: removing the lab is a hard test failure.
        try:
            from labs.stateful_workflow import workflow
        except ImportError as exc:
            self.fail(f"Mandatory lab unavailable: {exc}")
        implementation = os.environ.get("ASIQ_LAB_IMPLEMENTATION", "fixed")
        classes = {"fixed": workflow.FixedWorkflow, "buggy": workflow.BuggyWorkflow}
        return classes[implementation](**kwargs)

    def test_permission_revoked_after_claim(self):
        lab = self.workflow()
        lab.claim("revoked")
        lab.allowed = False
        self.assertEqual(lab.deliver("revoked"), "REFUSED")
        self.assertEqual(lab.provider.calls, [])

    def test_ambiguous_provider_failure_is_unknown(self):
        lab = self.workflow(provider_outcome="ambiguous")
        lab.claim("ambiguous")
        self.assertEqual(lab.deliver("ambiguous"), "UNKNOWN")
        self.assertEqual(lab.provider.calls, ["ambiguous"])
        # The simulator accepted the effect before losing the acknowledgment.
        self.assertEqual(lab.provider.accepted, ["ambiguous"])

    def test_explicit_provider_refusal_is_refused(self):
        lab = self.workflow(provider_outcome="refused")
        lab.claim("refused")
        self.assertEqual(lab.deliver("refused"), "REFUSED")
        self.assertEqual(lab.provider.accepted, [])

    def test_replay_never_resends_terminal_or_unknown(self):
        for outcome, expected in (("delivered", "DELIVERED"),
                                  ("ambiguous", "UNKNOWN"), ("refused", "REFUSED")):
            with self.subTest(outcome=outcome):
                lab = self.workflow(provider_outcome=outcome)
                lab.claim("replay-" + outcome)
                key = "replay-" + outcome
                self.assertEqual(lab.deliver(key), expected)
                lab.allowed = False
                self.assertEqual(lab.claim(key), expected)
                self.assertEqual(lab.deliver(key), expected)
                self.assertEqual(lab.provider.calls, [key])

    def test_concurrent_workers_send_once(self):
        from concurrent.futures import ThreadPoolExecutor
        from threading import Barrier
        lab = self.workflow()
        start = Barrier(4)

        def worker(_):
            start.wait(timeout=5)
            lab.claim("concurrent")
            return lab.deliver("concurrent")

        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(worker, range(4)))
        self.assertEqual(results, ["DELIVERED"] * 4)
        self.assertEqual(lab.provider.calls, ["concurrent"])
        self.assertEqual(lab.provider.accepted, ["concurrent"])

    def test_unclaimed_delivery_has_no_effect(self):
        lab = self.workflow()
        with self.assertRaises(KeyError):
            lab.deliver("absent")
        self.assertEqual(lab.provider.calls, [])

    def test_historical_snapshot_matches_independent_decimal_oracle(self):
        from decimal import Decimal, ROUND_HALF_UP
        lab = self.workflow()
        lines = (("0.05", 3), ("19.995", 2))
        # Oracle uses Decimal line rounding, independently of integer-cent lab.
        cents = Decimal("0.01")
        subtotal = sum((Decimal(price) * qty).quantize(cents, rounding=ROUND_HALF_UP)
                       for price, qty in lines)
        tax = (subtotal * Decimal("0.075")).quantize(cents, rounding=ROUND_HALF_UP)
        expected = format(subtotal + tax, ".2f")
        invoice = lab.issue_invoice(lines, "0.075")
        lines = (("999.99", 100),)  # Later catalog/input changes are irrelevant.
        lab.tax_rate = "0.50"
        self.assertEqual(lab.invoice_total(invoice), expected)
        self.assertEqual(lab.invoice_total(invoice), "43.15")

    def test_fixture_isolation(self):
        first = self.workflow()
        second = self.workflow()
        first.claim("isolation")
        self.assertEqual(second.jobs, {})
        self.assertIsNot(first.jobs, second.jobs)


if __name__ == "__main__":
    unittest.main()
