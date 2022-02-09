"""
Repository for manual overrides on identity checks. We add to this data store
when applications are put in a pending state, but upon manual review, the
identity of the customer is verified and manually marked as clear to proceed
with their applications. The store is indexed by (customer_ssn, override_type),
where override_type is an enum corresponding to one of the following:
1. the customer's credit report has an extended victim fraud alert
2. the customer's information matches one or more watchlists, such as OFAC
"""
from loan_application.models.enums import OverrideType


## ADD TO THIS SET TO MANUALLY OVERRIDE CHECKS FOR THE CUSTOMER
_REPO = {
    ("987-65-4321", OverrideType.watchlist)
}


def does_customer_have_override(ssn: str, override_type: OverrideType) -> bool:
    return (ssn, override_type) in _REPO
