from enum import Enum


class PendingState(Enum):
    needs_ssn = 'needs_ssn'
    needs_income = 'needs_income'
    watchlist_hit = 'watchlist_hit'
    extended_fraud_victim = 'extended_fraud_victim'


class DeniedReason(Enum):
    geography = 'geography'
    too_young = 'too_young'
    identity_not_found = 'identity_not_found'
    credit_report_frozen = 'credit_report_frozen'
    identity_mismatch = 'identity_mismatch'
    insufficient_credit = 'insufficient_credit'
    amount_over_max = 'amount_over_max'
    amount_under_min = 'amount_under_min'
