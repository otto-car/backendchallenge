from app import db


class Car(db.Model):
    __tablename__ = 'car'

    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(100))
    model = db.Column(db.String(100))
    year = db.Column(db.Integer())
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

    def get(car_id):
        return db.session.query(Car).filter(Car.id == car_id).first()

    def serialize(self):
        return {
            "make": self.make,
            "model": self.model,
            "year": self.year,
            "assign_type": self.assigned_type,
            "assign_id": self.assigned_id
        }