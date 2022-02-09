import dataclasses
import datetime
import os
import unittest

from loan_application.external_services.credit_bureaus.extrafax import parser
from loan_application.external_services.credit_bureaus.extrafax import sandbox
from loan_application.models.addresses import Address
from loan_application.models.credit_report import \
    CreditReport, \
    CreditReportIdentityInfo,\
    CreditReportPull
from loan_application.models.enums import \
    CreditBureau, CreditReportPullStatus, Watchlist


_EV_MESSAGE_EN = (
    "This file has an extended fraud alert activated. Please verify the "
    "customer's identity in person before extending credit.")

_FROZEN_MESSAGE_EN = (
    "Your credit file has a temporary freeze. If you want to apply for credit "
    "products, please call ExTraFax at +1-555-123-1234 to remove the freeze.")


class ExTraFaxCreditReportParserTestCase(unittest.TestCase):
    _gold_mapping = {
        'ehemingway.xml': CreditReportPull(
            status=CreditReportPullStatus.hit,
            credit_report=CreditReport(
                pull_date=datetime.date(2019, 11, 26),
                bureau=CreditBureau.extrafax,
                identity_info=CreditReportIdentityInfo(
                    full_name="E Hemingway",
                    date_of_birth=datetime.date(1961, 7, 2),
                    address=Address(
                        street1="1140 Broadway",
                        street2="Suite 1001",
                        city="New York",
                        region1_code="NY",
                        postal_code="10001",
                        country_code="US"
                    ),
                    ssn="987-65-2222"
                ),
                watchlist_hits=[],
                frozen_indicator=False,
                frozen_message_en=dataclasses.MISSING,
                extended_fraud_victim_indicator=False,
                extended_fraud_victim_message_en=dataclasses.MISSING,
                fico_score=803
            ),
            raw_xml=''
        ),
        'fscott.xml': CreditReportPull(
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
        ),
        'jsalinger.xml': CreditReportPull(
            status=CreditReportPullStatus.hit,
            credit_report=CreditReport(
                pull_date=datetime.date(2019, 11, 26),
                bureau=CreditBureau.extrafax,
                identity_info=CreditReportIdentityInfo(
                    full_name="J Salinger",
                    date_of_birth=datetime.date(1919, 1, 1),
                    address=Address(
                        street1="1140 Broadway",
                        street2="Suite 1001",
                        city="New York",
                        region1_code="NY",
                        postal_code="10001",
                        country_code="US"
                    ),
                    ssn="987-65-4444"
                ),
                watchlist_hits=[],
                frozen_indicator=False,
                frozen_message_en=dataclasses.MISSING,
                extended_fraud_victim_indicator=True,
                extended_fraud_victim_message_en=_EV_MESSAGE_EN,
                fico_score=675
            ),
            raw_xml=''
        ),
        'nohit.xml': CreditReportPull(
            status=CreditReportPullStatus.no_hit,
            credit_report=dataclasses.MISSING,
            raw_xml=''
        ),
        'sketcherswashington.xml': CreditReportPull(
            status=CreditReportPullStatus.hit,
            credit_report=CreditReport(
                pull_date=datetime.date(2019, 11, 26),
                bureau=CreditBureau.extrafax,
                identity_info=CreditReportIdentityInfo(
                    full_name="Sketchers Washington",
                    date_of_birth=datetime.date(1972, 5, 5),
                    address=Address(
                        street1="1140 Broadway",
                        street2="Suite 1001",
                        city="New York",
                        region1_code="NY",
                        postal_code="10001",
                        country_code="US"
                    ),
                    ssn="987-65-5555"
                ),
                watchlist_hits=[Watchlist.ofac, Watchlist.osfi],
                frozen_indicator=False,
                frozen_message_en=dataclasses.MISSING,
                extended_fraud_victim_indicator=False,
                extended_fraud_victim_message_en=dataclasses.MISSING,
                fico_score=602
            ),
            raw_xml=''
        ),
        'zscott.xml': CreditReportPull(
            status=CreditReportPullStatus.hit,
            credit_report=CreditReport(
                pull_date=datetime.date(2019, 11, 26),
                bureau=CreditBureau.extrafax,
                identity_info=CreditReportIdentityInfo(
                    full_name="Z Fitzgerald",
                    date_of_birth=datetime.date(1948, 3, 10),
                    address=Address(
                        street1="1140 Broadway",
                        street2="Suite 1001",
                        city="New York",
                        region1_code="NY",
                        postal_code="10001",
                        country_code="US"
                    ),
                    ssn="987-65-3333"
                ),
                watchlist_hits=[],
                frozen_indicator=True,
                frozen_message_en=_FROZEN_MESSAGE_EN,
                extended_fraud_victim_indicator=False,
                extended_fraud_victim_message_en=dataclasses.MISSING,
                fico_score=794
            ),
            raw_xml=''
        ),
    }

    def _load_fixture_parse_and_check(
            self,
            filename: str,
            gold: CreditReportPull
    ):
        fixture_path = os.path.join(sandbox.__path__[0], 'fixtures', filename)
        with open(fixture_path, 'r') as f:
            raw_xml=f.read()
            parsed = parser.parse_credit_report(raw_xml)
        self.assertEqual(parsed, dataclasses.replace(gold, raw_xml=raw_xml))

    def test_parse_fixtures(self):
        for filename, gold in self._gold_mapping.items():
            self._load_fixture_parse_and_check(filename, gold)
