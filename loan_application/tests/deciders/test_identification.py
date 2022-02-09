import dataclasses
import datetime
import unittest

from loan_application.deciders import identification as api
from loan_application.external_services.credit_bureaus.extrafax.sandbox.fetcher import fixture_repo
from loan_application.models.addresses import Address
from loan_application.models.credit_report import \
    CreditReport, CreditReportIdentityInfo, CreditReportPull
from loan_application.models.decisions import \
    ApplicationDenied, \
    ApplicationPending, \
    IdentityApproved
from loan_application.models.enums import\
    CreditBureau,\
    CreditReportPullStatus,\
    DeniedReason,\
    PendingState

_FSCOTT_REPORT = CreditReportPull(
        status=CreditReportPullStatus.hit,
        credit_report=CreditReport(
            pull_date=datetime.date(2019, 11, 26),
            bureau=CreditBureau.extrafax,
            identity_info=CreditReportIdentityInfo(
                full_name="Francis Fitzgerald",
                date_of_birth=datetime.date(1940, 12, 21),
                address=Address(
                    street1="1140 Broadway",
                    street2="Suite 1001",
                    city="New York",
                    region1_code="NY",
                    postal_code="10001",
                    country_code="US"
                ),
                ssn="987-65-1111"
            ),
            watchlist_hits=[],
            frozen_indicator=False,
            frozen_message_en=dataclasses.MISSING,
            extended_fraud_victim_indicator=False,
            extended_fraud_victim_message_en=dataclasses.MISSING,
            fico_score=575
        ),
        raw_xml=''
)

_MISSING_REPORT = CreditReportPull(
        status=CreditReportPullStatus.no_hit,
        credit_report=dataclasses.MISSING,
        raw_xml=''
)

