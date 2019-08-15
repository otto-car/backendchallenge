import unittest
from app import create_app, db
from flask import json


def api_call(self, method, url, data, status_code, return_jason=False):
    """
    Helper method to make API calls and check for status code straight away

    :param self
    :param method: currently accepting only POST, GET, DELETE, PUT methods
    :param url: endpoint url like /car/get
    :param data: dict object of params to be sent to endpoint
    :param status_code: requests status code to check for
    :param return_jason: return json data or not
    :returns: json of a request if return_jason is True
    """
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
        # sets up clean app with testing config
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client()

        # set up test db
        with self.app.app_context():
            db.create_all()

    def test_can_create_car(self):
        """ Test that API can create a new car via POST request to the endpoint"""
        api_call(self, "POST", "/driver/create", dict(first_name="Alan", last_name="Turing", dob="23/06/1962"), 200,
                 True)
        json_response = api_call(self, "POST", "/car/create", dict(make="Tesla", model="Model 3", year=2018,
                                                                   assigned_type=1, assigned_id=1), 200, True)
        self.assertEqual(json_response["status_code"], 201)
        self.assertEqual(json_response["message"], 'Car created')

    def test_cant_create_car_unassigned(self):
        """" Test that we can't create car without assigning it to driver or branch"""
        json_response = api_call(self, "POST", "/car/create", dict(make="Tesla", model="Model 3", year=2018), 200, True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], 'Missing assigned_type')

        json_response = api_call(self, "POST", "/car/create", dict(make="Tesla", model="Model 3", year=2018,
                                                                   assigned_type=1), 200, True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], 'Missing assigned_id')

    def test_cant_create_car_invalid_request(self):
        """ Test that API will correct response codes for invalid requests"""
        json_response = api_call(self, "POST", '/car/create', None, 200)
        self.assertEqual(json_response, None)

        res = self.client.post('/car/create')
        self.assertEqual(res.status_code, 200)

        res = self.client.post('/car/create', data=None, content_type='application/json')
        self.assertEqual(res.status_code, 200)

        res = self.client.get('/car/create')
        self.assertEqual(res.status_code, 405)

        res = self.client.delete('/car/create')
        self.assertEqual(res.status_code, 405)

        res = self.client.put('/car/create')
        self.assertEqual(res.status_code, 405)

    def test_cant_create_car_missing_invalid_params(self):
        """ Test that API will return expected errors when params are missing"""
        json_response = api_call(self, "POST", "/car/create", dict(), 200, True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], 'Missing make')

        json_response = api_call(self, "POST", "/car/create", dict(make="Tesla", model="Model 3",
                                                                   year="Stringy McStringface"), 200, True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], 'Invalid year')

        json_response = api_call(self, "POST", "/car/create", dict(model="Model 3", year=2018), 200, True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], 'Missing make')

        json_response = api_call(self, "POST", "/car/create", dict(make="Tesla", year=2018), 200, True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], 'Missing model')

        json_response = api_call(self, "POST", "/car/create", dict(make="Tesla", model="Model 3"), 200, True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], 'Missing year')

        json_response = api_call(self, "POST", "/car/create", dict(make="Tesla", model="Model 3", year=2018,
                                                                   assigned_type=1), 200, True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], 'Missing assigned_id')

        json_response = api_call(self, "POST", "/car/create", dict(make="Tesla", model="Model 3", year=2018, assigned_id=1), 200, True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], 'Missing assigned_type')

    def test_can_get_car(self):
        """ Test that API can retrieve a car"""
        api_call(self, "POST", "/driver/create", dict(first_name="Alan", last_name="Turing", dob="23/06/1962"), 200,
                 True)
        api_call(self, "POST", '/car/create', dict(make="BMW", model="530d", year=2018, assigned_type=1, assigned_id=1),
                 200)

        json_response = api_call(self, "GET", '/car/get', dict(id=1), 200, True)
        self.assertEqual(json_response['make'], 'BMW')
        self.assertEqual(json_response['model'], '530d')
        self.assertEqual(json_response['year'], 2018)
        self.assertEqual(json_response['assigned_type'], 1)
        self.assertEqual(json_response['assigned_id'], 1)

        api_call(self, "POST", "/branch/create", dict(city="London", postcode="E1W3SS", capacity=10), 200, True)
        api_call(self, "POST", '/car/create', dict(make="Vauxhall", model="Corsa", year=2001, assigned_type=2,
                                                   assigned_id=1), 200)

        json_response = api_call(self, "GET", '/car/get', dict(id=2), 200, True)
        self.assertEqual(json_response['make'], 'Vauxhall')
        self.assertEqual(json_response['model'], 'Corsa')
        self.assertEqual(json_response['year'], 2001)
        self.assertEqual(json_response['assigned_type'], 2)
        self.assertEqual(json_response['assigned_id'], 1)

    def test_cant_get_car_invalid_request(self):
        """ Test that endpoint can deal with missing query string"""
        res = self.client.post('/car/get')
        self.assertEqual(res.status_code, 405)

        res = self.client.delete('/car/get')
        self.assertEqual(res.status_code, 405)

        res = self.client.put('/car/get')
        self.assertEqual(res.status_code, 405)

        res = self.client.get('/car/get')
        self.assertEqual(res.status_code, 200)
        json_response = res.get_json()
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], "Invalid request")

    def test_cant_get_car_invalid_params(self):
        """ Test that endpoint can deal with invalid or missing params"""
        json_response = api_call(self, "GET", '/car/get', dict(), 200, True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], "Invalid request")

        json_response = api_call(self, "GET", '/car/get', dict(id=None), 200, True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], "Invalid request")

        json_response = api_call(self, "GET", '/car/get', dict(id=100), 200, True)
        self.assertEqual(json_response["status_code"], 404)
        self.assertEqual(json_response["message"], 'Car not found')

        json_response = api_call(self, "GET", '/car/get', dict(id="abcd"), 200, True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], 'Invalid id')

        json_response = api_call(self, "GET", '/car/get', dict(id=1), 200, True)
        self.assertEqual(json_response["status_code"], 404)
        self.assertEqual(json_response["message"], 'Car not found')

        api_call(self, "POST", "/branch/create", dict(city="London", postcode="E1W3SS", capacity=10), 200, True)
        api_call(self, "POST", '/car/create', dict(make="Vauxhall", model="Corsa", year=2001, assigned_type=2,
                                                   assigned_id=1), 200)

        json_response = api_call(self, "GET", '/car/get', dict(id=1, year="twenty five"), 200, True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], 'Invalid year')

        json_response = api_call(self, "GET", '/car/get', dict(assigned_type="twenty"), 200, True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], 'Missing assigned_id')

        json_response = api_call(self, "GET", '/car/get', dict(assigned_type=3, assigned_id=1), 200, True)
        self.assertEqual(json_response["status_code"], 404)
        self.assertEqual(json_response["message"], 'Car not found')

        json_response = api_call(self, "GET", '/car/get', dict(assigned_type="blabla", assigned_id=1), 200, True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], 'Invalid assigned_type')

        json_response = api_call(self, "GET", '/car/get', dict(assigned_type=1, assigned_id="onetwothree"), 200, True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], 'Invalid assigned_id')

    def test_can_update_car(self):
        """ Test for updating car details and successfuly retrieving it"""
        api_call(self, "POST", "/driver/create", dict(first_name="Alan", last_name="Turing", dob="23/06/1962"), 200,
                 True)
        api_call(self, "POST", "/branch/create", dict(city="London", postcode="E1W3SS", capacity=10), 200, True)

        api_call(self, "POST", '/car/create', dict(make="Tesla", model="Model 3", year=2015, assigned_type=1,
                                                   assigned_id=1), 200)

        api_call(self, "POST", '/car/create', dict(make="BMW", model="530d", year=2018, assigned_type=2, assigned_id=1),
                 200)

        api_call(self, "PUT", '/car/update', dict(id=1, assigned_type=2, assigned_id=1), 200, True)
        json_response = api_call(self, "GET", '/car/get', dict(id=1), 200, True)
        self.assertEqual(json_response['assigned_type'], 2)
        self.assertEqual(json_response['assigned_id'], 1)

        api_call(self, "PUT", '/car/update', dict(id=1, model="Model X", year=2018), 200, True)
        json_response = api_call(self, "GET", '/car/get', dict(id=1), 200, True)
        self.assertEqual(json_response['make'], "Tesla")
        self.assertEqual(json_response['model'], "Model X")
        self.assertEqual(json_response['year'], 2018)

        api_call(self, "PUT", '/car/update', dict(id=2, assigned_type=1, assigned_id=1), 200, True)
        json_response = api_call(self, "GET", '/car/get', dict(id=2), 200, True)
        self.assertEqual(json_response['assigned_type'], 1)
        self.assertEqual(json_response['assigned_id'], 1)

        api_call(self, "PUT", '/car/update', dict(id=2,make="Mercedes", model="E-Class", year=2019), 200, True)
        json_response = api_call(self, "GET", '/car/get', dict(id=2), 200, True)
        self.assertEqual(json_response['make'], "Mercedes")
        self.assertEqual(json_response['model'], "E-Class")
        self.assertEqual(json_response['year'], 2019)

    def test_cant_update_car_invalid_requests(self):
        """" Test for correct method to be used when sending update requests"""
        res = self.client.post('/car/update')
        self.assertEqual(res.status_code, 405)

        res = self.client.delete('/car/update')
        self.assertEqual(res.status_code, 405)

        res = self.client.put('/car/update')
        self.assertEqual(res.status_code, 200)

        res = self.client.get('/car/update')
        self.assertEqual(res.status_code, 405)

    def test_cant_update_car_invalid_parameters(self):
        """ Test can't update car with wrong or missing ID"""
        json_response = api_call(self, "PUT", '/car/update', dict(id=257, year=2015), 200, True)
        self.assertEqual(json_response["status_code"], 404)
        self.assertEqual(json_response["message"], "Car not found")

        json_response = api_call(self, "PUT", '/car/update', dict(year=2018, make="Ford"), 200, True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], "Missing id")

        json_response = api_call(self, "PUT", '/car/update', dict(id="cowabunga!", model="C45 AMG"), 200, True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], "Invalid id")

        api_call(self, "POST", "/branch/create", dict(city="London", postcode="E1W3SS", capacity=10), 200, True)
        api_call(self, "POST", '/car/create', dict(make="BMW", model="530d", year=2018, assigned_type=2, assigned_id=1),
                 200)

        json_response = api_call(self, "PUT", '/car/update', dict(id=1, year="C45 AMG", make="Mercedes-Benz"), 200,
                                 True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], "Invalid year")

        json_response = api_call(self, "PUT", '/car/update', dict(id=1, assigned_type=3, assigned_id=1), 200, True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], "Invalid assigned_type")

        json_response = api_call(self, "PUT", '/car/update', dict(id=1, assigned_type="oogabooga", assigned_id=1), 200,
                                 True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], "Invalid assigned_type")

        json_response = api_call(self, "PUT", '/car/update', dict(id=1, assigned_type=2, assigned_id="hey"), 200, True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], "Invalid assigned_id")

        json_response = api_call(self, "PUT", '/car/update', dict(id=1, assigned_type=2, assigned_id=20), 200, True)
        self.assertEqual(json_response["status_code"], 404)
        self.assertEqual(json_response["message"], "Branch not found")

        json_response = api_call(self, "PUT", '/car/update', dict(id=1, assigned_type=1, assigned_id=20), 200, True)
        self.assertEqual(json_response["status_code"], 404)
        self.assertEqual(json_response["message"], "Driver not found")

        api_call(self, "POST", "/branch/create", dict(city="London", postcode="E1W3SS", capacity=1), 200, True)
        api_call(self, "POST", '/car/create', dict(make="BMW", model="530d", year=2018, assigned_type=2, assigned_id=2),
                 200)
        json_response = api_call(self, "POST", '/car/create', dict(make="BMW", model="530d", year=2018, assigned_type=2,
                                                                   assigned_id=2), 200, True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], "Branch has reached its capacity")

    def test_can_delete_car(self):
        """ Test can delete car """
        api_call(self, "POST", "/driver/create", dict(first_name="Alan", last_name="Turing", dob="23/06/1962"), 200)
        api_call(self, "POST", '/car/create', dict(make="Tesla", model="Model 3", year=2015, assigned_type=1,
                                                   assigned_id=1), 200)

        json_response = api_call(self, "DELETE", '/car/delete', dict(id=1), 200, True)
        self.assertEqual(json_response["status_code"], 200)
        self.assertEqual(json_response["message"], "Car deleted")

        json_response = api_call(self, "GET", '/car/get', dict(id=1), 200, True)
        self.assertEqual(json_response["status_code"], 404)
        self.assertEqual(json_response["message"], "Car not found")

    def test_cant_delete_car_invalid_id(self):
        """ Test we cant delete car with invalid ID """
        json_response = api_call(self, "DELETE", '/car/delete', dict(id=102030), 200, True)
        self.assertEqual(json_response["status_code"], 404)
        self.assertEqual(json_response["message"], "Car not found")

        json_response = api_call(self, "DELETE", '/car/delete', dict(id="i_love_pizza"), 200, True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], "Invalid id")

    def test_cant_delete_car_invalid_request(self):
        """ Test we can't delete car with bad request"""
        json_response = api_call(self, "DELETE", '/car/delete', dict(), 200, True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], 'Missing id')

        res = self.client.post('/car/delete')
        self.assertEqual(res.status_code, 405)

        res = self.client.put('/car/delete')
        self.assertEqual(res.status_code, 405)

        res = self.client.get('/car/delete')
        self.assertEqual(res.status_code, 405)

    def tearDown(self):
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()


