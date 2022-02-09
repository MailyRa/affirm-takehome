from dataclasses import MISSING
from datetime import date
from typing import Tuple
from xml.etree import ElementTree as ET
from loan_application.models.addresses import Address
from loan_application.models.credit_report import \
    CreditReportPull,\
    CreditReport, \
    CreditReportIdentityInfo
from loan_application.models.enums import \
    CreditBureau, \
    CreditReportPullStatus,\
    Watchlist


def parse_credit_report(
        raw_xml: str
) -> CreditReportPull:
    root = ET.fromstring(raw_xml)
    hit_status_raw = root.find('HitStatus').text
    if hit_status_raw.lower() == 'hit':
        hit_status = CreditReportPullStatus.hit
    elif hit_status_raw.lower() == 'no hit':
        hit_status = CreditReportPullStatus.no_hit
    else:
        raise Exception("Unhandled HitStatus: {}".format(hit_status_raw))

    if hit_status is CreditReportPullStatus.no_hit:
        return CreditReportPull(
            status=CreditReportPullStatus.no_hit,
            credit_report=MISSING,
            raw_xml=raw_xml
        )

    watchlist_hits = [
        Watchlist(elem.text.lower())
        for elem in root.findall('AML/WatchlistHits/WatchlistHit')
    ]

    frozen_indicator, freeze_message_en = _parse_indicator_flag_and_message(
        root, 'ReportFreeze', 'FrozenIndicator')

    evf_indicator, evf_message_en = _parse_indicator_flag_and_message(
        root, 'FraudAlerts', 'ExtendedFraudVictimAlert')

    pull_date = date.fromisoformat(root.find('PullDate').text)

    fico_score = int(root.find('FICO8').text)

    identity_info = _parse_identity_info(root)

    credit_report = CreditReport(
        watchlist_hits=watchlist_hits,
        frozen_indicator=frozen_indicator,
        frozen_message_en=freeze_message_en,
        extended_fraud_victim_indicator=evf_indicator,
        extended_fraud_victim_message_en=evf_message_en,
        fico_score=fico_score,
        identity_info=identity_info,
        pull_date=pull_date,
        bureau=CreditBureau.extrafax
    )
    return CreditReportPull(
        status=hit_status, credit_report=credit_report, raw_xml=raw_xml)


def _parse_indicator_flag_and_message(
        root: ET,
        path_prefix: str,
        indicator_tag: str
) -> Tuple[bool, str]:
    indicator_raw = root.find(path_prefix).find(indicator_tag).text
    if indicator_raw.lower() == 'y':
        indicator = True
    elif indicator_raw.lower() == 'n':
        indicator = False
    else:
        raise Exception(
            "Unhandled {}: {}".format(indicator_tag, indicator_raw))

    if indicator:
        message_en = root.find(
            path_prefix).find('AlertMessage').find('EN-US').text
    else:
        message_en = MISSING
    return indicator, message_en


def _parse_identity_info(root: ET) -> CreditReportIdentityInfo:
    id_elem = root.find('IdentityInfo')
    full_name = "{} {}".format(
        id_elem.find('FirstName').text, id_elem.find('LastName').text)
    date_of_birth = date.fromisoformat(id_elem.find('DateOfBirth').text)
    ssn = id_elem.find('SSN').text
    address_elem = id_elem.find('Address')
    address = Address(
        street1=address_elem.find('Street1').text,
        street2=address_elem.find('Street2').text,
        city=address_elem.find('City').text,
        region1_code=address_elem.find('Region1Code').text,
        postal_code=address_elem.find('PostalCode').text,
        country_code=address_elem.find('CountryCode').text
    )
    return CreditReportIdentityInfo(
        full_name=full_name,
        date_of_birth=date_of_birth,
        ssn=ssn,
        address=address
    )
