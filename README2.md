# Design decision implementing new endpoint #

I made the decision to modify the existing data model MerchantConfiguration located in ``loan_application/models/merchants/merchant.py.`` I added a boolean field called prequal_enabled. Since this prequal_enabled configuration is also at the merchant level like the maximum and minimum loan amount I felt it made sense to store this in the same data model.  

To update the merchant information I added a function called set_merchant_configuration located in ``loan_application/repo/merchant/api.py.`` The function takes the following parameters:  
```
merchant_id
minimum_loan_amount
maximum_loan_amount
prequal_enabled
```
I decided to add a new function to this file because this is where the merchant config repo is defined and there was already an existing api in this file to fetch information from the merchant config repo. 

set_merchant_configuration checks that the merchant exists in the data source and if it does it returns the MerchantConfiguration data model. If the merchant_id does not exist, None, is returned. Returning None in this case helped with the endpoint ``/api/v1/merchantconfig/{merchant_id}`` since we can return a 400 error in this case.

I also added some validation in ``app/implementation.py.`` In this function I checked that the user does not pass in a negative minimum loan amount and I also checked that the maximum loan amount is larger than the minimum loan amount. This is some basic data validation that is done before updating the in-memory data model. 

I added unittests in ``loan_application/app/tests/repo/merchant/test_api.py`` to test functions get_merchant_configuration and set_merchant_configuration. I also added E2E unit tests in ``loan_application/app/openapi/test_endpoints.py`` to test the new api endpoint.


# Future Improvements or Extensions #

Some future improvements or extensions that I am looking to add are:

1. Some sort of user authentication so not everyone can update the data model for any merchant id. 
2. Possibly have global variables for a minimum loan amount and maximum loan amount to restrict the values set by the merchant.
3. Changing the in-memory data source to a persistent data source such as MySQL. 

