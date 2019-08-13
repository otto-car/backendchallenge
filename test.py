import unittest
from app import create_app, db
from flask import json


class CarTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def test_can_create_car(self):
        """ Test that API can create a new car via POST request to the endpoint"""
        data = dict(make="Tesla", model="Model 3", year=2018)

        res = self.client.post('/car/create', data=json.dumps(data), content_type='application/json')
        self.assertEqual(res.status_code, 200)

        json_response = res.get_json()
        self.assertEqual(json_response['response'], 'Successfully saved a car object.')

    def test_cant_create_car_invalid_request(self):
        """ Test that API will return 400 (bad request) for invalid requests"""
        res = self.client.post('/car/create')
        self.assertEqual(res.status_code, 400)

        res = self.client.post('/car/create', data=None, content_type='application/json')
        self.assertEqual(res.status_code, 400)

    def test_cant_create_car_missing_params(self):
        pass

    def test_can_get_car(self):
        pass

    def test_can_update_car(self):
        pass

    def test_can_delete_car(self):
        pass

    def test_can_assign_car_to_driver(self):
        pass

    def test_can_assign_car_to_branch(self):
        pass

    def tearDown(self):
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()


class BranchTestCase(unittest.TestCase):
    pass


class DriverTestCase(unittest.TestCase):
    pass


if __name__ == "__main__":
    unittest.main()
