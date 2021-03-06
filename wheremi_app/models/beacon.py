from wheremi_app import sql as db
from datetime import datetime


class Beacon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    identifier = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    home_floor_id = db.Column(db.Integer, db.ForeignKey('floor.id'), nullable=False)
    description = db.Column(db.String(150), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    x = db.Column(db.Integer, nullable=False, default=0)
    y = db.Column(db.Integer, nullable=False, default=0)

    accuracy = db.Column(db.Boolean, nullable=False, default=False)

    decay = db.Column(db.Float)
    rssi_ref = db.Column(db.Float)

    home_floor = db.relationship('Floor', foreign_keys=home_floor_id)

    def __init__(self, identifier, home_floor_id, name, description, x, y, accuracy=False, decay=None, rssi_ref=None):
        self.identifier = identifier
        self.home_floor_id = home_floor_id
        self.name = name
        self.description = description
        self.x = x
        self.y = y
        self.accuracy = accuracy
        if accuracy:
            self.decay = decay
            self.rssi_ref = rssi_ref

    def __str__(self):
        return "" + str(self.id) + " - " + self.name

    def serialize(self):

        ret = {
            'id': self.id,
            'identifier': self.identifier,
            'name': self.name,
            'home_floor_id': self.home_floor_id,
            'description': self.description,
            'created_at': self.created_at,
            'x': self.x,
            'y': self.y,
            'accuracy': self.accuracy,
        }

        if self.accuracy:
            ret['decay'] = self.decay,
            ret['rssi_ref'] = self.rssi_ref

        return ret

    def serialize_for_map(self):
        return {
            'identifier': self.identifier,
            'name': self.name,
            'home_floor_id': self.home_floor_id,
            'description': self.description,
            'created_at': self.created_at,
            'x': self.home_floor.get_x_coordinate_on_map(self.x),
            'y': self.home_floor.get_y_coordinate_on_map(self.y)
        }
