from enum import Enum


class SignalKey(Enum):
    address_country_code = 'address_country_code'
    address_postal_code = 'address_postal_code'
    address_region1_code = 'address_region1_code'
    address_street1 = 'address_street1'
    address_street2 = 'address_street2'
    user_age = 'user_age'
    user_email = 'user_email'
    user_first_name = 'user_first_name'
    user_last_name = 'user_last_name'
    merchant_minimum_loan_amount = 'merchant_minimum_loan_amount'
    merchant_maximum_loan_amount = 'merchant_maximum_loan_amount'
    ask_income_above_threshold = 'ask_income_above_threshold'
    ask_income_disabled = 'ask_income_disabled'
    ask_ssn_disabled = 'ask_income_disabled'
    minimum_age = 'minimum_age'
    requested_loan_amount = 'requested_loan_amount'
