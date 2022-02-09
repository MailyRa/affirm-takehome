from dataclasses import MISSING, replace
from datetime import date
from typing import Union

from loan_application.models.credit_report import CreditReportPull
from loan_application.models.decisions import \
    ApplicationDenied,\
    ApplicationPending,\
    IdentityApproved
from loan_application.models.enums import CreditReportPullStatus, OverrideType
from loan_application.models.enums.decisions import \
    DeniedReason,\
    PendingState
from loan_application.models.requests import Address
from loan_application.external_services.credit_bureaus.extrafax import \
    api as credit_report_api
from loan_application.repo.manual_overrides.api import \
    does_customer_have_override


def _compute_age(
        date_of_birth: date,
        as_of_date: date
) -> int:
    assert as_of_date >= date_of_birth, "DOBs in the future disallowed"
    if date_of_birth.month < as_of_date.month or (
            date_of_birth.month == as_of_date.month and
            date_of_birth.day <= as_of_date.day
        ):
        return as_of_date.year - date_of_birth.year
    else:
        return as_of_date.year - date_of_birth.year - 1


def policy(
        as_of_date: date,
        full_name: str,
        date_of_birth: date,
        address: Address,
        ssn_last4: str,
        ssn: Union[str, MISSING.__class__] = MISSING,
        credit_report_pull: Union[CreditReportPull, MISSING.__class__] = MISSING,
        watchlist_check_cleared: bool = False,
        extended_victim_check_cleared: bool = False
) -> Union[ApplicationDenied, ApplicationPending, IdentityApproved]:
    """
    Pure logic checks to vet the user's identity. This policy includes a mix
    of compliance enforcement and internal risk mitigation checks. Ensures that
    the customer corresponds to a real person with a credit report, that the
    customer is not a known victim of identity theft, and that the customer is
    not subject to political sanctions (e.g. through OFAC). Details of each
    policy rule are inline as comments in the function. The customer can either
    be approved (identity is established), declined (identity cannot be
    established), or pending (more information must be provided in order to
    come to a final decision).
    :param as_of_date:
    :param full_name:
    :param date_of_birth:
    :param address:
    :param ssn_last4:
    :param ssn:
    :param credit_report_pull:
    :param watchlist_check_cleared:
    :param extended_victim_check_cleared:
    :return:
    """
    ## USER INPUT CHECKS
    #
    # loans are only available in the US (for now)
    if address.country_code != 'US':
        return ApplicationDenied(reason=DeniedReason.geography)

    # check if customer meets minimum age requirements
    user_age = _compute_age(date_of_birth, as_of_date)
    if address.region1_code == 'AL':
        # Alabama law dictates that people younge than 18 are ineligible for
        # credit products.
        minimum_age = 19
    else:
        minimum_age = 18
    if user_age < minimum_age:
        return ApplicationDenied(reason=DeniedReason.too_young)
    #
    ## END USER INPUT CHECKS

    ## CREDIT REPORT CHECKS
    #
    # ensure we have a credit report
    missing_cr = (
        credit_report_pull is MISSING
        or credit_report_pull.status is CreditReportPullStatus.no_hit
    )
    if missing_cr and ssn is MISSING:
        # if no report, ask for full SSN if it hasn't
        # been provided yet
        return ApplicationPending(state=PendingState.needs_ssn)
    elif missing_cr:
        # if full SSN has been provided, cannot proceed
        return ApplicationDenied(reason=DeniedReason.identity_not_found)
    credit_report = credit_report_pull.credit_report

    # ensure the customer hasn't placed a short-term freeze on their report
    if credit_report.frozen_indicator:
        return ApplicationDenied(
            reason=DeniedReason.credit_report_frozen,
            message=credit_report.frozen_message_en
        )

    # ensure that the name on the credit report matches the customer-provided
    # name. currently applies a strict match; conversion could be improved by
    # better accounting for typos.
    if full_name.lower() != credit_report.identity_info.full_name.lower():
        return ApplicationDenied(reason=DeniedReason.identity_mismatch)

    # ensure that the customer inputted SSN matches the credit report SSN.
    # if the customer wasn't prompted for a full SSN, matching on the SSN
    # last 4 is sufficient for this cohesion check.
    if ssn is not MISSING and ssn != credit_report.identity_info.ssn:
        return ApplicationDenied(reason=DeniedReason.identity_mismatch)
    elif ssn is MISSING and ssn_last4 != credit_report.identity_info.ssn[-4:]:
        return ApplicationDenied(reason=DeniedReason.identity_mismatch)

    # ensure that the customer's date of birth matches the credit report DOB.
    if date_of_birth != credit_report.identity_info.date_of_birth:
        return ApplicationDenied(reason=DeniedReason.identity_mismatch)

    # ensure that identity on the credit report does not match a sanctions list
    # such as OFAC (USA) or OSFI (Canada).
    # the user can be marked as clear manually if internal investigation shows
    # that the hit was spurious, so we set the application in a pending state
    # and prompt them to call in to verify their identity.
    if len(credit_report.watchlist_hits) > 0 and \
            not watchlist_check_cleared:
        return ApplicationPending(state=PendingState.watchlist_hit)

    # ensure that the customer doesn't have a long-term identity theft victim
    # alert on their report. if they do, the customer needs to call in to
    # verify that it's really them, and we can mark them as clear if so.
    if credit_report.extended_fraud_victim_indicator and not extended_victim_check_cleared:
        return ApplicationPending(
            state=PendingState.extended_fraud_victim,
            message=credit_report.extended_fraud_victim_message_en
        )
    #
    ## END CREDIT REPORT CHECKS

    # customer passed identity checks!
    return IdentityApproved(
        credit_report_pull=replace(credit_report_pull, raw_xml=''))


