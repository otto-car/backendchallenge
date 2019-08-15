from flask_api import FlaskAPI, exceptions
from flask_sqlalchemy import SQLAlchemy
from instance.config import app_config
from flask import request, jsonify
import re
import datetime
from app import helpers

db = SQLAlchemy()


def create_app(config_name):
    from app.models import Car, Branch, Driver

    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    @app.route('/car/create', methods=['POST'])
    def car_create():
        if request.method == "POST":
            if request.data is None:
                return jsonify({"status_code": 400, "message": "Invalid request"})
            request_data = request.data

            try:
                make = helpers.check_missing('list', request_data, 'make')
                model = helpers.check_missing('list', request_data, 'model')
                year = helpers.check_missing('list', request_data, 'year')
                year = helpers.validate_year(year)
                assigned_type = helpers.check_missing('list', request_data, 'assigned_type')
                assigned_id = helpers.check_missing('list', request_data, 'assigned_id')
                assigned_id = helpers.validate_int(assigned_id, 'assigned_id')
                assigned_type, assigned_id = helpers.validate_assigning(assigned_type, assigned_id)
                car = Car(make, model, year, assigned_type, assigned_id)
                car.save()
                return jsonify({"status_code": 201, "message": "Car created"})
            except Exception as e:
                return jsonify({"status_code": e.args[0]['status_code'], "message": e.args[0]['message']})

    @app.route('/car/get', methods=['GET'])
    def car_get():
        if request.method == "GET":
            if request.args is None:
                return jsonify({"status_code": 400, "message": "Invalid request"})

            try:
                params = {}
                if "id" in request.args.keys():
                    params['id'] = helpers.validate_int(request.args.get('id'), 'id')
                if "make" in request.args.keys():
                    params['make'] = helpers.validate_string(request.args.get('make'), 'make')
                if "model" in request.args.keys():
                    params['model'] = helpers.validate_string(request.args.get('model'), 'model')
                if "year" in request.args.keys():
                    params['year'] = helpers.validate_year(request.args.get('year'))
                if not params:
                    raise Exception({"status_code": 400, "message": "Invalid request"})
                car = Car.get(params)
                if not car:
                    raise Exception({"status_code": 404, "message": "Car not found"})
                return jsonify(car.serialize())
            except Exception as e:
                return jsonify({"status_code": e.args[0]['status_code'], "message": e.args[0]['message']})

    @app.route('/car/update', methods=['PUT'])
    def car_update():
        if request.method == "PUT":
            if request.data is None:
                return jsonify({"status_code": 400, "message": "Invalid request"})
            request_data = request.data

            try:
                id = helpers.check_missing('list', request_data, 'id')
                id = helpers.validate_int(id, 'id')
                params = {"id": id}
                car = Car.get(params)
                if not car:
                    raise Exception({"status_code": 404, "message": "Car not found"})

                if "make" in request_data.keys():
                    car.make = helpers.validate_string(request_data['make'], 'make')
                if "model" in request_data.keys():
                    car.model = helpers.validate_string(request_data['model'], 'model')
                if "year" in request.data.keys():
                    car.year = helpers.validate_year(request_data['year'])
                if "assigned_type" in request_data.keys() and not "assigned_id" in request_data.keys():
                    raise Exception({"status_code": 400, "message": "Missing assigned_id"})
                elif "assigned_id" in request_data.keys() and not "assigned_type" in request_data.keys():
                    raise Exception({"status_code": 400, "message": "Missing assigned_type"})
                elif set(("assigned_type", "assigned_id")) <= request_data.keys():
                    assigned_type, assigned_id = helpers.validate_assigning(request_data['assigned_type'], request_data['assigned_id'])
                    car.assigned_type = assigned_type
                    car.assigned_id = assigned_id
                car.save()

                return jsonify({"status_code": 200, "message": "Car record was updated"})
            except Exception as e:
                return jsonify({"status_code": e.args[0]['status_code'], "message": e.args[0]['message']})

    @app.route('/car/delete', methods=['DELETE'])
    def car_delete():
        if request.method == "DELETE":
            if request.args is None:
                return jsonify({"status_code": 400, "message": "Invalid request"})

            try:
                id = helpers.check_missing('args', request, 'id')
                id = helpers.validate_int(id, 'id')
                params = {"id": id}
                car = Car.get(params)
                if not car:
                    return jsonify({"status_code": 404, "message": "Car not found"})

                car.delete()
                return jsonify({"status_code": 200, "message": "Car deleted"})
            except Exception as e:
                return jsonify({"status_code": e.args[0]['status_code'], "message": e.args[0]['message']})

    @app.route('/branch/create', methods=['POST'])
    def branch_create():
        if request.method == "POST":
            if request.data is None:
                return jsonify({"status_code": 400, "message": "Invalid request"})
            request_data = request.data

            try:
                city = helpers.check_missing('list', request_data, 'city')
                city = helpers.validate_string(city, 'city')
                postcode = helpers.check_missing('list', request_data, 'postcode')
                postcode = helpers.validate_postcode(postcode)
                capacity = helpers.check_missing('list', request_data, 'capacity')
                capacity = helpers.validate_int(capacity, 'capacity')
                branch = Branch(city, postcode, capacity)
                branch.save()
                return jsonify({"status_code": 201, "message": "Branch created"})
            except Exception as e:
                return jsonify({"status_code": e.args[0]['status_code'], "message": e.args[0]['message']})

    @app.route('/branch/get', methods=['GET'])
    def branch_get():
        if request.method == "GET":
            if request.args is None:
                return jsonify({"status_code": 400, "message": "Invalid request"})

            try:
                params = {}
                if "id" in request.args.keys():
                    params['id'] = helpers.validate_int(request.args.get('id'), 'id')
                if "city" in request.args.keys():
                    params['city'] = helpers.validate_string(request.args.get('city'), 'city')
                if "postcode" in request.args.keys():
                    params['postcode'] = helpers.validate_postcode(request.args.get('postcode'))
                if "capacity" in request.args.keys():
                    params['capacity'] = helpers.validate_int(request.args.get('capacity'), 'capacity')
                if not params:
                    return jsonify({"status_code": 400, "message": "Invalid request"})
                branch = Branch.get(params)
                if not branch:
                    return jsonify({"status_code": 404, "message": "Branch not found"})
                return jsonify(branch.serialize())

            except Exception as e:
                return jsonify({"status_code": e.args[0]['status_code'], "message": e.args[0]['message']})

    @app.route('/branch/update', methods=['PUT'])
    def branch_update():
        if request.method == "PUT":
            if request.data is None:
                return jsonify({"status_code": 400, "message": "Invalid request"})
            request_data = request.data

            try:
                id = helpers.check_missing('list', request_data, 'id')
                id = helpers.validate_int(id, 'id')
                params = {"id": id}
                branch = Branch.get(params)
                if not branch:
                    return jsonify({"status_code": 404, "message": "Branch not found"})
                if "city" in request_data.keys():
                    branch.city = helpers.validate_string(request_data['city'], 'city')
                if "postcode" in request_data.keys():
                    branch.postcode = helpers.validate_postcode(request_data['postcode'])
                if "capacity" in request_data.keys():
                    branch.capacity = helpers.validate_int(request_data['capacity'], 'capacity')
                branch.save()
                return jsonify({"status_code": 200, "message": "Branch record was updated"})
            except Exception as e:
                return jsonify({"status_code": e.args[0]['status_code'], "message": e.args[0]['message']})

    @app.route('/branch/delete', methods=['DELETE'])
    def branch_delete():
        if request.method == "DELETE":
            if request.args is None:
                return jsonify({"status_code": 400, "message": "Invalid request"})

            try:
                id = helpers.check_missing('args', request, 'id')
                id = helpers.validate_int(id, 'id')
                params = {"id": id}
                branch = Branch.get(params)
                if not branch:
                    return jsonify({"status_code": 404, "message": "Branch not found"})

                branch.delete()
                return jsonify({"status_code": 200, "message": "Branch deleted"})
            except Exception as e:
                return jsonify({"status_code": e.args[0]['status_code'], "message": e.args[0]['message']})

    @app.route('/driver/create', methods=['POST'])
    def driver_create():
        if request.method == "POST":
            if request.data is None:
                return jsonify({"status_code": 400, "message": "Invalid request"})
            request_data = request.data

            try:
                first_name = helpers.check_missing('list', request_data, 'first_name')
                first_name = helpers.validate_string(first_name, 'first_name')
                middle_name = None
                if "middle_name" in request_data.keys():
                    middle_name = helpers.validate_string(request_data['middle_name'], 'middle_name')
                last_name = helpers.check_missing('list', request_data, 'last_name')
                last_name = helpers.validate_string(last_name, 'last_name')
                dob = helpers.check_missing('list', request_data, 'dob')
                dob = helpers.validate_dob(dob)
                driver = Driver(first_name, middle_name, last_name, dob)
                driver.save()
                return jsonify({"status_code": 201, "message": "Driver created"})
            except Exception as e:
                return jsonify({"status_code": e.args[0]['status_code'], "message": e.args[0]['message']})

    @app.route('/driver/get', methods=['GET'])
    def driver_get():
        if request.method == "GET":
            if request.args is None:
                return jsonify({"status_code": 400, "message": "Invalid request"})

            try:
                params = {}
                if "id" in request.args.keys():
                    params['id'] = helpers.validate_int(request.args.get('id'), 'id')
                if "first_name" in request.args.keys():
                    params["first_name"] = helpers.validate_string(request.args.get('first_name'), 'first_name')

                if "middle_name" in request.args.keys():
                    params["middle_name"] = helpers.validate_string(request.args.get('middle_name'), 'middle_name')

                if "last_name" in request.args.keys():
                    params["last_name"] = helpers.validate_string(request.args.get('last_name'), 'last_name')
                if "dob" in request.args.keys():
                    params["dob"] = helpers.validate_dob(request.args.get('dob'))

                if not params:
                    return jsonify({"status_code": 400, "message": "Invalid request"})
                driver = Driver.get(params)
                if not driver:
                    return jsonify({"status_code": 404, "message": "Driver not found"})
                return jsonify(driver.serialize())
            except Exception as e:
                return jsonify({"status_code": e.args[0]['status_code'], "message": e.args[0]['message']})

    @app.route('/driver/update', methods=['PUT'])
    def driver_update():
        if request.method == "PUT":
            if request.data is None:
                return jsonify({"status_code": 400, "message": "Invalid request"})
            request_data = request.data

            try:
                id = helpers.check_missing('list', request_data, 'id')
                id = helpers.validate_int(id, 'id')
                params = {"id": id}
                driver = Driver.get(params)
                if not driver:
                    return jsonify({"status_code": 404, "message": "Driver not found"})

                if "first_name" in request_data.keys():
                    driver.first_name = helpers.validate_string(request_data['first_name'], 'first_name')
                if "middle_name" in request_data.keys():
                    driver.middle_name = helpers.validate_string(request_data['middle_name'], 'middle_name')
                if "last_name" in request_data.keys():
                    driver.last_name = helpers.validate_string(request_data['last_name'], 'last_name')
                if "dob" in request_data.keys():
                    driver.dob = helpers.validate_dob(request_data["dob"])
                driver.save()
                return jsonify({"status_code": 200, "message": "Driver record was updated"})
            except Exception as e:
                return jsonify({"status_code": e.args[0]['status_code'], "message": e.args[0]['message']})

    @app.route('/driver/delete', methods=['DELETE'])
    def driver_delete():
        if request.method == "DELETE":
            if request.args is None:
                return jsonify({"status_code": 400, "message": "Invalid request"})

            try:
                id = helpers.check_missing('args', request, 'id')
                id = helpers.validate_int(id, 'id')
                params = {"id": id}
                driver = Driver.get(params)
                if not driver:
                    return jsonify({"status_code": 404, "message": "Driver not found"})
                driver.delete()
                return jsonify({"status_code": 200,"message": "Driver deleted"})
            except Exception as e:
                return jsonify({"status_code": e.args[0]['status_code'], "message": e.args[0]['message']})

    return app
