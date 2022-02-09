from datetime import date
from dataclasses import MISSING
from typing import Union
from loan_application.models.credit_report import CreditReportPull
from loan_application.models.addresses import Address
from .parser import parse_credit_report
from .sandbox.fetcher import RemoteFetcherSandbox


fetcher_cls = RemoteFetcherSandbox


def pull_credit_report(
    full_name: str,
    date_of_birth: date,
    address: Address,
    ssn_last4: str,
    ssn: Union[str, MISSING.__class__] = MISSING
) -> CreditReportPull:
    """
    Pulls and denomalizes a credit report from remote. For testing purposes,
    monkey patch `fetcher_class = RemoteFetcherSandbox`, which will pull
    based off of a local file index of fixtures defined in `sandbox/fetcher.py`.

    Live pulls should use `fetcher_class = RemoteFetcherLive`.
    :param full_name:
    :param date_of_birth:
    :param address:
    :param ssn_last4:
    :param ssn:
    :return:
    """
    fetcher = fetcher_cls(
        full_name=full_name,
        date_of_birth=date_of_birth,
        address=address,
        ssn_last4=ssn_last4,
        ssn=ssn
    )
    raw_xml = fetcher.pull_remote()
    return parse_credit_report(raw_xml)


__all__ = (
    'pull_credit_report',
)
