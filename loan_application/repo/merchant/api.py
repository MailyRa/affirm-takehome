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
            maximum_loan_amount=Decimal('3000.00'), 
            prequal_enabled=True 
        )
    }
)

def get_merchant_configuration(
        merchant_id: str) -> Optional[MerchantConfiguration]:
    return _REPO.repo.get(merchant_id)

def set_merchant_configuration(
    merchant_id: str, minimum_loan_amount: int, maximum_loan_amount: int, prequal_enabled: bool):
    merchant_data = _REPO.repo.get(merchant_id)
    if merchant_data:
        _REPO.repo[merchant_id] = MerchantConfiguration(
            merchant_id=merchant_id,
            name=merchant_data.name,
            minimum_loan_amount=Decimal(minimum_loan_amount),
            maximum_loan_amount=Decimal(maximum_loan_amount),
            prequal_enabled=prequal_enabled
        )
        return _REPO.repo[merchant_id]
    else:
        return None
