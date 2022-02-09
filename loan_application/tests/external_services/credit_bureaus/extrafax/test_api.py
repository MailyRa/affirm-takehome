import dataclasses
import datetime
import unittest

from loan_application.external_services.credit_bureaus.extrafax import api
from loan_application.external_services.credit_bureaus.extrafax.sandbox.fetcher \
    import fixture_repo
from loan_application.models.addresses import Address
from loan_application.models.enums import CreditReportPullStatus


class ExTraFaxAPIIntegrationTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixture_repo.load_fixtures()

    def test_hit(self):
        pull = api.pull_credit_report(
            full_name="Francis Fitzgerald",
            date_of_birth=datetime.date(1940, 12, 21),
            ssn_last4="1111",
            address=Address(
                street1="1140 Broadway",
                street2="Suite 1001",
                city="New York",
                region1_code="NY",
                postal_code="10001",
                country_code="US"
            ),
            ssn=dataclasses.MISSING
        )
        # make sure we got a hit
        self.assertEqual(pull.status, CreditReportPullStatus.hit)

        # do some sanity checks to make sure the right fixture was pulled/parsed
        self.assertEqual(pull.credit_report.identity_info.ssn, "987-65-1111")
        self.assertEqual(pull.credit_report.fico_score, 575)

    def test_no_hit_without_ssn_hit_with_ssn(self):
        params = dict(
            full_name="E Hemingway",
            date_of_birth=datetime.date(1961, 7, 2),
            ssn_last4="2222",
            address=Address(
                street1="1140 Broadway",
                street2="Suite 1001",
                city="New York",
                region1_code="NY",
                postal_code="10001",
                country_code="US"
            ),
            ssn=dataclasses.MISSING
        )
        pull = api.pull_credit_report(**params)

        # shouldn't get a hit without SSN
        self.assertEqual(pull.status, CreditReportPullStatus.no_hit)
        self.assertEqual(pull.credit_report, dataclasses.MISSING)

        # now pull with the full SSN
        params.update(ssn="987-65-2222")
        pull = api.pull_credit_report(**params)

        # do some sanity checks to make sure the right fixture was pulled/parsed
        self.assertEqual(pull.credit_report.identity_info.ssn, "987-65-2222")
        self.assertEqual(pull.credit_report.fico_score, 803)