class BranchTestCase(unittest.TestCase):
    def setUp(self):
        # sets up clean app with testing config
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client()

        # set up test db
        with self.app.app_context():
            db.create_all()

    def test_can_create_branch(self):
        """ Test can create normal branch"""
        json_response = api_call(self, "POST", "/branch/create", dict(city="London", postcode="E1W 3SS", capacity=5),
                                 200, True)
        self.assertEqual(json_response["status_code"], 201)
        self.assertEqual(json_response["message"], 'Branch created')

    def test_cant_create_branch_invalid_request(self):
        """ Test cant create branch with invalid requests"""
        json_response = api_call(self, "POST", '/branch/create', None, 200)
        self.assertEqual(json_response, None)

        res = self.client.post('/branch/create')
        self.assertEqual(res.status_code, 200)

        res = self.client.post('/branch/create', data=None, content_type='application/json')
        self.assertEqual(res.status_code, 200)

        res = self.client.get('/branch/create')
        self.assertEqual(res.status_code, 405)

        res = self.client.delete('/branch/create')
        self.assertEqual(res.status_code, 405)

        res = self.client.put('/branch/create')
        self.assertEqual(res.status_code, 405)

    def test_cant_create_branch_missing_or_invalid_params(self):
        """ Test cant create branch with wrong or missing params"""
        json_response = api_call(self, "POST", "/branch/create", dict(), 200, True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], "Missing city")

        json_response = api_call(self, "POST", "/branch/create", dict(postcode="E1W 3SS", capacity=5), 200, True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], "Missing city")

        json_response = api_call(self, "POST", "/branch/create", dict(city="London", capacity=5), 200, True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], "Missing postcode")

        json_response = api_call(self, "POST", "/branch/create", dict(city="London", postcode="123456789123",
                                                                      capacity=5), 200, True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], "Invalid postcode")

        json_response = api_call(self, "POST", "/branch/create", dict(city="London", postcode="SE157 258GU2",
                                                                      capacity=5), 200, True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], "Invalid postcode")

        json_response = api_call(self, "POST", "/branch/create", dict(city="London", postcode="SE2", capacity=5), 200,
                                 True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], "Invalid postcode")

        json_response = api_call(self, "POST", "/branch/create", dict(city="London", postcode="SE2X2", capacity=5),
                                 200, True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], "Invalid postcode")

        json_response = api_call(self, "POST", "/branch/create", dict(city="London", postcode="E1W 3SS"), 200, True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], "Missing capacity")

        json_response = api_call(self, "POST", "/branch/create", dict(city="London", postcode="E1W 3SS",
                                                                      capacity="super"), 200, True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], "Invalid capacity")

    def test_can_get_branch(self):
        """ Test that API can retrieve a branch"""
        api_call(self, "POST", '/branch/create', dict(city="London", postcode="E1W 3SS", capacity=5), 200)

        json_response = api_call(self, "GET", '/branch/get', dict(id=1), 200, True)
        self.assertEqual(json_response['city'], 'London')
        self.assertEqual(json_response['postcode'], 'E1W 3SS')
        self.assertEqual(json_response['capacity'], 5)

        api_call(self, "POST", '/branch/create', dict(city="Guildford", postcode="GU11EA", capacity=10), 200)
        json_response = api_call(self, "GET", '/branch/get', dict(id=2), 200, True)
        self.assertEqual(json_response['city'], 'Guildford')
        self.assertEqual(json_response['postcode'], 'GU11EA')
        self.assertEqual(json_response['capacity'], 10)

    def test_cant_get_branch_invalid_request(self):
        """ Test that endpoint can deal with missing query string"""
        res = self.client.post('/branch/get')
        self.assertEqual(res.status_code, 405)

        res = self.client.delete('/branch/get')
        self.assertEqual(res.status_code, 405)

        res = self.client.put('/branch/get')
        self.assertEqual(res.status_code, 405)

        res = self.client.get('/branch/get')
        self.assertEqual(res.status_code, 200)
        json_response = res.get_json()
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], 'Invalid request')

    def test_cant_get_branch_missing_params(self):
        """ Test that endpoint can deal with empty param"""
        json_response = api_call(self, "GET", '/branch/get', dict(), 200, True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], 'Invalid request')

        json_response = api_call(self, "GET", '/branch/get', dict(id=None), 200, True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], 'Invalid request')

    def test_cant_get_branch_id_doesnt_exist(self):
        """ Test can't get branch ID that doesn't exist"""
        json_response = api_call(self, "GET", '/branch/get', dict(id=100), 200, True)
        self.assertEqual(json_response["status_code"], 404)
        self.assertEqual(json_response["message"], "Branch not found")

    def test_cant_get_branch_id_has_to_be_int(self):
        """ Test can't get a branch with invalid ID """
        json_response = api_call(self, "GET", '/branch/get', dict(id="abcd"), 200, True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], "Invalid id")

    def test_can_update_branch(self):
        """ Test for updating branch details"""
        api_call(self, "POST", '/branch/create', dict(city="London", postcode="E1W 3SS", capacity=5), 200)

        json_response = api_call(self, "GET", '/branch/get', dict(id=1), 200, True)
        self.assertEqual(json_response['city'], 'London')
        self.assertEqual(json_response['postcode'], 'E1W 3SS')
        self.assertEqual(json_response['capacity'], 5)

        json_response = api_call(self, "PUT", '/branch/update', dict(id=1, city="Guildford", postcode="GU2 8DJ",
                                                                     capacity=100), 200, True)
        self.assertEqual(json_response["status_code"], 200)
        self.assertEqual(json_response["message"], "Branch record was updated")

        json_response = api_call(self, "GET", '/branch/get', dict(id=1), 200, True)
        self.assertEqual(json_response['city'], 'Guildford')
        self.assertEqual(json_response['postcode'], 'GU2 8DJ')
        self.assertEqual(json_response['capacity'], 100)

        json_response = api_call(self, "PUT", '/branch/update', dict(id=1, capacity=90), 200, True)
        self.assertEqual(json_response["status_code"], 200)
        self.assertEqual(json_response["message"], "Branch record was updated")

        json_response = api_call(self, "GET", '/branch/get', dict(id=1), 200, True)
        self.assertEqual(json_response['city'], 'Guildford')
        self.assertEqual(json_response['postcode'], 'GU2 8DJ')
        self.assertEqual(json_response['capacity'], 90)

        json_response = api_call(self, "PUT", '/branch/update', dict(id=1, city="Northampton", postcode="NN11 1AA",
                                                                     capacity=5), 200, True)
        self.assertEqual(json_response["status_code"], 200)
        self.assertEqual(json_response["message"], "Branch record was updated")

        json_response = api_call(self, "GET", '/branch/get', dict(id=1), 200, True)
        self.assertEqual(json_response['city'], 'Northampton')
        self.assertEqual(json_response['postcode'], 'NN11 1AA')
        self.assertEqual(json_response['capacity'], 5)

    def test_cant_update_branch_invalid_requests(self):
        """" Test for correct method to be used when sending update requests"""
        res = self.client.post('/branch/update')
        self.assertEqual(res.status_code, 405)

        res = self.client.delete('/branch/update')
        self.assertEqual(res.status_code, 405)

        res = self.client.put('/branch/update')
        self.assertEqual(res.status_code, 200)

        res = self.client.get('/branch/update')
        self.assertEqual(res.status_code, 405)

    def test_cant_update_branch_invalid_id(self):
        """ Test that cant update branch with ID that doesn't exist"""
        json_response = api_call(self, "PUT", '/branch/update', dict(id=257, capacity=25), 200, True)
        self.assertEqual(json_response["status_code"], 404)
        self.assertEqual(json_response["message"], "Branch not found")

    def test_cant_update_branch_invalid_parameters(self):
        """ Test can't update branch with wrong or missing ID"""
        json_response = api_call(self, "PUT", '/branch/update', dict(capacity=2018), 200, True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], "Missing id")

        json_response = api_call(self, "PUT", '/branch/update', dict(id="xplain_this", capacity=30), 200, True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], "Invalid id")

        json_response = api_call(self, "PUT", '/branch/update', dict(id=1, capacity=30), 200, True)
        self.assertEqual(json_response["status_code"], 404)
        self.assertEqual(json_response["message"], "Branch not found")

        api_call(self, "POST", '/branch/create', dict(city="Northampton", postcode="NN11 1AA", capacity=5), 200)

        json_response = api_call(self, "PUT", '/branch/update', dict(id=1, postcode="ggggg", capacity=30), 200, True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], "Invalid postcode")

        json_response = api_call(self, "PUT", '/branch/update', dict(id=1, city=123123123), 200, True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], "Invalid city")

        json_response = api_call(self, "PUT", '/branch/update', dict(id=1, capacity="a lot!"), 200, True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], "Invalid capacity")

    def test_can_delete_branch(self):
        """ Test can delete branch """
        api_call(self, "POST", '/branch/create', dict(city="London", postcode="E1W 3SS", capacity=5), 200)

        json_response = api_call(self, "DELETE", '/branch/delete', dict(id=1), 200, True)
        self.assertEqual(json_response["status_code"], 200)
        self.assertEqual(json_response["message"], "Branch deleted")

        json_response = api_call(self, "GET", '/branch/get', dict(id=1), 200, True)
        self.assertEqual(json_response["status_code"], 404)
        self.assertEqual(json_response["message"], "Branch not found")

    def test_cant_delete_branch_invalid_id(self):
        """ Test we cant delete branch with invalid ID """
        json_response = api_call(self, "DELETE", '/branch/delete', dict(id=102030), 200, True)
        self.assertEqual(json_response["status_code"], 404)
        self.assertEqual(json_response["message"], "Branch not found")

        json_response = api_call(self, "DELETE", '/branch/delete', dict(id="i_love_sushi"), 200, True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], "Invalid id")

    def test_cant_delete_branch_invalid_request(self):
        """ Test we can't delete branch with bad request"""
        json_response = api_call(self, "DELETE", '/branch/delete', dict(), 200, True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], 'Missing id')

        res = self.client.post('/branch/delete')
        self.assertEqual(res.status_code, 405)

        res = self.client.put('/branch/delete')
        self.assertEqual(res.status_code, 405)

        res = self.client.get('/branch/delete')
        self.assertEqual(res.status_code, 405)

    def tearDown(self):
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()


