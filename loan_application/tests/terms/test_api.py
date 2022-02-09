from dataclasses import MISSING
from datetime import date
from decimal import Decimal
import unittest

from loan_application.models.enums import Currency, PaymentFrequency
from loan_application.models.terms import Plan, Schedule
from loan_application.terms import api


_PLAN = Plan(
    payment_frequency=PaymentFrequency.monthly,
    number_of_payments=3,
    apr=Decimal(0)
)

class ComputeScheduleTestCase(unittest.TestCase):
    _params_to_gold_mapping = [
        (
             dict(
                plan=_PLAN,
                amount=Decimal("999.99"),
                currency=Currency.usd,
                loan_start_date=date(2020, 3, 14)
             ),
            Schedule(
                schedule_id=MISSING,
                payment_frequency=PaymentFrequency.monthly,
                number_of_payments=3,
                currency=Currency.usd,
                payment_amount=Decimal("333.33"),
                first_payment_amount=Decimal("333.33"),
                last_payment_amount=Decimal("333.33"),
                payments_total=Decimal("999.99"),
                principal_total=Decimal("999.99"),
                interest_total=Decimal(0),
                apr=Decimal(0),
                loan_start_date=date(2020, 3, 14),
                first_payment_date=date(2020, 4, 14)
            )
        ),
        (
             dict(
                plan=_PLAN,
                amount=Decimal("1000.00"),
                currency=Currency.usd,
                loan_start_date=date(2020, 3, 14)
             ),
            Schedule(
                schedule_id=MISSING,
                payment_frequency=PaymentFrequency.monthly,
                number_of_payments=3,
                currency=Currency.usd,
                payment_amount=Decimal("333.34"),
                first_payment_amount=Decimal("333.34"),
                last_payment_amount=Decimal("333.32"),
                payments_total=Decimal("1000.00"),
                principal_total=Decimal("1000.00"),
                interest_total=Decimal(0),
                apr=Decimal(0),
                loan_start_date=date(2020, 3, 14),
                first_payment_date=date(2020, 4, 14)
            )
        ),
        (
             dict(
                plan=_PLAN,
                amount=Decimal("1000.01"),
                currency=Currency.usd,
                loan_start_date=date(2020, 3, 14)
             ),
            Schedule(
                schedule_id=MISSING,
                payment_frequency=PaymentFrequency.monthly,
                number_of_payments=3,
                currency=Currency.usd,
                payment_amount=Decimal("333.34"),
                first_payment_amount=Decimal("333.34"),
                last_payment_amount=Decimal("333.33"),
                payments_total=Decimal("1000.01"),
                principal_total=Decimal("1000.01"),
                interest_total=Decimal(0),
                apr=Decimal(0),
                loan_start_date=date(2020, 3, 14),
                first_payment_date=date(2020, 4, 14)
            )
        ),
        (
             dict(
                plan=_PLAN,
                amount=Decimal("1000.01"),
                currency=Currency.usd,
                loan_start_date=date(2020, 3, 30)
             ),
            Schedule(
                schedule_id=MISSING,
                payment_frequency=PaymentFrequency.monthly,
                number_of_payments=3,
                currency=Currency.usd,
                payment_amount=Decimal("333.34"),
                first_payment_amount=Decimal("333.34"),
                last_payment_amount=Decimal("333.33"),
                payments_total=Decimal("1000.01"),
                principal_total=Decimal("1000.01"),
                interest_total=Decimal(0),
                apr=Decimal(0),
                loan_start_date=date(2020, 3, 30),
                first_payment_date=date(2020, 4, 28)
            )
        ),
    ]

    def test_compute_schedule(self):
        self.maxDiff = None
        for params, gold in self._params_to_gold_mapping:
            self.assertEqual(api.compute_schedule(**params), gold)
