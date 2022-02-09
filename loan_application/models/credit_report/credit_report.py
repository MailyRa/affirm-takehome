from dataclasses import dataclass, MISSING
from datetime import date
from typing import List, Union
from ..addresses import Address
from ..enums import CreditBureau, CreditReportPullStatus, Watchlist


@dataclass(frozen=True)
class CreditReportIdentityInfo:
    full_name: str
    date_of_birth: date
    address: Address
    ssn: str


@dataclass(frozen=True)
class CreditReport:
    pull_date: date
    bureau: CreditBureau
    identity_info: CreditReportIdentityInfo
    watchlist_hits: List[Watchlist]
    frozen_indicator: bool
    frozen_message_en: Union[str, MISSING.__class__] = MISSING
    extended_fraud_victim_indicator: bool
    extended_fraud_victim_message_en: Union[str, MISSING.__class__] = MISSING
    fico_score: int


@dataclass(frozen=True)
class CreditReportPull:
    status: CreditReportPullStatus
    credit_report: Union[CreditReport, MISSING.__class__] = MISSING
    raw_xml: str
