from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Address:
    street1: str
    street2: Optional[str]
    city: str
    region1_code: str
    postal_code: str
    country_code: str