def decide(
        full_name: str,
        date_of_birth: date,
        address: Address,
        ssn_last4: str,
        ssn: Union[str, MISSING.__class__] = MISSING
) -> Union[ApplicationDenied, ApplicationPending, IdentityApproved]:
    """
    Orchestrates fetching necessary data to determine if the customer's
    identity meets criteria for a loan and running the logic checks in policy.
    Necessary data that needs to be fetched:
    1. the current date (used for determining the customer's age)
    2. credit report
    3. any manual overrides for identity checks configured for the customer
    :param full_name:
    :param date_of_birth:
    :param address:
    :param ssn_last4:
    :param ssn:
    :return:
    """
    ## COLLECT SIDE-EFFECTS
    #
    current_date = date.today()
    credit_report_pull = credit_report_api.pull_credit_report(
        full_name=full_name,
        date_of_birth=date_of_birth,
        address=address,
        ssn_last4=ssn_last4,
        ssn=ssn
    )
    if credit_report_pull.credit_report is MISSING:
        credit_report_ssn = MISSING
    else:
        credit_report_ssn = credit_report_pull.credit_report.identity_info.ssn
    if credit_report_ssn is not MISSING:
        watchlist_check_cleared = does_customer_have_override(
            credit_report_ssn, OverrideType.watchlist
        )
        extended_victim_check_cleared = does_customer_have_override(
            credit_report_ssn, OverrideType.extended_fraud_victim
        )
    else:
        # No credit report, so the customer can't be approved anyway.
        watchlist_check_cleared = False
        extended_victim_check_cleared = False

    ## RUN POLICY LOGIC
    #
    return policy(
        as_of_date=current_date,
        full_name=full_name,
        date_of_birth=date_of_birth,
        address=address,
        ssn_last4=ssn_last4,
        ssn=ssn,
        credit_report_pull=credit_report_pull,
        watchlist_check_cleared=watchlist_check_cleared,
        extended_victim_check_cleared=extended_victim_check_cleared
    )
