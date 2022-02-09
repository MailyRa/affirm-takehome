from dataclasses import MISSING
from decimal import Decimal
from typing import Union

from loan_application.models.credit_report import CreditReportPull
from loan_application.models.decisions import \
    ApplicationDenied,\
    ApplicationPending,\
    ApplicationApproved
from loan_application.models.enums import \
    Currency,\
    IncomeFrequency,\
    PaymentFrequency
from loan_application.models.enums.decisions import \
    DeniedReason,\
    PendingState
from loan_application.models.income import Income
from loan_application.models.requests import Address
from loan_application.models.terms import Plan

_MAX_LOAN_AMOUNT = Decimal('10000.00')
_MIN_LOAN_AMOUNT = Decimal('100.00')

# Latest currency convesions as of March 13, 2020.
# TODO: integrate a data provider so that we can refresh automatically
_CONVERSION_TO_USD_RATIOS = {
    Currency.usd: Decimal('1.0'),
    Currency.cad: Decimal('0.72'),
    Currency.gbp: Decimal('1.23'),
    Currency.eur: Decimal('1.11')
}

_INCOME_FREQUENCY_TO_ANNUAL_MULTIPLIER = {
    IncomeFrequency.biweekly: 26, # Biweekly paychecks happen 26x a year
    IncomeFrequency.monthly: 12,  # Monthly paychecks happen 12x a year
    IncomeFrequency.anually: 1
}


# for now, only 3 month, no interest loans are supported
_PLAN = Plan(
    payment_frequency=PaymentFrequency.monthly,
    number_of_payments=3,
    apr=Decimal('0.000')
)


def _compute_annualized_income_in_usd(
        income: Income
) -> Decimal:
    """
    Converts user supplied income to an annualized amount in USD, based on
    conversion rates from March 13, 2020
    :param income:
    :return:
    """
    conversion_rate = _CONVERSION_TO_USD_RATIOS[income.currency]
    freq_multiplier = _INCOME_FREQUENCY_TO_ANNUAL_MULTIPLIER[income.frequency]
    return income.amount * conversion_rate * freq_multiplier


def decide(
    requested_amount: Decimal,
    currency: Currency,
    credit_report_pull: CreditReportPull,
    address: Address,
    income: Union[Income, MISSING.__class__] = MISSING
) -> Union[ApplicationDenied, ApplicationPending, ApplicationApproved]:
    """
    Applies a simple credit policy, which inputs the customer's credit report,
    address, and (optionally) income. Since all of this data is fetched
    upstream either from the application repo or the identification decider,
    this is a pure function.
    :param requested_amount:
    :param currency:
    :param credit_report_pull:
    :param address:
    :param income:
    :return:
    """
    # Nobody should request a loan in non-USD for now. It's fair to error out
    # if they try
    assert currency is Currency.usd

    # Due to state-specific regulation, loans are not available in West
    # Virginia and Iowa
    if address.region1_code in ('WV', 'IA'):
        return ApplicationDenied(
            reason=DeniedReason.geography
        )

    # Don't allow people to borrow more than the maximum amount, $10,000
    if requested_amount > _MAX_LOAN_AMOUNT:
        return ApplicationDenied(
            reason=DeniedReason.amount_over_max
        )

    # Don't allow people to borrow less than the minimum amount, $100
    if requested_amount <= _MIN_LOAN_AMOUNT:
        return ApplicationDenied(
            reason=DeniedReason.amount_under_min
        )

    # Customers with credit score less than 575 are too high risk without
    # a richer statistical model
    if credit_report_pull.credit_report.fico_score < 575:
        return ApplicationDenied(
            reason=DeniedReason.insufficient_credit
        )

    # Customers with credit score over 720 are likely to pay back without
    # additional inputs required
    if credit_report_pull.credit_report.fico_score >= 720:
        return ApplicationApproved(
            amount=requested_amount,
            currency=currency,
            approved_plans=[_PLAN]
        )

    # Customers with FICO between 575 and 719 requesting under $1000 get
    # approved. If the amount is over that and they haven't supplied income,
    # ask them to. Customers with FICO between 575 and 719 requesting over
    # $1000 and annualized income over $50,000 qualify for the loan
    if requested_amount < Decimal('1000.00'):
        return ApplicationApproved(
            amount=requested_amount,
            currency=currency
        )
    elif income is MISSING:
        return ApplicationPending(
            state=PendingState.needs_income
        )
    elif _compute_annualized_income_in_usd(income) > Decimal('50000.00'):
        return ApplicationApproved(
            amount=requested_amount,
            currency=currency,
            approved_plans=[_PLAN]
        )
    else:
        return ApplicationDenied(
            reason=DeniedReason.insufficient_credit
        )
