from dataclasses import asdict, MISSING, replace
from datetime import date
from decimal import Decimal
import json
import uuid
from typing import Union

from flask import Response, url_for

from loan_application.deciders import identification, credit
from loan_application.models.decisions import \
    ApplicationApproved,\
    ApplicationDenied,\
    ApplicationPending,\
    IdentityApproved
from loan_application.models.enums import Currency
from loan_application.models.enums.decisions import PendingState
from loan_application.models.requests import \
    InitializeLoanApplication, \
    SubmitConfirmation, \
    SubmitIdentity, \
    SubmitIncome, \
    SubmitSSN
from loan_application.repo.loan_application import api as loan_application_repo
from loan_application.repo.loan_application.models import \
    LoanApplication, LoanApplicationUserInput
from loan_application.repo.merchant.api import get_merchant_configuration
from loan_application.repo.terms import api as terms_repo
from loan_application.terms.api import compute_schedule


def initialize_loan_application(
        body: dict
) -> Union[Response, dict]:
    data = InitializeLoanApplication(**body)
    requested_amount = Decimal(data.requested_amount_cents) / Decimal(100)
    currency = Currency(data.currency.lower())
    if currency is not Currency.usd:
        content_type = mimetype = 'application/json'
        return Response(
            status=400, content_type=content_type, mimetype=mimetype,
            response=json.dumps({
                "field": "currency",
                "message": "Only USD is supported presently."
            })
        )
    merchant_conf = get_merchant_configuration(data.merchant_id)
    if merchant_conf is None:
        content_type = mimetype = 'application/json'
        return Response(
            status=400, content_type=content_type, mimetype=mimetype,
            response=json.dumps({
                "field": "merchant_id",
                "message": "Could not find that merchant."
            })
        )
    loan_application = loan_application_repo.create(
        merchant_id=data.merchant_id,
        requested_amount=requested_amount,
        currency=currency
    )
    return {
        "loan_application_id": loan_application.loan_application_id,
        "next_step": "identity",
        "submit_url": url_for(
            '.loan_application_app_implementation_submit_identity',
            loan_application_id=loan_application.loan_application_id)
    }


def _map_pending_state_to_step_endpoint_copy(decision: ApplicationPending):
    state = decision.state
    if state is PendingState.needs_ssn:
        return (
            "ssn",
            ".loan_application_app_implementation_submit_ssn",
            "Please submit your full SSN to continue."
        )
    elif state is PendingState.needs_income:
        return (
            "income",
            ".loan_application_app_implementation_submit_income",
            "Please submit your income information to continue."
        )
    elif state is PendingState.extended_fraud_victim:
        return (
            "exit",
            ".loan_application_app_implementation_submit_exit",
            decision.extended_fraud_victim_message_en
        )
    elif state is PendingState.watchlist_hit:
        return (
            "exit",
            ".loan_application_app_implementation_submit_exit",
            "Please contact Affirm at (888) 555-1111 to "
        )
    else:
        raise Exception("Unknown PendingState: {}".format(state))


def _parse_application_pending(decision: ApplicationPending):
    return _map_pending_state_to_step_endpoint_copy(decision)


def _handle_pending_decision(
    loan_application: LoanApplication,
    decision: ApplicationPending
) -> dict:
    next_step, endpoint_name, msg = _parse_application_pending(decision)
    return {
        "loan_application_id": loan_application.loan_application_id,
        "next_step": next_step,
        "data": {
            "message": msg,
        },
        "submit_url": url_for(
            endpoint_name,
            loan_application_id=loan_application.loan_application_id
        )
    }


def _handle_identity_approved(
    loan_application: LoanApplication,
    identity_approval: IdentityApproved
) -> dict:
    credit_decision = credit.decide(
        loan_application.requested_amount,
        loan_application.currency,
        identity_approval.credit_report_pull,
        loan_application.user_input.address,
        income=loan_application.user_input.income
    )
    loan_application_repo.handle_decision(
        loan_application.loan_application_id,
        credit_decision)
    if isinstance(credit_decision, ApplicationApproved):
        today = date.today()
        schedules = [compute_schedule(
            p,
            credit_decision.amount,
            credit_decision.currency,
            today
        ) for p in credit_decision.approved_plans]
        schedules = terms_repo.save_schedules(schedules)
        return {
            "loan_application_id": loan_application.loan_application_id,
            "next_step": 'confirmation',
            "data": {
                "message": "You're approved!",
                "approved_terms": [s.to_display_json() for s in schedules],
            },
            "submit_url": url_for(
                '.loan_application_app_implementation_submit_confirmation',
                loan_application_id=loan_application.loan_application_id
            )
        }
    elif isinstance(credit_decision, ApplicationDenied):
        return {
            "loan_application_id": loan_application.loan_application_id,
            "next_step": "exit",
            "data": {
                "declination": {
                    "header": "We're sorry",
                    "message": (
                        "We couldn't approve your application because "
                        "we you didn't match our credit criteria.")
                },
            },
            "submit_url": url_for(
                '.loan_application_app_implementation_submit_exit',
                loan_application_id=loan_application.loan_application_id)
        }
    elif isinstance(credit_decision, ApplicationPending):
        return _handle_pending_decision(loan_application, credit_decision)
    else:
        raise Exception("Unhandled decision result class {}".format(
            credit_decision.__class__.__name__))


