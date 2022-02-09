from dataclasses import dataclass
from decimal import Decimal
from ..enums import Currency, IncomeFrequency
from ..income import Income


@dataclass(frozen=True)
class SubmitIncome:
    loan_application_id: str
    income: Income

    @classmethod
    def from_json(cls, loan_application_id, body):
        amount = Decimal(body.pop('amount_cents')) / Decimal(100)
        currency = Currency(body.pop('currency').lower())
        frequency = IncomeFrequency(body.pop('frequency'))
        income = Income(amount=amount, currency=currency, frequency=frequency)
        return cls(
            loan_application_id=loan_application_id,
            income=income)
