from dataclasses import MISSING, replace
from typing import Dict, List, Union
import uuid

from loan_application.models.terms import Schedule


_REPO = {}  # Dict[str, Schedule]


def save_schedules(
    schedules: List[Schedule]
) -> List[Schedule]:
    keyed_schedules = [
        replace(s, schedule_id=str(uuid.uuid1())) for s in schedules
    ]
    _REPO.update({s.schedule_id: s for s in keyed_schedules})
    return keyed_schedules


def get_schedule(schedule_id: str) -> Union[Schedule, MISSING.__class__]:
    return _REPO.get(schedule_id, MISSING)
