from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional
from ..credit_report import CreditReportPull
from ..enums import Currency, DeniedReason, PendingState
from ..terms import Plan


@dataclass(frozen=True)
class IdentityApproved:
    credit_report_pull: CreditReportPull


@dataclass(frozen=True)
class ApplicationPending:
    state: PendingState
    message: Optional[str] = None


@dataclass(frozen=True)
class ApplicationDenied:
    reason: DeniedReason


@dataclass(frozen=True)
class ApplicationApproved:
    amount: Decimal
    currency: Currency
    approved_plans: List[Plan]
