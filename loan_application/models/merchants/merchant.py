from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class MerchantConfiguration:
    merchant_id: str
    name: str
    minimum_loan_amount: Decimal
    maximum_loan_amount: Decimal
