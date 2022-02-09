from dataclasses import dataclass, MISSING
from datetime import date
from decimal import Decimal
from typing import Union

from .enums import Currency, PaymentFrequency


@dataclass(frozen=True)
class Plan:
    payment_frequency: PaymentFrequency
    number_of_payments: int
    apr: Decimal


@dataclass(frozen=True)
class Schedule:
    schedule_id: Union[str, MISSING.__class__]
    payment_frequency: PaymentFrequency
    number_of_payments: int
    currency: Currency
    payment_amount: Decimal
    first_payment_amount: Decimal
    last_payment_amount: Decimal
    payments_total: Decimal
    principal_total: Decimal
    interest_total: Decimal
    apr: Decimal
    loan_start_date: date
    first_payment_date: date

    @staticmethod
    def _format_dollar(decimal_val: Decimal) -> str:
        return "${}".format(decimal_val.quantize(Decimal("1.00")))

    @staticmethod
    def _format_apr(decimal_val: Decimal) -> str:
        return "{}% APR".format(decimal_val.quantize(Decimal("1.000")))

    def to_display_json(self):
        # display of non-USD currency not presently supported
        assert self.currency is Currency.usd

        # only monthly terms presently supported fro display
        assert self.payment_frequency is PaymentFrequency.monthly

        return {
            "schedule_id": self.schedule_id,
            "payment_frequency": self.payment_frequency.value,
            "number_of_payments": str(self.number_of_payments),
            "currency": self.currency.value.upper(),
            "payment_amount": "{} per month".format(
                self._format_dollar(self.payment_amount)),
            "first_payment_amount": self._format_dollar(
                self.first_payment_amount
            ),
            "last_payment_amount": self._format_dollar(
                self.last_payment_amount
            ),
            "payments_total": self._format_dollar(self.payments_total),
            "principal_total": self._format_dollar(self.principal_total),
            "interest_total": self._format_dollar(self.interest_total),
            "apr": self._format_apr(self.apr),
            "loan_start_date": self.loan_start_date.strftime(
                '%B %d, %Y'
            ),
            "first_payment_date": self.first_payment_date.strftime(
                '%B %d, %Y')
        }
