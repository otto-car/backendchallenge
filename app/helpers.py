import re
UK_POSTCODE_PATTERN = r'\b[A-Z]{1,2}[0-9][A-Z0-9]?( )?[0-9][ABD-HJLNP-UW-Z]{2}\b'


# Helper function for validating missing fields
def check_missing(format, data, field):
    if format == "args":
        if field in data.args.keys():
            return data.args.get(field)
        else:
            raise Exception({"status_code": 400, "message": "Missing " + field})
    if format == "list":
        if field in data.keys():
            return data[field]
        else:
            raise Exception({"status_code": 400, "message": "Missing " + field})


def validate_year(year):
    try:
        int(year)
        if len(str(year)) != 4:
            raise Exception({"status_code": 400, "message": "Invalid year"})
        return year
    except:
        raise Exception({"status_code": 400, "message": "Invalid year"})


def validate_int(number, field):
    try:
        int(number)
        return number
    except:
        raise Exception({"status_code": 400, "message": "Invalid " + field})


def validate_string(string, field):
    if not isinstance(string, str):
        raise Exception({"status_code": 400, "message": "Invalid " + field})
    return string


def validate_postcode(postcode):
    postcode = str(postcode)
    if len(postcode) > 8:
        raise Exception({"status_code": 400, "message": "Invalid postcode"})
    pattern = re.compile(UK_POSTCODE_PATTERN)
    if not pattern.match(postcode):
        raise Exception({"status_code": 400, "message": "Invalid postcode"})
    return postcode.upper()


def validate_assigning(assigned_type, assigned_id):
    from app.models import Branch, Driver

    if assigned_type not in (1, 2):
        raise Exception({"status_code": 400, "message": "Invalid assigned type"})

    # type 1 is driver
    if assigned_type == 1:
        params = {"id": assigned_id}
        driver = Driver.get(params)
        if driver:
            assigned_id = driver.id
            return [assigned_type, assigned_id]
        else:
            raise Exception({"status_code": 404, "message": "Driver not found"})

    # type 2 is branch
    if assigned_type == 2:
        params = {"id": assigned_id}
        branch = Branch.get(params)

        if branch:
            occupancy = branch.get_assigned_cars_count(assigned_id)
            if branch.capacity > occupancy:
                return [assigned_type, assigned_id]
            else:
                raise Exception({"status_code": 400, "message": "Branch has reached its capacity"})
        else:
            raise Exception({"status_code": 404, "message": "Branch not found"})