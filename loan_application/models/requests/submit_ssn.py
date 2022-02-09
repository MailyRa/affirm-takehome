from dataclasses import dataclass


@dataclass(frozen=True)
class SubmitSSN:
    loan_application_id: str
    ssn: str