class IdentificationPolicyTestCase(unittest.TestCase):
    _params_to_gold_mapping = [
        (
            dict(
                as_of_date=datetime.date(2019, 11, 27),
                full_name="Francis Fitzgerald",
                date_of_birth=datetime.date(1940, 12, 21),
                address=Address(
                    street1="1140 Broadway",
                    street2="Suite 1001",
                    city="New York",
                    region1_code="NY",
                    postal_code="10001",
                    country_code="US"
                ),
                ssn_last4="1111",
                ssn=dataclasses.MISSING,
                credit_report_pull=_FSCOTT_REPORT,
                watchlist_check_cleared=False,
                extended_victim_check_cleared=False
            ),
            IdentityApproved(credit_report_pull=_FSCOTT_REPORT)
        ),
        (
            # Name mismatches
            dict(
                as_of_date=datetime.date(2019, 11, 27),
                full_name="Scott Fitzgerald",
                date_of_birth=datetime.date(1940, 12, 21),
                address=Address(
                    street1="1140 Broadway",
                    street2="Suite 1001",
                    city="New York",
                    region1_code="NY",
                    postal_code="10001",
                    country_code="US"
                ),
                ssn_last4="1111",
                ssn=dataclasses.MISSING,
                credit_report_pull=_FSCOTT_REPORT,
                watchlist_check_cleared=False,
                extended_victim_check_cleared=False
            ),
            ApplicationDenied(reason=DeniedReason.identity_mismatch)
        ),
        (
            # SSN mismatches
            dict(
                as_of_date=datetime.date(2019, 11, 27),
                full_name="Francis Fitzgerald",
                date_of_birth=datetime.date(1940, 12, 21),
                address=Address(
                    street1="1140 Broadway",
                    street2="Suite 1001",
                    city="New York",
                    region1_code="NY",
                    postal_code="10001",
                    country_code="US"
                ),
                ssn_last4="1112",
                ssn=dataclasses.MISSING,
                credit_report_pull=_FSCOTT_REPORT,
                watchlist_check_cleared=False,
                extended_victim_check_cleared=False
            ),
            ApplicationDenied(reason=DeniedReason.identity_mismatch)
        ),
        (
            # DOB mismatches
            dict(
                as_of_date=datetime.date(2019, 11, 27),
                full_name="Francis Fitzgerald",
                date_of_birth=datetime.date(1940, 12, 20),
                address=Address(
                    street1="1140 Broadway",
                    street2="Suite 1001",
                    city="New York",
                    region1_code="NY",
                    postal_code="10001",
                    country_code="US"
                ),
                ssn_last4="1111",
                ssn=dataclasses.MISSING,
                credit_report_pull=_FSCOTT_REPORT,
                watchlist_check_cleared=False,
                extended_victim_check_cleared=False
            ),
            ApplicationDenied(reason=DeniedReason.identity_mismatch)
        ),
        (
            # non-Alabama resident, 17 years old
            dict(
                as_of_date=datetime.date(2019, 11, 27),
                full_name="Francis Fitzgerald",
                date_of_birth=datetime.date(2001,12, 21),
                address=Address(
                    street1="1140 Broadway",
                    street2="Suite 1001",
                    city="New York",
                    region1_code="NY",
                    postal_code="10001",
                    country_code="US"
                ),
                ssn_last4="1111",
                ssn=dataclasses.MISSING,
                credit_report_pull=_FSCOTT_REPORT,
                watchlist_check_cleared=False,
                extended_victim_check_cleared=False
            ),
            ApplicationDenied(reason=DeniedReason.too_young)
        ),
        (
            # Alabama resident, 18 years old
            dict(
                as_of_date=datetime.date(2019, 11, 27),
                full_name="Francis Fitzgerald",
                date_of_birth=datetime.date(2000,12, 21),
                address=Address(
                    street1="1140 Broadway",
                    street2="Suite 1001",
                    city="New York",
                    region1_code="AL",
                    postal_code="10001",
                    country_code="US"
                ),
                ssn_last4="1111",
                ssn=dataclasses.MISSING,
                credit_report_pull=_FSCOTT_REPORT,
                watchlist_check_cleared=False,
                extended_victim_check_cleared=False
            ),
            ApplicationDenied(reason=DeniedReason.too_young)
        ),
        (
            # No hit with credit bureau, no full SSN provided
            dict(
                as_of_date=datetime.date(2019, 11, 27),
                full_name="Francis Fitzgerald",
                date_of_birth=datetime.date(1940,12, 21),
                address=Address(
                    street1="1140 Broadway",
                    street2="Suite 1001",
                    city="New York",
                    region1_code="AL",
                    postal_code="10001",
                    country_code="US"
                ),
                ssn_last4="1111",
                ssn=dataclasses.MISSING,
                credit_report_pull=_MISSING_REPORT,
                watchlist_check_cleared=False,
                extended_victim_check_cleared=False
            ),
            ApplicationPending(state=PendingState.needs_ssn)
        ),
        (
            # No hit with credit bureau, SSN already provided
            dict(
                as_of_date=datetime.date(2019, 11, 27),
                full_name="Francis Fitzgerald",
                date_of_birth=datetime.date(1940,12, 21),
                address=Address(
                    street1="1140 Broadway",
                    street2="Suite 1001",
                    city="New York",
                    region1_code="AL",
                    postal_code="10001",
                    country_code="US"
                ),
                ssn_last4="1111",
                ssn="987-65-1111",
                credit_report_pull=_MISSING_REPORT,
                watchlist_check_cleared=False,
                extended_victim_check_cleared=False
            ),
            ApplicationDenied(reason=DeniedReason.identity_not_found)
        ),
    ]

    def test_policy(self):
        for params, gold in self._params_to_gold_mapping:
            self.assertEqual(api.policy(**params), gold)


class IdentificationDeciderIntegrationTestCase(unittest.TestCase):
    _params_to_gold_mapping = [
        (
            # Happy path approval
            dict(
                full_name="Francis Fitzgerald",
                date_of_birth=datetime.date(1940, 12, 21),
                address=Address(
                    street1="1140 Broadway",
                    street2="Suite 1001",
                    city="New York",
                    region1_code="NY",
                    postal_code="10001",
                    country_code="US"
                ),
                ssn_last4="1111",
                ssn=dataclasses.MISSING
            ),
            IdentityApproved(credit_report_pull=_FSCOTT_REPORT)
        ),
        (
            # No credit report found
            dict(
                full_name="Francis Fitzgerald",
                date_of_birth=datetime.date(1940, 12, 21),
                address=Address(
                    street1="1140 Broadway",
                    street2="Suite 1001",
                    city="New York",
                    region1_code="NY",
                    postal_code="10001",
                    country_code="US"
                ),
                ssn_last4="2222",
                ssn=dataclasses.MISSING
            ),
            ApplicationPending(state=PendingState.needs_ssn)
        ),
    ]

    @classmethod
    def setUpClass(cls):
        fixture_repo.load_fixtures()

    def test_decide(self):
        for params, gold in self._params_to_gold_mapping:
            self.assertEqual(api.decide(**params), gold)
