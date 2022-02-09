from enum import Enum


class CreditBureau(Enum):
    extrafax = 'extrafax'


class CreditReportPullStatus(Enum):
    hit = 'hit'
    no_hit = 'no_hit'
