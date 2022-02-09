import json
import unittest

import connexion

flask_app = connexion.FlaskApp(__name__)
flask_app.add_api('openapi.yaml')


class EndpointTestCase(unittest.TestCase):
    def _create_loan_application(self):
        """
        Helper function to create a loan application successfully
        :return: response with loan_application_id and next step information
        """
        data = {
            "currency": "USD",
            "merchant_id": "4f572866-0e85-11ea-94a8-acde48001122",
            "requested_amount_cents": 100000
        }
        return flask_app.app.test_client().post('/api/v1/loanapplication/',
                                                content_type='application/json',
                                                data=json.dumps(data))

    def test_loan_application_success(self):
        response = self._create_loan_application()
        self.assertEquals(response.status_code, 200)

        response_dict = json.loads(response.data)
        self.assertNotEqual(response_dict.get('loan_application_id'), None)
        self.assertEquals(response_dict.get('next_step'), "identity")

    def test_loan_application_failure_invalid_request(self):
        data = {
          "currency": "cad",
          "merchant_id": "abcd",
          "requested_amount_cents": "abcd"
        }
        response = flask_app.app.test_client().post('/api/v1/loanapplication/',
                                                    content_type='application/json',
                                                    data=json.dumps(data))
        self.assertEquals(response.status_code, 400)

    def test_loan_application_failure_bad_currency(self):
        data = {
          "currency": "CAD",
          "merchant_id": "4f572866-0e85-11ea-94a8-acde48001122",
          "requested_amount_cents": 100000
        }
        response = flask_app.app.test_client().post('/api/v1/loanapplication/',
                                                    content_type='application/json',
                                                    data=json.dumps(data))
        self.assertEquals(response.status_code, 400)

        response_dict = json.loads(response.data)
        self.assertEquals(response_dict.get('message'), "Only USD is supported presently.")
        self.assertEquals(response_dict.get('field'), "currency")

    def test_loan_application_failure_bad_merchant_id(self):
        data = {
          "currency": "USD",
          "merchant_id": "ABCD",
          "requested_amount_cents": 100000
        }
        response = flask_app.app.test_client().post('/api/v1/loanapplication/',
                                                    content_type='application/json',
                                                    data=json.dumps(data))
        self.assertEquals(response.status_code, 400)

        response_dict = json.loads(response.data)
        self.assertEquals(response_dict.get('message'), "Could not find that merchant.")
        self.assertEquals(response_dict.get('field'), "merchant_id")

    def test_submit_exit_success(self):
        response = self._create_loan_application()
        loan_application_id = json.loads(response.data).get('loan_application_id')
        data = {
            "loan_application_id": loan_application_id
        }
        response = flask_app.app.test_client().post('/api/v1/loanapplication/{}/exit'.format(loan_application_id),
                                                    content_type='application/json',
                                                    data=json.dumps(data))
        self.assertEquals(response.status_code, 200)

        response_dict = json.loads(response.data)
        self.assertEquals(response_dict.get('message'), "Goodbye.")
