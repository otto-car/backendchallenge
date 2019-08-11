import unittest
import os
import json
from app import create_app, db


class CarTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config_name='testing')
        self.client = self.app.test_client

        with self.app.app_context():
            db.create_all()

    def test_can_create_car(self):
        """ Test that API can create a new car via POST request to the endpoint"""
        car_data = {"make": "Tesla", "model": "Model 3", "year": 2018, "assigned_to_type": "", "assigned_id": ""}
        res = self.client().post('/cars/create', data=car_data)
        self.assertEqual(res.status_code, 201)

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
            db.session.remove()
            db.drop_all()


class BranchTestCase(unittest.TestCase):
    pass


class DriverTestCase(unittest.TestCase):
    pass


if __name__ == "__main__":
    unittest.main()