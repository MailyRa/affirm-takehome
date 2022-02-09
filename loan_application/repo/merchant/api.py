from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Optional
from loan_application.models.merchants.merchant import MerchantConfiguration


@dataclass(frozen=True)
class _MerchantConfigurationsRepo:
    repo: Dict[str, MerchantConfiguration]


_REPO = _MerchantConfigurationsRepo(
    repo={
        '4f572866-0e85-11ea-94a8-acde48001122': MerchantConfiguration(
            merchant_id='4f572866-0e85-11ea-94a8-acde48001122',
            name="Zelda's Stationary",
            minimum_loan_amount=Decimal('100.00'),
            maximum_loan_amount=Decimal('3000.00')
        )
    }
)


def get_merchant_configuration(
        merchant_id: str) -> Optional[MerchantConfiguration]:
    return _REPO.repo.get(merchant_id)
