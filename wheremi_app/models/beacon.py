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

    home_floor = db.relationship('Floor', foreign_keys=home_floor_id)

    def __init__(self, identifier, home_floor_id, name, description):
        self.identifier = identifier
        self.home_floor_id = home_floor_id
        self.name = name
        self.description = description

    def __str__(self):

        return "" + str(self.id) + " - " + self.name
