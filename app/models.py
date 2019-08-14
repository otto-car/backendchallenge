from app import db


class Car(db.Model):
    __tablename__ = 'car'

    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer(), nullable=False)
    assigned_type = db.Column(db.Integer(), nullable=True)
    assigned_id = db.Column(db.Integer(), nullable=True)

    def __init__(self, make, model, year, assigned_type=None, assigned_id=None):
        self.make = make
        self.model = model
        self.year = year
        self.assigned_type = assigned_type
        self.assigned_id = assigned_id

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def get(params):
        query = db.session.query(Car)
        for attr, value in params.items():
            query = query.filter(getattr(Car, attr) == value)
        return db.session.query(Car).first()

    def serialize(self):
        return {
            "id": self.id,
            "make": self.make,
            "model": self.model,
            "year": self.year,
            "assign_type": self.assigned_type,
            "assign_id": self.assigned_id
        }


class Branch(db.Model):
    __tablename__ = 'branch'

    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(60), nullable=False)
    postcode = db.Column(db.String(8), nullable=False)
    capacity = db.Column(db.Integer(), nullable=False)

    def __init__(self, city, postcode, capacity):
        self.city = city
        self.postcode = postcode
        self.capacity = capacity

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def get(params):
        query = db.session.query(Branch)
        for attr, value in params.items():
            query = query.filter(getattr(Branch, attr) == value)
        return db.session.query(Branch).first()

    def serialize(self):
        return {
            "id": self.id,
            "city": self.city,
            "postcode": self.postcode,
            "capacity": self.capacity
        }


class Driver(db.Model):
    __tablename__ = 'driver'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    dob = db.Column(db.Date, nullable=False)

    def __init__(self, name, dob):
        self.name = name
        self.dob = dob

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def get(driver_id):
        return db.session.query(Driver).filter(Driver.id == driver_id).first()

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "dob": self.dob.strftime('%d/%m/%Y')
        }