def _handle_user_input(loan_application_id, user_input):
    loan_application = loan_application_repo.handle_user_input(
        loan_application_id=loan_application_id,
        user_input=user_input
    )
    decision = identification.decide(
        loan_application.user_input.full_name,
        loan_application.user_input.date_of_birth,
        loan_application.user_input.address,
        loan_application.user_input.ssn_last4,
        ssn=loan_application.user_input.ssn
    )
    loan_application_repo.handle_decision(loan_application_id, decision)

    if isinstance(decision, IdentityApproved):
        return _handle_identity_approved(loan_application, decision)
    elif isinstance(decision, ApplicationDenied):
        return {
            "loan_application_id": loan_application.loan_application_id,
            "next_step": "exit",
            "data": {
                "declination": {
                    "header": "We're sorry",
                    "message": (
                        "We couldn't approve your application because "
                        "we couldn't verify your identity.")
                },
            },
            "submit_url": url_for(
                '.loan_application_app_implementation_submit_exit',
                loan_application_id=loan_application.loan_application_id)
        }
    elif isinstance(decision, ApplicationPending):
        next_step, endpoint_name, msg = _parse_application_pending(decision)
        return {
            "loan_application_id": loan_application.loan_application_id,
            "next_step": next_step,
            "data": {
                "message": msg,
            },
            "submit_url": url_for(
                endpoint_name,
                loan_application_id=loan_application.loan_application_id
            )
        }
    else:
        raise Exception("Unhandled decision result class {}".format(
            decision.__class__.__name__))


def submit_identity(
        loan_application_id: str,
        body: dict
) -> Union[Response, dict]:
    data = SubmitIdentity.from_json(loan_application_id, body)
    user_input = LoanApplicationUserInput(
            full_name=data.full_name,
            date_of_birth=date.fromisoformat(data.date_of_birth),
            address=data.address,
            ssn_last4=data.ssn_last4,
            ssn=MISSING,
            income=MISSING,
            schedule_id=MISSING
        )

    return _handle_user_input(loan_application_id, user_input)


def submit_ssn(
        loan_application_id: str,
        body: dict
) -> Union[Response, dict]:
    data = SubmitSSN(loan_application_id=loan_application_id, **body)
    user_input = LoanApplicationUserInput(
            full_name=MISSING,
            date_of_birth=MISSING,
            address=MISSING,
            ssn_last4=MISSING,
            ssn=data.ssn,
            income=MISSING,
            schedule_id=MISSING
        )
    return _handle_user_input(loan_application_id, user_input)


def submit_income(
        loan_application_id: str,
        body: dict
) -> Union[Response, dict]:
    data = SubmitIncome.from_json(loan_application_id, body)
    user_input = LoanApplicationUserInput(
            full_name=MISSING,
            date_of_birth=MISSING,
            address=MISSING,
            ssn_last4=MISSING,
            ssn=MISSING,
            income=data.income,
            schedule_id=MISSING
        )
    return _handle_user_input(loan_application_id, user_input)


def submit_confirmation(
        loan_application_id: str,
        body: dict
) -> Union[Response, dict]:
    data = SubmitConfirmation(loan_application_id=loan_application_id, **body)
    schedule = terms_repo.get_schedule(data.schedule_id)
    if schedule is MISSING:
        content_type = mimetype = 'application/json'
        return Response(
            status=400, content_type=content_type, mimetype=mimetype,
            response=json.dumps({
                "field": "schedule_id",
                "message": "Could not find that schedule."
            })
        )
    loan_application_repo.handle_user_input(
        loan_application_id,
        LoanApplicationUserInput(
            full_name=MISSING,
            date_of_birth=MISSING,
            address=MISSING,
            ssn_last4=MISSING,
            ssn=MISSING,
            income=MISSING,
            schedule_id=data.schedule_id
        )
    )
    return {
        "message": "Use this token to complete your purchase.",
        "merchant_payment_token": loan_application_id
    }


def submit_exit(
        loan_application_id: str
) -> Union[Response, dict]:
    return {"message": "Goodbye."}
