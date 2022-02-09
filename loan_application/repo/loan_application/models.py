from dataclasses import dataclass
import datetime
import decimal
import enum
from typing import List, Union

from loan_application.models.addresses import Address
from loan_application.models.decisions import \
    ApplicationApproved,\
    ApplicationDenied,\
    ApplicationPending,\
    IdentityApproved
from loan_application.models.enums import Currency
from loan_application.models.income import Income


class LoanApplicationState(enum.Enum):
    pending_identity = 'pending_identity'
    pending_underwriting = 'pending_underwriting'
    denied = 'denied'
    approved = 'approved'
    confirmed = 'confirmed'


@dataclass(frozen=True)
class LoanApplicationUserInput:
    full_name: str
    date_of_birth: datetime.date
    address: Address
    ssn_last4: str
    ssn: str
    income: Income
    schedule_id: str


@dataclass(frozen=True)
class LoanApplication:
    loan_application_id: str
    state: LoanApplicationState
    merchant_id: str
    requested_amount: decimal.Decimal
    currency: Currency
    user_input: LoanApplicationUserInput
    user_input_events: List[LoanApplicationUserInput]
    final_decision: Union[ApplicationApproved, ApplicationDenied]
    decision_events: List[Union[ApplicationApproved, ApplicationDenied, ApplicationPending, IdentityApproved]]
    selected_terms_id: str
