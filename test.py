import unittest
from app import create_app, db
from flask import json


class CarTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def test_can_create_car_without_assigning(self):
        """ Test that API can create a new car via POST request to the endpoint"""
        data = dict(make="Tesla", model="Model 3", year=2018)

        res = self.client.post('/car/create', data=json.dumps(data), content_type='application/json')
        self.assertEqual(res.status_code, 200)

        json_response = res.get_json()
        self.assertEqual(json_response['response'], 'Successfully saved a car object.')

    def test_can_create_car_with_assigning(self):
        pass

    def test_cant_create_car_invalid_request(self):
        """ Test that API will return 400 (bad request) for invalid requests"""
        res = self.client.post('/car/create')
        self.assertEqual(res.status_code, 400)

        res = self.client.post('/car/create', data=None, content_type='application/json')
        self.assertEqual(res.status_code, 400)

    def test_cant_create_car_missing_params(self):
        """ Test that API will return expected errors when params are missing"""
        data = dict()
        res = self.client.post('/car/create', data=json.dumps(data), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        json_response = res.get_json()
        self.assertEqual(json_response['response'], 'Missing car make. Missing car model. Missing car year. ')

        data = dict(model="Model 3", year=2018)
        res = self.client.post('/car/create', data=json.dumps(data), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        json_response = res.get_json()
        self.assertEqual(json_response['response'], 'Missing car make. ')

        data = dict(make="Tesla", year=2018)
        res = self.client.post('/car/create', data=json.dumps(data), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        json_response = res.get_json()
        self.assertEqual(json_response['response'], 'Missing car model. ')

        data = dict(make="Tesla", model="Model 3")
        res = self.client.post('/car/create', data=json.dumps(data), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        json_response = res.get_json()
        self.assertEqual(json_response['response'], 'Missing car year. ')

        data = dict(make="Tesla", model="Model 3", year=2018, assigned_type=1)
        res = self.client.post('/car/create', data=json.dumps(data), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        json_response = res.get_json()
        self.assertEqual(json_response['response'], 'Both assigned type and assigned id must be provided.')

        data = dict(make="Tesla", model="Model 3", year=2018, assigned_id=1)
        res = self.client.post('/car/create', data=json.dumps(data), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        json_response = res.get_json()
        self.assertEqual(json_response['response'], 'Both assigned type and assigned id must be provided.')

    def test_can_get_car(self):
        """ Test that API can retrieve a car"""
        data = dict(make="BMW", model="530d", year=2018)
        self.client.post('/car/create', data=json.dumps(data), content_type='application/json')

        data = dict(car_id=1)
        res = self.client.get('/car/get', query_string=data, content_type='application/json')
        self.assertEqual(res.status_code, 200)
        json_response = res.get_json()
        self.assertEqual(json_response['make'], 'BMW')
        self.assertEqual(json_response['model'], '530d')
        self.assertEqual(json_response['year'], 2018)

    def test_cant_get_car_invalid_request(self):
        """ Test that endpoint can deal with missing query string"""
        res = self.client.get('/car/get')
        self.assertEqual(res.status_code, 200)
        json_response = res.get_json()
        self.assertEqual(json_response['response'], 'Missing car ID parameter')

    def test_cant_get_car_missing_params(self):
        """ Test that endpoint can deal with empty param"""
        data = dict()
        res = self.client.get('/car/get', query_string=data, content_type='application/json')
        self.assertEqual(res.status_code, 200)
        json_response = res.get_json()
        self.assertEqual(json_response['response'], 'Missing car ID parameter')

        data = dict(car_id=None)
        res = self.client.get('/car/get', query_string=data, content_type='application/json')
        self.assertEqual(res.status_code, 200)
        json_response = res.get_json()
        self.assertEqual(json_response['response'], 'Missing car ID parameter')

    def test_cant_get_car_id_doesnt_exist(self):
        """ Test can't get car ID that doesn't exist"""
        data = dict(car_id=100)
        res = self.client.get('/car/get', query_string=data, content_type='application/json')
        self.assertEqual(res.status_code, 200)
        json_response = res.get_json()
        self.assertEqual(json_response['response'], "Car doesn't exist")

    def test_cant_get_car_id_has_to_be_int(self):
        """ Test can't get a car with invalid car ID """
        data = dict(car_id="abcd")
        res = self.client.get('/car/get', query_string=data, content_type='application/json')
        self.assertEqual(res.status_code, 200)
        json_response = res.get_json()
        self.assertEqual(json_response['response'], "Invalid car ID parameter")

    def test_can_update_car(self):
        """ Test for updating car details"""
        data = dict(make="Tesla", model="Model 3", year=2015)
        self.client.post('/car/create', data=json.dumps(data), content_type='application/json')

        data = dict(car_id=1, model="Model X")
        res = self.client.post('/car/update', data=json.dumps(data), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = dict(car_id=1)
        res = self.client.get('/car/get', query_string=data, content_type='application/json')
        self.assertEqual(res.status_code, 200)
        json_response = res.get_json()
        self.assertEqual(json_response['model'], 'Model X')

        data = dict(car_id=1, model="545i", year=2015)
        res = self.client.post('/car/update', data=json.dumps(data), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = dict(car_id=1)
        res = self.client.get('/car/get', query_string=data, content_type='application/json')
        self.assertEqual(res.status_code, 200)
        json_response = res.get_json()
        self.assertEqual(json_response['model'], '545i')
        self.assertEqual(json_response['year'], 2015)

    def test_cant_update_car_invalid_id(self):
        """ Test that cant update car with ID taht doesn't exist"""
        data = dict(car_id=257, year=2015)
        res = self.client.post('/car/update', data=json.dumps(data), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        json_response = res.get_json()
        self.assertEqual(json_response['response'], "Couldn't update car: ID doesn't exist")

    def test_cant_update_car_invalid_parameters(self):
        """ Test can't update car with wrong or missing ID"""
        data = dict(year=2018, make="Ford")
        res = self.client.post('/car/update', data=json.dumps(data), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        json_response = res.get_json()
        self.assertEqual(json_response['response'], "Missing car ID parameter")

        data = dict(car_id="kawabanga!", model="C45 AMG")
        res = self.client.post('/car/update', data=json.dumps(data), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        json_response = res.get_json()
        self.assertEqual(json_response['response'], "Invalid car ID parameter")

    def test_can_delete_car(self):
        """ Test can delete car """
        data = dict(make="Tesla", model="Model 3", year=2015)
        self.client.post('/car/create', data=json.dumps(data), content_type='application/json')

        data = dict(car_id=1)
        res = self.client.delete('/car/delete', query_string=data, content_type='application/json')
        self.assertEqual(res.status_code, 200)
        json_response = res.get_json()
        self.assertEqual(json_response['response'], 'Car deleted')

        data = dict(car_id=1)
        res = self.client.get('/car/get', query_string=data, content_type='application/json')
        self.assertEqual(res.status_code, 200)
        json_response = res.get_json()
        self.assertEqual(json_response['response'], "Car doesn't exist")

    def test_cant_delete_car_invalid_id(self):
        """ Test we cant delete car with invalid ID """
        data = dict(car_id=102030)
        res = self.client.delete('/car/delete', query_string=data, content_type='application/json')
        self.assertEqual(res.status_code, 200)
        json_response = res.get_json()
        self.assertEqual(json_response['response'], "Car doesn't exist")

        data = dict(car_id="i_love_pizza")
        res = self.client.delete('/car/delete', query_string=data, content_type='application/json')
        self.assertEqual(res.status_code, 200)
        json_response = res.get_json()
        self.assertEqual(json_response['response'], 'Invalid car ID parameter')

    def test_cant_delete_car_invalid_request(self):
        """ Test we can't delete car with bad request"""
        data = dict()
        res = self.client.delete('/car/delete', data=data, content_type='application/json')
        self.assertEqual(res.status_code, 200)
        json_response = res.get_json()
        self.assertEqual(json_response['response'], 'Missing car ID parameter')

    def test_can_assign_car_to_driver(self):
        pass

    def test_can_assign_car_to_branch(self):
        pass

    def test_wont_assign_to_non_existing_driver(self):
        pass

    def test_wont_assign_to_non_existing_branch(self):
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
