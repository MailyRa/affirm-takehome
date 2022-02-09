from dataclasses import dataclass


@dataclass(frozen=True)
class InitializeLoanApplication:
    merchant_id: str
    requested_amount_cents: int
    currency: str
