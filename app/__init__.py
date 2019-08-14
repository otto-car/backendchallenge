from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy
from instance.config import app_config
from flask import request, jsonify, abort
import re
import datetime
from datetime import date

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
            request_data = request.get_json(force=True)

            if request_data is None:
                return jsonify({
                    "status_code": 400,
                    "message": "Invalid request"
                })

            # Make, model and year are necessary in order to create a car object
            if "make" in request_data.keys():
                make = request_data['make']
            else:
                return jsonify({
                    "status_code": 400,
                    "message": "Missing make"
                })

            if "model" in request_data.keys():
                model = request_data['model']
            else:
                return jsonify({
                    "status_code": 400,
                    "message": "Missing model"
                })

            if "year" in request_data.keys():
                try:
                    int(request_data['year'])
                    if len(str(request_data['year'])) != 4:
                        return jsonify({
                            "status_code": 400,
                            "message": "Invalid year"
                        })
                    year = request_data['year']
                except:
                    return jsonify({
                        "status_code": 400,
                        "message": "Invalid year"
                    })
            else:
                return jsonify({
                    "status_code": 400,
                    "message": "Missing year"
                })

            assigned_type = None
            if "assigned_type" in request_data.keys():
                assigned_type = request_data['assigned_type']

            assigned_id = None
            if "assigned_id" in request_data.keys():
                assigned_id = request_data['assigned_id']

            if (assigned_type or assigned_id) and not (assigned_type and assigned_id):
                return jsonify({
                    "status_code": 400,
                    "message": "Both assigned type and id must be present"
                })

            car = Car(make, model, year, assigned_type, assigned_id)
            car.save()
            return jsonify({
                "status_code": 201,
                "message": "Car created"}
            )

    @app.route('/car/get', methods=['GET'])
    def car_get():
        if request.method == "GET":
            if request.args is None:
                return jsonify({
                    "status_code": 400,
                    "message": "Invalid request"
                })

            params = {}
            if "id" in request.args.keys():
                id = request.args.get('id')

                try:
                    int(id)
                except:
                    return jsonify({
                        "status_code": 400,
                        "message": "Invalid ID"
                    })

                params['id'] = id

            if "make" in request.args.keys():
                params['make'] = request.args.get('make')

            if "model" in request.args.keys():
                params['model'] = request.args.get('model')

            if "year" in request.args.keys():
                year = request.args.get('year')
                try:
                    int(year)
                    if len(str(year)) != 4:
                        return jsonify({
                            "status_code": 400,
                            "message": "Invalid year"
                        })
                    params['year'] = year
                except:
                    return jsonify({
                        "status_code": 400,
                        "message": "Invalid year"
                    })

            # check if params are empty
            if not params:
                return jsonify({
                    "status_code": 400,
                    "message": "Invalid request"
                })

            car = Car.get(params)

            if not car:
                return jsonify({
                    "status_code": 404,
                    "message": "Car not found"
                })

            return jsonify(car.serialize())

    @app.route('/car/update', methods=['PUT'])
    def car_update():
        if request.method == "PUT":
            request_data = request.get_json(force=True)

            if request_data is None:
                return jsonify({
                    "status_code": 400,
                    "message": "Invalid request"
                })

            if "id" not in request_data.keys():
                return jsonify({
                    "status_code": 400,
                    "message": "Missing ID"
                })

            id = request_data['id']

            try:
                int(id)
            except:
                return jsonify({
                    "status_code": 400,
                    "message": "Invalid ID"
                })
            params = {"id": id}

            car = Car.get(params)

            if not car:
                return jsonify({
                    "status_code": 404,
                    "message": "Car not found"
                })

            if "make" in request_data.keys():
                car.make = request_data['make']

            if "model" in request_data.keys():
                car.model = request_data['model']

            if "year" in request_data.keys():
                try:
                    int(request_data['year'])
                    if len(str(request_data['year'])) != 4:
                        return jsonify({
                            "status_code": 400,
                            "message": "Invalid year"
                        })
                    car.year = request_data['year']
                except:
                    return jsonify({
                        "status_code": 400,
                        "message": "Invalid year"
                    })

            car.save()

            return jsonify({
                "status_code": 200,
                "message": "Car record was updated"
            })

    @app.route('/car/assign', methods=['POST'])
    def car_assign():
        if request.method == "POST":
            request_data = request.get_json(force=True)

            if not "id" in request_data.keys():
                return jsonify({
                    "status_code": 400,
                    "message": "Missing ID"
                })
            params = {"id": request_data['id']}
            car = Car.get(params)

            if not car:
                return jsonify({
                    "status_code": 404,
                    "message": "Car not found"
                })

            if not "assigned_type" in request_data.keys():
                return jsonify({
                    "status_code": 400,
                    "message": "Missing assigned_type"
                })
            assigned_type = request_data["assigned_type"]
            try:
                int(assigned_type)
            except:
                return jsonify({
                    "status_code": 400,
                    "message": "Invalid assigned_type"
                })

            if assigned_type not in (0, 1, 2):
                return jsonify({
                    "status_code": 400,
                    "message": "Invalid assigned_type"
                })

            if assigned_type == 0:
                car.assigned_type = None
                car.assigned_id = None
                car.save()
                return jsonify({
                    "status_code": 200,
                    "message": "Unassigned car from everything"
                })

            if not "assigned_id" in request_data.keys():
                return jsonify({
                    "status_code": 400,
                    "message": "Missing assigned_id"
                })

            assigned_id = request_data["assigned_id"]
            try:
                int(assigned_id)
            except:
                return jsonify({
                    "status_code": 400,
                    "message": "Invalid assigned_id"
                })

            # type 1 is driver
            if assigned_type == 1:
                params = {"id": assigned_id}
                driver = Driver.get(params)
                if driver:
                    car.assigned_type = assigned_type
                    car.assigned_id = driver.id
                else:
                    return jsonify({
                        "status_code": 404,
                        "message": "Driver not found"
                    })

            # type 2 is branch
            if assigned_type == 2:

                params = {"id": assigned_id}
                branch = Branch.get(params)

                if branch:
                    occupancy = branch.get_assigned_cars_count(assigned_id)

                    if branch.capacity > occupancy:
                        car.assigned_type = assigned_type
                        car.assigned_id = assigned_id
                    else:
                        return jsonify({
                            "status_code": 400,
                            "message": "Branch has reached its capacity"
                        })
                else:
                    return jsonify({
                        "status_code": 404,
                        "message": "Branch not found"
                    })

            car.save()

            return jsonify({
                "status_code": 200,
                "message": "Successfully assigned a car"
            })

    @app.route('/car/delete', methods=['DELETE'])
    def car_delete():
        if request.method == "DELETE":

            if not "id" in request.args:
                return jsonify({
                    "status_code": 400,
                    "message": "Missing ID"
                })

            id = request.args.get("id")

            try:
                int(id)
            except:
                return jsonify({
                    "status_code": 400,
                    "message": "Invalid ID"
                })

            params = {"id": id}

            car = Car.get(params)

            if not car:
                return jsonify({
                    "status_code": 404,
                    "message": "Car not found"
                })

            car.delete()

            return jsonify({
                "status_code": 200,
                "message": "Car deleted"
            })

    @app.route('/branch/create', methods=['POST'])
    def branch_create():
        if request.method == "POST":
            request_data = request.get_json(force=True)

            if request_data is None:
                return jsonify({
                    "status_code": 400,
                    "message": "Invalid request"
                })

            if "city" in request_data.keys():
                city = request_data['city']
                if not isinstance(city, str):
                    return jsonify({
                        "status_code": 400,
                        "message": "Invalid city"
                    })
            else:
                return jsonify({
                    "status_code": 400,
                    "message": "Missing city"
                })

            if "postcode" in request_data.keys():
                postcode = str(request_data['postcode'])
                if len(postcode) > 8:
                    return jsonify({
                        "status_code": 400,
                        "message": "Invalid postcode"
                    })
                pattern = re.compile(r'\b[A-Z]{1,2}[0-9][A-Z0-9]? [0-9][ABD-HJLNP-UW-Z]{2}\b')
                if not pattern.match(postcode):
                    return jsonify({
                        "status_code": 400,
                        "message": "Invalid postcode"
                    })
            else:
                return jsonify({
                    "status_code": 400,
                    "message": "Missing postcode"
                })

            if "capacity" in request_data.keys():
                try:
                    int(request_data['capacity'])
                    capacity = request_data['capacity']
                except:
                    return jsonify({
                        "status_code": 400,
                        "message": "Invalid capacity"
                    })
            else:
                return jsonify({
                    "status_code": 400,
                    "message": "Missing capacity"
                })

            car = Branch(city, postcode, capacity)
            car.save()
            return jsonify({
                "status_code": 201,
                "message": "Branch created"}
            )

    @app.route('/branch/get', methods=['GET'])
    def branch_get():
        if request.method == "GET":
            if request.args is None:
                return jsonify({
                    "status_code": 400,
                    "message": "Invalid request"
                })

            params = {}
            if "id" in request.args.keys():
                id = request.args.get('id')

                try:
                    int(id)
                except:
                    return jsonify({
                        "status_code": 400,
                        "message": "Invalid ID"
                    })

                params['id'] = id

            if "city" in request.args.keys():
                city = request.args.get('city')
                if not isinstance(city, str):
                    return jsonify({
                        "status_code": 400,
                        "message": "Invalid city"
                    })

                params['city'] = city

            if "postcode" in request.args.keys():
                postcode = request.args.get('postcode')

                if len(postcode) > 8:
                    return jsonify({
                        "status_code": 400,
                        "message": "Invalid postcode"
                    })

                pattern = re.compile(r'\b[A-Z]{1,2}[0-9][A-Z0-9]? [0-9][ABD-HJLNP-UW-Z]{2}\b')
                if not pattern.match(postcode):
                    return jsonify({
                        "status_code": 400,
                        "message": "Invalid postcode"
                    })

                params["postcode"] = postcode

            if not params:
                return jsonify({
                    "status_code": 400,
                    "message": "Invalid request"
                })

            branch = Branch.get(params)
            if not branch:
                return jsonify({
                    "status_code": 404,
                    "message": "Branch not found"
                })

            return jsonify(branch.serialize())

    @app.route('/branch/update', methods=['PUT'])
    def branch_update():
        if request.method == "PUT":
            request_data = request.get_json(force=True)

            if request_data is None:
                return jsonify({
                    "status_code": 400,
                    "message": "Invalid request"
                })

            if "id" not in request_data.keys():
                return jsonify({
                    "status_code": 400,
                    "message": "Missing ID"
                })

            id = request_data['id']

            try:
                int(id)
            except:
                return jsonify({
                    "status_code": 400,
                    "message": "Invalid ID"
                })
            params = {"id": id}
            branch = Branch.get(params)

            if not branch:
                return jsonify({
                    "status_code": 404,
                    "message": "Branch not found"
                })

            if "city" in request_data.keys():
                city = request_data['city']

                if not isinstance(city, str):
                    return jsonify({
                        "status_code": 400,
                        "message": "Invalid city"
                    })

                branch.city = city

            if "postcode" in request_data.keys():
                postcode = request_data['postcode']
                if len(postcode) > 8:
                    return jsonify({
                        "status_code": 400,
                        "message": "Invalid postcode"
                    })
                pattern = re.compile(r'\b[A-Z]{1,2}[0-9][A-Z0-9]? [0-9][ABD-HJLNP-UW-Z]{2}\b')
                if not pattern.match(postcode):
                    return jsonify({
                        "status_code": 400,
                        "message": "Invalid postcode"
                    })
                branch.postcode = request_data['postcode']

            if "capacity" in request_data.keys():
                try:
                    int(request_data['capacity'])
                    branch.capacity = request_data['capacity']
                except:
                    return jsonify({
                        "status_code": 400,
                        "message": "Invalid capacity"
                    })

            branch.save()

            return jsonify({
                "status_code": 200,
                "message": "Branch record was updated"
            })

    @app.route('/branch/delete', methods=['DELETE'])
    def branch_delete():
        if request.method == "DELETE":

            if not "id" in request.args:
                return jsonify({
                    "status_code": 400,
                    "message": "Missing ID"
                })

            id = request.args.get("id")

            try:
                int(id)
            except:
                return jsonify({
                    "status_code": 400,
                    "message": "Invalid ID"
                })

            params = {"id": id}
            branch = Branch.get(params)

            if not branch:
                return jsonify({
                    "status_code": 404,
                    "message": "Branch not found"
                })

            branch.delete()

            return jsonify({
                "status_code": 200,
                "message": "Branch deleted"
            })

    @app.route('/driver/create', methods=['POST'])
    def driver_create():
        if request.method == "POST":
            request_data = request.get_json(force=True)

            if request_data is None:
                return jsonify({
                    "status_code": 400,
                    "message": "Invalid request"
                })

            if "first_name" in request_data.keys():
                first_name = request_data['first_name']
                if not isinstance(first_name, str):
                    return jsonify({
                        "status_code": 400,
                        "message": "Invalid first_name"
                    })
            else:
                return jsonify({
                    "status_code": 400,
                    "message": "Missing name"
                })

            middle_name = None
            if "middle_name" in request_data.keys():
                middle_name = request_data['middle_name']
                if not isinstance(middle_name, str):
                    return jsonify({
                        "status_code": 400,
                        "message": "Invalid middle_name"
                    })

            if "last_name" in request_data.keys():
                last_name = request_data['last_name']
                if not isinstance(last_name, str):
                    return jsonify({
                        "status_code": 400,
                        "message": "Invalid last_name"
                    })
            else:
                return jsonify({
                    "status_code": 400,
                    "message": "Missing name"
                })

            if "dob" in request_data.keys():
                try:
                    dob = datetime.datetime.strptime(request_data['dob'], '%d/%m/%Y')

                    # Won't let drivers below age 18 to join
                    min_age = datetime.timedelta(weeks=52 * 18)
                    if datetime.datetime.now() - dob < min_age:
                        return jsonify({
                            "status_code": 400,
                            "message": "Invalid DOB"
                        })

                    dob = dob.strftime("%m/%d/%Y")

                except:
                    return jsonify({
                        "status_code": 400,
                        "message": "Invalid DOB"
                    })
            else:
                return jsonify({
                    "status_code": 400,
                    "message": "Missing DOB"
                })

            driver = Driver(first_name, middle_name, last_name, dob)
            driver.save()
            return jsonify({
                "status_code": 201,
                "message": "Driver created"}
            )

    @app.route('/driver/get', methods=['GET'])
    def driver_get():
        if request.method == "GET":
            if request.args is None:
                return jsonify({
                    "status_code": 400,
                    "message": "Invalid request"
                })

            params = {}

            if "id" in request.args.keys():
                id = request.args.get('id')

                try:
                    int(id)
                except:
                    return jsonify({
                        "status_code": 400,
                        "message": "Invalid ID"
                    })

                params['id'] = id

            if "first_name" in request.args.keys():
                params["first_name"] = request.args.get('first_name')

            if "middle_name" in request.args.keys():
                params["middle_name"] = request.args.get('middle_name')

            if "last_name" in request.args.keys():
                params["last_name"] = request.args.get('last_name')

            if "dob" in request.args.keys():
                dob = datetime.datetime.strptime(request.args.get('dob'), '%d/%m/%Y')
                params["dob"] = dob.strftime("%m/%d/%Y")

            if not params:
                return jsonify({
                    "status_code": 400,
                    "message": "Invalid request"
                })

            driver = Driver.get(params)

            if not driver:
                return jsonify({
                    "status_code": 404,
                    "message": "Driver not found"
                })

            return jsonify(driver.serialize())

    @app.route('/driver/update', methods=['PUT'])
    def driver_update():
        if request.method == "PUT":
            request_data = request.get_json(force=True)

            if request_data is None:
                return jsonify({
                    "status_code": 400,
                    "message": "Invalid request"
                })

            if "id" not in request_data.keys():
                return jsonify({
                    "status_code": 400,
                    "message": "Missing ID"
                })

            id = request_data['id']

            try:
                int(id)
            except:
                return jsonify({
                    "status_code": 400,
                    "message": "Invalid ID"
                })

            params = {"id": id}
            driver = Driver.get(params)

            if not driver:
                return jsonify({
                    "status_code": 404,
                    "message": "Driver not found"
                })

            if "first_name" in request_data.keys():
                first_name = request_data['first_name']
                if not isinstance(first_name, str):
                    return jsonify({
                        "status_code": 400,
                        "message": "Invalid first_name"
                    })
                driver.first_name = first_name

            if "middle_name" in request_data.keys():
                middle_name = request_data['middle_name']
                if not isinstance(middle_name, str):
                    return jsonify({
                        "status_code": 400,
                        "message": "Invalid middle_name"
                    })
                driver.middle_name = middle_name

            if "last_name" in request_data.keys():
                last_name = request_data['last_name']
                if not isinstance(last_name, str):
                    return jsonify({
                        "status_code": 400,
                        "message": "Invalid last_name"
                    })
                driver.last_name = last_name


            if "dob" in request_data.keys():
                try:
                    dob = datetime.datetime.strptime(request_data['dob'], '%d/%m/%Y')

                    # Won't let drivers below age 18 to join
                    min_age = datetime.timedelta(weeks=52 * 18)
                    if datetime.datetime.now() - dob < min_age:
                        return jsonify({
                            "status_code": 400,
                            "message": "Invalid DOB"
                        })

                    driver.dob = request_data['dob']

                except:
                    return jsonify({
                        "status_code": 400,
                        "message": "Invalid DOB"
                    })

            driver.save()

            return jsonify({
                "status_code": 200,
                "message": "Driver record was updated"
            })

    @app.route('/driver/delete', methods=['DELETE'])
    def driver_delete():
        if request.method == "DELETE":

            if not "id" in request.args:
                return jsonify({
                    "status_code": 400,
                    "message": "Missing driver ID"
                })

            id = request.args.get("id")

            try:
                int(id)
            except:
                return jsonify({
                    "status_code": 400,
                    "message": "Invalid driver ID"
                })

            params = {"id": id}
            driver = Driver.get(params)

            if not driver:
                return jsonify({
                    "status_code": 404,
                    "message": "Driver not found"
                })

            driver.delete()

            return jsonify({
                "status_code": 200,
                "message": "Driver deleted"
            })

    return app
