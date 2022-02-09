# Python Specific Instructions 

## Setting up your Development Environment
**Install your virtual environment**. Please note this requires Python3.7+

```bash=
$ python3 -m venv .venv
$ . .venv/bin/activate
(.venv) $ pip3 install -r requirements.txt
(.venv) $ python setup.py develop -N
```


**Ensure your tests run**. You must be in the server directory for this.

```python
(.venv) $ nosetests --nologcapture loan_application/tests/
.........
---------------------------------------------------------------------
Ran 9 tests in 0.014s

OK
```


**Run the Server and access the Open API v3.0 Portal**
```python
(.venv) $ python loan_application/app/
```


Then, navigate to http://0.0.0.0:8001/ui/. You should now be able to make JSON requests to the API through the Open API v3.0 UI

You should be able to hit all 6 endpoints (receiving 200 or 400 responses) in the following order. Note that these API endpoints already have pre-populated data you can try out. Any information input will NOT be sent to Affirm, this data is purely for local testing purposes.

| Function      | Endpoint (POST) |
| ----------- | ----------- |
| Initialize Loan Application      | /api​/v1​/loanapplication​/ |
| Submit Identity   | /api/v1/loanapplication/{loan_application_id}/identity |
| Submit SSN (if needed)  | /api/v1/loanapplication/{loan_application_id}/ssn |
| Submit Income (if needed)  | /api/v1/loanapplication/{loan_application_id}/income |
| Submit Confirmation (if approved)  | /api/v1/loanapplication/{loan_application_id}/confirmation |
| Submit Exit (if denied)  | /api/v1/loanapplication/{loan_application_id}/exit |

**Code Navigation: this is the codebase structure**

| File | Function |
| ---- | -------- |
| app/\_\_main__.py | App entrypoint |
| app/openapi/openapi.yaml | Open API 3.0 file defining the API contract |
| app/implementation.py | Implementation of the API endpoints |
| deciders/identification.py | Business logic for identity verification |
| deciders/credit.py | Business logic for credit-worthiness verification |
| repo/ | Storage for loan application data |
| models/ | In-memory data models and enums |
| external_services/credit_bureaus/extrafax/api.py | A mock credit report service interface |
| external_services/credit_bureaus/extrafax/sandbox/fixtures | Mock credit report fixtures |
| tests/ | Unit tests for the Deciders |
| app/openapi/test_endpoints.py | E2E unit tests |

&nbsp;

## Creating Merchant Config
For the Set Merchant Configuration endpoint schema, we’ve provided the following API contract you can use:

```
/api/v1/merchantconfig/{merchant_id}:
 post:
   x-openapi-router-controller: 'loan_application.app.implementation'
   operationId: submit_merchant_config
   parameters:
     - description: Identifier for the merchant
       explode: false
       in: path
       name: merchant_id
       required: true
       schema:
         type: string
       style: simple
   requestBody:
     content:
       application/json:
         schema:
           $ref: '#/components/schemas/CreateMerchantConfigRequest'
   responses: 
     200:
       content:
         application/json:
           schema:
             $ref: '#/components/schemas/CreateMerchantConfigResponse'
       description: Request successfully processed
     400:
       content:
         application/json:
           schema:
             $ref: '#/components/schemas/BadInputResponse'
       description: Request invalid
   summary: Create and store the configurations for a Merchant
   tags:
     - Create Merchant Configuration

CreateMerchantConfigRequest:
 example:
   minimum_amount: 30000
   maximum_amount: 200000
   prequal_enabled: true
 properties:
   minimum_amount:
     type: integer
     description: "Minimum amount (in cents) that a consumer can get a loan for"
   maximum_amount:
     type: integer
     description: "Maximum amount (in cents) that a consumer can get a loan for"
   prequal_enabled:
     type: boolean
     description: "Flag to indicate if Prequal feature is enabled for this merchant"
 type: object
 required:
   - minimum_amount
   - maximum_amount
   - prequal_enabled

CreateMerchantConfigResponse:
 example:
   merchant_configuration_id: "3345919e-0e85-11ea-94a8-acde48001122"
 properties:
   merchant_configuration_id:
     type: string
     format: uuid
 type: object
 required:
   - merchant_configuration_id
```