class DriverTestCase(unittest.TestCase):
    def setUp(self):
        # sets up clean app with testing config
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client()

        # set up test db
        with self.app.app_context():
            db.create_all()

    def test_can_create_driver(self):
        """ Test can create normal driver"""
        json_response = api_call(self, "POST", "/driver/create", dict(first_name="Alan", last_name="Turing",
                                                                      dob="23/06/1962"), 200, True)
        self.assertEqual(json_response["status_code"], 201)
        self.assertEqual(json_response["message"], 'Driver created')

    def test_cant_create_driver_invalid_request(self):
        """ Test cant create driver with invalid requests"""
        json_response = api_call(self, "POST", '/driver/create', None, 200)
        self.assertEqual(json_response, None)

        res = self.client.post('/driver/create')
        self.assertEqual(res.status_code, 200)

        res = self.client.post('/driver/create', data=None, content_type='application/json')
        self.assertEqual(res.status_code, 200)

        res = self.client.get('/driver/create')
        self.assertEqual(res.status_code, 405)

        res = self.client.delete('/driver/create')
        self.assertEqual(res.status_code, 405)

        res = self.client.put('/driver/create')
        self.assertEqual(res.status_code, 405)

    def test_cant_create_driver_missing_or_invalid_params(self):
        """ Test cant create driver with wrong or missing params"""
        json_response = api_call(self, "POST", "/driver/create", dict(), 200, True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], "Missing first_name")

        json_response = api_call(self, "POST", "/driver/create", dict(dob="23/06/1962"), 200, True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], "Missing first_name")

        json_response = api_call(self, "POST", "/driver/create", dict(first_name="Alan", last_name="Turing"), 200, True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], "Missing dob")

        json_response = api_call(self, "POST", "/driver/create", dict(first_name="Alan", last_name="Turing",
                                                                      dob="23/06/2025"), 200, True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], "Invalid dob")

        json_response = api_call(self, "POST", "/driver/create", dict(first_name="Alan", last_name="Turing",
                                                                      dob="23 June"), 200, True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], "Invalid dob")

        json_response = api_call(self, "POST", "/driver/create", dict(first_name="Alan", last_name="Turing",
                                                                      dob="never"), 200, True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], "Invalid dob")

    def test_can_get_driver(self):
        """ Test that API can retrieve a driver"""
        api_call(self, "POST", '/driver/create', dict(first_name="Bill", middle_name="John", last_name="Gates",
                                                      dob="11/05/1950"), 200)

        json_response = api_call(self, "GET", '/driver/get', dict(id=1), 200, True)
        self.assertEqual(json_response['first_name'], 'Bill')
        self.assertEqual(json_response['last_name'], 'Gates')
        self.assertEqual(json_response['middle_name'], 'John')
        self.assertEqual(json_response['dob'], '11/05/1950')

    def test_cant_get_driver_invalid_request(self):
        """ Test that endpoint can deal with missing query string"""
        res = self.client.post('/driver/get')
        self.assertEqual(res.status_code, 405)

        res = self.client.delete('/driver/get')
        self.assertEqual(res.status_code, 405)

        res = self.client.put('/driver/get')
        self.assertEqual(res.status_code, 405)

        res = self.client.get('/driver/get')
        self.assertEqual(res.status_code, 200)
        json_response = res.get_json()
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], 'Invalid request')

    def test_cant_get_driver_invalid_params(self):
        """ Test that endpoint can deal with invalid or missing param"""
        json_response = api_call(self, "GET", '/driver/get', dict(), 200, True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], 'Invalid request')

        json_response = api_call(self, "GET", '/driver/get', dict(id=None), 200, True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], 'Invalid request')

        json_response = api_call(self, "GET", '/driver/get', dict(id=100), 200, True)
        self.assertEqual(json_response["status_code"], 404)
        self.assertEqual(json_response["message"], "Driver not found")

        json_response = api_call(self, "GET", '/driver/get', dict(id="abcd"), 200, True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], "Invalid id")

    def test_can_get_driver_by_name(self):
        api_call(self, "POST", '/driver/create', dict(first_name="Bill", middle_name="John", last_name="Gates",
                                                      dob="11/05/1950"), 200)

        json_response = api_call(self, "GET", '/driver/get', dict(first_name="Bill", last_name="Gates",
                                                                  middle_name="John"), 200, True)
        self.assertEqual(json_response['dob'], "11/05/1950")

    def test_failing_validation_bad_params(self):
        api_call(self, "POST", '/driver/create', dict(first_name="Bill", middle_name="John", last_name="Gates",
                                                      dob="11/05/1950"), 200)

        json_response = api_call(self, "GET", '/driver/get', dict(dob="John"), 200, True)
        self.assertEqual(json_response['status_code'], 400)
        self.assertEqual(json_response['message'], "Invalid dob")

    def test_can_update_driver(self):
        """ Test for updating driver details"""
        api_call(self, "POST", '/driver/create', dict(first_name="Nicola", last_name="Tesla", middle_name="Testovich",
                                                      dob="07/11/1952"), 200)

        json_response = api_call(self, "PUT", '/driver/update', dict(id=1, first_name="John", last_name="Malkovich"),
                                 200, True)
        self.assertEqual(json_response["status_code"], 200)
        self.assertEqual(json_response["message"], "Driver record was updated")

        json_response = api_call(self, "GET", '/driver/get', dict(id=1), 200, True)
        self.assertEqual(json_response['first_name'], 'John')
        self.assertEqual(json_response['middle_name'], 'Testovich')
        self.assertEqual(json_response['last_name'], 'Malkovich')

        json_response = api_call(self, "PUT", '/driver/update', dict(id=1, first_name="Tesla", middle_name="Test",
                                                                     last_name="Nicola", dob="12/12/2000"), 200, True)
        self.assertEqual(json_response["status_code"], 200)
        self.assertEqual(json_response["message"], "Driver record was updated")

        json_response = api_call(self, "GET", '/driver/get', dict(id=1), 200, True)
        self.assertEqual(json_response['first_name'], 'Tesla')
        self.assertEqual(json_response['middle_name'], 'Test')
        self.assertEqual(json_response['last_name'], 'Nicola')
        self.assertEqual(json_response['dob'], "12/12/2000")

    def test_cant_update_driver_invalid_requests(self):
        """" Test for correct method to be used when sending update requests"""
        res = self.client.post('/driver/update')
        self.assertEqual(res.status_code, 405)

        res = self.client.delete('/driver/update')
        self.assertEqual(res.status_code, 405)

        res = self.client.put('/driver/update')
        self.assertEqual(res.status_code, 200)

        res = self.client.get('/driver/update')
        self.assertEqual(res.status_code, 405)

    def test_cant_update_driver_invalid_parameters(self):
        """ Test can't update driver with invalid or missing params"""
        json_response = api_call(self, "PUT", '/driver/update', dict(first_name="Henry", last_name="Ford"), 200, True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], "Missing id")

        json_response = api_call(self, "PUT", '/driver/update', dict(id="cowabunga!", first_name="Eminem",
                                                                     last_name="McRapburger"), 200, True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], "Invalid id")

        json_response = api_call(self, "PUT", '/driver/update', dict(id=1, first_name="Eminem",
                                                                     last_name="McRapburger"), 200, True)
        self.assertEqual(json_response["status_code"], 404)
        self.assertEqual(json_response["message"], "Driver not found")

        api_call(self, "POST", '/driver/create', dict(first_name="Nicola", last_name="Tesla", middle_name="Testovich",
                                                      dob="07/11/1952"), 200)

        json_response = api_call(self, "PUT", '/driver/update', dict(id=1, first_name="Eminem", last_name="McRapburger",
                                                                     dob="First of whatever"), 200, True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], "Invalid dob")

    def test_can_delete_driver(self):
        """ Test can delete driver """
        api_call(self, "POST", '/driver/create', dict(first_name="Nicola", last_name="Tesla", dob="23/12/1983"), 200)

        json_response = api_call(self, "DELETE", '/driver/delete', dict(id=1), 200, True)
        self.assertEqual(json_response["status_code"], 200)
        self.assertEqual(json_response["message"], "Driver deleted")

        json_response = api_call(self, "GET", '/driver/get', dict(id=1), 200, True)
        self.assertEqual(json_response["status_code"], 404)
        self.assertEqual(json_response["message"], "Driver not found")

    def test_cant_delete_driver_invalid_id(self):
        """ Test we cant delete driver with invalid ID """
        json_response = api_call(self, "DELETE", '/driver/delete', dict(id=102030), 200, True)
        self.assertEqual(json_response["status_code"], 404)
        self.assertEqual(json_response["message"], "Driver not found")

        json_response = api_call(self, "DELETE", '/driver/delete', dict(id="i_love_pizza"), 200, True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], "Invalid id")

    def test_cant_delete_driver_invalid_request(self):
        """ Test we can't delete driver with bad request"""
        json_response = api_call(self, "DELETE", '/driver/delete', dict(), 200, True)
        self.assertEqual(json_response["status_code"], 400)
        self.assertEqual(json_response["message"], 'Missing id')

        res = self.client.post('/driver/delete')
        self.assertEqual(res.status_code, 405)

        res = self.client.put('/driver/delete')
        self.assertEqual(res.status_code, 405)

        res = self.client.get('/driver/delete')
        self.assertEqual(res.status_code, 405)

    def tearDown(self):
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()


if __name__ == "__main__":
    unittest.main()
