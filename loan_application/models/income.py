from dataclasses import dataclass
from decimal import Decimal
from .enums import Currency, IncomeFrequency


@dataclass(frozen=True)
class Income:
    frequency: IncomeFrequency
    amount: Decimal
    currency: Currency
