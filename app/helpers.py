# Helper function for validating missing fields
def check_missing(format, data, field):
    if format == "json":
        pass
    if format == "list":
        if field in data.keys():
            return data[field]
        else:
            raise Exception({"status_code": 400, "message": "Missing " + field})


def check_correct_year(year):
    try:
        int(year)
        if len(str(year)) != 4:
            raise Exception({"status_code": 400, "message": "Invalid year"})
        return year
    except:
        raise Exception({"status_code": 400, "message": "Invalid year"})


def check_int(number, field):
    try:
        int(number)
        return number
    except:
        raise Exception({"status_code": 400, "message": "Invalid " + field})


def validate_assigning(assigned_type, assigned_id):
    from app.models import Branch, Driver
    if assigned_type not in (1, 2):
        return Exception({"status_code": 400, "message": "Invalid assigned type"})

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
                assigned_id = assigned_id
            else:
                return Exception({"status_code": 400, "message": "Branch has reached its capacity"})
        else:
            return Exception({"status_code": 404, "message": "Branch not found"})