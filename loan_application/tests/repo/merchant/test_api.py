from dataclasses import MISSING
from datetime import date
from decimal import Decimal
import unittest

from loan_application.models.merchants.merchant import MerchantConfiguration
from loan_application.repo.merchant import api


class Testing(unittest.TestCase):
    def test_submit_merchant_config(self):
        
