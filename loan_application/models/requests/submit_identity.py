from dataclasses import dataclass
from datetime import date
from ..addresses import Address


@dataclass(frozen=True)
class SubmitIdentity:
    loan_application_id: str
    full_name: str
    date_of_birth: date
    ssn_last4: str
    address: Address
    email: str

    @classmethod
    def from_json(cls, loan_application_id, body):
        address = Address(**body.pop('address'))
        return cls(
            loan_application_id=loan_application_id,
            address=address, **body)
