import unittest
from app import create_app, db
from flask import json


def api_call(self, method, url, data, status_code, return_jason=False):
    if method == "POST":
        res = self.client.post(url, data=json.dumps(data), content_type='application/json')
    elif method == "GET":
        res = self.client.get(url, query_string=data, content_type='application/json')
    elif method == "DELETE":
        res = self.client.delete(url, query_string=data, content_type='application/json')
    elif method == "PUT":
        res = self.client.put(url, data=json.dumps(data), content_type='application/json')
    else:
        return False

    self.assertEqual(res.status_code, status_code)

    if return_jason:
        return res.get_json()


class CarTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client()

        # set up test db
        with self.app.app_context():
            db.create_all()

    def test_can_create_car_without_assigning(self):
        """ Test that API can create a new car via POST request to the endpoint"""
        data = dict(make="Tesla", model="Model 3", year=2018)
        json_response = api_call(self, "POST", "/car/create", data, 200, True)
        self.assertEqual(json_response['status'], 201)
        self.assertEqual(json_response['message'], 'Car created')

    def test_can_create_car_with_assigning(self):
        pass

    def test_cant_create_car_invalid_request(self):
        """ Test that API will return 400 (bad request) for invalid requests"""
        res = self.client.post('/car/create')
        self.assertEqual(res.status_code, 400)

        res = self.client.post('/car/create', data=None, content_type='application/json')
        self.assertEqual(res.status_code, 400)

        data = dict(make="Tesla", model="Model 3", year="Stringy McStringface")
        json_response = api_call(self, "POST", "/car/create", data, 200, True)
        self.assertEqual(json_response['status'], 400)
        self.assertEqual(json_response['message'], 'Invalid year')

    def test_cant_create_car_missing_params(self):
        """ Test that API will return expected errors when params are missing"""
        json_response = api_call(self, "POST", "/car/create", dict(), 200, True)
        self.assertEqual(json_response['status'], 400)
        self.assertEqual(json_response['message'], 'Missing make')

        data = dict(model="Model 3", year=2018)
        json_response = api_call(self, "POST", "/car/create", data, 200, True)
        self.assertEqual(json_response['status'], 400)
        self.assertEqual(json_response['message'], 'Missing make')

        data = dict(make="Tesla", year=2018)
        json_response = api_call(self, "POST", "/car/create", data, 200, True)
        self.assertEqual(json_response['status'], 400)
        self.assertEqual(json_response['message'], 'Missing model')

        data = dict(make="Tesla", model="Model 3")
        json_response = api_call(self, "POST", "/car/create", data, 200, True)
        self.assertEqual(json_response['status'], 400)
        self.assertEqual(json_response['message'], 'Missing year')

        data = dict(make="Tesla", model="Model 3", year=2018, assigned_type=1)
        json_response = api_call(self, "POST", "/car/create", data, 200, True)
        self.assertEqual(json_response['status'], 400)
        self.assertEqual(json_response['message'], 'Both assigned type and id must be present')

        data = dict(make="Tesla", model="Model 3", year=2018, assigned_id=1)
        json_response = api_call(self, "POST", "/car/create", data, 200, True)
        self.assertEqual(json_response['status'], 400)
        self.assertEqual(json_response['message'], 'Both assigned type and id must be present')

    def test_can_get_car(self):
        """ Test that API can retrieve a car"""
        data = dict(make="BMW", model="530d", year=2018)
        self.client.post('/car/create', data=json.dumps(data), content_type='application/json')

        data = dict(car_id=1)
        json_response = api_call(self, "GET", '/car/get', data, 200, True)
        self.assertEqual(json_response['make'], 'BMW')
        self.assertEqual(json_response['model'], '530d')
        self.assertEqual(json_response['year'], 2018)

    def test_cant_get_car_invalid_request(self):
        """ Test that endpoint can deal with missing query string"""
        res = self.client.get('/car/get')
        self.assertEqual(res.status_code, 200)
        json_response = res.get_json()
        self.assertEqual(json_response['status'], 400)
        self.assertEqual(json_response['message'], 'Missing car ID')

    def test_cant_get_car_missing_params(self):
        """ Test that endpoint can deal with empty param"""
        data = dict()
        json_response = api_call(self, "GET", '/car/get', data, 200, True)
        self.assertEqual(json_response['status'], 400)
        self.assertEqual(json_response['message'], 'Missing car ID')

        data = dict(car_id=None)
        json_response = api_call(self, "GET", '/car/get', data, 200, True)
        self.assertEqual(json_response['status'], 400)
        self.assertEqual(json_response['message'], 'Missing car ID')

    def test_cant_get_car_id_doesnt_exist(self):
        """ Test can't get car ID that doesn't exist"""
        data = dict(car_id=100)
        json_response = api_call(self, "GET", '/car/get', data, 200, True)
        self.assertEqual(json_response['status'], 404)
        self.assertEqual(json_response['message'], "Car not found")

    def test_cant_get_car_id_has_to_be_int(self):
        """ Test can't get a car with invalid car ID """
        data = dict(car_id="abcd")
        json_response = api_call(self, "GET", '/car/get', data, 200, True)
        self.assertEqual(json_response['status'], 400)
        self.assertEqual(json_response['message'], "Invalid car ID")

    def test_can_update_car(self):
        """ Test for updating car details"""
        data = dict(make="Tesla", model="Model 3", year=2015)
        api_call(self, "POST", '/car/create', data, 200)

        data = dict(car_id=1, model="Model X")
        json_response = api_call(self, "PUT", '/car/update', data, 200, True)
        self.assertEqual(json_response['status'], 200)
        self.assertEqual(json_response['message'], "Car record was updated")

        data = dict(car_id=1)
        res = self.client.get('/car/get', query_string=data, content_type='application/json')
        self.assertEqual(res.status_code, 200)
        json_response = res.get_json()
        self.assertEqual(json_response['model'], 'Model X')

        data = dict(car_id=1, model="545i", year=2015)
        json_response = api_call(self, "PUT", '/car/update', data, 200, True)
        self.assertEqual(json_response['status'], 200)
        self.assertEqual(json_response['message'], "Car record was updated")

        data = dict(car_id=1)
        json_response = api_call(self, "GET", '/car/get', data, 200, True)
        self.assertEqual(json_response['model'], '545i')
        self.assertEqual(json_response['year'], 2015)

    def test_cant_update_car_invalid_id(self):
        """ Test that cant update car with ID taht doesn't exist"""
        data = dict(car_id=257, year=2015)
        json_response = api_call(self, "PUT", '/car/update', data, 200, True)
        self.assertEqual(json_response['status'], 404)
        self.assertEqual(json_response['message'], "Car not found")

    def test_cant_update_car_invalid_parameters(self):
        """ Test can't update car with wrong or missing ID"""
        data = dict(year=2018, make="Ford")
        json_response = api_call(self, "PUT", '/car/update', data, 200, True)
        self.assertEqual(json_response['status'], 400)
        self.assertEqual(json_response['message'], "Missing car ID")

        data = dict(car_id="cowabunga!", model="C45 AMG")
        json_response = api_call(self, "PUT", '/car/update', data, 200, True)
        self.assertEqual(json_response['status'], 400)
        self.assertEqual(json_response['message'], "Invalid car ID")

    def test_can_delete_car(self):
        """ Test can delete car """
        data = dict(make="Tesla", model="Model 3", year=2015)
        api_call(self, "POST", '/car/create', data, 200)

        data = dict(car_id=1)
        json_response = api_call(self, "DELETE", '/car/delete', data, 200, True)
        self.assertEqual(json_response['status'], 200)
        self.assertEqual(json_response['message'], "Car deleted")

        data = dict(car_id=1)
        json_response = api_call(self, "GET", '/car/get', data, 200, True)
        self.assertEqual(json_response['status'], 404)
        self.assertEqual(json_response['message'], "Car not found")

    def test_cant_delete_car_invalid_id(self):
        """ Test we cant delete car with invalid ID """
        data = dict(car_id=102030)
        json_response = api_call(self, "DELETE", '/car/delete', data, 200, True)
        self.assertEqual(json_response['status'], 404)
        self.assertEqual(json_response['message'], "Car not found")

        data = dict(car_id="i_love_pizza")
        json_response = api_call(self, "DELETE", '/car/delete', data, 200, True)
        self.assertEqual(json_response['status'], 400)
        self.assertEqual(json_response['message'], "Invalid car ID")

    def test_cant_delete_car_invalid_request(self):
        """ Test we can't delete car with bad request"""
        data = dict()
        json_response = api_call(self, "DELETE", '/car/delete', data, 200, True)
        self.assertEqual(json_response['status'], 400)
        self.assertEqual(json_response['message'], 'Missing car ID')

    def test_can_assign_car_to_driver(self):
        pass

    def test_can_assign_car_to_branch(self):
        pass

    def test_wont_assign_to_branch_over_capacity(self):
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
    def setUp(self):
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client()

        # set up test db
        with self.app.app_context():
            db.create_all()

    def test_can_create_branch(self):
        """ Test can create normal branch"""
        data = dict(city="London", postcode="E1W 3SS", capacity=5)
        json_response = api_call(self, "POST", "/branch/create", data, 200, True)
        self.assertEqual(json_response["status"], 201)
        self.assertEqual(json_response["message"], 'Branch created')

    def test_cant_create_branch_invalid_request(self):
        """ Test cant create branch with invalid requests"""
        res = self.client.post('/branch/create')
        self.assertEqual(res.status_code, 400)

        res = self.client.post('/branch/create', data=None, content_type='application/json')
        self.assertEqual(res.status_code, 400)

        res = self.client.get('/branch/create')
        self.assertEqual(res.status_code, 405)

    def test_cant_create_branch_missing_or_invalid_params(self):
        """ Test cant create branch with wrong or missing params"""
        data = dict()
        json_response = api_call(self, "POST", "/branch/create", data, 200, True)
        self.assertEqual(json_response["status"], 400)
        self.assertEqual(json_response["message"], "Missing city")

        data = dict(postcode="E1W 3SS", capacity=5)
        json_response = api_call(self, "POST", "/branch/create", data, 200, True)
        self.assertEqual(json_response["status"], 400)
        self.assertEqual(json_response["message"], "Missing city")

        data = dict(city="London", capacity=5)
        json_response = api_call(self, "POST", "/branch/create", data, 200, True)
        self.assertEqual(json_response["status"], 400)
        self.assertEqual(json_response["message"], "Missing postcode")

        data = dict(city="London", postcode="123456789123", capacity=5)
        json_response = api_call(self, "POST", "/branch/create", data, 200, True)
        self.assertEqual(json_response["status"], 400)
        self.assertEqual(json_response["message"], "Invalid postcode")

        data = dict(city="London", postcode="SE157 258GU2", capacity=5)
        json_response = api_call(self, "POST", "/branch/create", data, 200, True)
        self.assertEqual(json_response["status"], 400)
        self.assertEqual(json_response["message"], "Invalid postcode")

        data = dict(city="London", postcode="SE2", capacity=5)
        json_response = api_call(self, "POST", "/branch/create", data, 200, True)
        self.assertEqual(json_response["status"], 400)
        self.assertEqual(json_response["message"], "Invalid postcode")

        data = dict(city="London", postcode="SE2X2", capacity=5)
        json_response = api_call(self, "POST", "/branch/create", data, 200, True)
        self.assertEqual(json_response["status"], 400)
        self.assertEqual(json_response["message"], "Invalid postcode")

        data = dict(city="London", postcode="E1W 3SS")
        json_response = api_call(self, "POST", "/branch/create", data, 200, True)
        self.assertEqual(json_response["status"], 400)
        self.assertEqual(json_response["message"], "Missing capacity")

        data = dict(city="London", postcode="E1W 3SS", capacity="super")
        json_response = api_call(self, "POST", "/branch/create", data, 200, True)
        self.assertEqual(json_response["status"], 400)
        self.assertEqual(json_response["message"], "Invalid capacity")

    def test_can_get_branch(self):
        """ Test that API can retrieve a branch"""
        data = dict(city="London", postcode="E1W 3SS", capacity=5)
        api_call(self, "POST", '/branch/create', data, 200)

        data = dict(branch_id=1)
        json_response = api_call(self, "GET", '/branch/get', data, 200, True)
        self.assertEqual(json_response['city'], 'London')
        self.assertEqual(json_response['postcode'], 'E1W 3SS')
        self.assertEqual(json_response['capacity'], 5)

    def test_cant_get_branch_invalid_request(self):
        """ Test that endpoint can deal with missing query string"""
        res = self.client.get('/branch/get')
        self.assertEqual(res.status_code, 200)
        json_response = res.get_json()
        self.assertEqual(json_response['status'], 400)
        self.assertEqual(json_response['message'], 'Missing branch ID')

    def test_cant_get_branch_missing_params(self):
        """ Test that endpoint can deal with empty param"""
        data = dict()
        json_response = api_call(self, "GET", '/branch/get', data, 200, True)
        self.assertEqual(json_response['status'], 400)
        self.assertEqual(json_response['message'], 'Missing branch ID')

        data = dict(branch_id=None)
        json_response = api_call(self, "GET", '/branch/get', data, 200, True)
        self.assertEqual(json_response['status'], 400)
        self.assertEqual(json_response['message'], 'Missing branch ID')

    def test_cant_get_branch_id_doesnt_exist(self):
        """ Test can't get branch ID that doesn't exist"""
        data = dict(branch_id=100)
        json_response = api_call(self, "GET", '/branch/get', data, 200, True)
        self.assertEqual(json_response['status'], 404)
        self.assertEqual(json_response['message'], "Branch not found")

    def test_cant_get_branch_id_has_to_be_int(self):
        """ Test can't get a branch with invalid ID """
        data = dict(branch_id="abcd")
        json_response = api_call(self, "GET", '/branch/get', data, 200, True)
        self.assertEqual(json_response['status'], 400)
        self.assertEqual(json_response['message'], "Invalid branch ID")

    def test_can_update_branch(self):
        """ Test for updating branch details"""
        data = dict(city="London", postcode="E1W 3SS", capacity=5)
        api_call(self, "POST", '/branch/create', data, 200)

        data = dict(branch_id=1)
        json_response = api_call(self, "GET", '/branch/get', data, 200, True)
        self.assertEqual(json_response['city'], 'London')
        self.assertEqual(json_response['postcode'], 'E1W 3SS')
        self.assertEqual(json_response['capacity'], 5)

        data = dict(branch_id=1, city="Guildford", postcode="GU2 8DJ", capacity=100)
        api_call(self, "PUT", '/branch/update', data, 200)

        data = dict(branch_id=1)
        json_response = api_call(self, "GET", '/branch/get', data, 200, True)
        self.assertEqual(json_response['city'], 'Guildford')
        self.assertEqual(json_response['postcode'], 'GU2 8DJ')
        self.assertEqual(json_response['capacity'], 100)

        data = dict(branch_id=1, capacity=90)
        api_call(self, "PUT", '/branch/update', data, 200)

        data = dict(branch_id=1)
        json_response = api_call(self, "GET", '/branch/get', data, 200, True)
        self.assertEqual(json_response['city'], 'Guildford')
        self.assertEqual(json_response['postcode'], 'GU2 8DJ')
        self.assertEqual(json_response['capacity'], 90)

    def test_cant_update_branch_invalid_id(self):
        """ Test that cant update branch with ID that doesn't exist"""
        data = dict(branch_id=257, capacity=25)
        json_response = api_call(self, "PUT", '/branch/update', data, 200, True)
        self.assertEqual(json_response['status'], 404)
        self.assertEqual(json_response['message'], "Branch not found")

    def test_cant_update_branch_invalid_parameters(self):
        """ Test can't update branch with wrong or missing ID"""
        data = dict(capacity=2018)
        json_response = api_call(self, "PUT", '/branch/update', data, 200, True)
        self.assertEqual(json_response['status'], 400)
        self.assertEqual(json_response['message'], "Missing branch ID")

        data = dict(branch_id="xplain_this", capacity=30)
        json_response = api_call(self, "PUT", '/branch/update', data, 200, True)
        self.assertEqual(json_response['status'], 400)
        self.assertEqual(json_response['message'], "Invalid branch ID")

    def test_can_delete_branch(self):
        """ Test can delete branch """
        data = dict(city="London", postcode="E1W 3SS", capacity=5)
        api_call(self, "POST", '/branch/create', data, 200)

        data = dict(branch_id=1)
        json_response = api_call(self, "DELETE", '/branch/delete', data, 200, True)
        self.assertEqual(json_response['status'], 200)
        self.assertEqual(json_response['message'], "Branch deleted")

        data = dict(branch_id=1)
        json_response = api_call(self, "GET", '/branch/get', data, 200, True)
        self.assertEqual(json_response['status'], 404)
        self.assertEqual(json_response['message'], "Branch not found")

    def test_cant_delete_branch_invalid_id(self):
        """ Test we cant delete branch with invalid ID """
        data = dict(branch_id=102030)
        json_response = api_call(self, "DELETE", '/branch/delete', data, 200, True)
        self.assertEqual(json_response['status'], 404)
        self.assertEqual(json_response['message'], "Branch not found")

        data = dict(branch_id="i_love_sushi")
        json_response = api_call(self, "DELETE", '/branch/delete', data, 200, True)
        self.assertEqual(json_response['status'], 400)
        self.assertEqual(json_response['message'], "Invalid branch ID")

    def test_cant_delete_branch_invalid_request(self):
        """ Test we can't delete branch with bad request"""
        data = dict()
        json_response = api_call(self, "DELETE", '/branch/delete', data, 200, True)
        self.assertEqual(json_response['status'], 400)
        self.assertEqual(json_response['message'], 'Missing branch ID')

    def tearDown(self):
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()


class DriverTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client()

        # set up test db
        with self.app.app_context():
            db.create_all()

    def test_can_create_driver(self):
        """ Test can create normal driver"""
        data = dict(name="Alan Turing", dob="23/06/1962")
        json_response = api_call(self, "POST", "/driver/create", data, 200, True)
        self.assertEqual(json_response["status"], 201)
        self.assertEqual(json_response["message"], 'Driver created')

    def test_cant_create_driver_invalid_request(self):
        """ Test cant create driver with invalid requests"""
        res = self.client.post('/driver/create')
        self.assertEqual(res.status_code, 400)

        res = self.client.post('/driver/create', data=None, content_type='application/json')
        self.assertEqual(res.status_code, 400)

        res = self.client.get('/driver/create')
        self.assertEqual(res.status_code, 405)

    def test_cant_create_driver_missing_or_invalid_params(self):
        """ Test cant create driver with wrong or missing params"""
        data = dict()
        json_response = api_call(self, "POST", "/driver/create", data, 200, True)
        self.assertEqual(json_response["status"], 400)
        self.assertEqual(json_response["message"], "Missing name")

        data = dict(dob="23/06/1962")
        json_response = api_call(self, "POST", "/driver/create", data, 200, True)
        self.assertEqual(json_response["status"], 400)
        self.assertEqual(json_response["message"], "Missing name")

        data = dict(name="Alan Turing")
        json_response = api_call(self, "POST", "/driver/create", data, 200, True)
        self.assertEqual(json_response["status"], 400)
        self.assertEqual(json_response["message"], "Missing DOB")

        data = dict(name="Alan Turing", dob="23/06/2025")
        json_response = api_call(self, "POST", "/driver/create", data, 200, True)
        self.assertEqual(json_response["status"], 400)
        self.assertEqual(json_response["message"], "Invalid DOB")

        data = dict(name="Alan Turing", dob="23 June")
        json_response = api_call(self, "POST", "/driver/create", data, 200, True)
        self.assertEqual(json_response["status"], 400)
        self.assertEqual(json_response["message"], "Invalid DOB")

        data = dict(name="Alan Turing", dob="never")
        json_response = api_call(self, "POST", "/driver/create", data, 200, True)
        self.assertEqual(json_response["status"], 400)
        self.assertEqual(json_response["message"], "Invalid DOB")

    def test_can_get_driver(self):
        """ Test that API can retrieve a driver"""
        data = dict(name="Andrej Lukasov", dob="25/02/1990")
        self.client.post('/driver/create', data=json.dumps(data), content_type='application/json')

        data = dict(driver_id=1)
        json_response = api_call(self, "GET", '/driver/get', data, 200, True)
        self.assertEqual(json_response['name'], 'Andrej Lukasov')
        self.assertEqual(json_response['dob'], '25/02/1990')

    def test_cant_get_driver_invalid_request(self):
        """ Test that endpoint can deal with missing query string"""
        res = self.client.get('/driver/get')
        self.assertEqual(res.status_code, 200)
        json_response = res.get_json()
        self.assertEqual(json_response['status'], 400)
        self.assertEqual(json_response['message'], 'Missing driver ID')

    def test_cant_get_driver_missing_params(self):
        """ Test that endpoint can deal with empty param"""
        data = dict()
        json_response = api_call(self, "GET", '/driver/get', data, 200, True)
        self.assertEqual(json_response['status'], 400)
        self.assertEqual(json_response['message'], 'Missing driver ID')

        data = dict(driver_id=None)
        json_response = api_call(self, "GET", '/driver/get', data, 200, True)
        self.assertEqual(json_response['status'], 400)
        self.assertEqual(json_response['message'], 'Missing driver ID')

    def test_cant_get_driver_id_doesnt_exist(self):
        """ Test can't get driver ID that doesn't exist"""
        data = dict(driver_id=100)
        json_response = api_call(self, "GET", '/driver/get', data, 200, True)
        self.assertEqual(json_response['status'], 404)
        self.assertEqual(json_response['message'], "Driver not found")

    def test_cant_get_driver_id_has_to_be_int(self):
        """ Test can't get a driver with invalid driver ID """
        data = dict(driver_id="abcd")
        json_response = api_call(self, "GET", '/driver/get', data, 200, True)
        self.assertEqual(json_response['status'], 400)
        self.assertEqual(json_response['message'], "Invalid driver ID")

    def test_can_update_driver(self):
        """ Test for updating driver details"""
        data = dict(name="Nicola Tesla", dob="07/11/1952")
        api_call(self, "POST", '/driver/create', data, 200)

        data = dict(driver_id=1, name="John Malkovich")
        res = self.client.put('/driver/update', data=json.dumps(data), content_type='application/json')
        self.assertEqual(res.status_code, 200)

        data = dict(driver_id=1)
        res = self.client.get('/driver/get', query_string=data, content_type='application/json')
        self.assertEqual(res.status_code, 200)
        json_response = res.get_json()
        self.assertEqual(json_response['name'], 'John Malkovich')

        data = dict(driver_id=1, name="Tesla Nicola", dob="12/12/2000")
        res = self.client.put('/driver/update', data=json.dumps(data), content_type='application/json')
        self.assertEqual(res.status_code, 200)

        data = dict(driver_id=1)
        json_response = api_call(self, "GET", '/driver/get', data, 200, True)
        self.assertEqual(json_response['name'], 'Tesla Nicola')
        self.assertEqual(json_response['dob'], "12/12/2000")

    def test_cant_update_driver_invalid_id(self):
        """ Test that cant update driver with ID taht doesn't exist"""
        data = dict(driver_id=257, dob="07/02/1975")
        json_response = api_call(self, "PUT", '/driver/update', data, 200, True)
        self.assertEqual(json_response['status'], 404)
        self.assertEqual(json_response['message'], "Driver not found")

    def test_cant_update_driver_invalid_parameters(self):
        """ Test can't update driver with wrong or missing ID"""
        data = dict(name="Henry Ford")
        json_response = api_call(self, "PUT", '/driver/update', data, 200, True)
        self.assertEqual(json_response['status'], 400)
        self.assertEqual(json_response['message'], "Missing driver ID")

        data = dict(driver_id="cowabunga!", name="Eminem McRapburger")
        json_response = api_call(self, "PUT", '/driver/update', data, 200, True)
        self.assertEqual(json_response['status'], 400)
        self.assertEqual(json_response['message'], "Invalid driver ID")

    def test_can_delete_driver(self):
        """ Test can delete driver """
        data = dict(name="Nicola Tesla", dob="23/12/1983")
        api_call(self, "POST", '/driver/create', data, 200)

        data = dict(driver_id=1)
        json_response = api_call(self, "DELETE", '/driver/delete', data, 200, True)
        self.assertEqual(json_response['status'], 200)
        self.assertEqual(json_response['message'], "Driver deleted")

        data = dict(driver_id=1)
        json_response = api_call(self, "GET", '/driver/get', data, 200, True)
        self.assertEqual(json_response['status'], 404)
        self.assertEqual(json_response['message'], "Driver not found")

    def test_cant_delete_driver_invalid_id(self):
        """ Test we cant delete driver with invalid ID """
        data = dict(driver_id=102030)
        json_response = api_call(self, "DELETE", '/driver/delete', data, 200, True)
        self.assertEqual(json_response['status'], 404)
        self.assertEqual(json_response['message'], "Driver not found")

        data = dict(driver_id="i_love_pizza")
        json_response = api_call(self, "DELETE", '/driver/delete', data, 200, True)
        self.assertEqual(json_response['status'], 400)
        self.assertEqual(json_response['message'], "Invalid driver ID")

    def test_cant_delete_driver_invalid_request(self):
        """ Test we can't delete driver with bad request"""
        data = dict()
        json_response = api_call(self, "DELETE", '/driver/delete', data, 200, True)
        self.assertEqual(json_response['status'], 400)
        self.assertEqual(json_response['message'], 'Missing driver ID')

    def tearDown(self):
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()


if __name__ == "__main__":
    unittest.main()
