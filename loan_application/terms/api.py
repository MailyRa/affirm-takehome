from dataclasses import MISSING
from datetime import date
from decimal import Decimal
from typing import Tuple

from loan_application.models.enums import Currency, PaymentFrequency
from loan_application.models.terms import Plan, Schedule


def _compute_total_interest_and_first_payment_date(
        principal_total: Decimal,
        apr: Decimal,
        loan_start_date: date
) -> Tuple[Decimal, date]:
    # TODO: support interest-bearing loans
    assert apr == Decimal(0)

    interest_total = Decimal(0)

    # for more predictability, only bill people the first through 28th of the
    # month
    if loan_start_date.day >= 28:
        first_payment_day = 28
    else:
        first_payment_day = loan_start_date.day

    if loan_start_date.month == 12:
        first_payment_month = 1
        first_payment_year = loan_start_date.year + 1
    else:
        first_payment_month = loan_start_date.month + 1
        first_payment_year = loan_start_date.year
    first_payment_date = date(
        first_payment_year, first_payment_month, first_payment_day)
    return interest_total, first_payment_date


def _compute_payment_amounts(
        payments_total: Decimal,
        number_of_payments: int
) -> Tuple[Decimal, Decimal]:
    # with only one payment, the first and last payments are equal
    if number_of_payments == 1:
        return payments_total, payments_total

    ## STRATEGY FOR COMPUTING PAYMENT AMOUNTS ##
    # 1. divide into equal payment amounts by rounding up the total a few cents
    # 2. this will be the payment amount for all but the last payment
    # 3. last payment will be that amount minus the amount we rounded

    # specific amount to round so that payments are even
    cents_to_round = \
        (number_of_payments - (100 * payments_total) % number_of_payments) % number_of_payments
    rounded_total = payments_total + (cents_to_round / Decimal(100))
    first_payment_amount = rounded_total / number_of_payments
    last_payment_amount = first_payment_amount - (cents_to_round / Decimal(100))
    return first_payment_amount, last_payment_amount

def compute_schedule(
        plan: Plan,
        amount: Decimal,
        currency: Currency,
        loan_start_date: date
) -> Schedule:
    """
    Pure function to compute a payment schedule from plan, amount,
    and starting date.
    :param plan:
    :param amount:
    :param currency:
    :param loan_start_date:
    :return:
    """
    # invariants
    assert amount > Decimal(0)
    assert currency is Currency.usd
    assert plan.number_of_payments > 0

    # invariants until we support certain product features...
    assert plan.apr == Decimal(0)
    assert plan.payment_frequency is PaymentFrequency.monthly
    assert plan.number_of_payments < 100

    principal_total = amount

    interest_total, first_payment_date = \
        _compute_total_interest_and_first_payment_date(
            principal_total, plan.apr, loan_start_date)

    payments_total = principal_total + interest_total

    first_payment_amount, last_payment_amount = _compute_payment_amounts(
        payments_total, plan.number_of_payments
    )

    return Schedule(
        schedule_id=MISSING,
        payment_frequency=plan.payment_frequency,
        number_of_payments=plan.number_of_payments,
        currency=currency,
        payment_amount=first_payment_amount,
        first_payment_amount=first_payment_amount,
        last_payment_amount=last_payment_amount,
        payments_total=principal_total + interest_total,
        principal_total=principal_total,
        interest_total=interest_total,
        apr=plan.apr,
        loan_start_date=loan_start_date,
        first_payment_date=first_payment_date
    )
