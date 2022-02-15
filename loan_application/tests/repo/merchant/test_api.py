from dataclasses import MISSING
from datetime import date
from decimal import Decimal
import unittest

from loan_application.models.merchants.merchant import MerchantConfiguration
from loan_application.repo.merchant import api
from loan_application.repo.merchant.api import get_merchant_configuration, set_merchant_configuration

#test get_merchant_config
#test submit_merchant_config
#test set_merchant_config
class Testing(unittest.TestCase):

    def setUp(self):
        self.merchant_id = "4f572866-0e85-11ea-94a8-acde48001122"
        self.name = "Zelda's Stationary"

    def test_get_merchant_configuration_exists(self):
        actual = get_merchant_configuration(merchant_id=self.merchant_id)
        expected = MerchantConfiguration(
            merchant_id=self.merchant_id,
            name=self.name,
            minimum_loan_amount=Decimal('100.00'),
            maximum_loan_amount=Decimal('3000.00'), 
            prequal_enabled=True 
        )
        self.assertEqual(actual, expected)

    def test_get_merchant_configuration_does_not_exist(self):
        actual = get_merchant_configuration(merchant_id="DOES_NOT_EXIST")
        self.assertIsNone(actual)

    def test_set_merchant_config_merchant_exists(self):
        minimun_loan_amount = Decimal('200.00')
        maximum_loan_amount = Decimal('4000.00')
        prequal_enabled = False
        actual = set_merchant_configuration(
            merchant_id=self.merchant_id, 
            minimum_loan_amount=minimun_loan_amount, 
            maximum_loan_amount=maximum_loan_amount, 
            prequal_enabled=prequal_enabled
        )
        expected = MerchantConfiguration(
            merchant_id=self.merchant_id,
            name=self.name,
            minimum_loan_amount=minimun_loan_amount,
            maximum_loan_amount=maximum_loan_amount, 
            prequal_enabled=prequal_enabled 
        )
        self.assertEqual(actual, expected)

        # check that it was updated in the repo
        actual = get_merchant_configuration(self.merchant_id)
        self.assertEqual(actual, expected)

    def test_set_merchant_config_merchant_does_not_exist(self):
        actual = set_merchant_configuration(
            merchant_id="DOES NOT EXIST", 
            minimum_loan_amount="DOES NOT EXIST", 
            maximum_loan_amount="DOES NOT EXIST", 
            prequal_enabled="DOES NOT EXIST"
        )
        self.assertIsNone(actual)