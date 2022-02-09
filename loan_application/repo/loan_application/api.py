"""
CRUD layer for customer-inputted data for the loan application. Backed by an
in-memory store, so storage of applications doesn't persist if the server
restarts. A production service would use durable storage (such as MySQL or
Postgres) as the backend.
"""
from dataclasses import asdict, MISSING, replace
from decimal import Decimal
from typing import Dict, Union
import uuid

from loan_application.models.enums import Currency

from .models import ApplicationApproved,\
    ApplicationDenied,\
    ApplicationPending,\
    IdentityApproved,\
    LoanApplication,\
    LoanApplicationState,\
    LoanApplicationUserInput


_REPO = {}  # Dict[str, LoanApplication]

def create(
    merchant_id: str,
    requested_amount: Decimal,
    currency: Currency
) -> LoanApplication:
    loan_application_id = str(uuid.uuid1())
    loan_application = LoanApplication(
        loan_application_id=loan_application_id,
        state=LoanApplicationState.pending_identity,
        merchant_id=merchant_id,
        requested_amount=requested_amount,
        currency=currency,
        user_input=MISSING,
        user_input_events=[],
        final_decision=MISSING,
        decision_events=[],
        selected_terms_id=MISSING
    )
    _REPO[loan_application_id] = loan_application
    return loan_application


def handle_user_input(
    loan_application_id: str,
    user_input: LoanApplicationUserInput
) -> LoanApplication:
    loan_application = _REPO[loan_application_id]
    if loan_application.user_input is MISSING:
        loan_application.user_input_events.append(user_input)
        new_loan_application = replace(loan_application, user_input=user_input)
        _REPO[loan_application_id] = new_loan_application
        return new_loan_application

    new_inputs = {
        k: getattr(user_input, k)
        for k, _ in asdict(user_input).items()
        if getattr(user_input, k) is not MISSING
    }
    for key, val in new_inputs.items():
        stored_val = getattr(loan_application.user_input, key)
        if stored_val is not MISSING and stored_val != val:
            raise Exception(
                "Cannot override key {} on loan application {}".format(
                    key, loan_application_id
                ))

    loan_application.user_input_events.append(user_input)
    new_user_input = replace(loan_application.user_input, **new_inputs)
    new_loan_application = replace(loan_application, user_input=new_user_input)
    _REPO[loan_application_id] = new_loan_application
    return new_loan_application


def handle_decision(
    loan_application_id: str,
    decision: Union[ApplicationApproved, ApplicationDenied, ApplicationPending, IdentityApproved]
) -> LoanApplication:
    loan_application = _REPO[loan_application_id]
    loan_application.decision_events.append(decision)
    new_loan_application = replace(loan_application, final_decision=decision)
    _REPO[loan_application_id] = new_loan_application
    return new_loan_application
