from dataclasses import dataclass


@dataclass(frozen=True)
class SubmitConfirmation:
    loan_application_id: str
    schedule_id: str
