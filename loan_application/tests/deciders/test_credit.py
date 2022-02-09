import dataclasses
import datetime
from decimal import Decimal
import unittest

from loan_application.deciders import credit as api
from loan_application.models.addresses import Address
from loan_application.models.credit_report import \
    CreditReport, CreditReportIdentityInfo, CreditReportPull
from loan_application.models.decisions import \
    ApplicationDenied, \
    ApplicationPending, \
    ApplicationApproved
from loan_application.models.enums import\
    Currency,\
    CreditBureau,\
    CreditReportPullStatus,\
    DeniedReason,\
    IncomeFrequency,\
    PendingState,\
    PaymentFrequency
from loan_application.models.income import Income
from loan_application.models.terms import Plan


_ADDRESS = Address(
    street1="1140 Broadway",
    street2="Suite 1001",
    city="New York",
    region1_code="NY",
    postal_code="10001",
    country_code="US"
)

_FSCOTT_REPORT = CreditReportPull(
        status=CreditReportPullStatus.hit,
        credit_report=CreditReport(
            pull_date=datetime.date(2019, 11, 26),
            bureau=CreditBureau.extrafax,
            identity_info=CreditReportIdentityInfo(
                full_name="Francis Fitzgerald",
                date_of_birth=datetime.date(1940, 12, 21),
                address=_ADDRESS,
                ssn="987-65-1111"
            ),
            watchlist_hits=[],
            frozen_indicator=False,
            frozen_message_en=dataclasses.MISSING,
            extended_fraud_victim_indicator=False,
            extended_fraud_victim_message_en=dataclasses.MISSING,
            fico_score=721
        ),
        raw_xml=''
)

_EXPECTED_PLAN = Plan(
    payment_frequency=PaymentFrequency.monthly,
    number_of_payments=3,
    apr=Decimal(0),
)


class CreditDeciderTestCase(unittest.TestCase):
    _params_to_gold_mapping = [
        (
            dict(
                requested_amount=Decimal('1000.01'),
                currency=Currency.usd,
                credit_report_pull=_FSCOTT_REPORT,
                address=dataclasses.replace(_ADDRESS, region1_code="WV")
            ),
            ApplicationDenied(reason=DeniedReason.geography)
        ),
        (
            dict(
                requested_amount=Decimal('1000.01'),
                currency=Currency.usd,
                credit_report_pull=_FSCOTT_REPORT,
                address=dataclasses.replace(_ADDRESS, region1_code="IA")
            ),
            ApplicationDenied(reason=DeniedReason.geography)
        ),
        (
            dict(
                requested_amount=Decimal('10000.01'),
                currency=Currency.usd,
                credit_report_pull=_FSCOTT_REPORT,
                address=_ADDRESS
            ),
            ApplicationDenied(reason=DeniedReason.amount_over_max)
        ),
        (
            dict(
                requested_amount=Decimal('99.99'),
                currency=Currency.usd,
                credit_report_pull=_FSCOTT_REPORT,
                address=_ADDRESS
            ),
            ApplicationDenied(reason=DeniedReason.amount_under_min)
        ),
        (
            dict(
                requested_amount=Decimal('1000.01'),
                currency=Currency.usd,
                credit_report_pull=dataclasses.replace(
                    _FSCOTT_REPORT,
                    credit_report=dataclasses.replace(
                        _FSCOTT_REPORT.credit_report, fico_score=574)
                ),
                address=_ADDRESS,
            ),
            ApplicationDenied(reason=DeniedReason.insufficient_credit)
        ),
        (
            dict(
                requested_amount=Decimal('1000.01'),
                currency=Currency.usd,
                credit_report_pull=_FSCOTT_REPORT,
                address=_ADDRESS,
            ),
            ApplicationApproved(
                amount=Decimal('1000.01'),
                currency=Currency.usd,
                approved_plans=[_EXPECTED_PLAN]
            )
        ),
        (
            dict(
                requested_amount=Decimal('9999.99'),
                currency=Currency.usd,
                credit_report_pull=_FSCOTT_REPORT,
                address=_ADDRESS,
            ),
            ApplicationApproved(
                amount=Decimal('9999.99'),
                currency=Currency.usd,
                approved_plans=[_EXPECTED_PLAN]
            )
        ),
        (
            dict(
                requested_amount=Decimal('1000.01'),
                currency=Currency.usd,
                credit_report_pull=dataclasses.replace(
                    _FSCOTT_REPORT,
                    credit_report=dataclasses.replace(
                        _FSCOTT_REPORT.credit_report, fico_score=575)
                ),
                address=_ADDRESS,
            ),
            ApplicationPending(state=PendingState.needs_income)
        ),
        (
            dict(
                requested_amount=Decimal('1000.01'),
                currency=Currency.usd,
                credit_report_pull=dataclasses.replace(
                    _FSCOTT_REPORT,
                    credit_report=dataclasses.replace(
                        _FSCOTT_REPORT.credit_report, fico_score=575)
                ),
                address=_ADDRESS,
                income=Income(
                    amount=Decimal('49999.99'),
                    currency=Currency.usd,
                    frequency=IncomeFrequency.anually
                )
            ),
            ApplicationDenied(reason=DeniedReason.insufficient_credit)
        ),
        (
            dict(
                requested_amount=Decimal('1000.01'),
                currency=Currency.usd,
                credit_report_pull=dataclasses.replace(
                    _FSCOTT_REPORT,
                    credit_report=dataclasses.replace(
                        _FSCOTT_REPORT.credit_report, fico_score=575)
                ),
                address=_ADDRESS,
                income=Income(
                    amount=Decimal('50000.01'),
                    currency=Currency.usd,
                    frequency=IncomeFrequency.anually
                )
            ),
            ApplicationApproved(
                amount=Decimal('1000.01'),
                currency=Currency.usd,
                approved_plans=[_EXPECTED_PLAN]
            )
        ),
    ]

    def test_decide(self):
        for params, gold in self._params_to_gold_mapping:
            self.assertEqual(api.decide(**params), gold)
