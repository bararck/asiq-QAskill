"""Synthetic in-memory workflow, with deliberately unsafe educational variant."""
from fractions import Fraction
from threading import RLock


def _half_up(value):
    """Round a nonnegative rational to an integer, without Decimal/float."""
    return (2 * value.numerator + value.denominator) // (2 * value.denominator)


class Provider:
    def __init__(self, outcome):
        self.outcome = outcome
        self.calls = []
        self.accepted = []

    def send(self, key):
        self.calls.append(key)
        if self.outcome == "refused":
            return "REFUSED"
        self.accepted.append(key)
        if self.outcome == "ambiguous":
            raise TimeoutError("Acceptance happened; acknowledgment lost")
        return "DELIVERED"


class FixedWorkflow:
    def __init__(self, provider_outcome="delivered"):
        self.jobs = {}
        self.allowed = True
        self.provider = Provider(provider_outcome)
        self._lock = RLock()
        self._invoices = {}
        self.tax_rate = "0"

    def claim(self, key):
        with self._lock:
            self.jobs.setdefault(key, "CLAIMED")
            return self.jobs[key]

    def deliver(self, key):
        with self._lock:
            if self.jobs[key] != "CLAIMED":
                return self.jobs[key]
            if not self.allowed:
                self.jobs[key] = "REFUSED"
            else:
                try:
                    self.jobs[key] = self.provider.send(key)
                except TimeoutError:
                    self.jobs[key] = "UNKNOWN"
            return self.jobs[key]

    def issue_invoice(self, lines, tax_rate):
        lines = tuple(lines)
        rate = Fraction(tax_rate)
        if rate < 0 or any(type(qty) is not int or qty < 0 or Fraction(price) < 0
                           for price, qty in lines):
            raise ValueError("Synthetic invoice requires nonnegative prices, integer quantities and tax")
        subtotal = sum(_half_up(Fraction(price) * qty * 100) for price, qty in lines)
        total = subtotal + _half_up(subtotal * rate)
        with self._lock:
            invoice = len(self._invoices) + 1
            self._invoices[invoice] = total
            return invoice

    def invoice_total(self, invoice):
        total = self._invoices[invoice]
        return f"{total // 100}.{total % 100:02d}"


class BuggyWorkflow(FixedWorkflow):
    # Seeded defect: fixtures leak state between instances.
    shared_jobs = {}

    def __init__(self, provider_outcome="delivered"):
        super().__init__(provider_outcome)
        self.jobs = self.shared_jobs

    def deliver(self, key):
        # Seeded defects: stale claim-time permission, no replay guard, false refusal.
        if key not in self.jobs:
            raise KeyError(key)
        try:
            self.jobs[key] = self.provider.send(key)
        except TimeoutError:
            self.jobs[key] = "REFUSED"
        return self.jobs[key]

    def issue_invoice(self, lines, tax_rate):
        self.tax_rate = tax_rate
        invoice = len(self._invoices) + 1
        self._invoices[invoice] = tuple(lines)
        return invoice

    def invoice_total(self, invoice):
        # Seeded defect: reinterpret history using today's tax rate.
        subtotal = sum(_half_up(Fraction(price) * qty * 100)
                       for price, qty in self._invoices[invoice])
        total = subtotal + _half_up(subtotal * Fraction(self.tax_rate))
        return f"{total // 100}.{total % 100:02d}"
